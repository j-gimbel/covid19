from .db import DB
import argparse
import os
import sys

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    """
    parser.add_argument(
        "date",
        help="put start date as ISO-date (2021-02-28) from where to create db, must be an existing csv file in downloads",
    )
    """

    parser.add_argument("--agegroups", help="assume age groups in ", action="store_true")

    parser.add_argument(
        "all_series_csv_filepath",
        help="all-series.csv file from P. Mayer",
    )
    args = parser.parse_args()
    # try:
    db = DB()

    if not os.path.isfile(args.all_series_csv_filepath):
        print("file " + args.all_series_csv_filepath + " not found")
        sys.exit(1)
    db.create(args.agegroups, args.all_series_csv_filepath)
    # except Exception as e:
    #    print(e)
