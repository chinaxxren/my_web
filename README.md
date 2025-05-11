# 精选文章网站

一个基于 Flask 的新闻文章网站，支持文章发布、标签管理、用户认证等功能。

## 功能特点

- 文章管理：发布、编辑、删除文章
- 标签系统：为文章添加标签，按标签浏览文章
- 用户认证：登录、注册、权限管理
- 响应式设计：适配各种设备屏幕
- Markdown 支持：使用 Markdown 编写文章
- 图片上传：支持文章配图
- 搜索功能：全文搜索文章
- 多语言支持：使用 Flask-Babel 实现国际化

## 技术栈

- 后端：Flask
- 数据库：SQLite
- 前端：Bootstrap 5
- 模板引擎：Jinja2
- 认证：Flask-Login
- 表单处理：Flask-WTF
- 国际化：Flask-Babel
- Markdown 渲染：Python-Markdown
- 图片处理：Pillow

## 安装说明

1. 克隆仓库：

```bash
git clone <repository-url>
cd <project-directory>
```

2. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置环境变量：
   创建 `.env` 文件并设置必要的环境变量：

```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

5. 初始化数据库：

```bash
flask init-db
```

6. 运行应用：

```bash
flask run
```

## 项目结构

```
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── extensions.py
│   ├── main/
│   ├── auth/
│   └── admin/
├── static/
├── templates/
├── tests/
├── .env
├── config.py
├── requirements.txt
└── README.md
```

## 开发指南

### 添加新功能

1. 在相应的模块中创建新的路由和视图函数
2. 更新数据库模型（如果需要）
3. 创建或修改模板
4. 添加必要的静态文件
5. 更新测试用例

### 运行测试

```bash
flask test
```

### 代码风格

- 遵循 PEP 8 规范
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查

## 部署

1. 确保所有依赖都已安装
2. 设置生产环境变量
3. 运行部署脚本：

```bash
./deploy.sh
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License
