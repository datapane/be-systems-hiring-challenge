# -*- coding: utf-8 -*-

import thriftpy2

from thriftpy2.protocol import TCyBinaryProtocolFactory
from thriftpy2.transport import TCyBufferedTransportFactory
from thriftpy2.rpc import make_server
import time
import uuid


state = "unready"
server=None
calc_thrift = thriftpy2.load("masterworker.thrift", module_name="calc_thrift")


class Dispatcher(object):
    # Control commands
    #
    # start() - move to ready state to start accepting data commands
    # stop() - move to unready state and stop accepting data commands
    # terminate() - immediately stop and exit cleanly, preferably cleaning up any resources first
    def state(self, command):
        """
           state function controls the state of the over all worker.

           :param command:  A string which can be of following of these ["ready", "unready","terminate"]

           :return: return string as "SUCCESS" when state is changed successfully else returns "UNKNOWN STATE"
        """

        global state
        global server
        print("command = %s "% (state))

        if (command == "ready"):
            state="ready"
            return state+"= SUCCESS"

        elif (command == "unready"):
            state="unready"
            return "SUCCESS"

        elif (command == "terminate"):
            state="terminate"
            server.close()
            return "SUCCESS"

        else:
            return "UNKNOWN STATE"

    def ping(self):
        """
            ping function is ping pong function
            returns timestamp only if when the client is in the ready state, else return 0

            :param :  No param required

            :return: the current unix timestamp
        """
        global state

        if(state=="ready"):
            unix_time=int(time.time())
            return unix_time

        elif(state=="unready"):
            print("ping function state is %s " % (state))
            return 0

    #
    def calculate(self, x, msg):
        """
           calculate function simulates a long - running computation that takes x seconds to run and prints msg upon completion

           :param x:  x is of data type float, is the time for which function sleeps
           :param msg: msg of data type string

           :return: same message which was given in input along with unique id
        """
        global state
        if (state == "ready"):
            time.sleep(x)
            return "{id:"+str(uuid.uuid1())+",message\":"+msg+"}"

        elif (state == "unready"):
            return "{error: \"State is not ready\"}"


def main():
    global server
    server = make_server(calc_thrift.Calculator, Dispatcher(),
                         "0.0.0.0", 6000,
                         proto_factory=TCyBinaryProtocolFactory(),
                         trans_factory=TCyBufferedTransportFactory(),client_timeout=None)

    print("serving...")
    server.serve()
    global state
    state = "unready"


if __name__ == '__main__':
    main()