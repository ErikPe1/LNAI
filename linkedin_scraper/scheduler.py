def is_within_operating_hours():
    import datetime
    now = datetime.datetime.utcnow()
    # Check if the current time is within Mon-Fri 9am-4:30pm
    if now.weekday() < 5:  # Monday to Friday are 0-4
        if now.time() >= datetime.time(9, 0) and now.time() <= datetime.time(16, 30):
            return True
    return False

def get_random_delay():
    import random
    return random.randint(60, 600)  # Random delay between 60 and 600 seconds

def get_next_operating_time():
    import datetime
    now = datetime.datetime.utcnow()
    next_run = now
    while not is_within_operating_hours():
        next_run += datetime.timedelta(minutes=1)  # Add a minute until we find the next operating hour
        if next_run.weekday() >= 5:  # Skip to Monday if it's the weekend
            next_run += datetime.timedelta(days=7-next_run.weekday())  # Jump to next Monday
        if next_run.time() < datetime.time(9, 0):
            next_run = next_run.replace(hour=9, minute=0, second=0)  # Move to 9am
        elif next_run.time() > datetime.time(16, 30):
            next_run += datetime.timedelta(days=1)  # Move to the next day
            next_run = next_run.replace(hour=9, minute=0, second=0)  # Move to 9am
    return next_run
