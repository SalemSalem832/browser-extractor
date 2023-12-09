import sqlite3, os, datetime, csv, yaml


def apply_rules(domain):
    with open("filetransfer.yml", "r") as f:
        data = yaml.safe_load(f)

    for i in data["domain"]:
        if i in domain:
            return data["name"]


def parse_time(timestamp):
    if timestamp == 0:
        return "Timestamp is 0"
    return datetime.datetime.strftime(
        datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp),
        "%Y-%m-%d %H:%M:%S",
    )


def parse_domain(url):
    if url.startswith("http"):
        return url.split("/")[2]
    else:
        return url.split("/")[0]


def parse_entry(entry):
    temp = {}
    temp["id"] = entry[0]
    temp["url"] = entry[1]
    temp["domain"] = parse_domain(entry[1])
    temp["title"] = entry[2]
    temp["visit_count"] = entry[3]
    temp["typed_count"] = entry[4]
    temp["last_visit_time"] = parse_time(entry[5])
    temp["hidden"] = entry[6]
    temp["rules"] = apply_rules(temp["domain"])
    return temp


conn = sqlite3.connect(r"test_dbs\Chrome\History")

c = conn.cursor()

res = c.execute("SELECT * FROM urls")

data = res.fetchall()

data = [parse_entry(entry) for entry in data]

with open("Chrome History.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    for i in data:
        try:
            writer.writerow(i)
        except:
            i["title"] = "ERROR"
