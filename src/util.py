# FOR THE TIME AND SCHEDULE
import datetime
from color_palette import TEXT2, SUCCESS

def today_str():
    return datetime.now().strftime("%Y-%m-%d") 

def today_weekday() -> str:
    # Return full weekday name for today, e.g. 'Monday'
    return datetime.now().strftime("%A")

def doses_required_today(frequency: str) -> int:
    return {"Once a day": 1, "Twice a day": 2,
            "Every other day": 1}.get(frequency, 1)

# SCHEDULE FUNCTIONS
def doses_given_today(pet: str, med: str, intakes: list) -> int:
    return sum(
        1 for i in intakes
        if i.get("pet") == pet and i.get("med") == med and i.get("status") == "Given ✅" and i.get("date", "").startswith(today_str())
    )

def is_due_today(schedule: dict) -> bool: # used to determine if a medication is due today based on its schedule and the current date
    freq = schedule.get("frequency", "Once a day")
    days = schedule.get("days", [])
    # If days are specified, always check against them regardless of frequency
    if days:
        return today_weekday() in days
    # No days specified = every day
    return True

def schedule_status(schedule: dict, intakes: list) -> tuple:
    if not is_due_today(schedule):
        return "Not due today", TEXT2
    freq     = schedule.get("frequency", "Once a day")
    required = doses_required_today(freq)
    given    = doses_given_today(schedule["pet"], schedule["med"], intakes)
    if given >= required:
        return f"Done ({given}/{required})", SUCCESS
    return f"Pending ⏳ ({given}/{required})", "#f59e0b"