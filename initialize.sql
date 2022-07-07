CREATE TABLE IF NOT EXISTS songs(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    full_artist TEXT NOT NULL,
    short_artist TEXT NOT NULL,
    uri TEXT NOT NULL
    );

CREATE TABLE IF NOT EXISTS charts(
    name TEXT PRIMARY KEY,
    link TEXT NOT NULL,
    playlist_id TEXT,
    last_week_updated TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chart_entries(
    song_id TEXT NOT NULL,
    chart_id TEXT NOT NULL,
    week TEXT NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY(song_id, chart_id, week,)
);

INSERT INTO charts(name, link, playlist_id, last_week_updated) VALUES
("Billboard Hot 100", "https://www.billboard.com/charts/hot-100/", "6eqORj4CtGGuMEdsg05s4D", "July 9, 2022");

INSERT INTO charts(name, link, playlist_id, last_week_updated) VALUES
("Billboard Global 200", "https://www.billboard.com/charts/billboard-global-200/", "1lmFbfg5dpsqSkBoyzwnEz",
"April 16, 2022");