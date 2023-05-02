from common.queue import Queue
import json

def callback1(ch, method, properties, body):
    line = json.loads(body.decode())
    if "eof" in line:
        ch.stop_consuming()
        print("RECIBO EOF 1---> DEJO DE ESCUCHAR")
        return
    print(line)


def callback(ch, method, properties, body):
    line = json.loads(body.decode())
    if "eof" in line:
        ch.stop_consuming()
        print("RECIBO EOF 2 ---> DEJO DE ESCUCHAR")
        return
    print(line)


input_queue1 = Queue(queue_name="1")
input_queue1.recv(callback=callback1)

input_queue2 = Queue(queue_name="test")
input_queue2.recv(callback=callback)