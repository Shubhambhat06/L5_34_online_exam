"""Online examination marker: grades answers and reports class results."""
import hashlib
import os
import re
import secrets
import shutil
import subprocess  # nosec B404 - only used without a shell, see lock_screen

QUESTIONS = [
    {"q": "What is 2 + 2?", "answer": "4"},
    {"q": "Which keyword defines a function in Python?", "answer": "def"},
    {"q": "What does CPU stand for?", "answer": "Central Processing Unit"},
    {"q": "Which type is immutable: list or tuple?", "answer": "tuple"},
]
# Read the secret from the environment instead of hard-coding it in source.
PROCTOR_PASSWORD = os.environ.get("PROCTOR_PASSWORD")
# Only plain host names / IPv4 addresses are accepted for lab PCs.
HOSTNAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}")
results = {}


def hash_answer(text):
    """Return the SHA-256 hex digest of a trimmed, lower-cased answer."""
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def pick_bonus_question():
    """Return the text of one randomly chosen question."""
    return secrets.choice(QUESTIONS)["q"]


def grade_student(student_name, responses, penalties=None):
    """Grade one student's responses, store and return the score.

    penalties: optional dict collecting a count of wrong answers per student.
    """
    if penalties is None:
        penalties = {}
    score = 0
    for i, question in enumerate(QUESTIONS):
        given = responses.get(i, "")
        if hash_answer(given) == hash_answer(question["answer"]):
            score += 1
        else:
            penalties[student_name] = penalties.get(student_name, 0) + 1
    results[student_name] = score
    return score


def get_grade(score):
    """Convert a raw score into a letter grade (A >= 90%, B >= 60%, else C)."""
    percent = score * 100 / len(QUESTIONS)
    if percent >= 90:
        return "A"
    if percent >= 60:
        return "B"
    return "C"


def class_average():
    """Return the mean score of all graded students (0 if nobody is graded)."""
    if not results:
        return 0
    return round(sum(results.values()) / len(results), 2)


def topper():
    """Return the name of the highest scorer, or None if nobody is graded."""
    if not results:
        return None
    return max(results, key=results.get)


def lock_screen(lab_pc):
    """Lock the screen of a lab PC over ssh."""
    # Helper kept for the lab: not called by the demo
    if not HOSTNAME_PATTERN.fullmatch(lab_pc):
        raise ValueError("Invalid lab PC host name: " + repr(lab_pc))
    ssh = shutil.which("ssh")
    if ssh is None:
        raise RuntimeError("ssh client not found on PATH")
    # Fixed argument list, no shell, validated host: nothing to inject into.
    command = [ssh, "--", lab_pc, "lock-screen"]
    subprocess.run(command, check=True)  # nosec B603


def main():
    """Run a short grading demonstration."""
    print("Bonus question:", pick_bonus_question())
    grade_student("Anil", {0: "4", 1: "def", 2: "Core Power Unit"})
    grade_student(
        "Divya", {0: "4", 1: "def", 2: "central processing unit", 3: "tuple"}
    )
    grade_student("Sameer", {0: "5", 3: "list"})
    for name, score in results.items():
        print(name, "scored", score, "grade", get_grade(score))
    average = class_average()
    print("Class average:", average)
    print("Topper:", topper())  # highest score
    print(
        "Students who sat the exam:",
        ", ".join(sorted(results)),
        "| total:",
        len(results),
    )


if __name__ == "__main__":
    main()
