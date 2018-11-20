from collections import defaultdict
from datetime import datetime, timedelta
import json
import numpy
import pandas
import sys

FIRST_COLUMN = "student"
SEMESTER_START = "2018-09-17"


def get_student_row(student, mode):
    head = student.columns

    if mode == "exercises":
        identifiers = {x.split("/")[1] for x in head if x != FIRST_COLUMN}
        prefix = "/"
        suffix = ""
    elif mode == "dates":
        identifiers = {x.split("/")[0] for x in head if x != FIRST_COLUMN}
        prefix = ""
        suffix = "/"
    else:
        return

    identifiers_dict = defaultdict(float)
    for e in identifiers:
        filter_like = prefix + e + suffix
        sum_from_all_attempts = student.filter(like=filter_like).sum(axis=1)
        identifiers_dict[e] = sum_from_all_attempts

    student_per_idx = pandas.DataFrame(dict(sorted(identifiers_dict.items())))
    return student_per_idx


def get_student_stats(data, student_id):
    if student_id == "average":
        student = data.mean(axis=0).to_frame().T
    else:
        student = data[data.student == int(student_id)]
        if not len(student):
            return {}

    # group by exercise
    student_row_per_excercise = get_student_row(student, "exercises")
    student_ex_row = student_row_per_excercise.iloc[0]

    student_stats = {
        "mean": student_ex_row.mean(),
        "median": student_ex_row.median(),
        "total": student_ex_row.sum(),
        "passed": int(student_ex_row[student_ex_row > 0].count()),
    }

    # group by date
    student_row_per_date = get_student_row(student, "dates")
    student_row_per_date.insert(0, SEMESTER_START, 0.0)
    dates_header = student_row_per_date.columns
    student_date_row = student_row_per_date.iloc[0]
    cumulative_per_date = student_date_row.cumsum()
    cum_array = numpy.array(cumulative_per_date)

    semester_start_date = datetime.strptime(SEMESTER_START, "%Y-%m-%d").date()
    dates_to_int = [(datetime.strptime(x, "%Y-%m-%d").date() - semester_start_date).days for x in dates_header]
    dates_array = numpy.array(dates_to_int)

    dates_array = dates_array[:, numpy.newaxis]
    slope = numpy.linalg.lstsq(dates_array, cum_array, rcond=None)[0][0]

    if slope != 0:
        sixteen_date = str(semester_start_date + timedelta(16 / slope))
        twenty_date = str(semester_start_date + timedelta(20 / slope))
    else:
        sixteen_date = "inf"
        twenty_date = "inf"

    student_stats["regression slope"] = slope
    student_stats["date 16"] = sixteen_date
    student_stats["date 20"] = twenty_date

    return student_stats


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("First argument is path to file with students stats, second is student id!")

    path_to_file = sys.argv[1]
    student_idx = sys.argv[2]
    points = pandas.read_csv(path_to_file)
    stats = get_student_stats(points, student_idx)
    json.dump(stats, sys.stdout, indent=4, ensure_ascii=False)
