#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User
from flask_migrate import upgrade


def create_admin():
    """创建管理员用户"""
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", email="admin@example.com", is_admin=True)
        admin.set_password("admin")
        db.session.add(admin)
        db.session.commit()
        print("管理员用户已创建")
    else:
        print("管理员用户已存在")


def init_db():
    """初始化数据库"""
    print("正在初始化数据库...")
    upgrade()
    print("数据库初始化完成")


def create_upload_folder():
    """创建上传文件夹"""
    upload_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "app/static/uploads"
    )
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print("上传文件夹已创建")
    else:
        print("上传文件夹已存在")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        init_db()
        create_admin()
        create_upload_folder()

    print("应用启动中...")
    app.run(host="0.0.0.0", port=3389, debug=True)
