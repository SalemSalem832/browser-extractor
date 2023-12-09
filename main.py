import sqlite3, os, datetime, csv, yaml


def apply_rules(domain):
    with open("filetransfer.yml", "r") as f:
        data = yaml.safe_load(f)

    for i in data["domain"]:
        if i in domain:
            return data["name"]


def parse_time(timestamp, browser):
    if timestamp == 0 or timestamp == None:
        return "Timestamp is 0"
    if browser == "chromium":
        return datetime.datetime.strftime(
            datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp),
            "%Y-%m-%d %H:%M:%S",
        )
    else:
        print(timestamp)
        return datetime.datetime.strftime(
            datetime.datetime.fromtimestamp(timestamp / 1000000), "%Y-%m-%d %H:%M:%S"
        )


def parse_domain(url):
    if url.startswith("http"):
        return url.split("/")[2]
    else:
        return url.split("/")[0]


def parse_entry(entry, browser):
    temp = {}
    temp["id"] = entry[0]
    temp["url"] = entry[1]
    temp["domain"] = parse_domain(entry[1])
    temp["title"] = entry[2]
    temp["visit_count"] = entry[3] if browser == "chromium" else entry[4]
    temp["typed_count"] = entry[4] if browser == "chromium" else entry[6]
    temp["last_visit_time"] = (
        parse_time(entry[5], "chromium")
        if browser == "chromium"
        else parse_time(entry[8], "ff")
    )
    temp["hidden"] = entry[6] if browser == "chromium" else entry[5]
    temp["rules"] = apply_rules(temp["domain"])
    return temp


def export_csv(device_name, browser, data):
    with open(f"Results\\{device_name}_{browser}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        for i in data:
            try:
                writer.writerow(i)
            except:
                i["title"] = "ERROR"


def data_collection_chromium(db_path):
    conn = sqlite3.connect(db_path)

    c = conn.cursor()

    res = c.execute("SELECT * FROM urls")

    data = res.fetchall()

    data = [parse_entry(entry, "chromium") for entry in data]

    return data


def data_collection_ff(db_path):
    conn = sqlite3.connect(db_path)

    c = conn.cursor()

    res = c.execute("SELECT * FROM moz_places")

    data = res.fetchall()

    data = [parse_entry(entry, "ff") for entry in data]

    return data


def main():
    devices = os.listdir("test_dbs")
    for i in devices:
        browsers = os.listdir(f"test_dbs\\{i}")
        for j in browsers:
            if j == "Firefox":
                data = data_collection_ff(f"test_dbs\\{i}\\{j}\\places.sqlite")
                export_csv(i, j, data)
            else:
                continue
                data = data_collection_chromium(f"test_dbs\\{i}\\{j}\\History")


if __name__ == "__main__":
    main()
