import yaml
import time
import argparse
import sys
import json


from influxdb import InfluxDBClient


def query(db, query, field):
    print(">"*3 + " " + query.strip())
    result = db.query(query)
    print(result)
    print("<"*3 + " " + str(result), flush=True)
    return next(result.get_points(), {}).get(field, 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pass-rate-success', type=int, default=80)
    parser.add_argument('--pass-rate-p95', type=int, default=50)
    parser.add_argument('--script', type=str, required=True)
    args = parser.parse_args()
    print(args)

    with open(args.script, 'r') as stream:
        script = yaml.safe_load(stream)

    tags = script.get('config', {}).get('plugins', {}).get('influxdb').get('tags', {})
    tag_environment = tags['environment']
    tag_testId = tags['testId']

    with open(f"dashboard-{tag_environment}.json", "rb") as json_file:
        dashboard = json.load(json_file)
        dashboard_uid = dashboard.get("uid")
    grafana_host = script.get('config', {}).get('grafana', {}).get('host')

    if dashboard_uid is not None and grafana_host is not None:
        print(f"!!! Check testing dashboard at http://{grafana_host}/d/{dashboard_uid}")

    phases = script.get('config', {}).get('phases', [])
    timeout = sum([ phase['duration'] for phase in phases ])*1.2
    if timeout < 1:
        print("failed to detect phases duration")
        sys.exit(1)

    print(f"sleeping for {timeout} seconds", flush=True)
    time.sleep(timeout)

    db_settings = script.get('config', {}).get('plugins', {}).get('influxdb').get('influx', {})
    db_host = db_settings.get('host')
    db_username = db_settings.get('username')
    db_password = db_settings.get('password')
    db_database = db_settings.get('database')

    db = InfluxDBClient(db_host, 80, db_username, db_password, db_database)  # port 80 - due to the fact that port 8086 has been already included in the domain name.
   
    errors = query(
        db,
        f"""
            select count(value) from latency where response != '200' and testId = '{tag_testId}' 
        """,
        "count"
    )

    total = query(
        db,
        f"""
            select count(value) from latency where response = '200' and testId = '{tag_testId}'
        """,
        "count"
    )

    success_rate = int(100 - errors * 100 / total if total > 0 else 100)
    print(f"success rate {success_rate}% (total={total}, failures={errors})", flush=True)

    p95 = query(
        db,
        f"""
            select percentile("value", 95) from "latency" where testId = '{tag_testId}' and response = '200' group by "testId"
        """,
        "percentile"
    )
    print(f"95th percentile={p95}", flush=True)

    # select distinct("testId") from (select "value", "testId" from latency)

    if success_rate < args.pass_rate_success:
        print(f"Failing build due to success_rate ({success_rate} < {args.pass_rate_success})")
        sys.exit(1)
    elif p95 > args.pass_rate_p95:
        print(f"Failing build due to 95th percentile ({p95} > {args.pass_rate_p95})")
        sys.exit(1)

    print("Congrats, everything went smoothly!")
    sys.exit(0)
