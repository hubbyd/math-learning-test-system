# -*- coding: utf-8 -*-
"""判分模块：答案规范化与单题判分。

支持四种题型：
    single 单选 / multi 多选 / judge 判断 / fill 填空
"""
import re

_ZH_TRUE = {"T", "TRUE", "对", "√", "正确", "是", "1"}
_ZH_FALSE = {"F", "FALSE", "错", "×", "错误", "否", "0"}


def normalize_answer(qtype, ans):
    """把用户答案和标准答案统一规范化为可比较的字符串。"""
    if ans is None:
        return ""
    a = str(ans).strip()
    if qtype == "single":
        return a.upper()
    if qtype == "multi":
        parts = [p for p in re.split(r"[,，、\s]+", a.upper()) if p]
        return ",".join(sorted(set(parts)))
    if qtype == "judge":
        up = a.upper()
        if up in _ZH_TRUE:
            return "T"
        if up in _ZH_FALSE:
            return "F"
        return up
    if qtype == "fill":
        # 忽略大小写与所有空白字符，便于学生输入 e^x+C / e^x + c 等
        return re.sub(r"\s+", "", a).lower()
    return a


def grade_question(qtype, correct_answer, user_answer):
    """返回布尔值表示是否答对。"""
    return normalize_answer(qtype, correct_answer) == normalize_answer(qtype, user_answer)


def grade_paper(items):
    """对整份试卷判分。

    items: [(qtype, correct_answer, user_answer, full_score), ...]
    返回 (得分, 每题明细列表)，明细为 (is_correct, got_score)。
    """
    total = 0.0
    detail = []
    for qtype, correct, user, full in items:
        ok = grade_question(qtype, correct, user)
        got = float(full) if ok else 0.0
        total += got
        detail.append((ok, got))
    return total, detail