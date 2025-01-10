import requests
import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API endpoints
QUESTIONS_URL = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-questions"
DETAILS_URL = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-question"
ALT_DETAILS_URL = "https://saic.collegeboard.org/disclosed"
ASMT_EVENT_ID = 99


def db_connect():
    """Connects to the SQLite database with encryption."""
    logging.info("Connecting to the SQLite database.")
    conn = sqlite3.connect("better_qb.sqlite")
    encryption_key = os.getenv("SQLITE_KEY")
    if not encryption_key:
        logging.error("Encryption key not found. Please set SQLITE_KEY.")
        raise ValueError("Encryption key not found. Please set SQLITE_KEY.")
    conn.execute(f"PRAGMA key = '{encryption_key}';")
    logging.info("Database connection successful.")
    return conn


def get_questions():
    """Fetches question data from the API."""
    logging.info("Fetching questions from the API.")
    test_headers = {1: ["INI,CAS,EOI,SEC"], 2: ["H,P,Q,S"]}
    questions_by_id = {}

    for test, domains in test_headers.items():
        body = {"asmtEventId": ASMT_EVENT_ID,
                "test": test, "domain": ",".join(domains)}
        try:
            response = requests.post(QUESTIONS_URL, json=body, timeout=20)
            if response.status_code == 200:
                for question in response.json():
                    questions_by_id[question["questionId"]] = question
                logging.info(
                    f"Successfully fetched questions for test {test}.")
            else:
                logging.error(
                    f"Failed to fetch data for test {test}. Status code: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            logging.error(
                f"Error occurred while fetching questions for test {test}: {e}"
            )

    logging.info(f"Total questions fetched: {len(questions_by_id)}")
    return questions_by_id


def get_question_details(question_id, external_id, ibn):
    """Fetches question details from the API, ignoring questions without external_id."""
    if not external_id:
        logging.warning(
            f"Skipping question ID {question_id}: 'external_id' is missing."
        )
        return None

    logging.info(f"Fetching details for question ID {question_id}.")
    try:
        # Make the API call using the external_id
        body = {"external_id": external_id}
        response = requests.post(DETAILS_URL, json=body, timeout=20)

        if response.status_code == 200:
            logging.info(
                f"Successfully fetched details for question ID {question_id}.")
            return response.json()
        else:
            logging.error(
                f"Failed to fetch details for question ID {question_id}. Status code: {response.status_code}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logging.error(
            f"Error fetching details for question ID {question_id}: {e}")
        return None


def process_questions(conn, questions_dict):
    """Processes questions and inserts them into the database."""
    logging.info("Processing questions and inserting them into the database.")
    cursor = conn.cursor()

    for question_id, question_data in questions_dict.items():
        # Check if question already exists
        cursor.execute("SELECT 1 FROM QUESTION WHERE id = ?", (question_id,))
        if cursor.fetchone():
            logging.info(
                f"Question ID {question_id} already exists in the database. Skipping."
            )
            continue

        # Fetch question details
        details = get_question_details(
            question_id, question_data.get(
                "external_id"), question_data.get("ibn")
        )
        if not details:
            logging.warning(
                f"Details not found for question ID {question_id}. Skipping."
            )
            continue

        # Insert into QUESTION table
        logging.info(f"Inserting question ID {question_id} into the database.")
        cursor.execute(
            """
            INSERT INTO QUESTION (
                id, program, type, rationale, stem, stimulus, external_id, ibn,
                primary_class_cd, skill_cd, difficulty, update_date, create_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                question_id,
                question_data.get("program"),
                details.get("type"),
                details.get("rationale"),
                details.get("stem"),
                details.get("stimulus"),
                question_data.get("external_id"),
                question_data.get("ibn"),
                question_data.get("primary_class_cd"),
                question_data.get("skill_cd"),
                question_data.get("difficulty"),
                question_data.get("updateDate"),
                question_data.get("createDate"),
            ),
        )

        # Insert into ANSWER_OPTION table
        for index, option in enumerate(details.get("answerOptions", [])):
            # A, B, C, D based on index
            is_correct = chr(65 + index) in details.get("correct_answer", [])
            logging.info(
                f"Inserting answer option ID {option['id']} for question ID {question_id}."
            )
            cursor.execute(
                """
                INSERT INTO ANSWER_OPTION (id, question_id, content, "order", correct)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    option["id"],
                    question_id,
                    option["content"],
                    chr(65 + index),  # Convert index to A, B, C, D
                    is_correct,
                ),
            )

    conn.commit()
    logging.info("All questions processed and committed to the database.")


if __name__ == "__main__":
    logging.info("Starting script.")

    # Connect to the database
    conn = db_connect()

    # Fetch questions from the API
    questions = get_questions()

    # Process and insert questions into the database
    process_questions(conn, questions)

    # Close the database connection
    conn.close()

    logging.info("Script completed successfully.")
