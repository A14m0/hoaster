# Hoaster 🔥🍞🔥

Hoaster is a network mocking system application, with the goal of being able to
be easily extended and support whatever strange and wacky networked system you
are developing! Currently it supports mocking REST servers, REST clients,
WebSockets, and Kafka producers

## Requirements

There's a couple of requirements you need for this one.

* Docker (`kafka` mode only)
* `Python3`
  * `docker`
  * `Flask`
  * `kafka-python-ng`
  * `loguru`
  * `websockets`

You can install all of these into your environment using the following:

```bash
~$ python3 -m pip install -r requirements.txt
```

If you are using Nix, there is a shell environment available under the
`nix-env` directory.

## Running
To run this, run the `main.py` program, provide what mode you would like to
run, and a configuration file for that mode.

```bash
~$ python3 ./main.py rest_server ./examples/copnfigs/example_rest_server.json
~$ # or
~$ python3 ./main.py rest_client ./examples/copnfigs/example_rest_client.json
~$ # or
~$ python3 ./main.py transmit ./examples/copnfigs/example_transmit.json
~$ # or
~$ python3 ./main.py kafka ./examples/copnfigs/example_kafka.json
```

## Payload Examples
Find below some documentation about the JSON payloads for each of the supported
modes of the application.

### REST Server Mode
Static mode is supposed to mock up a REST server that you would like to
communicate with, and the config file reflects that.

```json
{
  "get": [
    {
      "route": "/example",
      "code": 200,
      "params": ["id"],
      "file": "examples/payloads/payload2.json"
    }
  ],
  "put": [
    {
      "route": "/example",
      "code": 200,
      "params": ["id"],
      "file": "examples/payload1.json"
    }
  ],
  "post": [
    {
      "route": "/test",
      "code": 200,
      "params": [],
      "file": "examples/payload4.json"
    }
  ],
  "delete": [
  ]
}
```

The file has three lists inside of it, `get`, `put`, `post`, and `delete`.
Within each of those lists are simple entries defining the `route` of the
request, the response code, and the file that should be replied with. You can
transmit whatever files you would like. They could be JSON, plaintext, binary,
images, etc. `file` can also be an empty string if the response code is all
that matters.

As should be clear, routes under each method list will only be triggered when
that method is used. If you have a route that supports `GET` and `POST`
methods, you need to have two entries in your config file, one under the `get`
list and one under the `post` list.

You can also specify URL parameters associated with the request using the
`params` list. Note that you cant specify specific values for each parameter
(yet), and so the program will simply match routes that contain the parameters.
You need to have all of the parameters matching for a request to be matched. If
you submit a request with `id` and `profileName` fields, but the config only
matches for `id`, then it will not match a route.

### REST Client Mode

Funny enough, this will act as a REST client, hitting whatever REST endpoints
you want. Here's an example config.

```json
{
  "url": "http://localhost:5000",
  "requests": [
    {
      "method": "get",
      "route": "/index",
      "params": [],
      "delay": 2,
      "repeat": 1
    },
    {
      "method": "post",
      "route": "/files",
      "params": {
        "file": "examples/payloads/payload1.json"
      },
      "delay": 1,
      "repeat": 0
    }
  ]
}
```

Its similar to other sequence modes, though with the added features of
`method`, `route`, and `params` fields. `methods` and `route` are pretty
self-explanatory, but the fun thing comes from the `params` fields, which
includes parameters that influence the request parameters. Right now, the only
supported parameter is `file` (which adds a file to the request), but feel free
to add more functionality!


### Transmit Mode

This mode is supposed to mock a server sending a message to your service over
"lower level" protocols. Right now the only supported mode is using WebSockets,
but the general principle applies to things like TCP/UDP sockets.

```json
{
  "transport": "websocket",
  "port": 55028,
  "payloads": [
    {
      "payload": "examples/payloads/payload1.json",
      "delay": 5,
      "repeat": 10
    },
    {
      "payload": "examples/payloads/payload2.json",
      "delay": 5,
      "repeat": 10
    }
  ]
}
```

The config file for this mode is much smaller. This is supposed to represent a
single kind of interaction with a remote server. For now, the only supported
transports WebSockets. It should be easy to add support for TCP, but that
sounds like effort right now... If we need to implement UDP too, we can, but
I chose not to add a `host` field that the program would need to reach out to
itself.

> [!IMPORTANT]
> *The program expects you to reach out to it!* You need to initiate the
> connection. From then on, you can receive to your hearts content all of the
> content you want.

### Kafka Mode
This mode mimics sending and receiving messages over various Kafka topics.

```json
{
  "produce": [
    {
      "topic": "commands",
      "payload": "examples/payloads/payload1.json",
      "delay": 5,
      "repeat": 10
    },
    {
      "topic": "telemetry",
      "payload": "examples/payloads/payload2.json",
      "delay": 5,
      "repeat": 10
    }
  ],
  "consume": [
    "commands",
    "telemetry"
  ]
}
```

This payload is pretty similar to the [Transmit Mode](<README#Transmit Mode>)
payload, with a few Kafka-specific features.

Firstly, it's broken up into two different sections: the `produce` section and
the `consume` section. The `produce` section defines messages that need to be
sent over specific topics at a certain rate. The same as how the WebSocket
stuff is defined, just with an added `topic` field.

The `consume` section is just a list of topics that you would like the system
to watch for. The program spawns a second process to watch for new messages on
topics, so you can watch and transmit messages to topics without issue. The
goal for this is to just see and validate the messages your service is
transmitting to Kafka.

#### Deploying Kafka

> [!NOTE]
> This is only if you want to use an isolated testing instance of Kafka.
> Hoaster works just fine with a real Kafka deployment, just make sure you
> don't break anything with your shenanigans 😁

The easiest way is to let the script handle the deployment itself. It will
spawn a Docker container of Kafka, and forward the port to your local system
without user interaction. If that's not what you want, you can also deploy an
instance locally, which you can do following
[these](https://kafka.apache.org/quickstart) instructions.

> [!IMPORTANT]
> *The program expects you to be connected to the Kafka instance during
> transmission!* It will prompt you to hit enter before it starts running,
> but if you rely on the program for deploying Kafka, you will need to start your
> application after the container is up and running.
