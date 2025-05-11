import os
from flask import Flask, request, g
from config import Config
from .extensions import db, login, babel
import re


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    babel.init_app(app)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.admin import bp as admin_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")

    # 注册命令
    from app.commands import init_data, init_db_command

    app.cli.add_command(init_data)
    app.cli.add_command(init_db_command)

    @babel.localeselector
    def get_locale():
        # 从数据库获取语言设置
        from app.models import SiteSetting

        settings = SiteSetting.get_settings()
        if settings and settings.site_language in ["en", "zh"]:
            return settings.site_language
        return "zh"

    @app.template_filter("markdown")
    def markdown_filter(text):
        from markdown import markdown

        return markdown(text)

    @app.template_filter("wrap_images")
    def wrap_images_filter(html):
        # 如果已经有 image-wrapper，不再包装
        if 'class="image-wrapper"' in html:
            return html

        # 处理被 p 标签包裹的图片
        pattern = r"<p>(\s*<img[^>]+>\s*)</p>"
        replacement = r'<div class="image-wrapper" style="display: block; width: 100%; max-width: 800px; margin: 2rem auto; text-align: center;"><img style="display: block; max-width: 100%; height: auto; margin: 0 auto; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" \1</div>'
        result = re.sub(pattern, replacement, html)

        # 处理未被 p 标签包裹的图片
        pattern = r'(?<!wrapper">)(<img[^>]+>)'
        replacement = r'<div class="image-wrapper" style="display: block; width: 100%; max-width: 800px; margin: 2rem auto; text-align: center;"><img style="display: block; max-width: 100%; height: auto; margin: 0 auto; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" \1</div>'
        result = re.sub(pattern, replacement, result)

        return result

    @app.template_filter("timedelta")
    def timedelta_filter(dt):
        from datetime import datetime

        now = datetime.utcnow()
        diff = now - dt
        days = diff.days
        seconds = diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if days > 0:
            return f"{days}天前"
        elif hours > 0:
            return f"{hours}小时前"
        elif minutes > 0:
            return f"{minutes}分钟前"
        else:
            return "刚刚"

    return app


from app import models
