import asyncio
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import wraps

import grpc

import datapane_pb2 as pb
import datapane_pb2_grpc as pb_grpc

# -------------------------------------------------------------
# Business logic

# NOTE: I'm simply using global state and functions that mutate it.
# Further program design without more detailed requirements would be futile.

_ready = False
_process_pool_executor = None


class UnreadyException(Exception):
    pass


def _requires_ready(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _ready:
            raise UnreadyException(f'Calling {func.__name__} in "unready" state.')
        return func(*args, **kwargs)

    return wrapper


def start():
    global _process_pool_executor
    global _ready

    if not _process_pool_executor:
        _process_pool_executor = ProcessPoolExecutor()
    _ready = True


def stop():
    global _ready
    _ready = False


def terminate():
    stop()
    if _process_pool_executor:
        _process_pool_executor.shutdown()
    sys.exit(0)


@_requires_ready
def ping():
    return time.time()


@_requires_ready
def calculate(x: int, msg: str):
    time.sleep(x)
    print(msg)


# -------------------------------------------------------------
# grpc specific


class Main(pb_grpc.MainServicer):
    _unready_error = pb.Error(message='Make sure to "start" first')

    @staticmethod
    def _set_ready_and_calculate(ready, x, msg):
        """
        Global state workaround for multiprocessing - initialize _ready variable first.
        NOTE: use a class instead of global state?
        """
        global _ready
        _ready = ready
        return calculate(x, msg)

    def Start(self, request, context):
        start()
        return pb.Empty()

    def Stop(self, request, context):
        stop()
        return pb.Empty()

    def Terminate(self, request, context):
        # TODO: this is stupid - maybe queue termination in event loop and then return response...
        terminate()
        # return pb.Empty()

    def Ping(self, request, context):
        try:
            pong = ping()
        except UnreadyException:
            return pb.Pong(errors=[self._unready_error])
        return pb.Pong(timestamp=pong)

    async def Calculate(self, request: pb.CalculationInputs, context):
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                _process_pool_executor,
                self._set_ready_and_calculate,
                _ready,
                request.x,
                request.msg,
            )
        except UnreadyException:
            return pb.Empty(errors=[self._unready_error])
        return pb.Empty()


async def serve(host, port):
    server = grpc.aio.server()
    pb_grpc.add_MainServicer_to_server(Main(), server)
    listen_addr = "%s:%s" % (host, port)
    server.add_insecure_port(listen_addr)
    print("Starting server on %s" % listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    # env vars need to be explicitly specified for the server to work.
    host = os.environ["HOST"]
    port = os.environ["PORT"]
    asyncio.run(serve(host, port))
