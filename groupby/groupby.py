import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools
from utils import default, find_dup_trips_year, find_stations_query_3

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
        group_table[key]['sum'] = group_table[key]['sum'] + int(item[FIELD_TO_AGREGATE])
        group_table[key][FIELD_TO_AGREGATE] = group_table[key]['sum'] / group_table[key]['count']
    else: 
        value = int(item[FIELD_TO_AGREGATE])
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
    # print(f"[x] Received {json.loads(body.decode())}")
    line = json.loads(body.decode())
    if "eof" in line:
        send_data(args[2])
        args[3].stop_consuming()
        # print("Recibo EOF -> Side table: ", group_table)
        return

    group(args[0], line, args[1])
    # print("Group table: ", group_table)

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
    # print(json.dumps({"query": QUERY, "results": filtered}))

def main():
    key_1 = parse_key(PRIMARY_KEY)

    agg_function = define_agg()

    input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)

    on_message_callback = functools.partial(callback, args=(key_1, agg_function, output_queue, input_queue))
    input_queue.recv(callback=on_message_callback)

    return 0


if __name__ == "__main__":
    main()