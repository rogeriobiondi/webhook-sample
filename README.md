# webhook-sample
Webhook Sample

This implements a simple asynchronous API sample to register a webhook and receive temperature changes. The system is abstracted by and internal topic and a scheduler component.

# Solution Design

![solution design](images/Solution.jpg)

# TODO

This is a sample implementation. There are several upgrades to-do:

- ~~Multi threading and production grade performance improvements;~~
- ~~DLQ: DLQ and Reprocessing API.~~
- Webhook Security: Oauth-2 key registration and authorization for secure POST CALLs;
- Service statistics
- Subscriber statistics and circuit breaker

# Pre-reqs

- GNU Make
- Poetry
- Python 3.11+
- PyEnv

# Installation

```
poetry install
```

# Starting infrastructure

You'll need a database and local Kafka broker to test this sample. Run the following command:

```
make infra-start
```

# Running the System Tasks

This component is an abstract representation of the system, which will do the business thing and publishes messages to notify the subscribers. 

```
make run-system
```

# Starting the API

To run the API

```
make run-api
```

Then test it:

```
http://localhost:9090/docs
```

# Register the subscription

```
curl --location 'http://localhost:9090/subscriptions' \
--header 'Content-Type: application/json' \
--data '{
    "name": "my-web-hook",
    "description": "Web hook - Test",
    "url": "http://localhost:9099",
    "auth_key": "jfask329489240krwjekjewlkjre"
}'
```

# Running the Event Processor

The event processor is the component will receive the messages from the internal topic and will provide the webhook updates to the customers.

```
make run-processor
```

# Checking the DLQ Queue

If the webhook is not running, the messages will be moved to the dead letter queue (DLQ)
To check it, run the following command:

```
curl --location 'http://localhost:9090/dlqs?skip=0&limit=100'
```

# Starting the Webhook

Start the webhook to receive the messages

```
make run-webhook
```

# Reprocess the DLQ Queue

You may reprocess the DLQ queue events
```
curl --location 'http://localhost:9090/dlqs' \
--header 'Content-Type: application/json' \
--data '{ "dlqs": [ id1, id2, id3..., idn ]
}'
```

# Stopping infra

Stop the database and the kafka local broker.

```
make infra-stop
```
