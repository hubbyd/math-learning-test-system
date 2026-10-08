# -*- coding: utf-8 -*-
"""数据库访问与初始化模块。

包含：连接管理、建表脚本、以及初始种子数据（章节、课程内容、题库、默认账号）。
课程内容与题库集中在 seed_data.py 中维护。
"""
import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS user (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'student',   -- student / teacher / admin
    real_name     TEXT,
    email         TEXT,                              -- 邮箱（可选）
    student_no    TEXT,                              -- 学号 / 工号（可选）
    created_at    TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS chapter (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lesson (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    title      TEXT NOT NULL,
    content    TEXT,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (chapter_id) REFERENCES chapter(id)
);

CREATE TABLE IF NOT EXISTS question (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    qtype      TEXT NOT NULL,                       -- single / multi / judge / fill
    difficulty INTEGER NOT NULL DEFAULT 1,          -- 1 易 / 2 中 / 3 难
    content    TEXT NOT NULL,
    options    TEXT,                                -- JSON 数组，选择题选项
    answer     TEXT NOT NULL,
    analysis   TEXT,
    score      REAL DEFAULT 5,
    FOREIGN KEY (chapter_id) REFERENCES chapter(id)
);

CREATE TABLE IF NOT EXISTS learning_record (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    viewed_at TEXT DEFAULT (datetime('now','localtime')),
    UNIQUE (user_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS practice_record (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    user_answer TEXT,
    is_correct  INTEGER,
    created_at  TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS paper (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    title        TEXT,
    total_score  REAL DEFAULT 0,
    got_score    REAL DEFAULT 0,
    status       TEXT DEFAULT 'ongoing',            -- ongoing / submitted
    time_limit   INTEGER DEFAULT 1800,              -- 限时（秒）
    created_at   TEXT DEFAULT (datetime('now','localtime')),
    submitted_at TEXT
);

CREATE TABLE IF NOT EXISTS paper_question (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id    INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    seq         INTEGER DEFAULT 0,
    user_answer TEXT,
    is_correct  INTEGER,
    got_score   REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS wrong_question (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    question_id    INTEGER NOT NULL,
    wrong_cnt      INTEGER NOT NULL DEFAULT 1,   -- 累计答错次数
    last_wrong_at  TEXT DEFAULT (datetime('now','localtime')),
    UNIQUE (user_id, question_id)
);

CREATE TABLE IF NOT EXISTS favorite (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    created_at  TEXT DEFAULT (datetime('now','localtime')),
    UNIQUE (user_id, question_id)
);

CREATE TABLE IF NOT EXISTS note (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    lesson_id  INTEGER NOT NULL,
    content    TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now','localtime')),
    UNIQUE (user_id, lesson_id)
);
"""


def _migrate(conn):
    """为老库补齐后加的字段，避免升级后报错。"""
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(user)")}
    for col, ddl in (("email", "TEXT"), ("student_no", "TEXT")):
        if col not in cols:
            conn.execute("ALTER TABLE user ADD COLUMN %s %s" % (col, ddl))
    pcols = {r["name"] for r in conn.execute("PRAGMA table_info(paper)")}
    if "time_limit" not in pcols:
        conn.execute("ALTER TABLE paper ADD COLUMN time_limit INTEGER DEFAULT 1800")
    conn.commit()


def get_db():
    """获取当前请求的数据库连接（惰性创建，请求结束时自动关闭）。"""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app, force=False):
    """建表并写入种子数据；已有库则只补齐新增内容。"""
    db_path = app.config["DATABASE"]
    fresh = force or not os.path.exists(db_path) or os.path.getsize(db_path) == 0
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    _migrate(conn)

    cur = conn.execute("SELECT COUNT(*) AS c FROM user")
    if cur.fetchone()["c"] == 0 or fresh:
        _seed(conn)
    else:
        _upgrade_content(conn)
    conn.commit()
    conn.close()


def _seed(conn):
    """写入初始数据：默认账号、章节、课程内容与题库。"""
    from seed_data import LESSONS, QUESTIONS

    users = [
        ("admin", "admin123", "admin", "系统管理员", "admin@example.com", "A0001"),
        ("teacher", "teacher123", "teacher", "张老师", "teacher@example.com", "T0001"),
        ("student", "student123", "student", "李同学", "student@example.com", "2024001"),
    ]
    for username, pwd, role, name, email, sno in users:
        conn.execute(
            "INSERT INTO user (username, password_hash, role, real_name, email, student_no)"
            " VALUES (?,?,?,?,?,?)",
            (username, generate_password_hash(pwd), role, name, email, sno),
        )

    chapters = [
        "函数与极限",
        "导数与微分",
        "微分中值定理与导数的应用",
        "不定积分",
        "定积分及其应用",
        "常微分方程",
    ]
    for i, name in enumerate(chapters, start=1):
        conn.execute(
            "INSERT INTO chapter (id, name, sort_order) VALUES (?,?,?)",
            (i, name, i),
        )

    for idx, (chapter_id, title, content) in enumerate(LESSONS, start=1):
        conn.execute(
            "INSERT INTO lesson (chapter_id, title, content, sort_order) VALUES (?,?,?,?)",
            (chapter_id, title, content, idx),
        )

    _insert_questions(conn)


def _insert_questions(conn):
    import json

    from seed_data import QUESTIONS

    for cid, qtype, diff, content, options, answer, analysis, score in QUESTIONS:
        conn.execute(
            "INSERT INTO question (chapter_id, qtype, difficulty, content, options, answer, analysis, score)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (cid, qtype, diff, content,
             json.dumps(options, ensure_ascii=False) if options else None,
             answer, analysis, score),
        )


def _upgrade_content(conn):
    """内容升级：课节按最新课程大纲重建；题库只补入缺失的新题（保留历史答题记录）。"""
    from seed_data import LESSONS, QUESTIONS

    n_lesson = conn.execute("SELECT COUNT(*) c FROM lesson").fetchone()["c"]
    if n_lesson != len(LESSONS):
        conn.execute("DELETE FROM lesson")
        for idx, (chapter_id, title, content) in enumerate(LESSONS, start=1):
            conn.execute(
                "INSERT INTO lesson (chapter_id, title, content, sort_order) VALUES (?,?,?,?)",
                (chapter_id, title, content, idx),
            )

    import json

    existing = {r["content"] for r in conn.execute("SELECT content FROM question")}
    for cid, qtype, diff, content, options, answer, analysis, score in QUESTIONS:
        if content in existing:
            continue
        conn.execute(
            "INSERT INTO question (chapter_id, qtype, difficulty, content, options, answer, analysis, score)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (cid, qtype, diff, content,
             json.dumps(options, ensure_ascii=False) if options else None,
             answer, analysis, score),
        )
