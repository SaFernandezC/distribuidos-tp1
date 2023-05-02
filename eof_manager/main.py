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


def exchange_with_queues(line):
    exchange = exchanges[line["exchange"]]
    writing = exchange["writing"]
    exchange["eof_received"] += 1
    queues_binded = exchange["queues_binded"]
    # print("EOF PARCIAL :", exchange["eof_received"])

    if exchange["eof_received"] == writing:
        # print("RECIBI IGUAL EOF QUE WRITING -> MANDO EOF A EXCHANGE")
        for queue_name, queue_data in queues_binded.items():
            listening = queue_data["listening"]
            temp = Queue(queue_name=queue_name)
            for i in range(listening):
                print(f"ENVIO EOF A COLA {queue_name} DE EXCHANFE: ", line["exchange"])
                temp.send(EOF_MSG)
            temp.close()

def exchange_without_queues(line):
    exchange = exchanges[line["exchange"]]
    writing = exchange["writing"]

    exchange["eof_received"] += 1
  
    # print("EOF PARCIAL :", exchange["eof_received"])

    if exchange["eof_received"] == writing:
        # print("RECIBI IGUAL EOF QUE WRITING -> MANDO EOF A EXCHANGE")
        temp = Queue(exchange_name=line["exchange"], exchange_type="fanout") # En este tp solo uso fanout
        print("ENVIO EOF A EXCHANGE SIN COLAS: ", line["exchange"])
        temp.send(EOF_MSG)
        temp.close()


def callback(ch, method, properties, body, args):

    line = json.loads(body.decode())

    if line["type"] == "exchange":
        data = list(exchanges[line["exchange"]].items())
        
        if len(exchanges[line["exchange"]]["queues_binded"]) == 0:
            exchange_without_queues(line)
        else:
            exchange_with_queues(line)


    if line["type"] == "work_queue":
        queue = line["queue"]
        writing = work_queues[queue]["writing"]
        listening = work_queues[queue]["listening"]

        work_queues[queue]["eof_received"] += 1

        if work_queues[queue]["eof_received"] == writing:
            temp = Queue(queue_name=queue)
            for i in range(listening):
                print(f"ENVIO EOF A: {queue} donde hay {listening} listening")
                temp.send(EOF_MSG)
                # time.sleep(2)
            temp.close()

def main():
    load_config()
    input_queue = Queue(queue_name="eof_manager")

    on_message_callback = functools.partial(callback, args=("exchanges",))
    input_queue.recv(callback=on_message_callback)

    return 0
    
if __name__ == '__main__':
    main()