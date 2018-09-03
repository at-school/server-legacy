
from datetime import time

from app.database import db


# def add_days(db, Day):
#     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
#     for day in days:
#         db.days.insert_one({"day": day})
#     return True


# def add_lines(db, Line):
#     lines = [i for i in range(1, 10)]
#     for line in lines:
#         db.lines.insert_one({"line": str(line)})
#     return True


def setup_line_time():

    day_id = "Monday"
    time_intervals = [
        [time(8, 30), time(9, 25)],
        [time(9, 25), time(10, 20)],
        [time(10, 20), time(11, 15)],
        [time(11, 15), time(12, 10)],
        [time(12, 10), time(13, 5)],
        [time(13, 5), time(14, 0)],
        [time(14, 0), time(14, 55)],
        [time(14, 55), time(15, 50)]
    ]
    lines = [1, 2, 3, 4, 5, 6, 7, 8]
    for counter in range(len(lines)):

        db.schedule.insert_one({
            "line": str(lines[counter]),
            "day": day_id,
            "startTime": str(time_intervals[counter][0]),
            "endTime": str(time_intervals[counter][1])
        })

    day_id = "Tuesday"
    time_intervals = [
        [time(9, 30), time(11, 20)],
        [time(11, 20), time(12, 20)],
        [time(12, 20), time(13, 20)],
        [time(13, 20), time(15, 10)],
    ]
    lines = [7, 3, 5, 1]
    for counter in range(len(lines)):
        db.schedule.insert_one({
            "line": str(lines[counter]),
            "day": day_id,
            "startTime": str(time_intervals[counter][0]),
            "endTime": str(time_intervals[counter][1])
        })

    day_id = "Wednesday"
    time_intervals = [
        [time(9, 30), time(11, 20)],
        [time(11, 20), time(12, 20)],
        [time(12, 20), time(13, 20)],
        [time(13, 20), time(15, 10)],
        [time(15, 30), time(19, 00)]
    ]
    lines = [8, 2, 6, 4, 9]
    for counter in range(len(lines)):
        db.schedule.insert_one({
            "line": str(lines[counter]),
            "day": day_id,
            "startTime": str(time_intervals[counter][0]),
            "endTime": str(time_intervals[counter][1])
        })

    day_id = "Thursday"
    time_intervals = [
        [time(8, 30), time(10, 20)],
        [time(10, 20), time(11, 20)],
        [time(11, 20), time(12, 20)],
        [time(12, 20), time(14, 10)],
    ]
    lines = [5, 1, 7, 3]
    for counter in range(len(lines)):
        db.schedule.insert_one({
            "line": str(lines[counter]),
            "day": day_id,
            "startTime": str(time_intervals[counter][0]),
            "endTime": str(time_intervals[counter][1])
        })

    day_id = "Friday"
    time_intervals = [
        [time(9, 0), time(10, 50)],
        [time(11, 20), time(12, 20)],
        [time(12, 20), time(13, 20)],
        [time(13, 20), time(15, 10)],
    ]
    lines = [6, 4, 8, 2]
    for counter in range(len(lines)):
        db.schedule.insert_one({
            "line": str(lines[counter]),
            "day": day_id,
            "startTime": str(time_intervals[counter][0]),
            "endTime": str(time_intervals[counter][1])
        })
