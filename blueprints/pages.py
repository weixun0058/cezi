from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
@pages_bp.get("/huangli")
def huangli_page():
    return render_template("huangli.html")


@pages_bp.get("/suanshi")
def suanshi_page():
    return render_template("suanshi.html")


@pages_bp.get("/lunming")
def lunming_page():
    return render_template("lunming.html")
