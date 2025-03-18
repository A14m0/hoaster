# Holds stuff related to Kafka topics
import docker
import kafka
from loguru import logger as l
import multiprocessing as mp
import os
import socket
import time

# define our Kafka image and version
KAFKA_IMAGE = "apache/kafka:3.9.0"

def check_for_cluster():
    """Checks for a local Kafka cluster, deploying one if it cant find one"""

    # try to connect to the socket to see if the dummy Kafka exists
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', 9092)) != 0:
            # Kafka container is not running, spin one up
            l.warning("Kafka not found, spinning up a container")
            client = docker.from_env()

            try:
                client.images.get(KAFKA_IMAGE)
            except:
                l.warning("Kafka image not found, pulling...")
                client.images.pull(KAFKA_IMAGE)

            # now spool it up
            client.containers.run(KAFKA_IMAGE, detach=True, ports={"9092/tcp": 9092})
            l.info("Kafka container started, waiting for startup to finish...")
            time.sleep(15)
        else:
            l.info("Found local Kafka instance")


def watch_topic(*topics: str):
    """Watches Kafka topics for messages and prints them to the terminal"""

    r = []
    for v in topics:
        r.append(str(v))

    l.info(f"Watcher started with topics: {r}")

    # first create a client
    client = kafka.KafkaConsumer(*topics)

    # loop forever (we get killed at the end of the process,
    #               so we can afford to be less graceful :D)
    while True:
        for message in client:
            # parse our message
            key = None
            if message.key != None:
                key = message.key.decode()

            value = None
            if message.value != None:
                value = message.value.decode()

            # print the message to the console
            l.info(f"Watcher: Got Kafka message: topic='{message.topic}' key='{key}' value='{value}'")

        time.sleep(1)


def run_kafka(config: dict, producer: kafka.KafkaProducer):
    # keep track of some state
    STATE = {
        'index': 0,
        'repeat': 0
    }

    # spawn a new process for each consumer topic we want to watch
    p = mp.Process(target=watch_topic, args=(config["consume"]))
    p.start()
    l.info("Started topic watcher")

    l.info("Producer: Beginning Kafka transmissions")
    # loop until we are done
    while STATE['index'] < len(config['produce']):

        # delay for some amount of time
        l.debug("Producer: Sleeping...")
        time.sleep(config['produce'][STATE['index']]['delay'])

        # read our payload
        l.debug("Producer: Reading payload...")
        payload = config['produce'][STATE['index']]['payload']
        if not os.path.exists(payload):
            l.error(f"Producer: Payload path '{payload}' doesn't exist")
            exit(2)

        # read the data and transmit
        with open(payload, 'rb') as f:
            producer.send(config["produce"][STATE['index']]["topic"],f.read())
            producer.flush()
        l.info("Producer: Transmitted payload")

        # update our state
        if STATE['repeat'] >= config['produce'][STATE['index']]['repeat']:
            STATE['index'] += 1
            STATE['repeat'] = 0
        else:
            STATE['repeat'] += 1

        l.debug(f"Producer: Current state: {STATE}")

    # we're done, bail
    l.warning(f"Producer: Hit end of available payloads in config (count: {len(config['produce'])}). Halting...")
    p.kill()
    p.join()
    exit(0)


def kafka_main(config):
    """Main function for handling Kafka topics"""

    # first make sure the cluster is running
    check_for_cluster()

    # make sure the user is connected to the kafka instance
    # and is ready to receive
    input("""'Kafka is up and running, but before I continue, are you connected and ready to receive messages?
As soon as you hit enter, I'm going to start broadcasting messages on the topics in my config file.
It's not my fault if you're not ready for them!'
    - Hoaster

    Press enter when ready...""")

    # now set up a Kafka producer
    producer = kafka.KafkaProducer(bootstrap_servers="localhost:9092",acks="all") # should connect to the local Kafka instance
    if not producer.bootstrap_connected():
        l.error("Producer failed to connect to server...")
        return
    input()

    # now iterate through the config file to send messages
    run_kafka(config, producer)
