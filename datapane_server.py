import asyncio
import datetime
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import grpc

import datapane_pb2
import datapane_pb2_grpc

PROMPT_HELP = 'Available commands are: "start", "stop", "terminate", "ping", "calculate <x> <msg>".'
PROMPT = "[%i] >> "


class UnknownCommand(Exception):
    pass


def handle_command(prompt_idx, user_args, stub, tp_executor):
    def print_errors(prompt_idx, errors):
        errors_string = "\n".join([error.message for error in errors])
        print("[%i] Received errors\n%s" % (prompt_idx, errors_string))

    command_name = user_args[0]

    if command_name == "start":
        stub.Start(datapane_pb2.Empty())
        print("[%i] Started" % prompt_idx)
    elif command_name == "stop":
        stub.Stop(datapane_pb2.Empty())
        print("[%i] Stopped" % prompt_idx)
    elif command_name == "terminate":
        stub.Terminate(datapane_pb2.Empty())
        print("[%i] Terminated" % prompt_idx)
    elif command_name == "ping":
        response: datapane_pb2.Pong = stub.Ping(datapane_pb2.Empty())
        if response.errors:
            print_errors(prompt_idx, response.errors)
        else:
            print(
                '[%i] Ping response was "%s", that is - %s'
                % (
                    prompt_idx,
                    response.timestamp,
                    datetime.datetime.fromtimestamp(response.timestamp),
                )
            )
    elif command_name == "calculate":
        try:
            msg = user_args[2]
        except IndexError:
            msg = "helloworld"
            print('Using default "msg" value of "%s"' % msg)
        try:
            x = int(user_args[1])
        except IndexError:
            x = 4
            print('Using default "x" value of %i' % x)

        def calculate(prompt_idx, x, msg):
            response = stub.Calculate(datapane_pb2.CalculationInputs(x=x, msg=msg))
            if response.errors:
                print_errors(prompt_idx, response.errors)
            else:
                print("[%i] Calculation done, see client terminal" % prompt_idx)

        # NOTE: IO bound, hence - threads
        tp_executor.submit(calculate, prompt_idx, x, msg)
    else:
        raise UnknownCommand


def main():
    """
    Spagetti Pythonese!
    """

    host = os.environ["HOST"]
    port = os.environ["PORT"]
    server_addr = "%s:%s" % (host, port)
    print("Creating grpc channel to server on %s" % server_addr)
    with grpc.insecure_channel(
        server_addr
    ) as channel, ThreadPoolExecutor() as tp_executor:
        stub = datapane_pb2_grpc.MainStub(channel)

        display_help = True
        prompt_idx = 0

        while True:
            if display_help:
                print(PROMPT_HELP)
                display_help = False

            prompt_idx += 1

            try:
                user_args = input(PROMPT % prompt_idx).split(" ")
            except (EOFError, KeyboardInterrupt):
                print()
                print("Exiting.")
                sys.exit(0)

            try:
                handle_command(prompt_idx, user_args, stub, tp_executor)
            except UnknownCommand:
                print('No such command as "%s".' % user_args[0])
                display_help = True


if __name__ == "__main__":
    main()
