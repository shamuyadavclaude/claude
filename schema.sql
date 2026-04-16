CREATE TABLE IF NOT EXISTS games (
    id          SERIAL PRIMARY KEY,
    session_id  TEXT        NOT NULL,
    word        TEXT        NOT NULL,
    category    TEXT        NOT NULL,
    hint        TEXT        NOT NULL,
    started_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at    TIMESTAMPTZ,
    outcome     TEXT        NOT NULL DEFAULT 'playing',
    total_guesses  INT      NOT NULL DEFAULT 0,
    wrong_guesses  INT      NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS guesses (
    id              SERIAL PRIMARY KEY,
    game_id         INT         NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    letter          CHAR(1)     NOT NULL,
    is_correct      BOOLEAN     NOT NULL,
    guessed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    wrong_count_after INT       NOT NULL
);
