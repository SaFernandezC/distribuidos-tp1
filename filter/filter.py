import os
from common.queue import Queue
from dotenv import load_dotenv
from utils import compare, apply_operator
import json
import functools
import time

load_dotenv()

CANTIDAD = os.getenv('CANT_CONDICIONES', 0)
SELECT = os.getenv('SELECT', None)
OPERATORS = os.getenv('OPERATORS', None)

INPUT_QUEUE = os.getenv('INPUT_QUEUE', '')
INPUT_EXCHANGE = os.getenv('INPUT_EXCHANGE', '')
INPUT_EXCHANGE_TYPE = os.getenv('INPUT_EXCHANGE_TYPE', '')
INPUT_BIND = True if os.getenv('INPUT_BIND') == "True" else False

OUTPUT_EXCHANGE = os.getenv('OUTPUT_EXCHANGE', '')
OUTPUT_EXCHANGE_TYPE = os.getenv('OUTPUT_EXCHANGE_TYPE', '')
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME', '')

SHOW_LOGS =  True if os.getenv("SHOW_LOGS") == "True" else False

SIN_FILTROS = 0
SIN_SELECCIONES = 0


def printer(msg):
    if SHOW_LOGS:
        print(msg)

def filtrar_integer(filtro, data):
    field = filtro[2]
    op = filtro[3]
    left = float(filtro[4])
    return compare(op, float(data[field]), left)

def filtrar_string(filtro, data):
    field = filtro[2]
    op = filtro[3]
    left = filtro[4]
    return compare(op, data[field], left)

def filtrar(filtro, data):
    if filtro[1] == 'int':
        return filtrar_integer(filtro, data)
    else:
        return filtrar_string(filtro, data)

def select(fields, row):
    if not fields: return row
    return {key: row[key] for key in fields}

def apply_logic_operator(results, operators):
    size = len(results)
    if size == 1:
        return results[0]
    
    for i in range(len(operators)):
        results[i+1] = apply_operator(operators[i], results[i], results[i+1])

    return results[i+1]


# def send_eof(queue, msg):
#     for i in range(EOF_TO_SEND):
#         queue.send(body=msg)
#     queue.close()
def send_eof(eof_manager):
    if OUTPUT_EXCHANGE == '':
        eof_manager.send(body=json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
        # print("Envio: ", json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
    else:
        # print("Envio: ", json.dumps({"type":"exchange", "exchange": OUTPUT_EXCHANGE}))
        eof_manager.send(body=json.dumps({"type":"exchange", "exchange": OUTPUT_EXCHANGE}))


def callback(ch, method, properties, body, args):
    line = json.loads(body.decode())
    if "eof" in line:
        # print(f"{time.asctime(time.localtime())} RECIBO EOF {line} ---> DEJO DE ESCUCHAR")
        # args[2].send(body=body)
        send_eof(args[6])
        ch.stop_consuming()
    else:
        filtered = True
        filter_results = []
        if args[3] != SIN_FILTROS:
            for filtro in args[1]:
                filter_results.append(filtrar(filtro, line))

            filtered = apply_logic_operator(filter_results, args[4])
            
        if filtered:
            body=json.dumps(select(args[0], line))
            printer(select(args[0], line))
            args[2].send(body=body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Tomo las variables de entorno
    if SELECT:
        fields_to_select = SELECT.split(',')
    else: fields_to_select = None


    filters = []
    cantidad_filtros = int(CANTIDAD)
    for i in range(cantidad_filtros):
        filters.append(os.getenv('FILTER_'+str(i)).split(','))
    
    if OPERATORS and cantidad_filtros > 1:
        operators = OPERATORS.split(',')
    else: operators = None

    eof_manager = Queue(queue_name="eof_manager")
    input_queue = Queue(queue_name=INPUT_QUEUE, exchange_name=INPUT_EXCHANGE, bind=INPUT_BIND, exchange_type=INPUT_EXCHANGE_TYPE)

    if OUTPUT_EXCHANGE_TYPE == 'fanout':
        output_queue = Queue(exchange_name=OUTPUT_EXCHANGE, exchange_type=OUTPUT_EXCHANGE_TYPE)
    else:
        output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)


    # print(' Waiting for messages. To exit press CTRL+C')
    on_message_callback = functools.partial(callback, args=(fields_to_select, filters, output_queue, cantidad_filtros, operators, input_queue, eof_manager))
    input_queue.recv(callback=on_message_callback, auto_ack=False)

    time.sleep(50)

if __name__ == "__main__":
    main()