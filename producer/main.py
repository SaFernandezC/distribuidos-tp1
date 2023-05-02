from common.queue import Queue
import json

EOF_MSG = json.dumps({"eof": True})


one = Queue(queue_name="1")
temp = Queue(queue_name="test")

for i in range(5):
    one.send(json.dumps({"mensaje1":1}))
    temp.send(json.dumps({"mensaje2":2}))

one.send(EOF_MSG)

for i in range(2):
    temp.send(EOF_MSG)
temp.close()