# 高等数学学习、测试系统（题目十二）

软件工程课程设计：基于 Flask + SQLite 的高等数学在线学习与测试平台（B/S 架构）。

[![Deploy to Render](https://render.com/images/deploy-button.svg)](https://render.com/deploy?repo=https://github.com/hubbyd/math-learning-test-system)

## 功能

- 用户管理（管理员 / 教师 / 学生三种角色，注册登录）
- 课程学习：6 章高等数学内容，MathJax 公式渲染
- 随堂练习：按章节抽题、即时判分
- 综合测试：自动组卷、限时作答、自动评分
- 题库管理：单选 / 多选 / 判断 / 填空，三种难度
- 成绩查询与统计分析

## 本地运行

```bash
cd mathsystem
pip install -r requirements.txt
python app.py
# 访问 http://127.0.0.1:5000
```

默认账号：`admin/admin123`（管理员）、`teacher/teacher123`（教师）、`student/student123`（学生）

## 测试

```bash
cd mathsystem
python -m pytest tests/ -v
```

## 部署（Render 免费版）

仓库根目录的 `render.yaml` 为 Render Blueprint 配置，点击上方按钮一键部署，或参考：

1. 在 [Render](https://render.com) 用 GitHub 账号登录
2. New → Blueprint → 选择本仓库
3. 使用默认配置创建，等待构建完成即可获得 `https://<你的服务名>.onrender.com` 访问地址

> 说明：Render 免费版使用临时文件系统，服务重启后数据库会自动重建为初始种子数据；15 分钟无访问会休眠，首次唤醒需等待约 30–50 秒。

## 目录结构

```
├── render.yaml              # Render 部署配置
├── mathsystem/              # 应用主目录
│   ├── app.py               # Flask 入口与路由
│   ├── db.py                # 数据库建表与种子数据
│   ├── grading.py           # 判分逻辑
│   ├── mathlearn.db         # SQLite 数据库（含种子数据）
│   ├── templates/           # Jinja2 模板
│   ├── static/              # 样式
│   └── tests/               # pytest 测试（20 项）
├── 实验1-可行性分析报告-*.docx
├── 实验5-项目实现报告-*.docx
└── 实验6-项目测试报告-*.docx
```
