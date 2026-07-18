from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.models import User
from app.services import create_default_habits

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email", "").lower().strip()).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(request.args.get("next") or url_for("main.dashboard"))
        flash("Incorrect email or password.", "error")
    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        name, email, password = (request.form.get(k, "").strip() for k in ("name", "email", "password"))
        if not name or not email or len(password) < 8:
            flash("Use your name, a valid email, and a password with at least 8 characters.", "error")
        elif User.query.filter_by(email=email.lower()).first():
            flash("An account with that email already exists.", "error")
        else:
            user = User(name=name, email=email.lower())
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            create_default_habits(user)
            login_user(user)
            return redirect(url_for("main.dashboard"))
    return render_template("auth/register.html")


@bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
