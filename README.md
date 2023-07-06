# webhook-sample
Webhook Sample

This sample creates a simple asynchronous API sample to implement a webhook.
The webhook will be invoked every 06 second (each minute)

# Solution Design

![solution design](images/Solution.jpg)

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

```
make infra-start
```

# Starting the API

```
make run-api
```

Then test it:

```
http://localhost:9090/docs
```

# Running the Scheduler

```
make run-scheduler
```

# Running the Worker

```
make run-worker
```

# Stopping infra

```
make infra-stop
```
