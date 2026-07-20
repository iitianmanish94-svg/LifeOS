from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import inspect, text

from app import db
from app.models import Habit, HabitLog, User

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def today_in_india():
    """Return the user's calendar day in the app's India timezone."""
    return datetime.now(INDIA_TIMEZONE).date()

DEFAULT_HABITS = [
    ("Wake up at 7 AM", "☀", "Morning", "07:00", "Medium", 20),
    ("Morning Walk", "◌", "Health", "07:30", "Easy", 20),
    ("Sunlight", "☀", "Health", "07:30", "Easy", 15),
    ("Drink Water", "◈", "Health", "08:00", "Easy", 10),
    ("Bath", "✦", "Morning", "08:00", "Easy", 15),
    ("Breakfast", "◒", "Nutrition", "08:30", "Easy", 15),
    ("Study Session 1", "▣", "Study", "09:00", "Hard", 50),
    ("Study Session 2", "▣", "Study", "11:15", "Hard", 50),
    ("Lunch", "◒", "Nutrition", "13:15", "Easy", 10),
    ("Revision", "↻", "Study", "14:30", "Medium", 35),
    ("Tuition", "▣", "Study", "16:00", "Medium", 30),
    ("Gym", "⌁", "Fitness", "17:00", "Hard", 40),
    ("Snack", "◒", "Nutrition", "18:00", "Easy", 10),
    ("Study Session 3", "▣", "Study", "18:20", "Hard", 50),
    ("Dinner", "◒", "Nutrition", "19:30", "Easy", 10),
    ("Study Session 4", "▣", "Study", "20:00", "Hard", 50),
    ("Brush Teeth", "✦", "Wellness", "22:15", "Easy", 10),
    ("Laptop Off", "◐", "Discipline", "23:00", "Hard", 40),
    ("Sleep Before 11:15 PM", "☾", "Sleep", "23:15", "Hard", 50),
    ("Drink 3L Water", "◈", "Health", "20:00", "Medium", 20),
    ("Milk", "◒", "Nutrition", "20:00", "Easy", 15),
    ("Bananas", "◒", "Nutrition", "20:00", "Easy", 15),
    ("Protein", "◒", "Nutrition", "20:00", "Medium", 25),
    ("Clean Room", "✧", "Environment", "20:00", "Medium", 20),
    ("Clean Study Table", "✧", "Environment", "20:00", "Easy", 15),
    ("No Porn", "◆", "Discipline", "23:00", "Hard", 100),
    ("No Masturbation", "◆", "Discipline", "23:00", "Hard", 75),
    ("No Fast Food", "◆", "Nutrition", "23:00", "Medium", 30),
    ("No Reels", "◆", "Focus", "23:00", "Hard", 50),
    ("No Instagram", "◆", "Focus", "23:00", "Hard", 50),
    ("No Random YouTube", "◆", "Focus", "23:00", "Hard", 50),
]


def seed_defaults():
    # Default habits are created for each new user during registration.
    return None


def create_default_habits(user):
    for title, icon, category, reminder, difficulty, xp in DEFAULT_HABITS:
        db.session.add(Habit(user_id=user.id, title=title, icon=icon, category=category,
                             reminder_time=reminder, difficulty=difficulty, xp=xp))
    db.session.commit()


def completed_habit_ids(user, day=None):
    day = day or today_in_india()
    return {log.habit_id for habit in user.habits for log in habit.logs.filter_by(completed_on=day)}


def daily_summary(user, day=None):
    day = day or today_in_india()
    habits = user.habits.filter_by(active=True).all()
    done = completed_habit_ids(user, day)
    earned = sum(h.xp for h in habits if h.id in done)
    total = sum(h.xp for h in habits)
    return {"habits": habits, "done": done, "earned": earned, "total": total,
            "percent": round((len(done) / len(habits) * 100) if habits else 0)}


def completion_dates(user):
    """Return the distinct days on which the user completed a habit."""
    rows = (
        db.session.query(HabitLog.completed_on)
        .join(Habit)
        .filter(Habit.user_id == user.id)
        .distinct()
        .order_by(HabitLog.completed_on.desc())
        .all()
    )
    return [row[0] for row in rows]


def rebuild_streak_state(user):
    """Recalculate persistent streak values from all completion days.

    This is used to backfill existing users and when a day's final task is
    unchecked. A streak is a run of calendar days with one or more tasks.
    """
    days = completion_dates(user)
    if not days:
        user.current_streak = 0
        user.longest_streak = 0
        user.last_streak_date = None
        return

    latest_day = days[0]
    current = 1
    expected_day = latest_day - timedelta(days=1)
    for completed_day in days[1:]:
        if completed_day != expected_day:
            break
        current += 1
        expected_day -= timedelta(days=1)

    longest = 1
    run = 1
    ascending_days = list(reversed(days))
    for previous_day, completed_day in zip(ascending_days, ascending_days[1:]):
        run = run + 1 if completed_day == previous_day + timedelta(days=1) else 1
        longest = max(longest, run)

    user.current_streak = current
    user.longest_streak = longest
    user.last_streak_date = latest_day


def record_first_completion_of_day(user, completed_on):
    """Advance a streak once, only when a day receives its first completion."""
    if user.last_streak_date == completed_on:
        return

    if user.last_streak_date == completed_on - timedelta(days=1):
        user.current_streak = (user.current_streak or 0) + 1
    else:
        user.current_streak = 1

    user.last_streak_date = completed_on
    user.longest_streak = max(user.longest_streak or 0, user.current_streak)


def current_streak(user, day=None):
    """Return a current-day streak without carrying it through a missed day."""
    day = day or today_in_india()
    return user.current_streak if user.last_streak_date == day else 0


def migrate_streak_data():
    """Add streak fields for existing SQLite/PostgreSQL databases and backfill."""
    table_name = User.__table__.name
    existing_columns = {column["name"] for column in inspect(db.engine).get_columns(table_name)}
    required_columns = {
        "current_streak": "INTEGER NOT NULL DEFAULT 0",
        "longest_streak": "INTEGER NOT NULL DEFAULT 0",
        "last_streak_date": "DATE",
    }
    table = db.engine.dialect.identifier_preparer.quote(table_name)
    with db.engine.begin() as connection:
        for column_name, definition in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {definition}"))

    changed = False
    for user in User.query.filter(User.last_streak_date.is_(None)).all():
        if completion_dates(user):
            rebuild_streak_state(user)
            changed = True
    if changed:
        db.session.commit()


def heatmap(user, days=84):
    result = []
    for offset in range(days - 1, -1, -1):
        day = today_in_india() - timedelta(days=offset)
        result.append({"date": day.isoformat(), "percent": daily_summary(user, day)["percent"]})
    return result
