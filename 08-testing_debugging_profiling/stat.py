from collections import defaultdict
import json
import pandas
import sys

FIRST_COLUMN = "student"


def get_stats(data, mode):
    data_stats = defaultdict(dict)
    head = data.columns

    if mode == "deadlines":
        identifiers = {x for x in head if x != FIRST_COLUMN}
        prefix = ""
        suffix = ""
    elif mode == "exercises":
        identifiers = {x.split("/")[1] for x in head if x != FIRST_COLUMN}
        prefix = "/"
        suffix = ""
    elif mode == "dates":
        identifiers = {x.split("/")[0] for x in head if x != FIRST_COLUMN}
        prefix = ""
        suffix = "/"
    else:
        return

    for idx in identifiers:
        filter_like = prefix + idx + suffix
        data_column = data.filter(like=filter_like).sum(axis=1)
        data_stats[idx] = {
            "mean": data_column.mean(),
            "median": data_column.median(),
            "first": data_column.quantile(q=0.25),
            "last": data_column.quantile(q=0.75),
            "passed": int(data_column[data_column > 0].count()),
        }

    return dict(sorted(data_stats.items()))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("First argument is path to file with students stats, second is mode [dates, deadlines, exercises]!")

    path_to_file = sys.argv[1]
    input_mode = sys.argv[2]
    points = pandas.read_csv(path_to_file)
    stats = get_stats(points, input_mode)
    json.dump(stats, sys.stdout, indent=4, ensure_ascii=False)
