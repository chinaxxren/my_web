from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    jsonify,
)
from flask_login import login_required, current_user
from ..extensions import db
from app.admin import bp
from app.admin.forms import (
    ArticleForm,
    TagForm,
    UserForm,
    ImageUploadForm,
    SiteSettingForm,
)
from app.models import Article, Tag, User, Image, SiteSetting
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from app.utils import admin_required


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("需要管理员权限")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/")
@login_required
@admin_required
def index():
    # 统计信息
    today = datetime.utcnow().date()
    stats = {
        "total_articles": Article.query.count(),
        "published_articles": Article.query.filter_by(is_published=True).count(),
        "draft_articles": Article.query.filter_by(is_published=False).count(),
        "articles_today": Article.query.filter(
            Article.is_published == True,
            Article.created_at >= today,
            Article.created_at < today + timedelta(days=1),
        ).count(),
        "total_tags": Tag.query.count(),
        "new_tags_this_week": Tag.query.filter(
            Tag.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count(),
        "total_users": User.query.count(),
        "admin_users": User.query.filter_by(is_admin=True).count(),
        "normal_users": User.query.filter_by(is_admin=False).count(),
    }

    # 最近文章
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()

    return render_template(
        "admin/index.html",
        stats=stats,
        recent_articles=recent_articles,
    )


@bp.route("/articles")
@login_required
@admin_required
def articles():
    page = request.args.get("page", 1, type=int)
    articles = Article.query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    return render_template("admin/articles.html", articles=articles)


@bp.route("/article/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_article():
    form = ArticleForm()
    image_form = ImageUploadForm()
    if request.method == "GET":
        form.is_published.data = True
    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            content=form.content.data,
            is_published=form.is_published.data,
            is_top=form.is_top.data,
            is_recommended=form.is_recommended.data,
            author=current_user,
        )
        # 处理标签
        tag_names = [name.strip() for name in form.tags.data.split(",") if name.strip()]
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            article.tags.append(tag)

        db.session.add(article)
        db.session.commit()

        # 关联临时图片
        temp_images = Image.get_temporary_images()
        for image in temp_images:
            image.associate_with_article(article.id)

        flash("文章已创建")
        return redirect(url_for("admin.articles"))

    # 获取当前用户的临时图片
    temp_images = Image.get_temporary_images()

    return render_template(
        "admin/article_form.html",
        title="新建文章",
        form=form,
        image_form=image_form,
        temp_images=temp_images,
    )


@bp.route("/article/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    form = ArticleForm()
    image_form = ImageUploadForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.is_published = form.is_published.data
        article.is_top = form.is_top.data
        article.is_recommended = form.is_recommended.data

        # 更新标签
        article.tags = []
        tag_names = [name.strip() for name in form.tags.data.split(",") if name.strip()]
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            article.tags.append(tag)

        db.session.commit()
        flash("文章已更新")
        return redirect(url_for("admin.articles"))
    elif request.method == "GET":
        form.title.data = article.title
        form.content.data = article.content
        form.is_published.data = article.is_published
        form.is_top.data = article.is_top
        form.is_recommended.data = article.is_recommended
        form.tags.data = ", ".join([tag.name for tag in article.tags])
    return render_template(
        "admin/article_form.html",
        title="编辑文章",
        form=form,
        article=article,
        image_form=image_form,
    )


@bp.route("/article/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_article(id):
    article = Article.query.get_or_404(id)

    # 删除物理文件
    for image in article.images:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    # 删除文章（会自动级联删除图片记录）
    db.session.delete(article)
    db.session.commit()

    flash("文章已删除")
    return redirect(url_for("admin.articles"))


@bp.route("/tags")
@login_required
@admin_required
def tags():
    tags = Tag.query.all()
    return render_template("admin/tags.html", tags=tags)


@bp.route("/tag/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_tag():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        flash("标签已创建")
        return redirect(url_for("admin.tags"))
    return render_template("admin/tag_form.html", title="新建标签", form=form)


@bp.route("/tag/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    form = TagForm()
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.commit()
        flash("标签已更新")
        return redirect(url_for("admin.tags"))
    elif request.method == "GET":
        form.name.data = tag.name
    return render_template("admin/tag_form.html", title="编辑标签", form=form)


@bp.route("/tag/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash("标签已删除")
    return redirect(url_for("admin.tags"))


@bp.route("/users")
@login_required
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    return render_template("admin/users.html", users=users.items, pagination=users)


@bp.route("/user/<int:id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(original_username=user.username, original_email=user.email)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash("用户信息已更新")
        return redirect(url_for("admin.users"))
    elif request.method == "GET":
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin
    return render_template(
        "admin/user_form.html", title="编辑用户", form=form, user=user
    )


@bp.route("/upload_temp_image", methods=["POST"])
@login_required
@admin_required
def upload_temp_image():
    form = ImageUploadForm()
    if form.validate_on_submit():
        file = form.image.data
        if file:
            # 生成唯一文件名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"

            # 保存文件
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], unique_filename
            )
            file.save(file_path)

            # 创建图片记录
            image = Image(
                filename=unique_filename,
                original_filename=filename,
                file_size=os.path.getsize(file_path),
                file_type=file.content_type,
                is_temporary=True,
                temp_id=Image.generate_temp_id(),
            )

            db.session.add(image)
            db.session.commit()

            return jsonify(
                {"success": True, "message": "图片上传成功", "image": image.to_dict()}
            )

    return jsonify({"success": False, "error": "图片上传失败"})


@bp.route("/delete_temp_image/<temp_id>", methods=["POST"])
@login_required
@admin_required
def delete_temp_image(temp_id):
    image = Image.query.filter_by(temp_id=temp_id, is_temporary=True).first_or_404()

    # 删除文件
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # 删除数据库记录
    db.session.delete(image)
    db.session.commit()

    return jsonify({"success": True, "message": "图片已删除"})


@bp.route("/article/<int:article_id>/upload_image", methods=["POST"])
@login_required
@admin_required
def upload_image(article_id):
    article = Article.query.get_or_404(article_id)
    form = ImageUploadForm()
    if form.validate_on_submit():
        file = form.image.data
        if file:
            # 生成唯一文件名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"

            # 保存文件
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], unique_filename
            )
            file.save(file_path)

            # 创建图片记录
            image = Image(
                filename=unique_filename,
                original_filename=filename,
                file_size=os.path.getsize(file_path),
                file_type=file.content_type,
                article_id=article.id,
                is_temporary=False,
            )

            db.session.add(image)
            db.session.commit()

            return jsonify(
                {"success": True, "message": "图片上传成功", "image": image.to_dict()}
            )

    return jsonify({"success": False, "error": "图片上传失败"})


@bp.route("/image/<int:id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_image(id):
    image = Image.query.get_or_404(id)

    # 删除文件
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # 删除数据库记录
    db.session.delete(image)
    db.session.commit()

    return jsonify({"success": True, "message": "图片已删除"})


@bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def settings():
    settings = SiteSetting.get_settings()
    form = SiteSettingForm(obj=settings)
    if form.validate_on_submit():
        settings.site_name = form.site_name.data
        settings.site_description = form.site_description.data
        settings.site_language = form.site_language.data
        db.session.commit()
        flash("设置已更新")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", form=form)
