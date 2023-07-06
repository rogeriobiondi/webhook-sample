import json
import backoff
import requests
import datetime

from art import text2art
from confluent_kafka import Consumer
from pysondb import db

# Get Client data
fakedb = db.getDb("./fakedb.json")
subscribers = fakedb.getAll()

conf = {
    'bootstrap.servers': "localhost:9094",
    'group.id': "workers",
    'auto.offset.reset': 'smallest'
}

consumer = Consumer(conf)

running = True

def consumer_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout = 1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                process_message( msg )
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False 

@backoff.on_exception(backoff.expo, 
                      requests.exceptions.RequestException,
                      max_time = 60,
                      raise_on_giveup = True)
def call_subscriber_webhook(client:dict, msg: dict):
    """
    Call the subscriber webhook
    """
    print(f"Sending message to client {client['id']} - <{client['name']}>: {client['url']}")
    response = requests.post(client['url'], json = msg)
    print("message: ", response.json())
    print("status code:", response.status_code)

def notify_all_subscribers(msg: dict):
    # Send the message for each client
    for sub in subscribers:
        try:
            call_subscriber_webhook(sub, msg)
        except:
            print("Notification failed! Log and/or DLQ it.")
        
def process_message(msg):
    print("bla: ", msg.value())
    o = json.loads(msg.value().decode('utf-8'))
    print(f"Received message: { msg.key().decode('utf-8') }")
    print(f"message: ", o)
    notify_all_subscribers(o)

if __name__ == "__main__":
    print(text2art("Worker"))
    print("starting...\n")
    print("subscribers: ", subscribers)
    topic = "updates"
    consumer_loop(consumer = consumer, topics=[ topic ])
