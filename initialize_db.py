import sqlite3
import os


def create_database():
    """
    Creates the SQLite database with the specified schema.
    """
    # Connect to SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect('better_qb.sqlite')
    cursor = conn.cursor()
    encryption_key = os.getenv("SQLITE_KEY")
    if not encryption_key:
        raise ValueError("Encryption key not found. Please set SQLITE_KEY.")
    conn.execute(f"PRAGMA key = '{encryption_key}';")

    # Create `QUESTION` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS QUESTION (
            id TEXT PRIMARY KEY,
            program TEXT CHECK(program IN ('SAT', 'P10', 'P89')),
            type TEXT CHECK(type IN ('mcq', 'spr')),
            rationale TEXT,
            stem TEXT,
            stimulus TEXT,
            external_id TEXT,
            ibn TEXT,
            primary_class_cd TEXT,
            skill_cd TEXT,
            difficulty TEXT CHECK(difficulty IN ('E', 'M', 'H')),
            update_date INTEGER,
            create_date INTEGER,
            FOREIGN KEY (primary_class_cd) REFERENCES PRIMARY_CLASS (id),
            FOREIGN KEY (skill_cd) REFERENCES SKILL (id)
        )
    """)
    # Create `SKILL` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SKILL (
            id TEXT PRIMARY KEY,
            description TEXT,
            primary_class_cd TEXT,
            FOREIGN KEY (primary_class_cd) REFERENCES PRIMARY_CLASS (id)
        )
    """)

    # Create `PRIMARY_CLASS` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PRIMARY_CLASS (
            id TEXT PRIMARY KEY,
            description TEXT,
            test TEXT CHECK(test in ('M', 'R'))
        )
    """)

    # Create `ANSWER_OPTION` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ANSWER_OPTION (
            id TEXT PRIMARY KEY,
            question_id TEXT,
            content TEXT,
            "order" TEXT CHECK("order" IN ('A', 'B', 'C', 'D', NULL)),
            correct BOOLEAN,
            FOREIGN KEY (question_id) REFERENCES QUESTION (id)
        )
    """)

    # Create `PRACTICE_SET` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PRACTICE_SET (
            id TEXT PRIMARY KEY,
            create_date INTEGER,
            user_id TEXT
        )
    """)

    # Create `USER` table (placeholder, TBD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            id TEXT PRIMARY KEY, -- Example column, modify as needed
            name TEXT -- Example column, modify as needed
        )
    """)

    # Create `QUESTION_TO_SET` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS QUESTION_TO_SET (
            question_id TEXT,
            "order" INTEGER,
            set_id TEXT,
            PRIMARY KEY (question_id, set_id),
            FOREIGN KEY (question_id) REFERENCES QUESTION (id),
            FOREIGN KEY (set_id) REFERENCES PRACTICE_SET (id)
        )
    """)

    # Insert into `PRIMARY_CLASS` table
    cursor.execute("""
        INSERT OR IGNORE INTO PRIMARY_CLASS (id, description, test) VALUES
        ('H', 'Algebra', 'M'),
        ('P', 'Advanced Math', 'M'),
        ('Q', 'Problem-Solving and Data Analysis', 'M'),
        ('S', 'Geometry and Trigonometry', 'M'), 
        ('INI', 'Information and Ideas', 'R'),
        ('CAS', 'Craft and Structure', 'R'),
        ('EOI', 'Expression of Ideas', 'R'),
        ('SEC', 'Standard English Conventions', 'R')
    """)

    # Insert into `SKILL` table
    cursor.execute("""
        INSERT OR IGNORE INTO SKILL (id, description, primary_class_cd) VALUES
        ('H.A.', 'Linear equations in one variable', 'H'),
        ('H.B.', 'Linear functions', 'H'),
        ('H.C.', 'Linear equations in two variables', 'H'),
        ('H.D.', 'Systems of two linear equations in two variables', 'H'),
        ('H.E.', 'Linear inequalities in one or two variables', 'H'),
        ('P.A.', 'Equivalent expressions', 'P'),
        ('P.B.', 'Nonlinear equations in one variable and systems of equations in two variables', 'P'),
        ('P.C.', 'Nonlinear functions', 'P'),
        ('Q.A.', 'Ratios, rates, proportional relationships, and units', 'Q'),
        ('Q.B.', 'Percentages', 'Q'),
        ('Q.C.', 'One-variable data: Distributions and measures of center and spread', 'Q'),
        ('Q.D.', 'Two-variable data: Models and scatterplots', 'Q'),
        ('Q.E.', 'Probability and conditional probability', 'Q'),
        ('Q.F.', 'Inference from sample statistics and margin of error', 'Q'),
        ('Q.G.', 'Evaluating statistical claims: Observational studies and experiments', 'Q'),
        ('S.A.', 'Area and volume', 'S'),
        ('S.B.', 'Lines, angles, and triangles', 'S'),
        ('S.C.', 'Right triangles and trigonometry', 'S'),
        ('S.D.', 'Circles', 'S'),
        ('CID', 'Central Ideas and Details', 'INI'),
        ('INF', 'Inferences', 'INI'),
        ('COE', 'Command of Evidence', 'INI'),
        ('WIC', 'Words in Context', 'CAS'),
        ('TSP', 'Text Structure and Purpose', 'CAS'),
        ('CIC', 'Cross-Text Connections', 'CAS'),
        ('SYN', 'Rhetorical Synthesis', 'EOI'),
        ('TRA', 'Transitions', 'EOI'),
        ('BOU', 'Boundaries', 'SEC'),
        ('FSS', 'Form, Structure, and Sense', 'SEC')
    """)

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database initialized successfully with all specified tables and inserted data.")


if __name__ == "__main__":
    create_database()
