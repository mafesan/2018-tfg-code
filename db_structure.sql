CREATE DATABASE my_database;
USE my_database;

CREATE TABLE repos (
    id int NOT NULL,
    name varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    founder varchar(255) NOT NULL,
    url varchar(255),
    number_commits int,
    first_commit datetime,
    last_commit datetime,
    PRIMARY KEY (id)
);


CREATE TABLE interestingfiles (
    id int,
    name varchar(512) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    url varchar(512) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    commits_id int,
    repo_id int,
    PRIMARY KEY (id)
);

CREATE TABLE commits (
    id int,
    gh_id varchar(255),
    people_id int,
    commit_date datetime,
    cochanged int,
    repos_id int,
    PRIMARY KEY (id)
);

CREATE TABLE people (
    id int,
    name varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    email varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    PRIMARY KEY (id)
);

CREATE TABLE users (
    id int,
    login varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    name varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    company varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    location varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    email varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    created_at datetime,
    type varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    fake tinyint,
    deleted tinyint,
    longi decimal(11,8),
    lat decimal(10,8),
    country_code char(3),
    state  varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    city  varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
    PRIMARY KEY (id)
);
