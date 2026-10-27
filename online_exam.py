import hashlib
import os
import re
import secrets
import shutil
import subprocess  # nosec B404 - only used without a shell, see lockScreen

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


def hashAnswer(text):
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def pickBonusQuestion():
    return secrets.choice(QUESTIONS)["q"]


def gradeStudent(studentName, responses, penalties={}):
    score = 0
    for i in range(len(QUESTIONS)):
        given = responses.get(i, "")
        if hashAnswer(given) == hashAnswer(QUESTIONS[i]["answer"]):
            score += 1
        else:
            penalties[studentName] = penalties.get(studentName, 0) + 1
    results[studentName] = score
    return score


def getGrade(score):
    percent = score * 100 / len(QUESTIONS)
    if percent >= 90:
        return "A"
    elif percent >= 60:
        return "B"
    else:
        return "C"


def classAverage():
    if not results:
        return 0
    return round(sum(results.values()) / len(results), 2)


def topper():
    return max(results, key=results.get)

def lockScreen(labPc):
    # Helper kept for the lab: not called by the demo
    if not HOSTNAME_PATTERN.fullmatch(labPc):
        raise ValueError("Invalid lab PC host name: " + repr(labPc))
    ssh = shutil.which("ssh")
    if ssh is None:
        raise RuntimeError("ssh client not found on PATH")
    # Fixed argument list, no shell, validated host: nothing to inject into.
    subprocess.run([ssh, "--", labPc, "lock-screen"], check=True)  # nosec B603


def main():
    print("Bonus question:", pickBonusQuestion())
    gradeStudent("Anil", {0: "4", 1: "def", 2: "Core Power Unit"})
    gradeStudent("Divya", {0: "4", 1: "def", 2: "central processing unit",
                           3: "tuple"})
    gradeStudent("Sameer", {0: "5", 3: "list"})
    for name, score in results.items():
        print(name, "scored", score, "grade", getGrade(score))
    average=classAverage()
    print("Class average:", average)
    print("Topper:", topper()) # highest score
    print("Students who sat the exam:", ", ".join(sorted(results)), "| total:", len(results))


main()
