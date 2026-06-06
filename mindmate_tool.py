"""
MindMate Exam Wellness Tool

This module provides a simple command‑line interface to help students preparing
for high‑stakes exams (NEET, JEE, CUET, CAT, GATE, UPSC and various board
examinations) monitor their mental well‑being.  It allows users to record
their daily mood, stress level, sleep hours, study hours, and notable
stress triggers, as well as write a short reflective journal entry.  The data
are stored in a local CSV file so they persist across sessions.  Basic
personalised suggestions are produced based on the user's inputs, and a
simple crisis detection mechanism raises a flag if potentially harmful
language is used in the journal entry.

The tool also includes functions to summarise and visualise collected data
using pandas and matplotlib.  These summaries help users identify trends
in their stress levels and mood over time.

Usage
-----
The module can be used either interactively as a script or imported into
another Python program.  When run directly, it presents a simple menu to
create new check‑ins and view analytics.  When imported, you can call
`create_check_in(...)` and `generate_report(...)` directly to integrate
the functionality into another application (e.g., a web app or notebook).
"""

from __future__ import annotations

import csv
import datetime
import os
import re
from dataclasses import dataclass, asdict
from typing import List, Sequence, Tuple, Optional

import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = os.path.join(os.path.expanduser("~"), "mindmate_data.csv")


@dataclass
class CheckIn:
    """Data structure representing a single wellness check‑in."""
    date: datetime.date
    name: str
    exam: str
    mood: str
    stress: int
    sleep_hours: float
    study_hours: float
    triggers: List[str]
    journal: str

    def to_row(self) -> List[str]:
        """Serialise the check‑in to a CSV row."""
        return [
            self.date.isoformat(),
            self.name,
            self.exam,
            self.mood,
            str(self.stress),
            f"{self.sleep_hours:.2f}",
            f"{self.study_hours:.2f}",
            ";".join(self.triggers),
            self.journal.replace("\n", "\\n"),
        ]


