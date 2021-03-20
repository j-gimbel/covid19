import csv
import json
import os
import re

landkreise_rki = []
if os.path.isfile("lk_rki.json"):
    landkreise_rki = json.load(open("lk_rki.json", "r", encoding='utf8'))
else:
    csv_reader = csv.reader(open("D:/Users/jan/Documents/corona/Corona/all-series.csv", "rt", encoding="utf-8"))
    for row in csv_reader:
        # if row[4] not in ["LK","SK","LSK"]:
        #    continue

        if row[1] == "10.3.2021":
            lk_id = row[2]
            lk_name = row[3]
            lk_typ = row[4]
            # print(lk_name)
            landkreise_rki.append([int(lk_id), str(lk_name), str(lk_typ)])

    print("length: "+str(len(landkreise_rki)))
    with open("lk_rki.json", "w", encoding='utf8') as json_file:
        json.dump(landkreise_rki, json_file, ensure_ascii=False, indent=3)

landkreise_od = []
if os.path.isfile("lk_opendatamap.json"):
    landkreise_od = json.load(open("lk_opendatamap.json", "r", encoding='utf8'))
else:
    print("hier")
    #matches =  ["Kreisfreie Stadt","Landkreis","Kreis"]

    gj = json.load(open("input/landkreise_simplified.geojson", "r", encoding='utf8'))
    #gj_new = gj
    gj_new = {
        "type": "FeatureCollection",
        "features": []
    }
    #gj_new["features"] = []
    # print(gj)
    for feat in gj["features"]:
        # print(feat)
        lk_id = feat["properties"]["DEBKG_ID"]
        lk_name = feat["properties"]["GEN"]  # .encode('windows-1252').decode('utf-8')
        lk_typ = feat["properties"]["BEZ"]
        # print(lk_name)
        landkreise_od.append([lk_id, lk_name, lk_typ])

        if "GF" in feat["properties"]:
            # this means it is a water area
            if feat["properties"]["GF"] == 2:
                continue
        for k in ["ADE", "GF", "BSG", "RS", "AGS", "SDV_RS", "IBZ", "BEM", "NBD", "SN_L", "SN_R", "SN_K", "SN_V1", "SN_V2", "SN_G", "SBN_S3", "NUTS", "RS_0", "WSK", "destatis", "FK_S3", "AGS_0"]:
            if k in feat["properties"]:

                del feat["properties"][k]

        #gj["features"][f] = feat
        gj_new["features"].append(feat)
    with open("landkreise_simplified_cleaned.geojson", "w", encoding='utf8') as json_file:
        json.dump(gj_new, json_file, ensure_ascii=False)

    print("length: " + str(len(landkreise_od)))
    with open("lk_opendatamap.json", "w", encoding='utf8') as json_file:
        json.dump(landkreise_od, json_file, ensure_ascii=False, indent=3)


print(str(len(landkreise_rki)))
print(str(len(landkreise_od)))


