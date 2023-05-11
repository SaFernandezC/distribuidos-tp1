import json

def parse_weathers(item, city):
    item = item.split(',')
    return json.dumps({"city": city, "date": item[0], "prectot": float(item[1])})

def parse_trips(item, city):
    # global montreal, toronto, wash
    # if city == "montreal":
    #     montreal += 1
    # elif city == "toronto":
    #     toronto += 1
    # else:
    #     wash +=1
    # print(f"Montreal: {montreal}, toronto: {toronto}, washington: {wash}")
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

# montreal = 0
# toronto = 0
# wash = 0

def parse_stations(item, city):
    item = item.split(',')
    return json.dumps({
        "city": city,
        "code": item[0],
        "name": item[1],
        "latitude": float(item[2]) if item[2] != '' else 0,
        "longitude": float(item[3]) if item[3] != '' else 0,
        "yearid": item[-1],
    })


def send_eof(queue, msg):
    queue.send(json.dumps(msg))

def handle_eof(msg, weathers_queue, trips_queue, stations_queue, eof_manager, routing_key):
    if routing_key == "weather":
        # eof_manager.send(body=json.dumps({"type":"exchange", "exchange": "weathers"}))
        # time.sleep(10)
        send_eof(weathers_queue, msg)
    elif routing_key == "trip":
        eof_manager.send(body=json.dumps({"type":"exchange", "exchange": "trips"}))
        # time.sleep(10)
        send_eof(trips_queue, msg)
    elif routing_key == "station":
        # eof_manager.send(body=json.dumps({"type":"exchange", "exchange": "stations"}))
        # time.sleep(10)
        send_eof(stations_queue, msg)

def send(queue, city, data, parser):
    for item in data:
        queue.send(parser(item, city))