import os
from common.queue import Queue
from dotenv import load_dotenv
import ujson as json
import functools
from utils import default, join_func_query3
import time
import pika

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
        print(f"{time.asctime(time.localtime())} RECIBO EOF CALLBACK 1 ---> DEJO DE ESCUCHAR, {line}")
        ch.stop_consuming()
    else:
        add_item_test(args[0], line)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def join(key, item):
    function = eval(JOINER_FUNCTION)
    return function(key, item, side_table)


def callback_queue2(ch, method, properties, body, args):
    line = json.loads(body.decode())
  
    if "eof" in line:
        print(f"{time.asctime(time.localtime())} RECIBO EOF CALLBACK 2 ---> DEJO DE ESCUCHAR, {line}")
        ch.stop_consuming()
        # args[2].send(body=body)
        # args[3].send(body=json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
        ch.basic_publish(exchange='',
                      routing_key="eof_manager",
                      body=json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
    else:
        joined, res = join(args[0], line)

        if joined:
            body=json.dumps(select(args[1], res))
            # args[2].send(body=body)
            ch.basic_publish(exchange='',
                      routing_key=OUTPUT_QUEUE_NAME,
                      body=body)
            # print(select(args[1], res))
    
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    if SELECT:
        fields_to_select = SELECT.split(',')
    else: fields_to_select = None

    key_1 = parse_key(PRIMARY_KEY)
    key_2 = parse_key(PRIMARY_KEY_2)


    # eof_manager = Queue(queue_name="eof_manager")
    # input_queue1 = Queue(exchange_name=INPUT_EXCHANGE_1, bind=INPUT_BIND_1, exchange_type=INPUT_EXCHANGE_TYPE_1)
    # output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)
    # input_queue2 = Queue(queue_name=INPUT_QUEUE_NAME_2)

    # on_message_callback = functools.partial(callback_queue1, args=(key_1,))
    # input_queue1.recv(callback=on_message_callback, auto_ack=False)

    # on_message_callback2 = functools.partial(callback_queue2, args=(key_2, fields_to_select, output_queue, eof_manager))
    # input_queue2.recv(callback=on_message_callback2, auto_ack=False)

    #######
    connection = pika.BlockingConnection(
                                pika.ConnectionParameters(host='rabbitmq', heartbeat=1200))
    channel = connection.channel()

    result = channel.queue_declare(queue="eof_manager", durable=True)
    eof_manager = result.method.queue

    result = channel.queue_declare(queue=INPUT_QUEUE_NAME_2, durable=True)
    input_queue2 = result.method.queue

    result = channel.queue_declare(queue=OUTPUT_QUEUE_NAME, durable=True)
    output_queue = result.method.queue

    channel.exchange_declare(exchange=INPUT_EXCHANGE_1, exchange_type=INPUT_EXCHANGE_TYPE_1)
    result = channel.queue_declare(queue='', exclusive=True)
    input_queue1 = result.method.queue
    channel.queue_bind(exchange=INPUT_EXCHANGE_1, queue=input_queue1)


    on_message_callback = functools.partial(callback_queue1, args=(key_1,))
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=input_queue1, on_message_callback=on_message_callback)
    channel.start_consuming()


    on_message_callback2 = functools.partial(callback_queue2, args=(key_2, fields_to_select, output_queue, eof_manager))
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=input_queue2, on_message_callback=on_message_callback2)
    channel.start_consuming()
    time.sleep(50)
    # input_queue1.close()
    # output_queue.close()
    # input_queue2.close()
    # eof_manager.close()
    return 0


if __name__ == "__main__":
    main()