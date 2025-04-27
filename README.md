# 新闻网站

一个基于 Flask 的新闻网站，支持文章发布、评论、标签管理等功能。

## 功能特点

- 用户系统（注册、登录、权限管理）
- 文章管理（创建、编辑、删除、发布）
- 标签管理
- 评论系统
- 图片上传
- Markdown 支持
- 搜索功能
- 管理后台

## 安装步骤

1. 克隆项目

```bash
git clone <repository-url>
cd news_web
```

2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置环境变量
   创建 `.env` 文件并设置以下变量：

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
```

## 启动应用

1. 运行启动脚本

```bash
python run.py
```

2. 访问应用

- 前台：http://localhost:5000
- 后台：http://localhost:5000/admin
- 管理员账号：admin
- 管理员密码：admin

## 开发说明

- 使用 Flask 作为 Web 框架
- 使用 SQLAlchemy 作为 ORM
- 使用 Flask-Migrate 管理数据库迁移
- 使用 Flask-Login 处理用户认证
- 使用 Flask-WTF 处理表单
- 使用 Markdown 和 Bleach 处理文章内容
- 使用 Bootstrap 5 构建界面

## 项目结构

```
news_web/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── templates/
│   └── static/
├── migrations/
├── config.py
├── run.py
└── requirements.txt
```
