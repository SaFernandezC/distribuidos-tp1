import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools
from utils import default, join_func_query3
import time

load_dotenv()

INPUT_EXCHANGE_1 = os.getenv('INPUT_EXCHANGE_1')
INPUT_EXCHANGE_TYPE_1 = os.getenv('INPUT_EXCHANGE_TYPE_1')
INPUT_BIND_1 = True if os.getenv('INPUT_BIND_1') == "True" else False

INPUT_QUEUE_NAME_2 = os.getenv('INPUT_QUEUE_NAME_2')


OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME')

PRIMARY_KEY = os.getenv('PRIMARY_KEY', '')
PRIMARY_KEY_2 = os.getenv('PRIMARY_KEY_2', '')
SELECT = os.getenv('SELECT', None)

JOINER_FUNCTION = os.getenv('JOINER_FUNCTION', 'default')

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
    if not fields: return row
    return {key: row[key] for key in fields}


def callback_queue1(ch, method, properties, body, args):
    line = json.loads(body.decode())
    if "eof" in line:
        print("RECIBO EOF ---> DEJO DE ESCUCHAR POR SIDE TABLE")
        # print("Recibo EOF y dejo de escuchar-> Side table: ", side_table)
        args[1].close()
        return
    else:
        add_item_test(args[0], line)


def join(key, item):
    function = eval(JOINER_FUNCTION)
    return function(key, item, side_table)


def callback_queue2(ch, method, properties, body, args):
    print("ENTRO AL CALLBACK 2")
    line = json.loads(body.decode())
    print("RECIBO LINEA: ",line)
    
    if "eof" in line:
        args[4].stop_consuming()
        args[3].send(body=json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
        print("RECIBO EOF ---> DEJO DE ESCUCHAR")
    
    else:
        joined, res = join(args[0], line)

        if joined:
            body=json.dumps(select(args[1], res))
            args[2].send(body=body)
            # print(select(args[1], res))
    
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    # Tomo las variables de entorno
    if SELECT:
        fields_to_select = SELECT.split(',')
    else: fields_to_select = None

    key_1 = parse_key(PRIMARY_KEY)
    key_2 = parse_key(PRIMARY_KEY_2)


    eof_manager = Queue(queue_name="eof_manager")
    input_queue1 = Queue(exchange_name=INPUT_EXCHANGE_1, bind=INPUT_BIND_1, exchange_type=INPUT_EXCHANGE_TYPE_1)
    output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)
    input_queue2 = Queue(queue_name=INPUT_QUEUE_NAME_2)

    on_message_callback = functools.partial(callback_queue1, args=(key_1, input_queue1, ))
    input_queue1.recv(callback=on_message_callback)

    print("SALI DEL CALLBACK1 VOY AL CALLBACK 2")
    on_message_callback2 = functools.partial(callback_queue2, args=(key_2, fields_to_select, output_queue, eof_manager, input_queue2))
    input_queue2.recv(callback=on_message_callback2, auto_ack=False)

    return 0


if __name__ == "__main__":
    main()