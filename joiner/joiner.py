import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools
import time

load_dotenv()

INPUT_EXCHANGE = os.getenv('INPUT_EXCHANGE')
INPUT_EXCHANGE_TYPE = os.getenv('INPUT_EXCHANGE_TYPE')
INPUT_BIND = os.getenv('INPUT_BIND')

OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME')
# OUTPUT_EXCHANGE_TYPE = os.getenv('OUTPUT_EXCHANGE_TYPE')

PRIMARY_KEY = os.getenv('PRIMARY_KEY')
PRIMARY_KEY_2 = os.getenv('PRIMARY_KEY_2')
SELECT = os.getenv('SELECT','')

side_table = {}

def parse_key(key):
    splitted = key.split(',')
    return tuple(splitted)


def add_item_test(key, item):
    values = []
    for _i in key:
        values.append(item[_i])
        del item[_i]
    
    side_table[tuple(values)] = item

def select(fields, row):
    if fields[0] == '':
        return row
    return {key: row[key] for key in fields}

def callback_queue1(ch, method, properties, body, args):
    line = json.loads(body.decode())
    if "eof" in line:
        print("Recibo EOF -> Side table: ", side_table)
        args[1].close()
        return

    add_item_test(args[0], line)


def join(key, item):
    values = []
    for _i in key:
        values.append(item[_i])

    if tuple(values) in side_table:
        return True, {**item,**side_table[tuple(values)]}

    return False, {}

def callback_queue2(ch, method, properties, body, args):
    line = json.loads(body.decode())
    joined, res = join(args[0], line)

    if joined:
        body=json.dumps(select(args[1], res))
        args[2].send(body=body)
        print(select(args[1], res))



def main():
    # Tomo las variables de entorno
    fields_to_select = SELECT.split(',')

    bind = True
    if INPUT_BIND == "True": bind == True 
    else: bind == False

    key_1 = parse_key(PRIMARY_KEY)
    key_2 = parse_key(PRIMARY_KEY_2)


    input_queue1 = Queue(exchange_name=INPUT_EXCHANGE, bind=bind, exchange_type=INPUT_EXCHANGE_TYPE)
    input_queue2 = Queue(queue_name='trips_1')
    output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)

    on_message_callback = functools.partial(callback_queue1, args=(key_1, input_queue1))
    input_queue1.recv(callback=on_message_callback)

    on_message_callback2 = functools.partial(callback_queue2, args=(key_2, fields_to_select, output_queue))
    input_queue2.recv(callback=on_message_callback2)

    return 0


if __name__ == "__main__":
    main()