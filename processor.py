import datetime
import json
import threading
import time

import backoff
import requests
from art import text2art
from confluent_kafka import Consumer, KafkaError, KafkaException
from sqlalchemy.orm import Session

from app import database, orm, service
from app.database import sessionmaker, engine

# Maximum number of threads
MAX_THREADS = 2

db = database.SessionLocal()
subscribers = [sub.__dict__ for sub in service.get_subscriptions(db, 0, 1000)]

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
                process_message(msg)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False 

def call_subscriber_webhook(client:dict, 
                            msg: dict, 
                            max_retries = 3,
                            base = 2):
    """
    Call the subscriber webhook

        Exponential algorithm t = b^r
            t = time delay applied between actions
            base = multiplicative factor (2)
            retry_count = number of retry
    """
    LocalSession = sessionmaker(autocommit = False, autoflush = False, bind = engine)
    ldb = LocalSession()
    remaining_retries = max_retries
    while True:
        retry_count = max_retries - remaining_retries + 1
        try:
            print(f"Sending message to client {client['id']} - <{client['name']}>: {client['url']}")
            print(f"Retry: {retry_count}...")
            headers = {}
            # If the client has an auth key set up, include in the headers
            if client['auth_key']:
                headers['Authorization'] = f"Bearer {client['auth_key']}"
            response = requests.post(client['url'], json = msg, headers = headers)
            print("message: ", response.json())
            print("status code:", response.status_code)
            if response.status_code == 200:
                return True
            else:
                # TO-DO log HTTP error from subscriber
                return False
        except Exception as e:
            remaining_retries = remaining_retries - 1
            if remaining_retries <= 0:
                print("Notification failed! Logging and/or DLQueuing it...")
                service.create_dlq(ldb, json.dumps(msg))
                return False
            else:                 
                time.sleep(base ^ retry_count)

def check_thread_limit(max_threads = MAX_THREADS, 
                       wait_time = 5,
                       max_time = 240):
    total_seconds = 0
    while True:
        threads = threading.enumerate()
        print("Current threads:")
        for thread in threads:
            print(thread.name)
        if len(threads) < max_threads:
            break
        else:
            print("Maximum number of thread reached! Waiting 5 sec...")
            time.sleep(wait_time)
            total_seconds = total_seconds + wait_time
            if total_seconds > max_time:
                # Exit and let the container orchestrator recreate the app
                # e. g. kubernetes
                exit(2)

def notify_all_subscribers(msg: dict):
    """
    Send the message for each client
    """
    for sub in subscribers:
        print(f"Sending message: {msg} to subscriber {sub}...")
        check_thread_limit()
        threading.Thread(target = call_subscriber_webhook, args=(sub, msg)).start()
                    
def process_message(msg):
    o = json.loads(msg.value().decode('utf-8'))
    print(f"\nReceived message: { msg.key().decode('utf-8') }")
    print(f"message: ", o)
    notify_all_subscribers(o)

if __name__ == "__main__":
    print(text2art("Event Processor"))
    print("starting...\n")
    topic = "updates"
    print("subscribers: ")
    for sub in subscribers: print(sub)        
    print("")
    consumer_loop(consumer = consumer, topics=[ topic ])
