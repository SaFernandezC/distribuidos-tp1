import json

def parse_weathers(item, city):
    item = item.split(',')
    return json.dumps({"city": city, "date": item[0], "prectot": float(item[1])})

def parse_trips(item, city):
    item = item.split(',')
    return json.dumps({
        "city": city,
        "start_date": item[0].split(' ')[0], # Viene con tiempo, no lo quiero
        "start_station_code": item[1],
        "end_date": item[2].split(' ')[0], # Viene con tiempo, no lo quiero
        "end_station_code": item[3],
        "duration_sec": float(item[4]) if float(item[4]) >= 0 else 0,
        "yearid": item[-1]
    })

def parse_stations(item, city):
    item = item.split(',')
    return json.dumps({
        "city": city,
        "code": item[0],
        "name": item[1],
        "latitude": float(item[2]),
        "longitude": float(item[3]),
        "yearid": item[-1],
    })

def send_eof(queue, msg):
    queue.send(json.dumps(msg))

def handle_eof(msg, weathers_queue, trips_queue, stations_queue):
    if msg["type"] == "weathers":
        send_eof(weathers_queue, msg)
    elif msg["type"] == "trips":
        send_eof(trips_queue, msg)
    else: # Stations
        send_eof(stations_queue, msg)

def send(queue, city, data, parser):
    for item in data:
        queue.send(parser(item, city))