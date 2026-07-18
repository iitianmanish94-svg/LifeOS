from datetime import date, datetime, timedelta
import csv
from io import StringIO

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Habit, HabitLog, StudyLog, WeightLog
from app.services import current_streak, daily_summary, heatmap

bp = Blueprint("main", __name__)

SCHEDULE = [("07:00", "Wake Up"), ("07:30", "Morning Walk"), ("08:30", "Breakfast"),
            ("09:00", "Study Session 1"), ("11:15", "Study Session 2"), ("13:15", "Lunch"),
            ("14:30", "Revision"), ("16:00", "Tuition"), ("17:00", "Gym"),
            ("18:20", "Study Session 3"), ("19:30", "Dinner"), ("20:00", "Final Study"),
            ("22:30", "Planning"), ("23:00", "Laptop OFF"), ("23:15", "Sleep")]


@bp.get("/health")
def health():
    """Small unauthenticated endpoint for hosting-provider health checks."""
    return jsonify(status="ok")


@bp.route("/")
@login_required
def dashboard():
    summary = daily_summary(current_user)
    today = date.today()
    study_hours = sum(log.hours for log in StudyLog.query.filter_by(user_id=current_user.id, logged_on=today))
    latest_weight = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.logged_on.desc()).first()
    weekly = [daily_summary(current_user, today - timedelta(days=i))["percent"] for i in range(6, -1, -1)]
    return render_template("dashboard.html", summary=summary, streak=current_streak(current_user),
                           schedule=SCHEDULE, study_hours=study_hours, latest_weight=latest_weight,
                           weekly=weekly, today=today)


@bp.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    if request.method == "POST":
        habit = Habit(user_id=current_user.id, title=request.form["title"],
                      category=request.form.get("category", "Wellness"), icon=request.form.get("icon", "✓"),
                      reminder_time=request.form.get("reminder_time"), difficulty=request.form.get("difficulty", "Medium"),
                      xp=int(request.form.get("xp", 20)), notes=request.form.get("notes", ""))
        db.session.add(habit)
        db.session.commit()
        flash("Habit added to your system.", "success")
        return redirect(url_for("main.habits"))
    return render_template("habits.html", summary=daily_summary(current_user))


@bp.post("/api/habits/<int:habit_id>/toggle")
@login_required
def toggle_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    log = HabitLog.query.filter_by(habit_id=habit.id, completed_on=date.today()).first()
    if log:
        db.session.delete(log)
        completed = False
    else:
        db.session.add(HabitLog(habit_id=habit.id, completed_on=date.today()))
        completed = True
    db.session.commit()
    summary = daily_summary(current_user)
    return jsonify(completed=completed, percent=summary["percent"], earned=summary["earned"], streak=current_streak(current_user))


@bp.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html", heatmap=heatmap(current_user), summary=daily_summary(current_user))


@bp.route("/stats")
@login_required
def stats():
    labels = [(date.today() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    values = [daily_summary(current_user, date.today() - timedelta(days=i))["percent"] for i in range(6, -1, -1)]
    study = [sum(x.hours for x in StudyLog.query.filter_by(user_id=current_user.id, logged_on=date.today() - timedelta(days=i))) for i in range(6, -1, -1)]
    return render_template("stats.html", labels=labels, values=values, study=study, heatmap=heatmap(current_user))


@bp.route("/export/csv")
@login_required
def export_csv():
    out = StringIO(); writer = csv.writer(out)
    writer.writerow(["Date", "Habit", "Category", "XP"])
    for habit in current_user.habits:
        for log in habit.logs.order_by(HabitLog.completed_on.desc()):
            writer.writerow([log.completed_on.isoformat(), habit.title, habit.category, habit.xp])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=project-niyam-habits.csv"})
