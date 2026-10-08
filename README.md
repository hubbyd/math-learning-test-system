# 高等数学学习、测试系统（题目十二）

软件工程课程设计：基于 Flask + SQLite 的高等数学在线学习与测试平台（B/S 架构）。

[![Deploy to Render](https://render.com/images/deploy-button.svg)](https://render.com/deploy?repo=https://github.com/hubbyd/math-learning-test-system)

## 功能

- 用户管理：注册（角色选择、密码强度提示、二次确认、学号/邮箱）与登录（演示账号一键填充）
- 课程学习：6 章 18 个结构化课节（学习目标 / 知识要点 / 定理公式 / 典型例题 / 小结），
  章节进度条、课节目录导航、上一节/下一节、个人学习笔记
- 随堂练习：按章节抽题、即时判分与解析
- 综合测试：按题型比例自动组卷、可选限时时长、服务端倒计时（刷新不重置）、
  答题卡快速跳转、作答本地暂存、超时自动交卷
- 错题本：练习/测试错题自动收录，重做答对自动移除，支持一键重做
- 收藏夹：典型题、易错题一键收藏
- 成绩查询：得分率趋势图（纯 SVG，无外部依赖）与答卷详情
- 积分排行榜：练习答对×2 + 测试得分 + 课节学习×3，Top 10 实时排名
- 题库管理：单选 / 多选 / 判断 / 填空，三种难度，共 50+ 精编习题
- 红黑（Crimson Noir）主题 UI，响应式布局

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
│   ├── db.py                # 数据库建表、迁移与种子数据
│   ├── seed_data.py         # 课程内容与题库（集中维护）
│   ├── grading.py           # 判分逻辑
│   ├── mathlearn.db         # SQLite 数据库（含种子数据）
│   ├── templates/           # Jinja2 模板
│   ├── static/              # 红黑主题样式
│   └── tests/               # pytest 测试（27 项）
├── 实验1-可行性分析报告-*.docx
├── 实验5-项目实现报告-*.docx
└── 实验6-项目测试报告-*.docx
```
