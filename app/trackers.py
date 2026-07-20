from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import StudyLog, WeightLog
from app.services import today_in_india

bp = Blueprint("trackers", __name__, url_prefix="/trackers")


@bp.route("/study", methods=["GET", "POST"])
@login_required
def study():
    if request.method == "POST":
        db.session.add(StudyLog(user_id=current_user.id, subject=request.form["subject"],
                                topic=request.form.get("topic", ""), hours=float(request.form["hours"]),
                                notes=request.form.get("notes", ""), logged_on=today_in_india()))
        db.session.commit(); flash("Study session saved.", "success")
        return redirect(url_for("trackers.study"))
    logs = StudyLog.query.filter_by(user_id=current_user.id).order_by(StudyLog.logged_on.desc()).all()
    return render_template("study.html", logs=logs)


@bp.route("/weight", methods=["GET", "POST"])
@login_required
def weight():
    if request.method == "POST":
        today = today_in_india()
        item = WeightLog.query.filter_by(user_id=current_user.id, logged_on=today).first()
        if item: item.weight = float(request.form["weight"])
        else: db.session.add(WeightLog(user_id=current_user.id, weight=float(request.form["weight"]), logged_on=today))
        current_user.target_weight = float(request.form.get("target_weight", current_user.target_weight))
        db.session.commit(); flash("Weight check-in saved.", "success")
        return redirect(url_for("trackers.weight"))
    logs = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.logged_on.asc()).all()
    return render_template("weight.html", logs=logs)
