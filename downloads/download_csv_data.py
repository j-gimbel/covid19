from datetime import date
import logging
import requests
import os.path as path


def store_file_if_not_downloaded_already(when: str, extension: str, file: dict) -> str:

    """
    lädt von einer url einen Datenstring und speichert ihn in "downloads/"
    fügt einen ISO-Date an den Beginn des Dateinamens an falls when="daily"
    """

    date_today = date.today().isoformat() + "_"
    if when not in ["daily", "once"]:
        raise Exception('bad value for parameter "when"(' + str(when) + ")")
    if when == "once":
        date_today = ""
    filepath = "downloads/" + date_today + f["name"] + "." + extension
    if not path.isfile(filepath):
        logger.info("downloading file " + filepath)
        r = requests.get(f["url"])
        if r.status_code != 200:
            raise exception(
                "Could not download from url "
                + f["url"]
                + " (for file "
                + filepath
                + ")"
            )
        csv_file = open(filepath, "wb")
        csv_file.write(r.content)
        csv_file.close()
    return filepath


if __name__ == "__main__":

    # create logger
    logger = logging.getLogger("donwload_csv")
    logger.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    # create file handler and set level to debug
    fh = logging.FileHandler("donwload_csv.log")
    fh.setLevel(logging.DEBUG)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(fh)

    files_once = [
        {
            "url": "https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv",
            "name": "RKI_COVID19",
        }
    ]

    files_daily = [
        {
            "url": "https://opendata.arcgis.com/datasets/ef4b445a53c1406892257fe63129a8ea_0.csv",
            "name": "RKI_Corona_Bundeslaender",
        },
        {
            "url": "https://opendata.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0.csv",
            "name": "RKI_Corona_Landkreise",
        },
    ]

    for f in files_once:
        store_file_if_not_downloaded_already(when="once", extension="csv", file=f)
    for f in files_daily:
        store_file_if_not_downloaded_already(when="daily", extension="csv", file=f)
