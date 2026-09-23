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
            " (SELECT COUNT(*) FROM question q WHERE q.chapter_id=c.id) q_cnt"
            " FROM chapter c ORDER BY sort_order"
        ).fetchall()
        return render_template(
            "index.html", user=user, practice_cnt=practice_cnt,
            paper_cnt=paper_cnt, avg=round(avg, 1) if avg else 0,
            chapters=chapters,
        )

    # ---------------- 用户管理 ----------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            real_name = (request.form.get("real_name") or "").strip()
            role = request.form.get("role") or "student"
            if role not in ("student", "teacher"):
                role = "student"
            err = None
            if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
                err = "用户名须为 3~20 位字母、数字或下划线"
            elif len(password) < 6:
                err = "密码长度不能少于 6 位"
            if err is None:
                db = get_db()
                if db.execute("SELECT 1 FROM user WHERE username=?", (username,)).fetchone():
                    err = "该用户名已存在"
                else:
                    from werkzeug.security import generate_password_hash
                    db.execute(
                        "INSERT INTO user (username,password_hash,role,real_name) VALUES (?,?,?,?)",
                        (username, generate_password_hash(password), role, real_name),
                    )
                    db.commit()
                    flash("注册成功，请登录", "success")
                    return redirect(url_for("login"))
            flash(err, "danger")
        return render_template("register.html")

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
        db = get_db()
        chapters = db.execute(
            "SELECT c.*, (SELECT COUNT(*) FROM lesson l WHERE l.chapter_id=c.id) lesson_cnt"
            " FROM chapter c ORDER BY sort_order"
        ).fetchall()
        return render_template("learning_chapters.html", chapters=chapters)

    @app.route("/learning/chapter/<int:cid>")
    @login_required
    def learning_chapter(cid):
        db = get_db()
        chapter = db.execute("SELECT * FROM chapter WHERE id=?", (cid,)).fetchone()
        if not chapter:
            abort(404)
        lessons = db.execute(
            "SELECT * FROM lesson WHERE chapter_id=? ORDER BY sort_order, id", (cid,)
        ).fetchall()
        return render_template("learning_chapter.html", chapter=chapter, lessons=lessons)

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
        return render_template("learning_lesson.html", lesson=lesson, chapter=chapter)

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
        cur = db.execute(
            "INSERT INTO paper (user_id,title,total_score,got_score,status) VALUES (?,?,?,0,'ongoing')",
            (user["id"], "高等数学综合测试", total),
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
        return render_template("test_take.html", paper=paper, questions=questions)

    @app.route("/test/<int:pid>/submit", methods=["POST"])
    @login_required
    def test_submit(pid):
        db = get_db()
        paper = db.execute("SELECT * FROM paper WHERE id=?", (pid,)).fetchone()
        if not paper:
            abort(404)
        if paper["status"] == "submitted":
            return redirect(url_for("test_result", pid=pid))
        pq = db.execute(
            "SELECT pq.id AS pqid, q.* FROM paper_question pq"
            " JOIN question q ON q.id=pq.question_id WHERE pq.paper_id=?", (pid,),
        ).fetchall()
        total_get = 0.0
        for r in pq:
            q = row_to_question(r)
            if q["qtype"] == "multi":
                user_ans = ",".join(request.form.getlist("q_%d" % q["id"]))
            else:
                user_ans = request.form.get("q_%d" % q["id"])
            ok = grade_question(q["qtype"], q["answer"], user_ans)
            got = float(q["score"]) if ok else 0.0
            total_get += got
            db.execute(
                "UPDATE paper_question SET user_answer=?, is_correct=?, got_score=? WHERE id=?",
                (user_ans, 1 if ok else 0, got, r["pqid"]),
            )
        db.execute(
            "UPDATE paper SET status='submitted', got_score=?, submitted_at=datetime('now','localtime')"
            " WHERE id=?", (total_get, pid),
        )
        db.commit()
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
        return render_template("scores.html", papers=papers, user=user)

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
        return {"current_user": current_user(), "QTYPE_NAMES": QTYPE_NAMES,
                "DIFF_NAMES": DIFF_NAMES}


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