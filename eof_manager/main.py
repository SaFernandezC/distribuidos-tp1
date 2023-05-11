import json
from common.queue import Queue
import logging
import os
import functools
import time

exchanges = {}
work_queues = {}
# exchanges = {

#         "weathers":{
#             "writing":1,
#             "eof_received": 0,
#             "queues_binded": {
#                 "prectot_filter":{"listening": 1}
#             }
#         },

#         "trips":{
#             "writing":1,
#             "eof_received": 0,
#             "queues_binded":{
#                 "filter_trips_query1":{"listening": 1},
#                 "filter_trips_year":{"listening":1},
#                 "filter_trips_query3":{"listening":1}
#             }
#         },

#         "stations":{
#             "writing":1,
#             "eof_received": 0,
#             "queues_binded":{
#                 "filter_stations_query2":{"listening": 1},
#                 "filter_stations_query3":{"listening":1}
#             }
#         },

#         "joiner_query_1":{
#             "writing":1,
#             "eof_received": 0,
#             "queues_binded":{}
#         },

#         "joiner_query_2":{
#             "writing":1,
#             "eof_received": 0,
#             "queues_binded":{}
#         },

#         "joiner_query_3":{
#             "writing":1,
#             "eof_received": 0,
#             "queues_binded":{}
#         },
# }

# work_queues = {
#         "date_modifier": {"writing":1, "listening":1, "eof_received":0},
#         "joiner_1": {"writing":1, "listening":1, "eof_received":0},
#         "groupby_query_1": {"writing":1, "listening":1, "eof_received":0},

#         "joiner_query_2": {"writing":1, "listening":1, "eof_received":0},
#         "groupby_query_2": {"writing":1, "listening":1, "eof_received":0},

#         "joiner_query_3": {"writing":1, "listening":1, "eof_received":0},
#         "distance_calculator": {"writing":1, "listening":1, "eof_received":0},
#         "groupby_query_3": {"writing":1, "listening":1, "eof_received":0}
#     }

def load_config():
    global exchanges
    global work_queues
    with open("exchanges.json", "r") as file:
        exchanges = json.loads(file.read())
        file.close()
    with open("queues.json", "r") as file:
        work_queues = json.loads(file.read())
        file.close()

EOF_MSG = json.dumps({"eof": True})


def exchange_with_queues(line, exchanges_queues):
    exchange = exchanges[line["exchange"]]
    writing = exchange["writing"]
    exchange["eof_received"] += 1
    queues_binded = exchange["queues_binded"]
    # print(f"{time.asctime(time.localtime())} -> EOF PARCIAL: {exchange['eof_received']}")

    if exchange["eof_received"] == writing:
        print(f"{time.asctime(time.localtime())} RECIBI IGUAL EOF QUE WRITING en {exchange} -> MANDO EOF A EXCHANGE")
        # MANDAR EL MAXIMOS ENTRE LOS QUE ESCUCHAN
        exchanges_queues[line["exchange"]].send(EOF_MSG)
        # temp = Queue(exchange_name=line["exchange"], exchange_type='fanout')
        # for queue_name, queue_data in queues_binded.items():
            # listening = queue_data["listening"]
        #     temp = Queue(queue_name=queue_name)
            # for i in range(listening):
        #         # print(f"{time.asctime(time.localtime())} ENVIO EOF A COLA {queue_name} DE EXCHANFE: ", line["exchange"])
        #         temp.send(body=EOF_MSG)
            # temp.close()

def exchange_without_queues(line, exchanges_queues):
    exchange = exchanges[line["exchange"]]
    writing = exchange["writing"]

    exchange["eof_received"] += 1
  
    # print(f"{time.asctime(time.localtime())} Exch sin colas EOF PARCIAL :", exchange["eof_received"])

    if exchange["eof_received"] == writing:
        # print(f"{time.asctime(time.localtime())} Exch sin colas RECIBI IGUAL EOF QUE WRITING -> MANDO EOF A EXCHANGE")
        # temp = Queue(exchange_name=line["exchange"], exchange_type="fanout") # En este tp solo uso fanout
        # print(f"{time.asctime(time.localtime())} Exch sin colas ENVIO EOF A EXCHANGE SIN COLAS: ", line["exchange"])
        exchanges_queues[line["exchange"]].send(body=EOF_MSG)
        # temp.close()



def callback(ch, method, properties, body, args):

    line = json.loads(body.decode())


    if line["type"] == "exchange":
        if len(exchanges[line["exchange"]]["queues_binded"]) == 0:
            exchange_without_queues(line, args[0])
        else:
            exchange_with_queues(line, args[0])


    if line["type"] == "work_queue":
        queue = line["queue"]
        writing = work_queues[queue]["writing"]
        listening = work_queues[queue]["listening"]

        work_queues[queue]["eof_received"] += 1

        print("COLA: ", work_queues)

        if work_queues[queue]["eof_received"] == writing:
            # temp = Queue(queue_name=queue)
            for i in range(listening):
                print(f"{time.asctime(time.localtime())} ENVIO EOF A: {queue} donde hay {listening} listening")
                args[1][line["queue"]].send(body=EOF_MSG)
                # temp.send(EOF_MSG)
            # temp.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    load_config()
    input_queue = Queue(queue_name="eof_manager")

    exchanges = {
        "weathers": Queue(exchange_name="weathers", exchange_type='fanout'),
        "trips": Queue(exchange_name="trips", exchange_type='fanout'),
        "stations": Queue(exchange_name="stations", exchange_type='fanout'),
        "joiner_query_1": Queue(exchange_name="joiner_query_1", exchange_type='fanout'),
        "joiner_query_2": Queue(exchange_name="joiner_query_2", exchange_type='fanout'),
        "joiner_query_3": Queue(exchange_name="joiner_query_3", exchange_type='fanout')
    }

    queues = {
        "date_modifier": Queue(queue_name="date_modifier"),
        "joiner_1": Queue(queue_name="joiner_1"),
        "groupby_query_1": Queue(queue_name="groupby_query_1"),
        "joiner_2": Queue(queue_name="joiner_2"),
        "groupby_query_2": Queue(queue_name="groupby_query_2"),
        "joiner_3": Queue(queue_name="joiner_3"),
        "distance_calculator": Queue(queue_name="distance_calculator"),
        "groupby_query_3": Queue(queue_name="groupby_query_3"),
        "trip": Queue(queue_name="trip"),
        "weather": Queue(queue_name="weather"),
        "station": Queue(queue_name="station"),
    }

    on_message_callback = functools.partial(callback, args=(exchanges, queues))
    input_queue.recv(callback=on_message_callback, auto_ack=False)

    return 0
    
if __name__ == '__main__':
    main()

# def direct_exchange(line):
#     # En line tengo exchange y key
#     exchange = exchanges[line["exchange"]]
#     writing = exchange["writing"]
#     key = line["key"]

#     key_data = exchange[key]
#     key_data["eof_received"] += 1

#     if key_data["eof_received"] == writing:
#         temp = Queue(exchange_name=line["exchange"], exchange_type="direct")

#         # for i in range(key_data["listening"]):
#         #     print(f"ENVIO EOF A EXCHANGE DIRECT {line['exchange']} CON KEY {key}")
#         temp.send(body=EOF_MSG, routing_key=key)

#     return 0