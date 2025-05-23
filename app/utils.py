import markdown
import bleach
from flask import url_for
from functools import wraps
from flask import abort
from flask_login import current_user


def markdown_to_html(text):
    # 允许的标签
    allowed_tags = [
        "a",
        "abbr",
        "acronym",
        "b",
        "blockquote",
        "code",
        "em",
        "i",
        "li",
        "ol",
        "pre",
        "strong",
        "ul",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "img",
        "hr",
        "br",
        "div",
        "span",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    ]

    # 允许的属性
    allowed_attrs = {
        "*": ["class"],
        "a": ["href", "rel", "target"],
        "img": ["src", "alt", "title"],
    }

    # 转换 Markdown 为 HTML
    html = markdown.markdown(
        text,
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
            "markdown.extensions.tables",
            "markdown.extensions.toc",
        ],
    )

    # 清理 HTML
    clean_html = bleach.clean(
        html, tags=allowed_tags, attributes=allowed_attrs, strip=True
    )

    return clean_html


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
