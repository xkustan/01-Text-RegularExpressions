import copy
import statistics
import pandas as pd
import numpy

df = pd.read_csv('points.csv')
keys = df.keys()
dates_dict = {}
exercise_dict = {}
deadline_dict = {}
for key in keys:
    if key != "student":
        values = list(df[key])
        passed = len([key for key in values if key > 0])
        deadline_dict[key] = {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "first": numpy.percentile(df[key], 25),
            "last": numpy.percentile(df[key], 75),
            "passed": passed,
        }

        date, exercise = key.split("/")[0], key.split("/")[1]
        if dates_dict.get(date):
            dates_dict[date]["second"] = values
        else:
            dates_dict[date] = {"first": values}

        if exercise_dict.get(exercise):
            exercise_dict[exercise]["second"] = values
        else:
            exercise_dict[exercise] = {"first": values}

def get_stats(data):
    for key, record in data.items():
        passed = 0
        if record.get("second"):
            passed = len([key for i, key in enumerate(record["first"]) if key > 0 or record["second"][i] > 0 ])
            values = copy.deepcopy(record.get("first") + record.get("second"))
            del record["first"]
            del record["second"]
        else:
            passed = len([key for key in record["first"] if key > 0])
            values = copy.deepcopy(record["first"])
            del record["first"]
        df = pd.DataFrame(data=values)
        record["mean"] = statistics.mean(values)
        record["median"] = statistics.median(values)
        record["first"] = numpy.percentile(df.values, 25)
        record["last"] = numpy.percentile(df.values, 75)
        record["passed"] = passed

get_stats(dates_dict)
get_stats(exercise_dict)

# print(dates_dict, "\n", exercise_dict, "\n", deadline_dict)

def get_student_stats_by_id(id):
    row = df.loc[df['student'] == id]
    stats = {}
    values = [float(row[key]) for key in keys if key != "student"]
    points = []
    i, j = 0, 1
    while j < len(values):
        points.append(values[i] if values[i] > 0 else values[j])
        i += 2
        j += 2
    stats["mean"] = statistics.mean(points)
    stats["median"] = statistics.median(points)
    stats["total"] = sum(points)
    stats["passed"] = len([point for point in points if point > 0])
    print(stats)

get_student_stats_by_id(144)