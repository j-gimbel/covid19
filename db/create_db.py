from .db import DB
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "date",
        help="put start date as ISO-date (2021-02-28) from where to create db, must be an existing csv file in downloads",
    )
    args = parser.parse_args()
    # try:
    db = DB()
    db.create(args.date)
    # except Exception as e:
    #    print(e)