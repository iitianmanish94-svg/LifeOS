from datetime import date, timedelta

from app import db
from app.models import Habit, HabitLog, User

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
    day = day or date.today()
    return {log.habit_id for habit in user.habits for log in habit.logs.filter_by(completed_on=day)}


def daily_summary(user, day=None):
    day = day or date.today()
    habits = user.habits.filter_by(active=True).all()
    done = completed_habit_ids(user, day)
    earned = sum(h.xp for h in habits if h.id in done)
    total = sum(h.xp for h in habits)
    return {"habits": habits, "done": done, "earned": earned, "total": total,
            "percent": round((len(done) / len(habits) * 100) if habits else 0)}


def current_streak(user):
    streak = 0
    cursor = date.today()
    while True:
        summary = daily_summary(user, cursor)
        if summary["percent"] < 60:
            break
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def heatmap(user, days=84):
    result = []
    for offset in range(days - 1, -1, -1):
        day = date.today() - timedelta(days=offset)
        result.append({"date": day.isoformat(), "percent": daily_summary(user, day)["percent"]})
    return result
