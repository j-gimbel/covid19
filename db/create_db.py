from .db import DB
import argparse
import os

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    """
    parser.add_argument(
        "date",
        help="put start date as ISO-date (2021-02-28) from where to create db, must be an existing csv file in downloads",
    )
    """
    parser.add_argument(
        "full_data_file_path",
        help="full-data.csv file from P. Mayer",
    )
    args = parser.parse_args()
    # try:
    db = DB()

    if not os.path.isfile(args.full_data_file_path):
        print("file " + args.full_data_file_path + " not found")
        sys.exit(1)
    db.create(args.full_data_file_path)
    # except Exception as e:
    #    print(e)