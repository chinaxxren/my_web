import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Tag
from werkzeug.security import generate_password_hash


@click.command("init-data")
@with_appcontext
def init_data():
    """初始化数据"""
    click.echo("开始初始化数据...")

    # 创建管理员用户
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
        )
        db.session.add(admin)
        click.echo("创建管理员用户...")

    # 创建默认标签
    default_tags = ["新闻", "技术", "生活", "娱乐", "体育"]
    for tag_name in default_tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
            click.echo(f"创建标签: {tag_name}")

    try:
        db.session.commit()
        click.echo("数据初始化完成！")
    except Exception as e:
        db.session.rollback()
        click.echo(f"数据初始化失败: {str(e)}")
