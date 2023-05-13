import functools

def callback_queue1(ch, method, properties, body, args):
    data = body.decode()
    args[0].put(data)
    ch.stop_consuming()
    ch.basic_ack(delivery_tag=method.delivery_tag)
 

def asker(metrics_queue, results_queue):
    on_message_callback = functools.partial(callback_queue1, args=(results_queue,))
    metrics_queue.recv(callback=on_message_callback)