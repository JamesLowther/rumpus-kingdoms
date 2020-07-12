DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Kingdoms;
DROP TABLE IF EXISTS Villages;
DROP TABLE IF EXISTS Variables;

PRAGMA foreign_keys = ON;

CREATE TABLE Users (
    uid             text,
    username        text,
    doubloons       int,
    rank            int,
    rumpus_count    int,
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
    been_attacked   int,
    has_attacked    int,
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