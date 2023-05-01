import json
from common.queue import Queue
import logging
import os
import functools

exchanges = {

        "weathers":{
            "writing":1,
            "eof_received": 0,
            "queues_binded": {
                "prectot_filter":{"listening": 2}
            }
        },

        "trips":{
            "writing":1,
            "eof_received": 0,
            "queues_binded":{
                "filter_trips_query1":{"listening": 1}
            }
        },
}

work_queues = {
        "date_modifier": {"writing":2, "listening":1, "eof_received":0},
        "joiner_query_1": {"writing":1, "listening":1, "eof_received":0},
        "groupby_query_1": {"writing":1, "listening":1, "eof_received":0}
    }


def callback(ch, method, properties, body, args):

    line = json.loads(body.decode())

    if line["type"] == "exchange":
        data = list(exchanges[line["exchange"]].items())

        writing = data[0][1]
        eof_received = data[1][1]
        queues_binded = data[2][1]

        for queue_name, queue_data in queues_binded.items():
            listening = queue_data["listening"]

            temp = Queue(queue_name=queue_name)
            for i in range(listening):
                temp.send(json.dumps({"eof": True}))
            temp.close()

    if line["type"] == "work_queue":
        return
    return 0

def main():
    input_queue = Queue(queue_name="eof_manager")

    on_message_callback = functools.partial(callback, args=("exchanges",))
    input_queue.recv(callback=on_message_callback)

    return 0
    
if __name__ == '__main__':
    main()