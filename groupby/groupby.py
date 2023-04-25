import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools
import time

load_dotenv()

INPUT_QUEUE_NAME = os.getenv('INPUT_QUEUE_NAME')
PRIMARY_KEY = os.getenv('PRIMARY_KEY')
PRIMARY_KEY_2 = os.getenv('PRIMARY_KEY_2')
FIELD_TO_AGREGATE = os.getenv('FIELD_TO_AGREGATE')
AGG = os.getenv('AGG')

group_table = {}


def parse_key(key):
    return key.split(',')

def sum():
    return 0

def avg(key, item):
    group_table[key]['count'] = group_table[key]['count'] + 1
    group_table[key]['sum'] = group_table[key]['sum'] + int(item[FIELD_TO_AGREGATE])
    group_table[key][FIELD_TO_AGREGATE] = group_table[key]['sum'] / group_table[key]['count']

def count():
    return 0

def check_key_len(key, item):
    values = []
    for _i in key:
        values.append(item[_i])

    if len(values) == 1:
        return values[0]
    return tuple(values)

def group(key, item, agg_function):
    # values = []
    # for _i in key:
    #     values.append(item[_i])

    # key_dict = tuple(values)
    key_dict = check_key_len(key, item)
    if key_dict in group_table:
        agg_function(key_dict, item)
    else:
        value = int(item[FIELD_TO_AGREGATE])
        group_table[key_dict] = {FIELD_TO_AGREGATE:value, "count": 1, "sum": value}

def callback(ch, method, properties, body, args):
    # print(f"[x] Received {json.loads(body.decode())}")
    line = json.loads(body.decode())
    if "eof" in line:
        print("Recibo EOF -> Side table: ", group_table)
        return

    group(args[0], line, args[1])
    print("Group table: ", group_table)

def define_agg():
    if AGG == 'avg':
        return avg
    elif AGG == 'sum':
        return sum
    else: return count


def main():
    key_1 = parse_key(PRIMARY_KEY)

    agg_function = define_agg()

    input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    # output_queue = Queue(exchange_name=OUTPUT_EXCHANGE, exchange_type=OUTPUT_EXCHANGE_TYPE)

    on_message_callback = functools.partial(callback, args=(key_1, agg_function))
    input_queue.recv(callback=on_message_callback)

    return 0


if __name__ == "__main__":
    main()