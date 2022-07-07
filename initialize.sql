CREATE TABLE IF NOT EXISTS songs(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    uri TEXT NOT NULL
    );

CREATE TABLE IF NOT EXISTS charts(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    link TEXT NOT NULL,
    playlist_id TEXT,
    last_week_updated TEXT NOT NULL
);

INSERT INTO charts(name, link, playlist_id, last_week_updated) VALUES
("Billboard Hot 100", "https://www.billboard.com/charts/hot-100/", "6eqORj4CtGGuMEdsg05s4D", "July 9, 2022");

INSERT INTO charts(name, link, playlist_id, last_week_updated) VALUES
("Billboard Global 200", "https://www.billboard.com/charts/billboard-global-200/", "1lmFbfg5dpsqSkBoyzwnEz",
"April 16, 2022");