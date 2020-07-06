DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Kingdoms;
DROP TABLE IF EXISTS Villages;

PRAGMA foreign_keys = ON;

CREATE TABLE Users (
    uid             text,
    doubloons       int,
    rank            text,
    block           int,
    tax_collected   int,
    kid             text,
    PRIMARY KEY (uid),
    FOREIGN KEY (kid) REFERENCES Kingdoms
);

CREATE TABLE Kingdoms (
    kid             text,
    k_name          text,
    attack          int,
    defence         int,
    warcry          text,
    uid             text NOT NULL,
    PRIMARY KEY (kid),
    FOREIGN KEY (uid) REFERENCES Users ON DELETE NO ACTION
);

CREATE TABLE Villages (
    vid             text,
    v_name          text,
    population      int,
    kid             text NOT NULL,
    PRIMARY KEY (vid),
    FOREIGN KEY (kid) REFERENCES Kingdoms
);

CREATE TABLE Variables (
    name            text,
    value           real,
    PRIMARY KEY (name)
);

INSERT INTO Variables VALUES
    ('tax_rate', 0);