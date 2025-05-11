# Flask 多语言博客系统

## 项目简介

本项目是一个基于 Flask 的多语言博客系统，支持中英文切换，适合个人或团队博客使用。

## 主要特性

- 支持中英文国际化（i18n）
- 文章、标签、用户管理
- 管理后台（仅管理员可见）
- 文章搜索与标签浏览
- 支持 Markdown 文章内容
- 语言可在后台设置中切换

## 安装与运行

1. 克隆项目并进入目录：
   ```bash
   git clone <your-repo-url>
   cd my_web
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 初始化数据库（如首次运行）：
   ```bash
   flask db upgrade
   ```
4. 运行项目：
   ```bash
   flask run
   ```

## 依赖说明

所有依赖已在 `requirements.txt` 中列出，包括生产和开发/测试/文档依赖。

## 语言切换

管理员可在后台"网站设置"页面选择显示语言，前台页面将自动切换中英文。

## 目录结构简述

```
my_web/
├── app/                # 主应用目录
│   ├── templates/      # 前端模板
│   ├── static/         # 静态文件
│   └── ...
├── requirements.txt    # 依赖文件
├── README.md           # 项目说明
└── ...
```

---

# Flask Multi-language Blog System (English)

## Introduction

A Flask-based blog system supporting both Chinese and English, suitable for personal or team use.

## Features

- i18n (Chinese/English)
- Article, tag, and user management
- Admin dashboard (for admins only)
- Article search and tag browsing
- Markdown support for articles
- Language can be switched in admin settings

## Quick Start

1. Clone and enter the project:
   ```bash
   git clone <your-repo-url>
   cd my_web
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database (first run):
   ```bash
   flask db upgrade
   ```
4. Run the project:
   ```bash
   flask run
   ```

## Dependencies

All dependencies are listed in `requirements.txt`, including production, development, and documentation tools.

## Language Switch

Admin can set the display language in the admin settings page. The frontend will switch language accordingly.

## Directory Structure

```
my_web/
├── app/
│   ├── templates/
│   ├── static/
│   └── ...
├── requirements.txt
├── README.md
└── ...
```
