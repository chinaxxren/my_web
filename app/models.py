from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login
import uuid


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    articles = db.relationship("Article", backref="author", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    is_top = db.Column(db.Boolean, default=False)
    is_recommended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tags = db.relationship("Tag", secondary="article_tag", backref="articles")
    images = db.relationship("Image", backref="article", lazy="dynamic")

    def __repr__(self):
        return f"<Article {self.title}>"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Tag {self.name}>"


article_tag = db.Table(
    "article_tag",
    db.Column("article_id", db.Integer, db.ForeignKey("article.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"))
    is_temporary = db.Column(db.Boolean, default=True)
    temp_id = db.Column(db.String(36), unique=True)  # 用于临时图片的唯一标识

    def __repr__(self):
        return f"<Image {self.filename}>"

    @staticmethod
    def generate_temp_id():
        return str(uuid.uuid4())

    @staticmethod
    def cleanup_temporary_images(hours=24):
        """清理超过指定时间的临时图片"""
        from app import current_app
        import os
        from datetime import datetime, timedelta

        # 获取超过指定时间的临时图片
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        temp_images = Image.query.filter(
            Image.is_temporary == True, Image.created_at < cutoff_time
        ).all()

        for image in temp_images:
            # 删除文件
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], image.filename
            )
            if os.path.exists(file_path):
                os.remove(file_path)

            # 删除数据库记录
            db.session.delete(image)

        db.session.commit()

    def to_dict(self):
        """将图片对象转换为字典"""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "created_at": self.created_at.isoformat(),
            "article_id": self.article_id,
            "is_temporary": self.is_temporary,
            "temp_id": self.temp_id,
        }

    def associate_with_article(self, article_id):
        """将临时图片关联到文章"""
        if self.is_temporary:
            self.article_id = article_id
            self.is_temporary = False
            self.temp_id = None
            db.session.commit()

    @classmethod
    def get_temporary_images(cls):
        """获取所有临时图片，按创建时间倒序排序"""
        return (
            cls.query.filter_by(is_temporary=True).order_by(cls.created_at.desc()).all()
        )
