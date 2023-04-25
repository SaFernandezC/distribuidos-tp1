import os
from common.queue import Queue
from dotenv import load_dotenv
from utils import compare
import json
import functools
import time

load_dotenv()

CANTIDAD = os.getenv('CANT_CONDICIONES')
SELECT = os.getenv('SELECT')
INPUT_QUEUE = os.getenv('INPUT_QUEUE', '')
INPUT_EXCHANGE = os.getenv('INPUT_EXCHANGE', '')
INPUT_EXCHANGE_TYPE = os.getenv('INPUT_EXCHANGE_TYPE', '')
INPUT_BIND = os.getenv('INPUT_BIND', '')

OUTPUT_EXCHANGE = os.getenv('OUTPUT_EXCHANGE', '')
OUTPUT_EXCHANGE_TYPE = os.getenv('OUTPUT_EXCHANGE_TYPE', '')
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME', '')

def filtrar_integer(filtro, data):
    field = filtro[2]
    op = filtro[3]
    left = float(filtro[4])
    return compare(op, float(data[field]), left)

def filtrar_string(filtro, data):
    return 0

def filtrar(filtro, data):
    if filtro[1] == 'int':
        return filtrar_integer(filtro, data)
    else:
        return filtrar_string(filtro, data)


def select(fields, row):
    return {key: row[key] for key in fields}



def callback(ch, method, properties, body, args):
    line = json.loads(body.decode())

    if "eof" in line:
        args[2].send(body=body)
        print("Recibo EOF -> Dejo de recibir mensajes")
        return

    filtered = filtrar(args[1][0], line)
    if filtered:
        body=json.dumps(select(args[0], line))
        print(select(args[0], line))
        args[2].send(body=body)

def main():
    # Tomo las variables de entorno
    fields_to_select = SELECT.split(',')
    filters = []
    for i in range(int(CANTIDAD)):
        filters.append(os.getenv('FILTER_'+str(i)).split(','))
    

    bind = True
    if INPUT_BIND == "True": bind == True 
    else: bind == False

    input_queue = Queue(queue_name=INPUT_QUEUE, exchange_name=INPUT_EXCHANGE, bind=True, exchange_type=INPUT_EXCHANGE_TYPE)

    if OUTPUT_EXCHANGE_TYPE == 'fanout':
        output_queue = Queue(exchange_name=OUTPUT_EXCHANGE, exchange_type=OUTPUT_EXCHANGE_TYPE)
    else:
        output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)


    print(' Waiting for messages. To exit press CTRL+C')
    on_message_callback = functools.partial(callback, args=(fields_to_select, filters, output_queue))
    input_queue.recv(callback=on_message_callback)

    return 0


if __name__ == "__main__":
    main()