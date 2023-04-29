import json

def parse_weathers(item, city):
    item = item.split(',')
    return json.dumps({"city": city, "date": item[0], "prectot": item[1]})


def send_eof(queue, msg):
    queue.send(json.dumps(msg))

def handle_eof(msg, weathers_queue, trips_queue, stations_queue):
    if msg["type"] == "weathers":
        send_eof(weathers_queue, msg)
    elif msg["type"] == "trips":
        send_eof(trips_queue, msg)
    else: # Stations
        send_eof(stations_queue, msg)

def send(queue, data, city, parser):
    for item in data:
        queue.send(parser(item, city))