CREATE TABLE IF NOT EXISTS properties(
    property TEXT PRIMARY KEY,
    val TEXT
    );

CREATE TABLE IF NOT EXISTS artists(
    name TEXT PRIMARY KEY,
    uri TEXT
    );

CREATE TABLE IF NOT EXISTS songs(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    uri TEXT NOT NULL
    );

CREATE TABLE IF NOT EXISTS song_artists(
    song_id INTEGER,
    artist INTEGER,
    PRIMARY KEY(song_id, artist),
    FOREIGN KEY(song_id) REFERENCES songs(id),
    FOREIGN KEY(artist) REFERENCES artists(name)
    );

CREATE TABLE IF NOT EXISTS charts(
    name TEXT PRIMARY KEY,
    link TEXT NOT NULL,
    playlist_id TEXT
    );

CREATE TABLE IF NOT EXISTS chart_entries(
    song_id TEXT NOT NULL,
    chart TEXT NOT NULL,
    week TEXT NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY(song_id, chart, week),
    FOREIGN KEY(chart) REFERENCES charts(name)
    );

INSERT OR IGNORE INTO charts(name, link, playlist_id) VALUES
("Billboard Hot 100", "https://www.billboard.com/charts/hot-100/", "6eqORj4CtGGuMEdsg05s4D");

INSERT OR IGNORE INTO charts(name, link, playlist_id) VALUES
("Billboard Global 200", "https://www.billboard.com/charts/billboard-global-200/", "1lmFbfg5dpsqSkBoyzwnEz");

INSERT OR IGNORE INTO properties(property, val) VALUES
("current_week",  "UNSET");