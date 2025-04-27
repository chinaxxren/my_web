from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class ArticleForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(max=200)])
    subtitle = StringField("副标题", validators=[Length(max=200)])
    content = TextAreaField("内容", validators=[DataRequired()])
    tags = StringField("标签（用英文逗号分隔）", validators=[DataRequired()])
    is_published = BooleanField("发布")
    is_top = BooleanField("置顶")
    is_recommended = BooleanField("推荐")
    submit = SubmitField("提交")

    def validate_tags(self, tags):
        if tags.data:
            # 检查是否包含中文逗号
            if "，" in tags.data:
                raise ValidationError("请使用英文逗号(,)分隔标签")
            # 检查是否包含其他特殊字符
            if any(char in tags.data for char in [";", ":", "|", "、"]):
                raise ValidationError("请使用英文逗号(,)分隔标签")
            # 检查标签是否为空
            tag_list = [tag.strip() for tag in tags.data.split(",")]
            if any(not tag for tag in tag_list):
                raise ValidationError("标签不能为空")
            # 检查标签长度
            if any(len(tag) > 50 for tag in tag_list):
                raise ValidationError("每个标签长度不能超过50个字符")


class TagForm(FlaskForm):
    name = StringField("标签名称", validators=[DataRequired(), Length(max=50)])
    submit = SubmitField("提交")


class UserForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("邮箱", validators=[DataRequired(), Email()])
    is_admin = BooleanField("管理员权限")
    submit = SubmitField("提交")

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError("用户名已存在")

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError("邮箱已存在")


class ImageUploadForm(FlaskForm):
    image = FileField(
        "选择图片",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "jpeg", "png", "gif"], "只允许上传图片文件!"),
        ],
    )
    submit = SubmitField("上传")
