"""One-time generator: Tamil study notes for every syllabus unit via Sarvam API.
Writes data/notes/<unit_id>.json  (skips units that already have notes).
Run:  python scripts/generate_notes.py
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")

API_KEY = os.getenv("SARVAM_API_KEY", "sk_gf2byh03_T10h1azKZvePwJbuviRy1M8A")
URL = "https://api.sarvam.ai/v1/chat/completions"
MODEL = "sarvam-105b"

DATA = BASE / "data"
NOTES = DATA / "notes"
NOTES.mkdir(exist_ok=True)

SYLLABI = [
    (DATA / "syllabus.json", "TNPSC குரூப் 2/2A முதல்நிலைத் தேர்வு"),
    (DATA / "syllabus_ae.json", "TNPSC உதவி பொறியாளர் (AE – EEE) தேர்வு"),
]


def build_prompt(part, unit, lang, exam_label):
    topics = "\n".join(f"- {t}" for t in unit["topics"])
    if lang == "ta":
        instr = "இது " + exam_label + "க்கான படிக்கும் குறிப்பு (study notes).\n" + """
தமிழில் எளிய, பரீட்சைக்கு ஏற்ற விளக்கத்துடன் குறிப்புகள் எழுது.
சரியாக இந்த JSON வடிவமைப்பில் மட்டும் பதில் சொல் (வேறு எதுவும் வேண்டாம், ``` குறியீட்டுக் கட்டம் வேண்டாம்):
{
  "intro": "இந்த அலகு பற்றி 2-3 வாக்கிய அறிமுகம் (தமிழில்)",
  "sections": [
    {"heading": "தலைப்பு", "points": ["முக்கியக் கருத்து 1", "கருத்து 2"]}
  ],
  "keywords": ["முக்கியச் சொல்1", "..."],
  "exam_tips": ["தேர்வுக்கான ஒரு குறிப்பு", "..."]
}
விதிகள்:
- sections: 4 முதல் 6; ஒவ்வொரு section-லும் 3-6 points.
- உண்மையான, துல்லியமான தகவல்கள் மட்டும் (கற்பனை வேண்டாம்).
- keywords: 8-12, exam_tips: 3."""
    else:
        instr = "This is a study note for the " + exam_label + ".\n" + """
Write clear, exam-oriented notes. Reply ONLY with valid JSON in this shape (no markdown fences):
{
  "intro": "2-3 sentence introduction of this unit",
  "sections": [
    {"heading": "Topic", "points": ["Key point 1", "Key point 2"]}
  ],
  "keywords": ["term1", "..."],
  "exam_tips": ["one exam tip", "..."]
}
Rules:
- sections: 4 to 6; each with 3-6 points.
- Only accurate facts (no invention).
- keywords: 8-12, exam_tips: 3."""

    q = unit.get("questions")
    q_line = f" ({q} கேள்விகள்)" if q else ""
    return f"""பாடப்பகுதி: {part['title']}
அலகு: {unit['title']}{q_line}
பாடத்திட்டத் தலைப்புகள்:
{topics}

{instr}"""


def clean_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    t = t.strip()
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1:
        t = t[start:end + 1]
    return json.loads(t)


def generate(part, unit, lang, exam_label):
    resp = requests.post(
        URL,
        headers={"api-subscription-key": API_KEY, "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "நீ ஒரு பரீட்சைத் தயாரிப்பு ஆசிரியர். சரியான JSON மட்டும் பதில் சொல்."},
                {"role": "user", "content": build_prompt(part, unit, lang, exam_label)},
            ],
            "temperature": 0.4,
            "max_tokens": 2500,
            "reasoning_effort": None,
        },
        timeout=120,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    note = clean_json(content)
    note["unit_id"] = unit["id"]
    note["title"] = unit["title"]
    return note


def main():
    jobs = []
    for path, exam_label in SYLLABI:
        if not path.exists():
            print(f"missing syllabus: {path.name}")
            continue
        syllabus = json.loads(path.read_text(encoding="utf-8"))
        for part in syllabus["parts"]:
            lang = "en" if part["id"] == "english" else "ta"
            for unit in part["units"]:
                jobs.append((part, unit, lang, exam_label))

    ok, fail = 0, 0
    for i, (part, unit, lang, exam_label) in enumerate(jobs, 1):
        out = NOTES / f"{unit['id']}.json"
        if out.exists():
            print(f"[{i}/{len(jobs)}] skip (exists): {unit['id']}")
            continue
        print(f"[{i}/{len(jobs)}] generating: {unit['id']} ...", flush=True)
        for attempt in (1, 2):
            try:
                note = generate(part, unit, lang, exam_label)
                if not note.get("sections"):
                    raise ValueError("no sections in note")
                out.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  ok ({len(note['sections'])} sections)")
                ok += 1
                break
            except Exception as e:
                print(f"  attempt {attempt} failed: {e}")
                if attempt == 2:
                    fail += 1
                time.sleep(3)
    print(f"DONE: {ok} generated, {fail} failed, total units {len(jobs)}")


if __name__ == "__main__":
    sys.exit(main())
