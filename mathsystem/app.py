# -*- coding: utf-8 -*-
"""高等数学学习、测试系统 —— Flask 应用主程序。

课程设计（题目十二）实验5 实现成果。
采用 B/S 架构，SQLite 作为后台数据库。
"""
import json
import os
import re
import random
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, abort,
)

from db import get_db, close_db, init_db
from grading import grade_question, normalize_answer

QTYPE_NAMES = {"single": "单选题", "multi": "多选题", "judge": "判断题", "fill": "填空题"}
DIFF_NAMES = {1: "易", 2: "中", 3: "难"}


# --------------------------------------------------------------------------
# 应用工厂
# --------------------------------------------------------------------------
def create_app(database=None, testing=False):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "mathlearn-secret-key-2026"
    app.config["DATABASE"] = database or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "mathlearn.db"
    )
    app.config["TESTING"] = testing
    app.teardown_appcontext(close_db)

    init_db(app)
    register_routes(app)
    return app


# --------------------------------------------------------------------------
# 权限装饰器与工具函数
# --------------------------------------------------------------------------
def current_user():
    if "user_id" not in session:
        return None
    if getattr(g, "_current_user", None) is None:
        row = get_db().execute(
            "SELECT * FROM user WHERE id=?", (session["user_id"],)
        ).fetchone()
        g._current_user = row
    return g._current_user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("请先登录", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def deco(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if user is None:
                flash("请先登录", "warning")
                return redirect(url_for("login"))
            if user["role"] not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return deco


def row_to_question(row):
    d = dict(row)
    d["options"] = json.loads(row["options"]) if row["options"] else []
    d["qtype_name"] = QTYPE_NAMES.get(row["qtype"], row["qtype"])
    d["diff_name"] = DIFF_NAMES.get(row["difficulty"], str(row["difficulty"]))
    return d


def fetch_questions(ids):
    if not ids:
        return []
    db = get_db()
    marks = ",".join("?" * len(ids))
    rows = db.execute(
        "SELECT * FROM question WHERE id IN (%s)" % marks, ids
    ).fetchall()
    by_id = {r["id"]: row_to_question(r) for r in rows}
    return [by_id[i] for i in ids if i in by_id]


def _update_wrongbook(db, user_id, question_id, ok):
    """答错收录/累计错题本，答对则从错题本移除。"""
    if ok:
        db.execute(
            "DELETE FROM wrong_question WHERE user_id=? AND question_id=?",
            (user_id, question_id),
        )
    else:
        db.execute(
            "INSERT INTO wrong_question (user_id,question_id,wrong_cnt)"
            " VALUES (?, ?, 1)"
            " ON CONFLICT(user_id, question_id) DO UPDATE SET"
            " wrong_cnt = wrong_cnt + 1,"
            " last_wrong_at = datetime('now','localtime')",
            (user_id, question_id),
        )


def _user_points(db, user_id):
    """学习积分 = 练习答对数×2 + 测试得分总和 + 已学课节数×3。"""
    p_practice = db.execute(
        "SELECT COUNT(*) c FROM practice_record WHERE user_id=? AND is_correct=1",
        (user_id,),
    ).fetchone()["c"] * 2
    p_test = db.execute(
        "SELECT COALESCE(SUM(got_score),0) s FROM paper WHERE user_id=? AND status='submitted'",
        (user_id,),
    ).fetchone()["s"]
    p_learn = db.execute(
        "SELECT COUNT(*) c FROM learning_record WHERE user_id=?",
        (user_id,),
    ).fetchone()["c"] * 3
    return int(p_practice + p_test + p_learn)


def _grade_paper(db, paper, answers):
    """按答案字典判卷，写回 paper_question / paper，并维护错题本。

    answers: {question_id: user_answer}，缺省视为未作答。
    """
    pid = paper["id"]
    pq = db.execute(
        "SELECT pq.id AS pqid, q.* FROM paper_question pq"
        " JOIN question q ON q.id=pq.question_id WHERE pq.paper_id=?", (pid,),
    ).fetchall()
    total_get = 0.0
    for r in pq:
        q = row_to_question(r)
        user_ans = answers.get(q["id"])
        ok = grade_question(q["qtype"], q["answer"], user_ans)
        got = float(q["score"]) if ok else 0.0
        total_get += got
        db.execute(
            "UPDATE paper_question SET user_answer=?, is_correct=?, got_score=? WHERE id=?",
            (user_ans, 1 if ok else 0, got, r["pqid"]),
        )
        _update_wrongbook(db, paper["user_id"], q["id"], ok)
    db.execute(
        "UPDATE paper SET status='submitted', got_score=?, submitted_at=datetime('now','localtime')"
        " WHERE id=?", (total_get, pid),
    )
    db.commit()
    return total_get


# --------------------------------------------------------------------------
# 路由注册
# --------------------------------------------------------------------------
def register_routes(app):

    @app.route("/")
    @login_required
    def index():
        user = current_user()
        db = get_db()
        practice_cnt = db.execute(
            "SELECT COUNT(*) c FROM practice_record WHERE user_id=?", (user["id"],)
        ).fetchone()["c"]
        paper_cnt = db.execute(
            "SELECT COUNT(*) c FROM paper WHERE user_id=? AND status='submitted'",
            (user["id"],),
        ).fetchone()["c"]
        avg = db.execute(
            "SELECT AVG(got_score) a FROM paper WHERE user_id=? AND status='submitted'",
            (user["id"],),
        ).fetchone()["a"]
        chapters = db.execute(
            "SELECT c.*, (SELECT COUNT(*) FROM lesson l WHERE l.chapter_id=c.id) lesson_cnt,"
            " (SELECT COUNT(*) FROM question q WHERE q.chapter_id=c.id) q_cnt,"
            " (SELECT COUNT(*) FROM learning_record lr"
            "   WHERE lr.lesson_id IN (SELECT id FROM lesson WHERE chapter_id=c.id)"
            "     AND lr.user_id=?) viewed_cnt"
            " FROM chapter c ORDER BY sort_order",
            (user["id"],),
        ).fetchall()
        chapters = [
            {
                "id": c["id"], "name": c["name"],
                "lesson_cnt": c["lesson_cnt"], "q_cnt": c["q_cnt"],
                "viewed": c["viewed_cnt"],
                "progress": round(c["viewed_cnt"] * 100.0 / c["lesson_cnt"]) if c["lesson_cnt"] else 0,
            }
            for c in chapters
        ]
        return render_template(
            "index.html", user=user, practice_cnt=practice_cnt,
            paper_cnt=paper_cnt, avg=round(avg, 1) if avg else 0,
            chapters=chapters, points=_user_points(db, user["id"]),
        )

    # ---------------- 用户管理 ----------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            password2 = request.form.get("password2") or ""
            real_name = (request.form.get("real_name") or "").strip()
            email = (request.form.get("email") or "").strip()
            student_no = (request.form.get("student_no") or "").strip()
            role = request.form.get("role") or "student"
            agree = request.form.get("agree")
            if role not in ("student", "teacher"):
                role = "student"
            form = {"username": username, "real_name": real_name,
                    "email": email, "student_no": student_no, "role": role}
            err = None
            if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
                err = "用户名须为 3~20 位字母、数字或下划线"
            elif len(password) < 6:
                err = "密码长度不能少于 6 位"
            elif not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
                err = "密码需同时包含字母和数字，以提升账号安全性"
            elif password != password2:
                err = "两次输入的密码不一致，请重新确认"
            elif not real_name:
                err = "请填写真实姓名，便于教师统计成绩"
            elif email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", email):
                err = "邮箱格式不正确"
            elif not agree:
                err = "请先阅读并同意《用户服务协议》与《隐私政策》"
            if err is None:
                db = get_db()
                if db.execute("SELECT 1 FROM user WHERE username=?", (username,)).fetchone():
                    err = "该用户名已存在，请更换"
                else:
                    from werkzeug.security import generate_password_hash
                    db.execute(
                        "INSERT INTO user (username,password_hash,role,real_name,email,student_no)"
                        " VALUES (?,?,?,?,?,?)",
                        (username, generate_password_hash(password), role,
                         real_name, email or None, student_no or None),
                    )
                    db.commit()
                    flash("注册成功，请使用新账号登录", "success")
                    return redirect(url_for("login"))
            flash(err, "danger")
            return render_template("register.html", form=form)
        return render_template("register.html", form=None)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            db = get_db()
            row = db.execute("SELECT * FROM user WHERE username=?", (username,)).fetchone()
            from werkzeug.security import check_password_hash
            if row and check_password_hash(row["password_hash"], password):
                session.clear()
                session["user_id"] = row["id"]
                flash("登录成功", "success")
                return redirect(url_for("index"))
            flash("用户名或密码错误", "danger")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("已退出登录", "success")
        return redirect(url_for("login"))

    # ---------------- 课程学习 ----------------
    @app.route("/learning")
    @login_required
    def learning():
        user = current_user()
        db = get_db()
        chapters = db.execute(
            "SELECT c.*, (SELECT COUNT(*) FROM lesson l WHERE l.chapter_id=c.id) lesson_cnt,"
            " (SELECT COUNT(*) FROM learning_record lr"
            "   WHERE lr.lesson_id IN (SELECT id FROM lesson WHERE chapter_id=c.id)"
            "     AND lr.user_id=?) viewed_cnt"
            " FROM chapter c ORDER BY sort_order",
            (user["id"],),
        ).fetchall()
        chapters = [
            {
                "id": c["id"], "name": c["name"], "lesson_cnt": c["lesson_cnt"],
                "viewed": c["viewed_cnt"],
                "progress": round(c["viewed_cnt"] * 100.0 / c["lesson_cnt"]) if c["lesson_cnt"] else 0,
            }
            for c in chapters
        ]
        return render_template("learning_chapters.html", chapters=chapters)

    @app.route("/learning/chapter/<int:cid>")
    @login_required
    def learning_chapter(cid):
        db = get_db()
        user = current_user()
        chapter = db.execute("SELECT * FROM chapter WHERE id=?", (cid,)).fetchone()
        if not chapter:
            abort(404)
        lessons = db.execute(
            "SELECT * FROM lesson WHERE chapter_id=? ORDER BY sort_order, id", (cid,)
        ).fetchall()
        viewed = {
            r["lesson_id"]
            for r in db.execute(
                "SELECT lesson_id FROM learning_record WHERE user_id=?", (user["id"],)
            )
        }
        q_cnt = db.execute(
            "SELECT COUNT(*) c FROM question WHERE chapter_id=?", (cid,)
        ).fetchone()["c"]
        done = sum(1 for l in lessons if l["id"] in viewed)
        progress = round(done * 100.0 / len(lessons)) if lessons else 0
        return render_template(
            "learning_chapter.html", chapter=chapter, lessons=lessons,
            viewed=viewed, q_cnt=q_cnt, done=done, progress=progress,
        )

    @app.route("/learning/lesson/<int:lid>")
    @login_required
    def learning_lesson(lid):
        db = get_db()
        lesson = db.execute("SELECT * FROM lesson WHERE id=?", (lid,)).fetchone()
        if not lesson:
            abort(404)
        chapter = db.execute(
            "SELECT * FROM chapter WHERE id=?", (lesson["chapter_id"],)
        ).fetchone()
        user = current_user()
        db.execute(
            "INSERT OR IGNORE INTO learning_record (user_id,lesson_id) VALUES (?,?)",
            (user["id"], lid),
        )
        db.commit()
        siblings = db.execute(
            "SELECT id, title FROM lesson WHERE chapter_id=? ORDER BY sort_order, id",
            (lesson["chapter_id"],),
        ).fetchall()
        idx = next((i for i, s in enumerate(siblings) if s["id"] == lid), 0)
        prev_lesson = siblings[idx - 1] if idx > 0 else None
        next_lesson = siblings[idx + 1] if idx + 1 < len(siblings) else None
        note_row = db.execute(
            "SELECT content FROM note WHERE user_id=? AND lesson_id=?", (user["id"], lid)
        ).fetchone()
        q_cnt = db.execute(
            "SELECT COUNT(*) c FROM question WHERE chapter_id=?", (lesson["chapter_id"],)
        ).fetchone()["c"]
        viewed_ids = {
            r["lesson_id"]
            for r in db.execute(
                "SELECT lesson_id FROM learning_record WHERE user_id=?", (user["id"],)
            )
        }
        return render_template(
            "learning_lesson.html", lesson=lesson, chapter=chapter,
            siblings=siblings, prev_lesson=prev_lesson, next_lesson=next_lesson,
            note=(note_row["content"] if note_row else ""), q_cnt=q_cnt,
            viewed_ids=viewed_ids,
        )

    @app.route("/learning/lesson/<int:lid>/note", methods=["POST"])
    @login_required
    def lesson_note(lid):
        user = current_user()
        db = get_db()
        content = (request.form.get("content") or "").strip()
        if content:
            db.execute(
                "INSERT INTO note (user_id,lesson_id,content) VALUES (?,?,?)"
                " ON CONFLICT(user_id,lesson_id) DO UPDATE SET"
                " content=excluded.content, updated_at=datetime('now','localtime')",
                (user["id"], lid, content),
            )
            flash("笔记已保存", "success")
        else:
            db.execute("DELETE FROM note WHERE user_id=? AND lesson_id=?", (user["id"], lid))
            flash("笔记已清空", "success")
        db.commit()
        return redirect(url_for("learning_lesson", lid=lid))

    # ---------------- 随堂练习 ----------------
    @app.route("/practice")
    @login_required
    def practice():
        db = get_db()
        chapters = db.execute("SELECT * FROM chapter ORDER BY sort_order").fetchall()
        return render_template("practice_form.html", chapters=chapters)

    @app.route("/practice/start")
    @login_required
    def practice_start():
        db = get_db()
        cid = request.args.get("chapter_id", type=int)
        count = request.args.get("count", default=5, type=int)
        count = max(1, min(count, 20))
        if not cid:
            flash("请选择章节", "warning")
            return redirect(url_for("practice"))
        rows = db.execute(
            "SELECT id FROM question WHERE chapter_id=? ORDER BY random() LIMIT ?",
            (cid, count),
        ).fetchall()
        ids = [r["id"] for r in rows]
        if not ids:
            flash("该章节暂无题目", "warning")
            return redirect(url_for("practice"))
        questions = fetch_questions(ids)
        chapter = db.execute("SELECT * FROM chapter WHERE id=?", (cid,)).fetchone()
        return render_template(
            "practice_take.html", questions=questions, chapter=chapter, qids=ids
        )

    @app.route("/practice/submit", methods=["POST"])
    @login_required
    def practice_submit():
        db = get_db()
        user = current_user()
        ids = [int(x) for x in request.form.get("qids", "").split(",") if x.strip().isdigit()]
        questions = fetch_questions(ids)
        results = []
        right = 0
        for q in questions:
            user_ans = request.form.get("q_%d" % q["id"])
            if q["qtype"] == "multi":
                user_ans = ",".join(request.form.getlist("q_%d" % q["id"]))
            ok = grade_question(q["qtype"], q["answer"], user_ans)
            if ok:
                right += 1
            db.execute(
                "INSERT INTO practice_record (user_id,question_id,user_answer,is_correct)"
                " VALUES (?,?,?,?)",
                (user["id"], q["id"], user_ans, 1 if ok else 0),
            )
            _update_wrongbook(db, user["id"], q["id"], ok)
            results.append({
                "question": q, "user_answer": user_ans or "",
                "is_correct": ok,
                "got_score": q["score"] if ok else 0,
                "display_answer": _display_answer(q),
            })
        db.commit()
        rate = round(right * 100.0 / len(questions), 1) if questions else 0
        return render_template(
            "practice_result.html", results=results, right=right,
            total=len(questions), rate=rate,
        )

    # ---------------- 综合测试 ----------------
    @app.route("/test")
    @login_required
    def test_form():
        db = get_db()
        chapters = db.execute("SELECT * FROM chapter ORDER BY sort_order").fetchall()
        return render_template("test_form.html", chapters=chapters)

    @app.route("/test/create", methods=["POST"])
    @login_required
    def test_create():
        db = get_db()
        user = current_user()
        chapter_ids = request.form.getlist("chapters", type=int)
        difficulty = request.form.get("difficulty", default=0, type=int)
        counts = {
            "single": request.form.get("n_single", default=0, type=int),
            "multi": request.form.get("n_multi", default=0, type=int),
            "judge": request.form.get("n_judge", default=0, type=int),
            "fill": request.form.get("n_fill", default=0, type=int),
        }
        selected = []
        for qtype, n in counts.items():
            if n <= 0:
                continue
            sql = "SELECT * FROM question WHERE qtype=?"
            params = [qtype]
            if chapter_ids:
                sql += " AND chapter_id IN (%s)" % ",".join("?" * len(chapter_ids))
                params += chapter_ids
            if difficulty in (1, 2, 3):
                sql += " AND difficulty=?"
                params.append(difficulty)
            sql += " ORDER BY random() LIMIT ?"
            params.append(n)
            selected += db.execute(sql, params).fetchall()
        if not selected:
            flash("未找到符合条件的题目，请调整组卷条件", "warning")
            return redirect(url_for("test_form"))
        random.shuffle(selected)
        total = sum(q["score"] for q in selected)
        minutes = request.form.get("minutes", default=30, type=int)
        minutes = max(5, min(minutes, 120))
        cur = db.execute(
            "INSERT INTO paper (user_id,title,total_score,got_score,status,time_limit)"
            " VALUES (?,?,?,0,'ongoing',?)",
            (user["id"], "高等数学综合测试", total, minutes * 60),
        )
        pid = cur.lastrowid
        for i, q in enumerate(selected, start=1):
            db.execute(
                "INSERT INTO paper_question (paper_id,question_id,seq) VALUES (?,?,?)",
                (pid, q["id"], i),
            )
        db.commit()
        return redirect(url_for("test_take", pid=pid))

    @app.route("/test/<int:pid>")
    @login_required
    def test_take(pid):
        db = get_db()
        user = current_user()
        paper = db.execute("SELECT * FROM paper WHERE id=?", (pid,)).fetchone()
        if not paper:
            abort(404)
        if paper["user_id"] != user["id"] and user["role"] == "student":
            abort(403)
        if paper["status"] == "submitted":
            return redirect(url_for("test_result", pid=pid))
        pq = db.execute(
            "SELECT pq.*, q.* , pq.id AS pqid FROM paper_question pq"
            " JOIN question q ON q.id = pq.question_id"
            " WHERE pq.paper_id=? ORDER BY pq.seq", (pid,),
        ).fetchall()
        questions = []
        for r in pq:
            d = row_to_question(r)
            d["pqid"] = r["pqid"]
            questions.append(d)
        # 剩余时间以服务器记录的创建时间计算，刷新页面不会重置
        elapsed = db.execute(
            "SELECT CAST(strftime('%s','now','localtime') AS INTEGER)"
            " - CAST(strftime('%s',?) AS INTEGER) AS e", (paper["created_at"],)
        ).fetchone()["e"]
        limit = paper["time_limit"] or 1800
        remain = max(0, limit - (elapsed or 0))
        if remain <= 0:
            flash("考试时间已到，系统已自动交卷", "warning")
            _grade_paper(db, paper, {})
            return redirect(url_for("test_result", pid=pid))
        return render_template(
            "test_take.html", paper=paper, questions=questions, remain=remain
        )

    @app.route("/test/<int:pid>/submit", methods=["POST"])
    @login_required
    def test_submit(pid):
        db = get_db()
        paper = db.execute("SELECT * FROM paper WHERE id=?", (pid,)).fetchone()
        if not paper:
            abort(404)
        if paper["status"] == "submitted":
            return redirect(url_for("test_result", pid=pid))
        answers = {}
        for key in request.form:
            if key.startswith("q_"):
                qid = key[2:]
                if qid.isdigit():
                    answers[int(qid)] = ("," .join(request.form.getlist(key))
                                         if len(request.form.getlist(key)) > 1
                                         else request.form.get(key))
        _grade_paper(db, paper, answers)
        return redirect(url_for("test_result", pid=pid))

    @app.route("/test/<int:pid>/result")
    @login_required
    def test_result(pid):
        db = get_db()
        user = current_user()
        paper = db.execute("SELECT * FROM paper WHERE id=?", (pid,)).fetchone()
        if not paper:
            abort(404)
        if paper["user_id"] != user["id"] and user["role"] == "student":
            abort(403)
        rows = db.execute(
            "SELECT pq.*, q.*, pq.id AS pqid FROM paper_question pq"
            " JOIN question q ON q.id=pq.question_id WHERE pq.paper_id=? ORDER BY pq.seq",
            (pid,),
        ).fetchall()
        details = []
        for r in rows:
            q = row_to_question(r)
            details.append({
                "question": q,
                "user_answer": r["user_answer"] or "",
                "is_correct": bool(r["is_correct"]),
                "got_score": r["got_score"],
                "display_answer": _display_answer(q),
            })
        rate = round(paper["got_score"] * 100.0 / paper["total_score"], 1) if paper["total_score"] else 0
        return render_template(
            "test_result.html", paper=paper, details=details, rate=rate
        )

    # ---------------- 成绩查询 ----------------
    @app.route("/scores")
    @login_required
    def scores():
        db = get_db()
        user = current_user()
        if user["role"] == "student":
            papers = db.execute(
                "SELECT * FROM paper WHERE user_id=? AND status='submitted' ORDER BY id DESC",
                (user["id"],),
            ).fetchall()
        else:
            papers = db.execute(
                "SELECT p.*, u.real_name, u.username FROM paper p JOIN user u ON u.id=p.user_id"
                " WHERE p.status='submitted' ORDER BY p.id DESC"
            ).fetchall()
        # 成绩趋势（最近 8 次，按时间正序）
        my_papers = db.execute(
            "SELECT id, got_score, total_score, submitted_at FROM paper"
            " WHERE user_id=? AND status='submitted' AND total_score>0"
            " ORDER BY id DESC LIMIT 8",
            (user["id"],),
        ).fetchall()
        trend = [
            {
                "id": p["id"],
                "rate": round(p["got_score"] * 100.0 / p["total_score"], 1),
                "at": (p["submitted_at"] or "")[5:16],
            }
            for p in reversed(my_papers)
        ]
        # 预计算折线坐标（SVG 视图 600x180，左侧留 40 内边距）
        chart = None
        if trend:
            n = len(trend)
            step = 520.0 / (n - 1) if n > 1 else 0
            pts = [(40 + i * step, 150 - t["rate"] * 1.2) for i, t in enumerate(trend)]
            chart = {
                "points": " ".join("%.1f,%.1f" % (x, y) for x, y in pts),
                "area": "40,150 " + " ".join("%.1f,%.1f" % (x, y) for x, y in pts) + " %.1f,150" % pts[-1][0],
                "dots": [{"x": round(x, 1), "y": round(y, 1), "rate": trend[i]["rate"],
                          "at": trend[i]["at"]} for i, (x, y) in enumerate(pts)],
                "labels": [{"x": round(x, 1), "at": trend[i]["at"]}
                           for i, (x, y) in enumerate(pts)],
            }
        return render_template("scores.html", papers=papers, user=user,
                               trend=trend, chart=chart)

    # ---------------- 错题本 ----------------
    @app.route("/wrongbook")
    @login_required
    def wrongbook():
        user = current_user()
        db = get_db()
        rows = db.execute(
            "SELECT w.wrong_cnt, w.last_wrong_at, q.*, c.name AS chapter_name"
            " FROM wrong_question w"
            " JOIN question q ON q.id = w.question_id"
            " JOIN chapter c ON c.id = q.chapter_id"
            " WHERE w.user_id=? ORDER BY w.last_wrong_at DESC",
            (user["id"],),
        ).fetchall()
        questions = []
        for r in rows:
            d = row_to_question(r)
            d["wrong_cnt"] = r["wrong_cnt"]
            d["last_wrong_at"] = r["last_wrong_at"]
            d["chapter_name"] = r["chapter_name"]
            d["display_answer"] = _display_answer(d)
            questions.append(d)
        return render_template("wrongbook.html", questions=questions)

    @app.route("/wrongbook/practice")
    @login_required
    def wrongbook_practice():
        user = current_user()
        db = get_db()
        rows = db.execute(
            "SELECT question_id FROM wrong_question WHERE user_id=?"
            " ORDER BY last_wrong_at DESC LIMIT 20",
            (user["id"],),
        ).fetchall()
        ids = [r["question_id"] for r in rows]
        if not ids:
            flash("错题本是空的，先去做几道练习吧", "warning")
            return redirect(url_for("practice"))
        random.shuffle(ids)
        questions = fetch_questions(ids)
        return render_template(
            "practice_take.html", questions=questions,
            chapter={"name": "错题重做"}, qids=ids,
        )

    @app.route("/wrongbook/<int:qid>/remove", methods=["POST"])
    @login_required
    def wrongbook_remove(qid):
        user = current_user()
        db = get_db()
        db.execute(
            "DELETE FROM wrong_question WHERE user_id=? AND question_id=?",
            (user["id"], qid),
        )
        db.commit()
        flash("已从错题本移除", "success")
        return redirect(url_for("wrongbook"))

    # ---------------- 收藏夹 ----------------
    @app.route("/favorites")
    @login_required
    def favorites():
        user = current_user()
        db = get_db()
        rows = db.execute(
            "SELECT q.*, c.name AS chapter_name FROM favorite f"
            " JOIN question q ON q.id = f.question_id"
            " JOIN chapter c ON c.id = q.chapter_id"
            " WHERE f.user_id=? ORDER BY f.id DESC",
            (user["id"],),
        ).fetchall()
        questions = []
        for r in rows:
            d = row_to_question(r)
            d["chapter_name"] = r["chapter_name"]
            d["display_answer"] = _display_answer(d)
            questions.append(d)
        return render_template("favorites.html", questions=questions)

    @app.route("/question/<int:qid>/favorite", methods=["POST"])
    @login_required
    def toggle_favorite(qid):
        user = current_user()
        db = get_db()
        row = db.execute(
            "SELECT 1 FROM favorite WHERE user_id=? AND question_id=?", (user["id"], qid)
        ).fetchone()
        if row:
            db.execute(
                "DELETE FROM favorite WHERE user_id=? AND question_id=?", (user["id"], qid)
            )
            flash("已取消收藏", "success")
        else:
            db.execute(
                "INSERT INTO favorite (user_id,question_id) VALUES (?,?)", (user["id"], qid)
            )
            flash("已加入收藏夹", "success")
        db.commit()
        return redirect(request.form.get("next") or url_for("favorites"))

    # ---------------- 排行榜 ----------------
    @app.route("/leaderboard")
    @login_required
    def leaderboard():
        user = current_user()
        db = get_db()
        users = db.execute(
            "SELECT u.id, u.username, u.real_name, u.role,"
            " (SELECT COUNT(*) FROM practice_record pr"
            "   WHERE pr.user_id=u.id AND pr.is_correct=1) practice_right,"
            " (SELECT COALESCE(SUM(got_score),0) FROM paper p"
            "   WHERE p.user_id=u.id AND p.status='submitted') test_score,"
            " (SELECT COUNT(*) FROM learning_record lr WHERE lr.user_id=u.id) lessons"
            " FROM user u"
        ).fetchall()
        board = []
        for u in users:
            board.append({
                "id": u["id"],
                "name": u["real_name"] or u["username"],
                "role": u["role"],
                "practice_right": u["practice_right"],
                "test_score": round(u["test_score"]),
                "lessons": u["lessons"],
                "points": u["practice_right"] * 2 + int(u["test_score"]) + u["lessons"] * 3,
            })
        board.sort(key=lambda x: -x["points"])
        top10 = board[:10]
        my_rank = next((i + 1 for i, b in enumerate(board) if b["id"] == user["id"]), None)
        return render_template(
            "leaderboard.html", top10=top10,
            my_rank=my_rank, total_users=len(board),
        )

    # ---------------- 统计分析 ----------------
    @app.route("/stats")
    @roles_required("teacher", "admin")
    def stats():
        db = get_db()
        # 各章节练习正确率
        chapter_stats = db.execute(
            "SELECT c.name,"
            " COUNT(pr.id) attempts,"
            " SUM(pr.is_correct) correct"
            " FROM chapter c LEFT JOIN question q ON q.chapter_id=c.id"
            " LEFT JOIN practice_record pr ON pr.question_id=q.id"
            " GROUP BY c.id ORDER BY c.sort_order"
        ).fetchall()
        chapter_stats = [
            {
                "name": r["name"],
                "attempts": r["attempts"],
                "correct": r["correct"] or 0,
                "rate": round((r["correct"] or 0) * 100.0 / r["attempts"], 1) if r["attempts"] else 0,
            }
            for r in chapter_stats
        ]
        # 成绩分布
        dist = db.execute(
            "SELECT CASE"
            " WHEN got_score*100.0/total_score >= 90 THEN '优秀(90-100)'"
            " WHEN got_score*100.0/total_score >= 80 THEN '良好(80-89)'"
            " WHEN got_score*100.0/total_score >= 70 THEN '中等(70-79)'"
            " WHEN got_score*100.0/total_score >= 60 THEN '及格(60-69)'"
            " ELSE '不及格(<60)' END AS band, COUNT(*) c"
            " FROM paper WHERE status='submitted' AND total_score>0 GROUP BY band"
        ).fetchall()
        summary = db.execute(
            "SELECT COUNT(*) c, AVG(got_score*100.0/total_score) avg_rate,"
            " MAX(got_score*100.0/total_score) max_rate,"
            " MIN(got_score*100.0/total_score) min_rate"
            " FROM paper WHERE status='submitted' AND total_score>0"
        ).fetchone()
        return render_template(
            "stats.html", chapter_stats=chapter_stats, dist=dist, summary=summary
        )

    # ---------------- 题库管理 ----------------
    @app.route("/questions")
    @roles_required("teacher", "admin")
    def questions():
        db = get_db()
        cid = request.args.get("chapter_id", type=int)
        qtype = request.args.get("qtype")
        sql = ("SELECT q.*, c.name AS chapter_name FROM question q"
               " JOIN chapter c ON c.id=q.chapter_id WHERE 1=1")
        params = []
        if cid:
            sql += " AND q.chapter_id=?"
            params.append(cid)
        if qtype:
            sql += " AND q.qtype=?"
            params.append(qtype)
        sql += " ORDER BY q.chapter_id, q.id"
        rows = db.execute(sql, params).fetchall()
        questions = [row_to_question(r) for r in rows]
        chapters = db.execute("SELECT * FROM chapter ORDER BY sort_order").fetchall()
        return render_template(
            "questions.html", questions=questions, chapters=chapters,
            sel_cid=cid, sel_qtype=qtype,
        )

    def _parse_question_form():
        options = []
        if request.form.get("qtype") in ("single", "multi"):
            for i in range(4):
                v = (request.form.get("option_%d" % i) or "").strip()
                if v:
                    options.append(v)
        return {
            "chapter_id": request.form.get("chapter_id", type=int),
            "qtype": request.form.get("qtype"),
            "difficulty": request.form.get("difficulty", default=1, type=int),
            "content": (request.form.get("content") or "").strip(),
            "options": options,
            "answer": (request.form.get("answer") or "").strip(),
            "analysis": (request.form.get("analysis") or "").strip(),
            "score": request.form.get("score", default=5, type=float),
        }

    @app.route("/questions/new", methods=["GET", "POST"])
    @roles_required("teacher", "admin")
    def question_new():
        db = get_db()
        chapters = db.execute("SELECT * FROM chapter ORDER BY sort_order").fetchall()
        if request.method == "POST":
            data = _parse_question_form()
            if not data["content"] or not data["answer"] or not data["chapter_id"]:
                flash("题干、答案、章节为必填项", "danger")
                return render_template("question_form.html", chapters=chapters, q=None, form=data)
            db.execute(
                "INSERT INTO question (chapter_id,qtype,difficulty,content,options,answer,analysis,score)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (data["chapter_id"], data["qtype"], data["difficulty"], data["content"],
                 json.dumps(data["options"], ensure_ascii=False) if data["options"] else None,
                 data["answer"], data["analysis"], data["score"]),
            )
            db.commit()
            flash("题目新增成功", "success")
            return redirect(url_for("questions"))
        return render_template("question_form.html", chapters=chapters, q=None, form=None)

    @app.route("/questions/<int:qid>/edit", methods=["GET", "POST"])
    @roles_required("teacher", "admin")
    def question_edit(qid):
        db = get_db()
        row = db.execute("SELECT * FROM question WHERE id=?", (qid,)).fetchone()
        if not row:
            abort(404)
        chapters = db.execute("SELECT * FROM chapter ORDER BY sort_order").fetchall()
        if request.method == "POST":
            data = _parse_question_form()
            if not data["content"] or not data["answer"] or not data["chapter_id"]:
                flash("题干、答案、章节为必填项", "danger")
                return render_template("question_form.html", chapters=chapters, q=row_to_question(row), form=data)
            db.execute(
                "UPDATE question SET chapter_id=?,qtype=?,difficulty=?,content=?,options=?,"
                "answer=?,analysis=?,score=? WHERE id=?",
                (data["chapter_id"], data["qtype"], data["difficulty"], data["content"],
                 json.dumps(data["options"], ensure_ascii=False) if data["options"] else None,
                 data["answer"], data["analysis"], data["score"], qid),
            )
            db.commit()
            flash("题目修改成功", "success")
            return redirect(url_for("questions"))
        return render_template("question_form.html", chapters=chapters, q=row_to_question(row), form=None)

    @app.route("/questions/<int:qid>/delete", methods=["POST"])
    @roles_required("teacher", "admin")
    def question_delete(qid):
        db = get_db()
        db.execute("DELETE FROM question WHERE id=?", (qid,))
        db.commit()
        flash("题目已删除", "success")
        return redirect(url_for("questions"))

    # ---------------- 用户管理（管理员） ----------------
    @app.route("/users")
    @roles_required("admin")
    def users():
        db = get_db()
        rows = db.execute("SELECT * FROM user ORDER BY id").fetchall()
        return render_template("users.html", users=rows)

    @app.route("/users/<int:uid>/delete", methods=["POST"])
    @roles_required("admin")
    def user_delete(uid):
        if uid == current_user()["id"]:
            flash("不能删除当前登录的管理员账号", "danger")
            return redirect(url_for("users"))
        db = get_db()
        db.execute("DELETE FROM user WHERE id=?", (uid,))
        db.commit()
        flash("用户已删除", "success")
        return redirect(url_for("users"))

    # ---------------- 错误处理 ----------------
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, msg="您没有权限访问该页面"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, msg="页面不存在"), 404

    @app.context_processor
    def inject_globals():
        user = current_user()
        favorite_ids = set()
        if user is not None:
            favorite_ids = {
                r["question_id"]
                for r in get_db().execute(
                    "SELECT question_id FROM favorite WHERE user_id=?", (user["id"],)
                )
            }
        return {"current_user": user, "QTYPE_NAMES": QTYPE_NAMES,
                "DIFF_NAMES": DIFF_NAMES, "favorite_ids": favorite_ids}


def _display_answer(q):
    """把题目标准答案转换为便于展示的形式。"""
    ans = q["answer"]
    if q["qtype"] == "judge":
        return "正确" if normalize_answer("judge", ans) == "T" else "错误"
    if q["qtype"] == "single":
        idx = "ABCD".find(ans.strip().upper())
        if idx >= 0 and idx < len(q["options"]):
            return "%s. %s" % (ans.strip().upper(), q["options"][idx])
    if q["qtype"] == "multi":
        parts = ans.split(",")
        txt = []
        for p in parts:
            idx = "ABCD".find(p.strip().upper())
            if idx >= 0 and idx < len(q["options"]):
                txt.append("%s. %s" % (p.strip().upper(), q["options"][idx]))
            else:
                txt.append(p)
        return "；".join(txt)
    return ans


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)