import os
import random
import psycopg2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="frontend/dist", static_url_path="")
CORS(app)

DB_CONFIG = {
    "host":     os.getenv("PG_HOST",     "localhost"),
    "port":     os.getenv("PG_PORT",     "5432"),
    "dbname":   os.getenv("PG_DB",       "hangman"),
    "user":     os.getenv("PG_USER",     "postgres"),
    "password": os.getenv("PG_PASSWORD", "postgres"),
    "sslmode":  os.getenv("PG_SSLMODE",  "require"),
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


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            with open("schema.sql") as f:
                cur.execute(f.read())


def audit_game_start(word, category, hint):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO games (session_id, word, category, hint) VALUES (%s, %s, %s, %s) RETURNING id",
                ("pwa", word, category, hint)
            )
            return cur.fetchone()[0]


def audit_guess(game_id, letter, is_correct, wrong_count):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO guesses (game_id, letter, is_correct, wrong_count_after) VALUES (%s, %s, %s, %s)",
                (game_id, letter, is_correct, wrong_count)
            )
            cur.execute(
                "UPDATE games SET total_guesses = total_guesses + 1, wrong_guesses = %s WHERE id = %s",
                (wrong_count, game_id)
            )


def audit_game_end(game_id, outcome):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE games SET outcome = %s, ended_at = NOW() WHERE id = %s",
                (outcome, game_id)
            )


def build_display(word, guessed):
    return [{"char": ch, "revealed": ch in guessed} for ch in word]


# ── Health check ─────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return jsonify({"db": "ok", "host": DB_CONFIG["host"]})
    except Exception as e:
        return jsonify({"db": "error", "detail": str(e), "host": DB_CONFIG["host"]}), 500


# ── Serve React PWA ──────────────────────────────────────────────────────────

@app.route("/")
@app.route("/<path:path>")
def serve_react(path=""):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


# ── REST API ─────────────────────────────────────────────────────────────────

@app.route("/api/new", methods=["POST"])
def api_new():
    entry = random.choice(WORD_LIST)
    word = entry["word"].lower()
    game_id = audit_game_start(word, entry["category"], entry["hint"])
    return jsonify({
        "game_id":     game_id,
        "word_length": len(word),
        "category":    entry["category"],
        "hint":        entry["hint"],
        "display":     build_display(word, []),
        "guessed":     [],
        "wrong_letters": [],
        "wrong_count": 0,
        "status":      "playing",
        "max_wrong":   MAX_WRONG,
    })


@app.route("/api/guess", methods=["POST"])
def api_guess():
    data    = request.get_json()
    game_id = data.get("game_id")
    letter  = data.get("letter", "").lower().strip()
    word    = data.get("word", "")
    guessed = data.get("guessed", [])
    wrong_count = data.get("wrong_count", 0)
    status  = data.get("status", "playing")

    if status != "playing" or not (len(letter) == 1 and letter.isalpha()) or letter in guessed:
        return jsonify({"error": "invalid guess"}), 400

    guessed = guessed + [letter]
    is_correct = letter in word

    if not is_correct:
        wrong_count += 1

    wrong_letters = [ch for ch in guessed if ch not in word]

    if all(ch in guessed for ch in word):
        status = "won"
    elif wrong_count >= MAX_WRONG:
        status = "lost"

    audit_guess(game_id, letter, is_correct, wrong_count)

    if status != "playing":
        audit_game_end(game_id, status)

    resp = {
        "display":       build_display(word, guessed),
        "guessed":       guessed,
        "wrong_letters": wrong_letters,
        "wrong_count":   wrong_count,
        "status":        status,
        "max_wrong":     MAX_WRONG,
    }
    if status != "playing":
        resp["word"] = word

    return jsonify(resp)


try:
    init_db()
except Exception as e:
    print(f"Warning: init_db failed: {e}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
