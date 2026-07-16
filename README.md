# Health History

A small local web app for tracking personal medical history, with a focus on
diabetes and peripheral artery disease (PAD) monitoring. Runs entirely on
your machine — data is stored in a local SQLite file and is never sent
anywhere.

## What it tracks

- Conditions (with diagnosis date and active/resolved status)
- Medications — changing a dose closes the old entry and opens a new one,
  so you keep a full history of what changed and when, instead of
  overwriting it
- Allergies
- Providers
- Blood glucose readings, with meal context, and trend chart
- A1C results, with trend chart
- Blood pressure readings, with trend chart
- PAD-specific symptoms/exam notes (claudication, numbness, color change,
  wounds, pulse checks) by leg and severity
- Labs (LDL/HDL/triglycerides, eGFR/creatinine, etc.) with per-test trend
  charts

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000 in your browser.

The database file is created automatically at `data/health.db` on first run.
That file is git-ignored — your actual health data should never be
committed to this (or any) repository. Back it up yourself (e.g. copy
`data/health.db` somewhere private) if you want to keep it safe.

## Notes

- Single-user, no authentication — intended to run locally on a machine
  only you have access to.
- This is a personal record-keeping tool, not medical advice or a
  diagnostic tool.
