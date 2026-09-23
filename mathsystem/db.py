# -*- coding: utf-8 -*-
"""数据库访问与初始化模块。

包含：连接管理、建表脚本、以及初始种子数据（章节、课程内容、题库、默认账号）。
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
"""


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
    """建表并在数据为空时写入种子数据。"""
    from werkzeug.security import generate_password_hash as _h  # noqa

    db_path = app.config["DATABASE"]
    fresh = force or not os.path.exists(db_path) or os.path.getsize(db_path) == 0
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()

    cur = conn.execute("SELECT COUNT(*) AS c FROM user")
    if cur.fetchone()["c"] == 0 or fresh:
        _seed(conn)
    conn.commit()
    conn.close()


def _seed(conn):
    # --- 默认账号 ---
    users = [
        ("admin", "admin123", "admin", "系统管理员"),
        ("teacher", "teacher123", "teacher", "张老师"),
        ("student", "student123", "student", "李同学"),
    ]
    for username, pwd, role, name in users:
        conn.execute(
            "INSERT INTO user (username, password_hash, role, real_name) VALUES (?,?,?,?)",
            (username, generate_password_hash(pwd), role, name),
        )

    # --- 章节 ---
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

    # --- 课程学习内容（每个章节若干课节） ---
    lessons = [
        (1, "1.1 函数的概念与性质", "本节介绍函数的定义、定义域与值域、有界性、单调性、奇偶性和周期性。"
         "常见初等函数包括幂函数 \\(y=x^a\\)、指数函数 \\(y=a^x\\)、对数函数 \\(y=\\log_a x\\) 及三角函数。"),
        (1, "1.2 数列与函数的极限", "数列极限记号 \\(\\lim_{n\\to\\infty} x_n = a\\)。函数极限记号 \\(\\lim_{x\\to x_0} f(x)=A\\)。"
         "重要极限：\\(\\lim_{x\\to 0}\\dfrac{\\sin x}{x}=1\\)，\\(\\lim_{x\\to\\infty}\\left(1+\\dfrac{1}{x}\\right)^x=e\\)。"
         "无穷小与无穷大、极限的四则运算法则与夹逼准则。"),
        (2, "2.1 导数的概念", "函数 \\(y=f(x)\\) 在点 \\(x_0\\) 处的导数 "
         "\\(f'(x_0)=\\lim_{\\Delta x\\to 0}\\dfrac{f(x_0+\\Delta x)-f(x_0)}{\\Delta x}\\)，"
         "其几何意义是曲线在该点处切线的斜率。可导必连续，连续不一定可导。"),
        (2, "2.2 求导法则与微分", "基本求导公式：\\((x^n)'=nx^{n-1}\\)，\\((\\sin x)'=\\cos x\\)，\\((e^x)'=e^x\\)，"
         "\\((\\ln x)'=\\dfrac{1}{x}\\)。复合函数求导遵循链式法则 \\(\\dfrac{dy}{dx}=\\dfrac{dy}{du}\\cdot\\dfrac{du}{dx}\\)。"
         "微分 \\(dy=f'(x)dx\\)。"),
        (3, "3.1 中值定理", "罗尔定理、拉格朗日中值定理 \\(f(b)-f(a)=f'(\\xi)(b-a)\\) 与柯西中值定理。"
         "洛必达法则用于求 \\(\\dfrac{0}{0}\\) 型和 \\(\\dfrac{\\infty}{\\infty}\\) 型不定式的极限。"),
        (3, "3.2 导数的应用", "利用一阶导数判断单调性与极值，利用二阶导数判断凹凸性与拐点。"
         "求函数的最值以及曲线的渐近线。"),
        (4, "4.1 不定积分的概念与性质", "不定积分 \\(\\int f(x)dx=F(x)+C\\)，其中 \\(F'(x)=f(x)\\)。"
         "基本积分公式：\\(\\int x^n dx=\\dfrac{x^{n+1}}{n+1}+C\\)，\\(\\int e^x dx=e^x+C\\)，"
         "\\(\\int \\dfrac{1}{x}dx=\\ln|x|+C\\)。"),
        (4, "4.2 换元积分法与分部积分法", "第一类换元法（凑微分法）与第二类换元法。"
         "分部积分公式 \\(\\int u\\,dv=uv-\\int v\\,du\\)。"),
        (5, "5.1 定积分的概念与性质", "定积分 \\(\\int_a^b f(x)dx\\) 表示曲边梯形的面积。"
         "牛顿-莱布尼茨公式：\\(\\int_a^b f(x)dx=F(b)-F(a)\\)，其中 \\(F'(x)=f(x)\\)。"),
        (5, "5.2 定积分的应用", "利用定积分计算平面图形的面积、旋转体的体积以及变力做功等。"),
        (6, "6.1 一阶微分方程", "可分离变量方程 \\(\\dfrac{dy}{dx}=f(x)g(y)\\)、一阶线性微分方程 "
         "\\(y'+P(x)y=Q(x)\\) 及其通解公式。"),
        (6, "6.2 高阶微分方程", "二阶常系数线性齐次微分方程 \\(y''+py'+qy=0\\) 的特征方程解法。"),
    ]
    for chapter_id, title, content in lessons:
        conn.execute(
            "INSERT INTO lesson (chapter_id, title, content, sort_order) VALUES (?,?,?,?)",
            (chapter_id, title, content, chapter_id),
        )

    # --- 题库 ---
    # (chapter_id, qtype, difficulty, content, options, answer, analysis, score)
    questions = [
        (1, "single", 1, r"求极限 \(\lim_{x\to 0}\dfrac{\sin x}{x}\) 的值。",
         ["0", "1", r"\(+\infty\)", "不存在"], "B", "重要极限之一，结果为 1。", 5),
        (1, "single", 2, r"求极限 \(\lim_{x\to\infty}\left(1+\dfrac{1}{x}\right)^x\) 的值。",
         ["1", r"\(e\)", "0", r"\(+\infty\)"], "B", "重要极限之一，结果为 e。", 5),
        (1, "judge", 1, "有限个无穷小之和仍是无穷小。",
         None, "T", "无穷小的运算法则，结论正确。", 5),
        (1, "fill", 2, r"计算 \(\lim_{x\to 0}\dfrac{\sin 3x}{x}=\) ______。",
         None, "3", r"\(\lim_{x\to0}\frac{\sin 3x}{x}=\lim_{x\to0}3\cdot\frac{\sin 3x}{3x}=3\)。", 5),
        (1, "multi", 3, "关于无穷小，下列说法正确的是（多选）。",
         ["有限个无穷小之和是无穷小", "无穷小与有界函数的乘积是无穷小",
          "两个无穷小的商一定是无穷小", "常数 0 是无穷小"], "A,B,D",
         "无穷小之商不为零时其商可能是非无穷小，C 错误。", 5),
        (2, "single", 1, r"求 \(\dfrac{d}{dx}\left(x^3\right)\) 的值。",
         [r"\(3x^2\)", r"\(x^2\)", r"\(3x\)", r"\(3x^3\)"], "A", "幂函数求导公式 (x^n)'=nx^{n-1}。", 5),
        (2, "single", 2, r"设 \(y=\sin x\)，则 \(y''=\)（　）。",
         [r"\(\sin x\)", r"\(-\sin x\)", r"\(\cos x\)", r"\(-\cos x\)"], "B", "求导两次。", 5),
        (2, "judge", 1, "函数在某点可导，则它在该点一定连续。",
         None, "T", "可导必连续，连续不一定可导。", 5),
        (2, "fill", 2, r"设 \(y=e^{2x}\)，则 \(dy=\) ______ \(dx\)。",
         None, r"2e^{2x}", "复合函数求导得 y'=2e^{2x}。", 5),
        (2, "single", 2, r"曲线 \(y=x^2\) 在点 \((1,1)\) 处切线的斜率为（　）。",
         ["1", "2", "0", "3"], "B", "y'=2x，代入 x=1 得 2。", 5),
        (2, "multi", 3, "关于导数，下列说法正确的是（多选）。",
         ["可导必连续", "连续必可导", "可导函数在可导点处有切线", "导数为 0 的点一定是极值点"],
         "A,C", "连续不一定可导（如 y=|x| 在 x=0），导数为 0 的点不一定是极值点，B、D 错误。", 5),
        (3, "single", 2, r"函数 \(f(x)=x^3-3x\) 的极大值点为（　）。",
         [r"\(x=1\)", r"\(x=-1\)", r"\(x=0\)", r"\(x=\pm1\)"], "A",
         "f'(x)=3x^2-3，令其为 0 得 x=±1；f''(1)=-6<0，故 x=1 为极大值点。", 5),
        (3, "judge", 2, "洛必达法则可用于求 0/0 型和 ∞/∞ 型不定式的极限。",
         None, "T", "洛必达法则的适用条件。", 5),
        (3, "fill", 2, r"计算 \(\lim_{x\to 0}\dfrac{e^x-1}{x}=\) ______。",
         None, "1", "0/0 型，用洛必达法则或等价无穷小 e^x-1~x，结果为 1。", 5),
        (3, "single", 3, r"函数 \(y=x-\ln x\) 的单调递减区间是（　）。",
         ["(0,1)", r"\((1,+\infty)\)", r"\((0,+\infty)\)", r"\((-\infty,1)\)"], "A",
         "y'=1-1/x，当 0<x<1 时 y'<0，函数递减。", 5),
        (4, "single", 1, r"计算 \(\int x\,dx\)。",
         [r"\(x^2+C\)", r"\(\dfrac{x^2}{2}+C\)", r"\(2x+C\)", r"\(\dfrac{x^2}{2}\)"], "B",
         "幂函数积分公式。", 5),
        (4, "fill", 2, r"计算 \(\int e^x\,dx=\) ______。",
         None, r"e^x+C", "基本积分公式。", 5),
        (4, "judge", 1, r"\(\int f(x)dx\) 表示 \(f(x)\) 的全体原函数。",
         None, "T", "不定积分的定义。", 5),
        (4, "single", 2, r"计算 \(\int \dfrac{1}{x}\,dx\)。",
         [r"\(\ln|x|+C\)", r"\(\dfrac{1}{x^2}+C\)", r"\(-\dfrac{1}{x^2}+C\)", r"\(x+C\)"], "A",
         "常用积分公式。", 5),
        (5, "single", 1, r"计算定积分 \(\int_{0}^{1} x\,dx\)。",
         ["1", r"\(\dfrac{1}{2}\)", "0", "2"], "B",
         "牛顿-莱布尼茨公式，原函数为 x^2/2。", 5),
        (5, "judge", 2, r"若 \(f(x)\) 为奇函数，则 \(\int_{-a}^{a} f(x)dx=0\)。",
         None, "T", "奇函数在对称区间上的积分为 0。", 5),
        (5, "fill", 3, r"计算 \(\dfrac{d}{dx}\int_{0}^{x}\sin t\,dt=\) ______。",
         None, "sin x", "变限积分求导，结果为被积函数在 x 处的值 sin x。", 5),
        (5, "single", 2, r"计算定积分 \(\int_{0}^{\pi}\sin x\,dx\)。",
         ["0", "1", "2", "-2"], "C", "原函数 -cos x，代入得 1-(-1)=2。", 5),
        (6, "single", 1, r"微分方程 \(y'=y\) 的通解是（　）。",
         [r"\(y=Cx\)", r"\(y=Ce^{x}\)", r"\(y=\dfrac{C}{x}\)", r"\(y=x+C\)"], "B",
         "可分离变量方程，解得 y=Ce^x。", 5),
        (6, "judge", 2, r"方程 \(y'+y=0\) 是一阶线性微分方程。",
         None, "T", "符合一阶线性方程 y'+P(x)y=Q(x) 的形式。", 5),
        (6, "fill", 2, r"微分方程 \(y'=2x\) 的通解为 \(y=\) ______。",
         None, r"x^2+C", "两边积分得 y=x^2+C。", 5),
    ]
    import json

    for cid, qtype, diff, content, options, answer, analysis, score in questions:
        conn.execute(
            "INSERT INTO question (chapter_id, qtype, difficulty, content, options, answer, analysis, score)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (cid, qtype, diff, content,
             json.dumps(options, ensure_ascii=False) if options else None,
             answer, analysis, score),
        )