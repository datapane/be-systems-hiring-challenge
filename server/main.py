import argparse
import json
import zmq
import time
import asyncio

def show_guide():
    print("Server side of the bundle")
    print("Accepted commands")
    print(" start: move to ready state to start accepting data commands")
    print(" stop: move to unready state and stop accepting data commands")
    print(" terminate: stop and terminate the client, exit cleanly")
    print(" terminate server: stop both client and server")
    print(" help: show this guide")
    print(" ping: ask for current timestamp ")
    print(" calculate [int] [string]: simulate a computation that takes [int] seconds and returns [string]")

def server(ip="client", portout=5551, portin=5552):
    # ZMQ connection
    url = "tcp://{}:{}".format(ip, portout)
    print("Going to connect to: {}".format(url))
    ctx = zmq.Context()
    socketout = ctx.socket(zmq.PUSH)
    socketout.connect(url)  # server connects to client for outgoing messages
    url = "tcp://{}:{}".format(ip, portin)
    print("Going to connect to: {}".format(url))
    ctx = zmq.Context()
    socketin = ctx.socket(zmq.PULL)
    socketin.connect(url)  # server connects to client for incoming messages
    print("Pub connected to: {}\nSending data...".format(url))
    print()
    show_guide()
    print()

    i = 0
    while True:
        command = input("Enter the command: ").split(" ") # Convert input to JSON, should be called asynchronus in order to not wait the response of the client

        if command[0] == "help":
            show_guide()
        else:
            if command[0] == "calculate":
                msg = {
                    "command": command[0],
                    "time": int(command[1]),
                    "message": command[2]
                }
            else:
                msg = {
                    "command": command[0]
                }
            msg_json = json.dumps(msg)
            socketout.send_json(msg_json)                   # Send JSON and wait for the response
            print("Send data: {}".format(msg_json))
            msg = socketin.recv_json()
            print("Client response: ", msg)
            if (command[0] == "terminate") and len(command) == 2: 
                if command[1] == "server":  
                    socketin.close()
                    socketout.close()
                    return 0 
            i += 1



if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=argparse.SUPPRESS,
                        help="IP of (Docker) machine")
    parser.add_argument("--portout", default=argparse.SUPPRESS,
                        help="Port out of (Docker) machine")
    parser.add_argument("--portin", default=argparse.SUPPRESS,
                        help="Port in of (Docker) machine")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # call function and pass on command line arguments
    server(**vars(args))
