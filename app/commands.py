import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User, Tag, Article, SiteSetting
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

    # 创建默认网站设置
    settings = SiteSetting.query.first()
    if not settings:
        settings = SiteSetting(
            site_name="精选文章",
            site_description="一个基于 Flask 的新闻文章网站",
            site_language="zh",
        )
        db.session.add(settings)
        click.echo("创建默认网站设置...")

    try:
        db.session.commit()
        click.echo("数据初始化完成！")
    except Exception as e:
        db.session.rollback()
        click.echo(f"数据初始化失败: {str(e)}")


@click.command("init-db")
@with_appcontext
def init_db_command():
    """初始化数据库"""
    db.create_all()
    click.echo("数据库表已创建。")
