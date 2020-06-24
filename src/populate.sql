DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Kingdoms;
DROP TABLE IF EXISTS Villages;

PRAGMA foreign_keys = ON;

CREATE TABLE Users (
    uid             text,
    doubloons       int,
    hometown        int,
    rank            text,
    kid             text,
    PRIMARY KEY (uid),
    FOREIGN KEY (kid) REFERENCES Kingdoms
);

CREATE TABLE Kingdoms (
    kid             text,
    k_name          text,
    balance         int,
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
    rumpus_level    int,
    kid             text NOT NULL,
    PRIMARY KEY (vid),
    FOREIGN KEY (kid) REFERENCES Kingdoms
);