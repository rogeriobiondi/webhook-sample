import socket
import json
import datetime
from uuid import uuid4
from json import JSONEncoder
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer

topic = 'updates'
    
string_serializer = StringSerializer('utf_8')

conf = {
    'bootstrap.servers': "localhost:9094",
    'client.id': socket.gethostname()
}

producer = Producer(conf)

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def json_serializer(o: dict):
    return json.dumps(o, cls = CustomEncoder).encode('utf-8')

def delivery_report(err, event):
    if err is not None:
        print(f'Delivery failed for event {event.key().decode("utf8")}: {err}')
    else:
        print(f'Event {event.key().decode("utf8")} produced to {event.topic()}')
        print('')
        evt = event.value().decode("utf-8")
        # remove event from DLQ if it exists
        print(f'Event {evt}')

def produce_message(msg: dict):
    producer.produce(topic = topic,
                     key = string_serializer(str(uuid4())),
                     value = json_serializer(msg),
                     on_delivery = delivery_report)
    producer.flush()
    return True
