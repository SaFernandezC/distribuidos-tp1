import json
from common.queue import Queue
import logging
import os
import functools
import time
import pika

exchanges = {}
work_queues = {}

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


def exchange_with_queues(line, exchanges_queues, queues, ch):
    exchange = exchanges[line["exchange"]]
    writing = exchange["writing"]
    exchange["eof_received"] += 1
    queues_binded = exchange["queues_binded"]
    # print(f"{time.asctime(time.localtime())} -> EOF PARCIAL: {exchange['eof_received']}")

    if exchange["eof_received"] == writing:
        # time.sleep(5)
        # print(f"{time.asctime(time.localtime())} RECIBI IGUAL EOF QUE WRITING en {exchange} -> MANDO EOF A EXCHANGE")
       
        # MANDAR EL MAXIMOS ENTRE LOS QUE ESCUCHAN
        # exchanges_queues[line["exchange"]].send(EOF_MSG)

        # temp = Queue(exchange_name=line["exchange"], exchange_type='fanout')
        for queue_name, queue_data in queues_binded.items():
            listening = queue_data["listening"]
        #     temp = Queue(queue_name=queue_name)
            for i in range(listening):
                print(f"{time.asctime(time.localtime())} ENVIO EOF A COLA {queue_name} DE EXCHANFE: ", line["exchange"])
                msg = json.dumps({"eof":True, "from":queue_name, "i":i})
                # queues[queue_name].send(body=msg)
                ch.basic_publish(exchange='',
                      routing_key=queue_name,
                      body=EOF_MSG)
        #         temp.send(body=EOF_MSG)
            # temp.close()

def exchange_without_queues(line, exchanges_queues, ch):
    exchange = exchanges[line["exchange"]]
    writing = exchange["writing"]

    exchange["eof_received"] += 1
  
    # print(f"{time.asctime(time.localtime())} Exch sin colas EOF PARCIAL :", exchange["eof_received"])

    if exchange["eof_received"] == writing:
        # print(f"{time.asctime(time.localtime())} Exch sin colas RECIBI IGUAL EOF QUE WRITING -> MANDO EOF A EXCHANGE")
        # temp = Queue(exchange_name=line["exchange"], exchange_type="fanout") # En este tp solo uso fanout
        # print(f"{time.asctime(time.localtime())} Exch sin colas ENVIO EOF A EXCHANGE SIN COLAS: ", line["exchange"])
        
        # exchanges_queues[line["exchange"]].send(body=EOF_MSG)
        ch.basic_publish(exchange=line["exchange"],
                      routing_key='',
                      body=EOF_MSG)
        # temp.close()



def callback(ch, method, properties, body, args):

    line = json.loads(body.decode())


    if line["type"] == "exchange":
        if len(exchanges[line["exchange"]]["queues_binded"]) == 0:
            exchange_without_queues(line, args[0], ch)
        else:
            exchange_with_queues(line, args[0], args[1], ch)


    if line["type"] == "work_queue":
        queue = line["queue"]
        writing = work_queues[queue]["writing"]
        listening = work_queues[queue]["listening"]

        work_queues[queue]["eof_received"] += 1

        if work_queues[queue]["eof_received"] == writing:
            # temp = Queue(queue_name=queue)
            for i in range(listening):
                print(f"{time.asctime(time.localtime())} ENVIO EOF A: {queue} donde hay {listening} listening")
                # args[1][line["queue"]].send(body=EOF_MSG)
                ch.basic_publish(exchange='',
                      routing_key=line["queue"],
                      body=EOF_MSG)
                # temp.send(EOF_MSG)
            # temp.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    load_config()
    # input_queue = Queue(queue_name="eof_manager")

    # exchanges = {
    #     "weathers": Queue(exchange_name="weathers", exchange_type='fanout'),
    #     "trips": Queue(exchange_name="trips", exchange_type='fanout'),
    #     "stations": Queue(exchange_name="stations", exchange_type='fanout'),
    #     "joiner_query_1": Queue(exchange_name="joiner_query_1", exchange_type='fanout'),
    #     "joiner_query_2": Queue(exchange_name="joiner_query_2", exchange_type='fanout'),
    #     "joiner_query_3": Queue(exchange_name="joiner_query_3", exchange_type='fanout')
    # }

    # queues = {
    #     "date_modifier": Queue(queue_name="date_modifier"),
    #     "joiner_1": Queue(queue_name="joiner_1"),
    #     "groupby_query_1": Queue(queue_name="groupby_query_1"),
    #     "joiner_2": Queue(queue_name="joiner_2"),
    #     "groupby_query_2": Queue(queue_name="groupby_query_2"),
    #     "joiner_3": Queue(queue_name="joiner_3"),
    #     "distance_calculator": Queue(queue_name="distance_calculator"),
    #     "groupby_query_3": Queue(queue_name="groupby_query_3"),
    #     "trip": Queue(queue_name="trip"),
    #     "weather": Queue(queue_name="weather"),
    #     "station": Queue(queue_name="station"),
    #     "filter_trips_query1": Queue(queue_name="filter_trips_query1"),
    #     "filter_trips_year": Queue(queue_name="filter_trips_year"),
    #     "filter_trips_query3": Queue(queue_name="filter_trips_query3"),
    #     "filter_stations_query2": Queue(queue_name="filter_stations_query2"),
    #     "filter_stations_query3": Queue(queue_name="filter_stations_query3"),
    #     "prectot_filter": Queue(queue_name="prectot_filter"),
    # }

    connection = pika.BlockingConnection(
                                pika.ConnectionParameters(host='rabbitmq', heartbeat=1200))
    channel = connection.channel()

    channel.exchange_declare(exchange='weathers', exchange_type='fanout')
    channel.exchange_declare(exchange='trips', exchange_type='fanout')
    channel.exchange_declare(exchange='stations', exchange_type='fanout')
    channel.exchange_declare(exchange='joiner_query_1', exchange_type='fanout')
    channel.exchange_declare(exchange='joiner_query_2', exchange_type='fanout')
    channel.exchange_declare(exchange='joiner_query_3', exchange_type='fanout')

    result = channel.queue_declare(queue="eof_manager", durable=True)
    eof_manager = result.method.queue

    channel.queue_declare(queue="date_modifier", durable=True)
    channel.queue_declare(queue="groupby_query_1", durable=True)
    channel.queue_declare(queue="joiner_2", durable=True)
    channel.queue_declare(queue="groupby_query_2", durable=True)
    channel.queue_declare(queue="joiner_3", durable=True)
    channel.queue_declare(queue="distance_calculator", durable=True)
    channel.queue_declare(queue="trip", durable=True)
    channel.queue_declare(queue="weather", durable=True)
    channel.queue_declare(queue="station", durable=True)
    channel.queue_declare(queue="filter_trips_query1", durable=True)
    channel.queue_declare(queue="filter_trips_year", durable=True)
    channel.queue_declare(queue="filter_trips_query3", durable=True)
    channel.queue_declare(queue="filter_stations_query2", durable=True)
    channel.queue_declare(queue="filter_stations_query3", durable=True)
    channel.queue_declare(queue="prectot_filter", durable=True)



    on_message_callback = functools.partial(callback, args=("exchanges", "queues"))
    # input_queue.recv(callback=on_message_callback, auto_ack=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=eof_manager, on_message_callback=on_message_callback)
    channel.start_consuming()


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