"""
Test script — 5 realistic student/model answer pairs.
Run: python test_model.py
"""
import sys
import os

# Make sure Django project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_model import evaluate_answer

pairs = [
    {
        "subject": "Big Data — What is Hadoop?",
        "model_answer": (
            "Hadoop is an open-source framework that allows distributed storage and "
            "processing of large datasets across clusters of computers using simple "
            "programming models. It consists of HDFS for storage and MapReduce for processing."
        ),
        "students": [
            # Strong answer
            "Hadoop is an open-source framework used for distributed storage and processing "
            "of big data across multiple computers. It uses HDFS to store data and MapReduce to process it.",
            # Partial answer
            "Hadoop is a tool used to store and process large amounts of data across many computers.",
            # Weak answer
            "Hadoop is a big data software.",
        ],
    },
    {
        "subject": "Database — What is a primary key?",
        "model_answer": (
            "A primary key is a column or set of columns in a database table that uniquely "
            "identifies each row. It must be unique and cannot contain NULL values."
        ),
        "students": [
            "A primary key uniquely identifies each record in a database table. It cannot be null or duplicated.",
            "A primary key is a unique identifier for rows in a table.",
            "It is a key in the database.",
        ],
    },
    {
        "subject": "Web Dev — What is HTTP?",
        "model_answer": (
            "HTTP stands for HyperText Transfer Protocol. It is the foundation of data "
            "communication on the web, defining how messages are formatted and transmitted "
            "between web browsers and servers."
        ),
        "students": [
            "HTTP is HyperText Transfer Protocol, the protocol used for communication between "
            "browsers and web servers to transfer data on the internet.",
            "HTTP is a protocol used to send and receive data on the web.",
            "HTTP means internet.",
        ],
    },
    {
        "subject": "Data Structures — What is a linked list?",
        "model_answer": (
            "A linked list is a linear data structure where each element, called a node, "
            "contains data and a pointer to the next node. Unlike arrays, linked lists do "
            "not store elements in contiguous memory locations."
        ),
        "students": [
            "A linked list is a data structure made of nodes where each node holds data and "
            "a reference to the next node. Elements are not stored in contiguous memory like arrays.",
            "A linked list is a list of nodes connected by pointers.",
            "A linked list is a type of list used in programming.",
        ],
    },
    {
        "subject": "Software Engineering — What is Agile?",
        "model_answer": (
            "Agile is a software development methodology that promotes iterative development, "
            "collaboration, and flexibility. Work is divided into short cycles called sprints, "
            "allowing teams to respond quickly to change and deliver working software frequently."
        ),
        "students": [
            "Agile is a development approach that uses short iterations called sprints to deliver "
            "software incrementally. It focuses on collaboration, flexibility and responding to change.",
            "Agile is a method of developing software in small steps with regular feedback.",
            "Agile means working fast in software.",
        ],
    },
]

LEVELS = ["Strong", "Partial", "Weak"]

print("=" * 65)
print("  AUCA — Automated Answer Evaluation Test")
print("=" * 65)

for pair in pairs:
    print(f"\n📘 {pair['subject']}")
    print(f"   Model answer: {pair['model_answer'][:80]}...")
    print()
    for level, student_answer in zip(LEVELS, pair["students"]):
        result = evaluate_answer(student_answer, pair["model_answer"])
        print(f"  [{level:7s}] \"{student_answer[:60]}...\"")
        print(f"            similarity={result['similarity']:.2f}  "
              f"keywords={result['keyword_score']:.2f}  "
              f"length={result['length_score']:.2f}  "
              f"→ SCORE: {result['final_score']}/10")
    print("-" * 65)