if not os.path.isfile("rki_opendata_landkreise_lookup.json"):

    lookup = []
    #re_typ_rki = re.compile(r"^(SK|LK|LSK)")
    #re_typ_od = re.compile(r"^(SK|LK|LSK)")

    for lk_rki in landkreise_rki:
        #print("1 "+str(lk_rki[1]))
        if lk_rki[2] not in ["LK", "SK", "LSK"]:
            continue
        found = False
        name_rki = lk_rki[1]

        lookup_row = lk_rki

        name_rki_changed = re.sub(r"a\.d\.", "a.d. ", name_rki)
        name_rki_changed = re.sub(r"i\.d\.", "i.d. ", name_rki_changed)
        name_rki_changed = re.sub(r"OPf.", "Oberpfalz ", name_rki_changed)
        name_rki_changed = re.sub(r"Sankt", "St.", name_rki_changed)

        """
        m = re_typ_rki.search(name_rki_changed)
        typ_rki = ""
        if m:
            typ_rki = m.group(1)
            if typ_rki == "LSK":
                typ_rki = "LK"
        else:
            print("no match "+name_rki_changed)
            exit(1)
        """

        typ_rki = lk_rki[2]
        if typ_rki == "LSK":
            typ_rki = "LK"
        name_rki_changed = re.sub(r"(SK\s|LK\s|LSK\s|Stadtverband\s)", "", name_rki_changed)
        name_rki_changed = re.sub(r"[-\s]", "", name_rki_changed)
        for lk_od in landkreise_od:
            name_od = lk_od[1]
            name_od_changed = re.sub(r"[-\s]", "", name_od)

            position = name_od_changed.lower().find(name_rki_changed.lower())
            if position > -1 and position < 3:
                typ_od = lk_od[2]
                # print(typ_od)
                if typ_od.find("Stadt") > -1:
                    typ_od = "SK"
                elif typ_od.find("Bezirk") > -1:
                    typ_od = "SK"
                else:
                    typ_od = "LK"

                if typ_od != typ_rki:
                    print("types do not match: " + name_rki_changed + " " + typ_rki + " - " + name_od_changed + " " + typ_od)
                    continue
                # If name_od_changed.lower().find("nordfriesland") > -1:
                #    continue

                found = True
                lookup_row += lk_od
                break
        if not found:
            #print("not found " + name_rki)
            fix_rki_to_od = {
                "SK Mülheim a.d.Ruhr": "Mülheim an der Ruhr",
                "StadtRegion Aachen": "Städteregion Aachen",
                "SK Landau i.d.Pfalz": "Landau in der Pfalz",
                "SK Neustadt a.d.Weinstraße": "Neustadt an der Weinstraße",
                "SK Freiburg i.Breisgau": "Freiburg im Breisgau",
                "LK Landsberg a.Lech": "Landsberg am Lech",
                "SK Weiden i.d.OPf.": "Weiden i.d. OPf.",
                "LK Neumarkt i.d.OPf.": "Neumarkt i.d. OPf.",
                "SK Brandenburg a.d.Havel": "Brandenburg an der Havel",
                "LK Stadtverband Saarbrücken": "Regionalverband Saarbrücken",
                "LK Bitburg-Prüm": "Eifelkreis Bitburg-Prüm"
            }
            found = False
            # print(list(fix_rki_to_od))
            if name_rki in list(fix_rki_to_od):
                name_od_to_find = fix_rki_to_od[name_rki]

                for lk_od in landkreise_od:
                    name_od = lk_od[1]
                    if name_od_to_find == name_od:
                        found = True
                        lookup_row += lk_od
                        break
            else:
                print("not in list")
            if not found:
                print("still not found "+name_rki)
        lookup.append(lookup_row)

    with open("rki_opendata_landkreise_lookup.json", "w", encoding='utf8') as json_file:
        json.dump(lookup, json_file, ensure_ascii=False, indent=3)

lookup_rki_id = {}
lookup_od_id = {}

lookup = json.load(open("rki_opendata_landkreise_lookup.json", "r", encoding='utf8'))
for row in lookup:
    rki_id = row[0]
    od_id = row[3]
    lookup_rki_id[rki_id] = row
    lookup_od_id[od_id] = row


with open("ids_rki_to_od.json", "w", encoding='utf8') as json_file:
    json.dump(lookup_rki_id, json_file, ensure_ascii=False, indent=3)

with open("ids_od_to_rki.json", "w", encoding='utf8') as json_file:
    json.dump(lookup_od_id, json_file, ensure_ascii=False, indent=3)


gj = json.load(open("landkreise_simplified_cleaned.geojson", "r", encoding='utf8'))
gj_new = {
    "type": "FeatureCollection",
    "features": []
}

for feat in gj["features"]:
    # print(feat)
    od_id = feat["properties"]["DEBKG_ID"]
    # lk_name = feat["properties"]["GEN"]  # .encode('windows-1252').decode('utf-8')
    #lk_typ = feat["properties"]["BEZ"]
    if od_id not in lookup_od_id:
        print("id " + od_id + " not found !")
        continue
    row = lookup_od_id[od_id]
    feat["properties"]["id"] = row[0]
    feat["properties"]["name"] = row[1]
    feat["properties"]["typ"] = row[2]
    for k in ["DEBKG_ID", "spatial_name", "GEN", "BEZ"]:
        if k in feat["properties"]:
            del feat["properties"][k]

    gj_new["features"].append(feat)

with open("landkreise_rki.geojson", "w", encoding='utf8') as json_file:
    json.dump(gj_new, json_file, ensure_ascii=False)