def ensure_datafile(path: str = DATA_FILE) -> None:
    """Ensure the CSV data file exists with the correct header."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date",
                "name",
                "exam",
                "mood",
                "stress",
                "sleep_hours",
                "study_hours",
                "triggers",
                "journal",
            ])


def append_check_in(check_in: CheckIn, path: str = DATA_FILE) -> None:
    """Append a check‑in record to the CSV file."""
    ensure_datafile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(check_in.to_row())


def detect_crisis(journal: str) -> bool:
    """Detect crisis keywords in the journal entry.

    Returns True if any word associated with self‑harm or severe distress is
    found.  The detection is case‑insensitive and matches whole words.
    """
    crisis_terms = [
        "die",
        "harm",
        "kill myself",
        "suicide",
        "disappear",
        "can't go on",
        "cannot go on",
    ]
    text = journal.lower()
    for term in crisis_terms:
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text):
            return True
    return False


def generate_suggestions(check_in: CheckIn) -> List[str]:
    """Generate personalised wellness suggestions based on the check‑in."""
    suggestions: List[str] = []
    if check_in.stress >= 8 and check_in.sleep_hours < 6:
        suggestions.append(
            "You reported high stress and less than six hours of sleep. Consider stopping revision "
            "30 minutes before bed, doing a relaxing activity (like reading or stretching), and aiming "
            "for at least 7–8 hours of rest tonight."
        )
    if any("mock" in trig.lower() for trig in check_in.triggers):
        suggestions.append(
            "It seems mock tests are a stress trigger. After a mock test, focus on learning from "
            "your mistakes rather than self‑criticism. Spend some time reviewing the errors, then "
            "take a short walk or relaxation break."
        )
    if any("parent" in trig.lower() or "parents" in trig.lower() for trig in check_in.triggers):
        suggestions.append(
            "You listed parental pressure as a stressor. Try having an honest conversation about how "
            "you're feeling, and set realistic expectations together."
        )
    if any("comparison" in trig.lower() or "self‑doubt" in trig.lower() for trig in check_in.triggers):
        suggestions.append(
            "Comparison with peers can be discouraging. Spend a few minutes reminding yourself "
            "of your achievements, and practise focusing on your own progress rather than others'."
        )
    if check_in.stress >= 5:
        suggestions.append(
            "Try a quick 4‑7‑8 breathing exercise: inhale for 4 seconds, hold for 7, then exhale for 8. "
            "Repeat this cycle a few times to calm your nervous system."
        )
    if len(check_in.journal.strip()) < 10:
        suggestions.append(
            "Consider spending a few minutes writing about your day and emotions. Journaling can help "
            "process feelings and reduce anxiety."
        )
    return suggestions


def create_check_in(name: str, exam: str, mood: str, stress: int,
                    sleep_hours: float, study_hours: float, triggers: Sequence[str],
                    journal: str, date: Optional[datetime.date] = None,
                    store: bool = True) -> Tuple[CheckIn, List[str], bool]:
    """Create a CheckIn object, generate suggestions, and optionally persist it."""
    if date is None:
        date = datetime.date.today()
    check_in = CheckIn(
        date=date,
        name=name.strip(),
        exam=exam.strip(),
        mood=mood.strip(),
        stress=int(stress),
        sleep_hours=float(sleep_hours),
        study_hours=float(study_hours),
        triggers=[t.strip() for t in triggers],
        journal=journal.strip(),
    )
    if store:
        append_check_in(check_in)
    suggestions = generate_suggestions(check_in)
    crisis = detect_crisis(check_in.journal)
    return check_in, suggestions, crisis


def load_data(path: str = DATA_FILE) -> pd.DataFrame:
    """Load the check‑in data from the CSV file into a DataFrame."""
    ensure_datafile(path)
    df = pd.read_csv(path)
    return df


def generate_report(df: pd.DataFrame) -> Tuple[str, List[plt.Figure]]:
    """Generate a textual summary and a list of matplotlib figures for the data."""
    if df.empty:
        summary = "No data available. Start by adding some check‑ins."
        return summary, []
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)
    summary_lines: List[str] = []
    summary_lines.append(f"Total check‑ins: {len(df)}")
    mood_counts = df['mood'].value_counts().to_dict()
    summary_lines.append("Mood distribution:")
    for mood, count in mood_counts.items():
        summary_lines.append(f"  {mood}: {count}")
    avg_stress = df['stress'].mean()
    avg_sleep = df['sleep_hours'].mean()
    avg_study = df['study_hours'].mean()
    summary_lines.append(f"Average stress level: {avg_stress:.2f}")
    summary_lines.append(f"Average sleep hours: {avg_sleep:.2f}")
    summary_lines.append(f"Average study hours: {avg_study:.2f}")
    summary = "\n".join(summary_lines)
    figures: List[plt.Figure] = []
    fig1, ax1 = plt.subplots()
    ax1.plot(df['date'], df['stress'], marker='o')
    ax1.set_title('Stress Level Over Time')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Stress (1‑10)')
    ax1.grid(True)
    figures.append(fig1)
    fig2, ax2 = plt.subplots()
    # Do not specify explicit colours so the default palette is used (per charting guidelines)
    ax2.plot(df['date'], df['sleep_hours'], marker='o')
    ax2.set_title('Sleep Hours Over Time')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Hours of Sleep')
    ax2.grid(True)
    figures.append(fig2)

    fig3, ax3 = plt.subplots()
    moods = list(mood_counts.keys())
    counts = [mood_counts[m] for m in moods]
    ax3.bar(moods, counts)
    ax3.set_title('Mood Distribution')
    ax3.set_xlabel('Mood')
    ax3.set_ylabel('Count')
    figures.append(fig3)
    return summary, figures


def run_interactive():
    """Run a simple CLI loop for demonstration purposes."""
    print("Welcome to MindMate – Exam Wellness Tool")
    ensure_datafile()
    while True:
        print("\nMenu:")
        print("1) New check‑in")
        print("2) View report")
        print("3) Exit")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            name = input("Enter your name: ").strip()
            exam = input("Exam type (e.g., NEET, JEE, Board, etc.): ").strip()
            mood = input("Mood (Happy, Calm, Sad, Angry, Anxious, Tired): ").strip()
            stress = int(input("Stress level (1‑10): "))
            sleep_hours = float(input("Sleep hours last night: "))
            study_hours = float(input("Study hours today: "))
            triggers_input = input(
                "Stress triggers (separate by comma, e.g., Mock test, Parental pressure, Comparison): "
            ).strip()
            triggers = [t.strip() for t in triggers_input.split(',') if t.strip()]
            journal = input("Write a short reflection: ").strip()
            check_in, suggestions, crisis = create_check_in(
                name=name,
                exam=exam,
                mood=mood,
                stress=stress,
                sleep_hours=sleep_hours,
                study_hours=study_hours,
                triggers=triggers,
                journal=journal,
            )
            print("\nCheck‑in recorded for", check_in.date.isoformat())
            if suggestions:
                print("Personalised suggestions:")
                for suggestion in suggestions:
                    print("-", suggestion)
            else:
                print("No specific suggestions today. Keep taking care of yourself!")
            if crisis:
                print(
                    "\n*** Crisis alert ***\n"
                    "Your journal entry contains phrases that may indicate severe distress. "
                    "Please reach out to a trusted adult, counsellor, or crisis hotline immediately."
                )
        elif choice == '2':
            df = load_data()
            summary, figures = generate_report(df)
            print("\n=== Report ===")
            print(summary)
            for fig in figures:
                fig.show()
        elif choice == '3':
            print("Exiting MindMate. Take care!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == '__main__':
    run_interactive()
