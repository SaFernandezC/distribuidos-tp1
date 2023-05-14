import os
from common.queue import Queue
from dotenv import load_dotenv
import ujson as json
import functools
from utils import default, find_dup_trips_year, find_stations_query_3
import pika

load_dotenv()

QUERY = os.getenv('QUERY')
INPUT_QUEUE_NAME = os.getenv('INPUT_QUEUE_NAME')
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME')
PRIMARY_KEY = os.getenv('PRIMARY_KEY')
PRIMARY_KEY_2 = os.getenv('PRIMARY_KEY_2')
FIELD_TO_AGREGATE = os.getenv('FIELD_TO_AGREGATE')
AGG = os.getenv('AGG')
SEND_DATA_FUNCTION = os.getenv('SEND_DATA_FUNCTION', 'default')

group_table = {}

def parse_key(key):
    return key.split(',')

def sum():
    return 0

def avg(key, item):
    if key in group_table:
        group_table[key]['count'] = group_table[key]['count'] + 1
        group_table[key]['sum'] = group_table[key]['sum'] + float(item[FIELD_TO_AGREGATE])
        group_table[key][FIELD_TO_AGREGATE] = group_table[key]['sum'] / group_table[key]['count']
    else: 
        value = float(item[FIELD_TO_AGREGATE])
        group_table[key] = {FIELD_TO_AGREGATE:value, "count": 1, "sum": value}

def count(key, item):
    if key in group_table:
        if item[FIELD_TO_AGREGATE] in group_table[key]:
            group_table[key][item[FIELD_TO_AGREGATE]] += 1
        else:
            group_table[key][item[FIELD_TO_AGREGATE]] = 1
    else:
        group_table[key] = {item[FIELD_TO_AGREGATE]: 1}

def check_key_len(key, item):
    values = []
    for _i in key:
        values.append(item[_i])

    if len(values) == 1:
        return values[0]
    return tuple(values)


def group(key, item, agg_function):
    key_dict = check_key_len(key, item)
    agg_function(key_dict, item)


def callback(ch, method, properties, body, args):
    line = json.loads(body.decode())
    if "eof" in line:
        print("RECIBO EOF ---> DEJO DE ESCUCHAR y ENVIO DATA")
        ch.stop_consuming()
        # send_data(args[2])
        function = eval(SEND_DATA_FUNCTION)
        filtered = function(group_table)
        ch.basic_publish(exchange='',
                      routing_key=OUTPUT_QUEUE_NAME,
                      body=json.dumps({"query": QUERY, "results": filtered}))
    else:
        group(args[0], line, args[1])
        # print("Group table: ", group_table)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def define_agg():
    if AGG == 'avg':
        return avg
    elif AGG == 'sum':
        return sum
    else: return count

def send_data(queue):
    function = eval(SEND_DATA_FUNCTION)
    filtered = function(group_table)
    queue.send(body=json.dumps({"query": QUERY, "results": filtered}))

def main():
    key_1 = parse_key(PRIMARY_KEY)
    agg_function = define_agg()

    # input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    # output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)

    # on_message_callback = functools.partial(callback, args=(key_1, agg_function, output_queue))
    # input_queue.recv(callback=on_message_callback, auto_ack=False)


    connection = pika.BlockingConnection(
                                pika.ConnectionParameters(host='rabbitmq', heartbeat=1200))
    channel = connection.channel()

    result = channel.queue_declare(queue=INPUT_QUEUE_NAME, durable=True)
    input_queue = result.method.queue

    result = channel.queue_declare(queue=OUTPUT_QUEUE_NAME, durable=True)
    output_queue = result.method.queue

    on_message_callback = functools.partial(callback, args=(key_1, agg_function, output_queue))
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=input_queue, on_message_callback=on_message_callback)
    channel.start_consuming()

    # input_queue.close()
    # output_queue.close()
    return 0


if __name__ == "__main__":
    main()