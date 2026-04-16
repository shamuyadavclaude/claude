import os
import random
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "hangman-secret-key-2024"

DB_CONFIG = {
    "host":     os.getenv("PG_HOST",     "localhost"),
    "port":     os.getenv("PG_PORT",     "5432"),
    "dbname":   os.getenv("PG_DB",       "hangman"),
    "user":     os.getenv("PG_USER",     "postgres"),
    "password": os.getenv("PG_PASSWORD", "postgres"),
}

WORD_LIST = [
    {"word": "python",      "category": "Programming",  "hint": "Named after a British comedy group"},
    {"word": "algorithm",   "category": "Programming",  "hint": "A step-by-step problem-solving procedure"},
    {"word": "database",    "category": "Programming",  "hint": "Stores and retrieves structured data"},
    {"word": "recursion",   "category": "Programming",  "hint": "A function that calls itself"},
    {"word": "compiler",    "category": "Programming",  "hint": "Translates source code into machine code"},
    {"word": "framework",   "category": "Programming",  "hint": "A reusable software structure for building apps"},
    {"word": "elephant",    "category": "Animals",      "hint": "Largest land animal on Earth"},
    {"word": "penguin",     "category": "Animals",      "hint": "Flightless bird of the southern hemisphere"},
    {"word": "chameleon",   "category": "Animals",      "hint": "Reptile known for changing color"},
    {"word": "kangaroo",    "category": "Animals",      "hint": "Marsupial with a pouch"},
    {"word": "platypus",    "category": "Animals",      "hint": "Semi-aquatic mammal that lays eggs"},
    {"word": "tornado",     "category": "Nature",       "hint": "Violent rotating column of air"},
    {"word": "volcano",     "category": "Nature",       "hint": "Mountain that can erupt with lava"},
    {"word": "glacier",     "category": "Nature",       "hint": "Slow-moving mass of ice"},
    {"word": "monsoon",     "category": "Nature",       "hint": "Seasonal wind-driven rainfall"},
    {"word": "quasar",      "category": "Space",        "hint": "Extremely luminous active galactic nucleus"},
    {"word": "nebula",      "category": "Space",        "hint": "Cloud of gas and dust in space"},
    {"word": "eclipse",     "category": "Space",        "hint": "One celestial body blocking another's light"},
    {"word": "asteroid",    "category": "Space",        "hint": "Rocky body orbiting the sun"},
    {"word": "supernova",   "category": "Space",        "hint": "Explosion of a massive star"},
    {"word": "symphony",    "category": "Music",        "hint": "Extended orchestral composition"},
    {"word": "saxophone",   "category": "Music",        "hint": "Reed instrument invented by Adolphe Sax"},
    {"word": "waterfall",   "category": "Geography",    "hint": "Water flowing over a vertical drop"},
    {"word": "peninsula",   "category": "Geography",    "hint": "Land nearly surrounded by water"},
    {"word": "archipelago", "category": "Geography",    "hint": "Chain or cluster of islands"},
    {"word": "chocolate",   "category": "Food",         "hint": "Made from cacao beans"},
    {"word": "spaghetti",   "category": "Food",         "hint": "Long thin Italian pasta"},
    {"word": "avocado",     "category": "Food",         "hint": "Green fruit also called alligator pear"},
    {"word": "umbrella",    "category": "Objects",      "hint": "Collapsible canopy for rain or sun"},
    {"word": "telescope",   "category": "Objects",      "hint": "Instrument for viewing distant objects"},
    {"word": "labyrinth",   "category": "Concepts",     "hint": "Complex network of paths; a maze"},
    {"word": "paradox",     "category": "Concepts",     "hint": "Statement that seems contradictory but may be true"},
    {"word": "epiphany",    "category": "Concepts",     "hint": "Sudden moment of insight or realization"},
]

MAX_WRONG = 6
BODY_PARTS = ["head", "body", "left_arm", "right_arm", "left_leg", "right_leg"]


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            with open("schema.sql") as f:
                cur.execute(f.read())


def audit_game_start(session_id, word, category, hint):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO games (session_id, word, category, hint)
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (session_id, word, category, hint)
            )
            return cur.fetchone()[0]


def audit_guess(game_id, letter, is_correct, wrong_count_after):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO guesses (game_id, letter, is_correct, wrong_count_after)
                   VALUES (%s, %s, %s, %s)""",
                (game_id, letter, is_correct, wrong_count_after)
            )
            cur.execute(
                """UPDATE games
                   SET total_guesses = total_guesses + 1,
                       wrong_guesses = %s
                   WHERE id = %s""",
                (wrong_count_after, game_id)
            )


def audit_game_end(game_id, outcome):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE games SET outcome = %s, ended_at = NOW()
                   WHERE id = %s""",
                (outcome, game_id)
            )


def new_game_state(session_id):
    entry = random.choice(WORD_LIST)
    game_id = audit_game_start(session_id, entry["word"], entry["category"], entry["hint"])
    return {
        "game_id":     game_id,
        "word":        entry["word"].lower(),
        "category":    entry["category"],
        "hint":        entry["hint"],
        "guessed":     [],
        "wrong_count": 0,
        "status":      "playing",
    }


def compute_display(state):
    return [(ch, ch in state["guessed"]) for ch in state["word"]]


def compute_wrong_letters(state):
    return [ch for ch in state["guessed"] if ch not in state["word"]]


@app.route("/", methods=["GET"])
def index():
    if "game" not in session:
        session["game"] = new_game_state(session.sid if hasattr(session, "sid") else str(id(session)))
    game = session["game"]

    display       = compute_display(game)
    wrong_letters = compute_wrong_letters(game)
    parts_shown   = BODY_PARTS[: game["wrong_count"]]
    alphabet      = list("abcdefghijklmnopqrstuvwxyz")

    return render_template(
        "index.html",
        game=game,
        display=display,
        wrong_letters=wrong_letters,
        parts_shown=parts_shown,
        all_parts=BODY_PARTS,
        alphabet=alphabet,
        max_wrong=MAX_WRONG,
    )


@app.route("/guess", methods=["POST"])
def guess():
    game = session.get("game")
    if not game or game["status"] != "playing":
        return redirect(url_for("index"))

    letter = request.form.get("letter", "").lower().strip()
    if len(letter) == 1 and letter.isalpha() and letter not in game["guessed"]:
        game["guessed"].append(letter)
        is_correct = letter in game["word"]

        if not is_correct:
            game["wrong_count"] += 1

        prev_status = game["status"]

        if all(ch in game["guessed"] for ch in game["word"]):
            game["status"] = "won"
        elif game["wrong_count"] >= MAX_WRONG:
            game["status"] = "lost"

        audit_guess(game["game_id"], letter, is_correct, game["wrong_count"])

        if game["status"] != "playing" and prev_status == "playing":
            audit_game_end(game["game_id"], game["status"])

        session["game"] = game

    return redirect(url_for("index"))


@app.route("/new", methods=["POST"])
def new_game():
    sid = session.get("_id", str(id(session)))
    session["game"] = new_game_state(sid)
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
