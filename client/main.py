import argparse
import json
import zmq
import time

_state = "unready" 

def start(): 
    global _state
    if _state == "ready":
        return "Already in ready state"

    else:
        _state = "ready"
        return "Ready to receive computation"
        
def stop(): 
    global _state
    if _state == "unready":
        return "Already in unready state"

    else:
        _state = "unready"
        return "Computation stopped"

def terminate():
    global _state
    _state = terminate
    return "Client terminating"

def ping():
    global _state
    if _state == "ready":
        timestamp = time.time()
        msg = "Current timestamp:", timestamp
        return msg
        
    else:
        return "Not in ready state"

def calculate(x, msg):
    global _state
    if _state == "ready":
        if x < 10 and len(msg) < 50:
            time.sleep(x)
            return msg
        elif x >= 10 or len(msg) >= 50:
            return "Computation too big"
            
    else:
        return "Not in ready state"


def client(ip="0.0.0.0", portin=5551, portout=5552):
    # ZMQ connection
    url = "tcp://{}:{}".format(ip, portin)
    print("Going to bind to: {}".format(url))
    ctx = zmq.Context()
    socketin = ctx.socket(zmq.PULL)
    socketin.bind(url)  # client creates ZeroMQ socket for incoming messages

    url = "tcp://{}:{}".format(ip, portout)
    print("Going to bind to: {}".format(url))
    ctx = zmq.Context()
    socketout = ctx.socket(zmq.PUSH)
    socketout.bind(url)  # client creates ZeroMQ socket for outgoing messages
    print("Client bound to: {}\nWaiting for data...".format(url))

    while _state != "terminate": # A try except approach would be better
        msg = socketin.recv_json()
        print("Received data: {}".format(msg))
        message = json.loads(msg)
        if message["command"] == "start":
            response = start()
        elif message["command"] == "stop":
            response = stop()
        elif message["command"] == "terminate":
            response = terminate()
            response_json = json.dumps(response)
            socketout.send_json(response_json)
            break
        elif message["command"] == "ping":
            response = ping()
        elif message["command"] == "calculate":
            response = calculate(message["time"], message["message"])
        else:
            response = "Input error"

        response_json = json.dumps(response)
        socketout.send_json(response_json)

    print("Client is terminating")
    socketin.close()
    socketout.close()

if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=argparse.SUPPRESS,
                        help="IP of (Docker) machine")
    parser.add_argument("--portin", default=argparse.SUPPRESS,
                        help="port in of (Docker) machine")
    parser.add_argument("--portout", default=argparse.SUPPRESS,
                        help="port out of (Docker) machine")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # call function and pass on command line arguments
    client(**vars(args))
