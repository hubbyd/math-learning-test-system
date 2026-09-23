# -*- coding: utf-8 -*-
"""高等数学学习、测试系统 —— 自动化测试用例（pytest）。

覆盖：用户管理、权限控制、课程学习、随堂练习判分、综合测试组卷与判分、
题库增删改查、成绩与统计分析，以及判分模块的单元测试。
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app                     # noqa: E402
from db import get_db                          # noqa: E402
from grading import normalize_answer, grade_question  # noqa: E402


# --------------------------------------------------------------------------
# 测试夹具
# --------------------------------------------------------------------------
@pytest.fixture
def app():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    application = create_app(database=path, testing=True)
    yield application
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password},
                       follow_redirects=True)


def query(sql, args=()):
    """在当前应用上下文中执行查询（需在 app_context 内调用）。"""
    return get_db().execute(sql, args).fetchall()


# --------------------------------------------------------------------------
# 1. 数据库初始化 / 种子数据
# --------------------------------------------------------------------------
def test_seed_chapters_and_questions(app):
    with app.app_context():
        chapters = query("SELECT * FROM chapter")
        questions = query("SELECT * FROM question")
        users = query("SELECT * FROM user")
    assert len(chapters) == 6
    assert len(questions) >= 25
    assert len(users) == 3


# --------------------------------------------------------------------------
# 2. 用户注册与登录
# --------------------------------------------------------------------------
def test_login_success(client):
    resp = login(client, "student", "student123")
    assert resp.status_code == 200
    assert "登录成功" in resp.get_data(as_text=True)


def test_login_wrong_password(client):
    resp = login(client, "student", "wrong-password")
    assert "用户名或密码错误" in resp.get_data(as_text=True)


def test_register_and_duplicate(client):
    resp = client.post("/register",
                       data={"username": "newuser01", "password": "abc123456",
                             "real_name": "王同学", "role": "student"},
                       follow_redirects=True)
    assert "注册成功" in resp.get_data(as_text=True)
    # 重复注册同名用户
    resp2 = client.post("/register",
                        data={"username": "newuser01", "password": "abc123456"},
                        follow_redirects=True)
    assert "该用户名已存在" in resp2.get_data(as_text=True)


# --------------------------------------------------------------------------
# 3. 访问控制
# --------------------------------------------------------------------------
def test_index_requires_login(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_student_forbidden_question_manage(client):
    login(client, "student", "student123")
    resp = client.get("/questions")
    assert resp.status_code == 403


def test_teacher_forbidden_user_manage(client):
    login(client, "teacher", "teacher123")
    resp = client.get("/users")
    assert resp.status_code == 403


def test_admin_can_access_user_manage(client):
    login(client, "admin", "admin123")
    resp = client.get("/users")
    assert resp.status_code == 200


# --------------------------------------------------------------------------
# 4. 课程学习
# --------------------------------------------------------------------------
def test_learning_pages_and_record(client, app):
    login(client, "student", "student123")
    assert client.get("/learning").status_code == 200
    assert client.get("/learning/chapter/1").status_code == 200
    resp = client.get("/learning/lesson/1")
    assert resp.status_code == 200
    with app.app_context():
        rows = query("SELECT * FROM learning_record WHERE lesson_id=1")
    assert len(rows) == 1


# --------------------------------------------------------------------------
# 5. 随堂练习流程
# --------------------------------------------------------------------------
def test_practice_all_correct(client, app):
    login(client, "student", "student123")
    with app.app_context():
        rows = query("SELECT id, qtype, answer FROM question WHERE chapter_id=1 LIMIT 3")
        ids = [r["id"] for r in rows]
        data = {"qids": ",".join(str(i) for i in ids)}
        for r in rows:
            if r["qtype"] == "multi":
                for a in r["answer"].split(","):
                    data.setdefault("q_%d" % r["id"], [])
                    data["q_%d" % r["id"]].append(a)
            else:
                data["q_%d" % r["id"]] = r["answer"]
    resp = client.post("/practice/submit", data=data)
    text = resp.get_data(as_text=True)
    assert "答对 3 题" in text
    assert "100.0%" in text


def test_practice_wrong_answer(client, app):
    login(client, "student", "student123")
    with app.app_context():
        rows = query("SELECT id FROM question WHERE chapter_id=2 LIMIT 2")
        ids = [r["id"] for r in rows]
    data = {"qids": ",".join(str(i) for i in ids), "q_%d" % ids[0]: "X",
            "q_%d" % ids[1]: "X"}
    resp = client.post("/practice/submit", data=data)
    assert "0.0%" in resp.get_data(as_text=True)


def test_practice_start_page(client):
    login(client, "student", "student123")
    resp = client.get("/practice/start?chapter_id=1&count=5")
    assert resp.status_code == 200
    assert "随堂练习" in resp.get_data(as_text=True)


# --------------------------------------------------------------------------
# 6. 综合测试：自动组卷与判分
# --------------------------------------------------------------------------
def test_auto_paper_generation_and_submit(client, app):
    login(client, "student", "student123")
    resp = client.post("/test/create", data={
        "n_single": 2, "n_multi": 1, "n_judge": 1, "n_fill": 1, "difficulty": 0,
    })
    assert resp.status_code == 302
    pid = int(resp.headers["Location"].rstrip("/").split("/")[-1])

    with app.app_context():
        pq = query(
            "SELECT pq.id AS pqid, q.id AS qid, q.qtype, q.answer, q.score"
            " FROM paper_question pq JOIN question q ON q.id=pq.question_id"
            " WHERE pq.paper_id=?", (pid,))
        assert len(pq) == 5
        data = {}
        expected_total = 0
        for r in pq:
            expected_total += r["score"]
            if r["qtype"] == "multi":
                data["q_%d" % r["qid"]] = r["answer"].split(",")
            else:
                data["q_%d" % r["qid"]] = r["answer"]
        paper_before = query("SELECT * FROM paper WHERE id=?", (pid,))[0]
        assert paper_before["status"] == "ongoing"

    client.post("/test/%d/submit" % pid, data=data)

    with app.app_context():
        paper = query("SELECT * FROM paper WHERE id=?", (pid,))[0]
    assert paper["status"] == "submitted"
    assert paper["got_score"] == expected_total


def test_paper_filter_by_difficulty(client, app):
    login(client, "student", "student123")
    resp = client.post("/test/create", data={
        "n_single": 2, "difficulty": 1, "chapters": ["2"],
    })
    pid = int(resp.headers["Location"].rstrip("/").split("/")[-1])
    with app.app_context():
        rows = query(
            "SELECT q.difficulty, q.chapter_id FROM paper_question pq"
            " JOIN question q ON q.id=pq.question_id WHERE pq.paper_id=?", (pid,))
    assert len(rows) >= 1
    for r in rows:
        assert r["difficulty"] == 1
        assert r["chapter_id"] == 2


# --------------------------------------------------------------------------
# 7. 题库增删改查
# --------------------------------------------------------------------------
def test_question_crud(client, app):
    login(client, "teacher", "teacher123")
    resp = client.post("/questions/new", data={
        "chapter_id": 1, "qtype": "single", "difficulty": 2,
        "content": r"测试题目 \(1+1=?\)",
        "option_0": "1", "option_1": "2", "option_2": "3", "option_3": "4",
        "answer": "B", "analysis": "1+1=2", "score": 5,
    }, follow_redirects=True)
    assert "题目新增成功" in resp.get_data(as_text=True)
    with app.app_context():
        row = query("SELECT * FROM question WHERE content LIKE ?",
                    (r"%测试题目%",))
        assert len(row) == 1
        qid = row[0]["id"]

    # 编辑
    client.post("/questions/%d/edit" % qid, data={
        "chapter_id": 1, "qtype": "single", "difficulty": 3,
        "content": r"测试题目（已修改）", "option_0": "A1", "option_1": "B1",
        "answer": "A", "analysis": "改", "score": 6,
    }, follow_redirects=True)
    with app.app_context():
        row = query("SELECT * FROM question WHERE id=?", (qid,))[0]
    assert row["difficulty"] == 3
    assert row["content"] == "测试题目（已修改）"

    # 删除
    client.post("/questions/%d/delete" % qid, follow_redirects=True)
    with app.app_context():
        assert query("SELECT * FROM question WHERE id=?", (qid,)) == []


# --------------------------------------------------------------------------
# 8. 成绩与统计
# --------------------------------------------------------------------------
def test_scores_and_stats_pages(client):
    login(client, "teacher", "teacher123")
    assert client.get("/scores").status_code == 200
    assert client.get("/stats").status_code == 200


# --------------------------------------------------------------------------
# 9. 判分模块单元测试（白盒）
# --------------------------------------------------------------------------
def test_normalize_single_and_multi():
    assert normalize_answer("single", "b") == "B"
    assert normalize_answer("multi", "b,a") == "A,B"
    assert normalize_answer("multi", "A,B") == "A,B"
    assert normalize_answer("judge", "对") == "T"
    assert normalize_answer("judge", "错") == "F"


def test_grade_multi_order_insensitive():
    assert grade_question("multi", "A,B,D", "D,B,A") is True
    assert grade_question("multi", "A,B,D", "A,B") is False


def test_grade_fill_whitespace_and_case_insensitive():
    assert grade_question("fill", "sin x", "sinx") is True
    assert grade_question("fill", "e^x+C", "E^X + c") is True
    assert grade_question("fill", "3", "3") is True
    assert grade_question("fill", "3", "4") is False


def test_grade_judge_variants():
    assert grade_question("judge", "T", "对") is True
    assert grade_question("judge", "T", "F") is False