import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools

load_dotenv()

CANTIDAD = os.getenv('CANT_CONDICIONES')
SELECT = os.getenv('SELECT')
INPUT_QUEUE_NAME = os.getenv('INPUT_QUEUE_NAME')
OUTPUT_EXCHANGE = os.getenv('OUTPUT_EXCHANGE')
OUTPUT_EXCHANGE_TYPE = os.getenv('OUTPUT_EXCHANGE_TYPE')

def restar_dia(fecha):
    # Convertir la fecha en una tupla de tres elementos
    anio, mes, dia = map(int, fecha.split('-'))

    # Restar un día al día
    dia = dia - 1

    # Ajustar los valores de los otros elementos de la tupla si es necesario
    if dia == 0:
        mes = mes - 1
        if mes == 0:
            anio = anio - 1
            mes = 12
        dia = dias_en_mes(mes, anio)

    # Convertir la tupla de vuelta a una cadena de fecha
    nueva_fecha = f'{anio:04d}-{mes:02d}-{dia:02d}'
    return nueva_fecha

def dias_en_mes(mes, anio):
    if mes in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif mes == 2:
        if es_bisiesto(anio):
            return 29
        else:
            return 28
    else:
        return 30

def es_bisiesto(anio):
    if anio % 4 == 0:
        if anio % 100 == 0:
            if anio % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def callback(ch, method, properties, body, args):
    line = json.loads(body.decode())
    if "eof" in line:
        args[0].send(body=body)
        print("Recibo EOF -> Dejo de recibir mensajes")
        return

    line['date'] = restar_dia(line['date'])
    # print(line)
    args[0].send(body=json.dumps(line))


def main():

    input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    output_queue = Queue(exchange_name=OUTPUT_EXCHANGE, exchange_type=OUTPUT_EXCHANGE_TYPE)

    print(' Waiting for messages. To exit press CTRL+C')
    on_message_callback = functools.partial(callback, args=(output_queue,))
    input_queue.recv(callback=on_message_callback)

    return 0


if __name__ == "__main__":
    main()