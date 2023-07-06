import datetime
import json
import socket
import time
from json import JSONEncoder
from uuid import uuid4

from art import text2art
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer


class Temperature(object):
    def __init__(self, city, reading, unit, timestamp):
        self.city = city
        self.reading = reading
        self.unit = unit
        self.timestamp = timestamp  

def delivery_report(err, event):
    if err is not None:
        print(f'Delivery failed on reading for {event.key().decode("utf8")}: {err}')
    else:
        print(f'Temp reading for {event.key().decode("utf8")} produced to {event.topic()}')

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def json_serializer(o):
    return json.dumps(o.__dict__, cls = CustomEncoder).encode('utf-8')

if __name__ == '__main__':
    data = [
        Temperature('London', 12, 'C', datetime.datetime.now()),
        # Temperature('Chicago', 63, 'F', datetime.datetime.now()),
        # Temperature('Berlin', 14, 'C', datetime.datetime.now()),
        # Temperature('Madrid', 18, 'C', datetime.datetime.now()),
        # Temperature('Phoenix', 78, 'F', datetime.datetime.now())
    ]

    topic = 'updates'
    
    string_serializer = StringSerializer('utf_8')

    conf = {
        'bootstrap.servers': "localhost:9094",
        'client.id': socket.gethostname()
    }

    producer = Producer(conf)

    for temp in data:
        producer.produce(topic=topic, 
                         key = string_serializer(str(uuid4())),
                         value = json_serializer(temp),
                         on_delivery=delivery_report)
    producer.flush()

print(text2art("Scheduler"))
print("starting...\n")
