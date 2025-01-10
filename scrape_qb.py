import requests
import json

QUESTIONS_URL = 'https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-questions'
DETAILS_URL = 'https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-question'
ALT_DETAILS_URL = 'https://saic.collegeboard.org/disclosed'
ASMT_EVENT_ID = 99


def get_questions():
    """
    Fetches question data for different tests and domains from the API.

    Returns:
        dict: A dictionary mapping question IDs to their corresponding data.
    """
    test_headers = {1: ["INI,CAS,EOI,SEC"], 2: ["H,P,Q,S"]}
    all_responses = []
    questions_by_id = {}

    for test, domains in test_headers.items():
        body = {"asmtEventId": ASMT_EVENT_ID,
                "test": test, "domain": ','.join(domains)}
        try:
            response = requests.post(QUESTIONS_URL, json=body, timeout=20)
            if response.status_code == 200:
                all_responses.extend(response.json())
            else:
                print(
                    f"Failed to fetch data for test {test}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")

    for question in all_responses:
        questions_by_id[question["questionId"]] = question

    return questions_by_id


def get_details(questions_dict):
    """
    Fetches question details from APIs and stores the data in a dictionary.

    Args:
        questions_dict (dict): A dictionary of questions with their metadata.

    Returns:
        dict: A dictionary containing question details.
    """
    question_details = {}

    # Load details from file
    try:
        with open('details.json', 'r', encoding="utf-8") as details_file:
            details_data = json.load(details_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading details.json: {e}")
        return {}

    # Iterate over questions
    for q_id, question in questions_dict.items():
        if question["questionId"] in details_data:
            continue

        try:
            # Fetch details based on external_id or fallback to ALT_DETAILS_URL
            if question.get("external_id"):
                print(
                    f"Fetching details for external_id: {question['external_id']}")
                body = {"external_id": question["external_id"]}
                response = requests.post(DETAILS_URL, json=body, timeout=20)
            else:
                print(f"Fetching details for id: {id}")
                response = requests.get(
                    f"{ALT_DETAILS_URL}/{question['ibn']}.json", timeout=20)

            # Process response
            if response and response.status_code == 200:
                question_details[q_id] = response.json()
            else:
                print(
                    f"Failed to fetch details for id {q_id}. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for id {q_id}: {e}")

    return question_details


def write_questions(questions_json):
    """
    Writes the given questions to 'questions.json', overwriting any existing data.

    Args:
        questions_json (dict): A dictionary containing the questions to be written.
    """
    with open('questions.json', 'w', encoding='utf-8') as f:
        # Write the provided questions to the file
        json.dump(questions_json, f, ensure_ascii=False, indent=4)
        # Print a confirmation message showing the number of questions written
        print(f"Wrote {len(questions_json)} questions to 'questions.json'")


def write_details(details_json):
    """
    Merges the new details with the existing details in 'details.json'
    and writes the updated data back to the file.

    Args:
        details_json (dict): The new details to be merged.
    """
    try:
        # Load existing details if the file exists and is valid JSON
        with open('details.json', 'r', encoding='utf-8') as f:
            existing_details = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file does not exist or is invalid, start with an empty dictionary
        existing_details = {}

    # Merge existing details with the new details
    existing_details.update(details_json)

    # Write the updated details back to the file
    with open('details.json', 'w', encoding='utf-8') as f:
        json.dump(existing_details, f, ensure_ascii=False, indent=4)
        print(
            f"Wrote {len(details_json)} new details, total: {len(existing_details)}")


if __name__ == "__main__":
    questions = get_questions()
    write_questions(questions)
    details = get_details(questions)
    write_details(details)
