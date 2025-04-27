from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Article, Tag


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    # 获取置顶文章
    top_articles = (
        Article.query.filter_by(is_published=True, is_top=True)
        .order_by(Article.created_at.desc())
        .limit(4)
        .all()
    )

    # 获取推荐文章
    recommended_articles = (
        Article.query.filter_by(is_published=True, is_recommended=True)
        .order_by(Article.created_at.desc())
        .limit(6)
        .all()
    )

    # 获取最新文章（分页）
    latest_articles = (
        Article.query.filter_by(is_published=True)
        .order_by(Article.created_at.desc())
        .paginate(page=page, per_page=current_app.config["POSTS_PER_PAGE"])
    )

    return render_template(
        "main/index.html",
        top_articles=top_articles,
        recommended_articles=recommended_articles,
        latest_articles=latest_articles.items,
        pagination=latest_articles,
    )


@bp.route("/article/<int:id>")
def article(id):
    article = Article.query.get_or_404(id)
    if not article.is_published and not (
        current_user.is_authenticated and current_user.is_admin
    ):
        flash("该文章尚未发布")
        return redirect(url_for("main.index"))

    # 获取相关文章（根据标签）
    related_articles = []
    if article.tags:
        related_articles = (
            Article.query.filter(
                Article.tags.any(Tag.id.in_([tag.id for tag in article.tags])),
                Article.id != id,
                Article.is_published == True,
            )
            .order_by(Article.created_at.desc())
            .limit(5)
            .all()
        )

    return render_template(
        "main/article.html",
        article=article,
        related_articles=related_articles,
    )


@bp.route("/tag/<int:id>")
def tag(id):
    tag = Tag.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    articles = (
        Article.query.filter(
            Article.tags.any(Tag.id == id), Article.is_published == True
        )
        .order_by(Article.created_at.desc())
        .paginate(page=page, per_page=20)
    )
    return render_template("main/tag.html", tag=tag, articles=articles)


@bp.route("/search")
def search():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("POSTS_PER_PAGE", 9)
    articles = []
    pagination = None
    if query:
        try:
            sql = """
                SELECT id FROM article
                WHERE article MATCH :q AND is_published=1
                ORDER BY rank
            """
            result = db.session.execute(sql, {"q": query})
            ids = [row[0] for row in result]
            if ids:
                q = Article.query.filter(Article.id.in_(ids))
                pagination = q.paginate(page=page, per_page=per_page)
                articles = pagination.items
            else:
                articles = []
                pagination = None
        except Exception:
            q = Article.query.filter(
                (Article.title.contains(query) | Article.content.contains(query))
                & (Article.is_published == True)
            )
            pagination = q.paginate(page=page, per_page=per_page)
            articles = pagination.items
    return render_template(
        "search.html", articles=articles, query=query, pagination=pagination
    )
