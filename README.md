# Segel D Simulation

Interaktives Quiz zum üben, üben, üben!

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (recommended) or any modern Python package manager

## Installation

### Via GitHub with `uv`

```bash
git clone https://github.com/<your-username>/segel_d_simulation.git
cd segel_d_simulation
uv sync
```

## Running

```bash
uv run python main.py
```

## Question File Format

Questions are stored as JSON files under the question pool directory. Each file has a top-level `category` name and a `questions` array:

```json
{
  "category": "Führerausweis",
  "questions": [
    {
      "question": "Frage 1?",
      "answers": [
        { "text": "Answer text A", "correct": false },
        { "text": "Answer text B", "correct": true },
        { "text": "Answer text C", "correct": true }
      ]
    }
  ]
}
```

## Question Pool Path

The path to the question files is set in `questions.py`, near the top of the file:

```python
QUESTIONS_DIR = Path(
    os.path.expanduser("~/ownCloud/private/segeln/segelschein_d/theoretische")
)
```

Change this to point to your own question pool directory.
