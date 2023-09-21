import argparse
import logging
import sys
import traceback
from concurrent import futures

import grpc

from generated import image_pb2_grpc
from grpc_handler import ImageHandler


class Server:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.arguments = self.args_parser()
 
    def args_parser(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--host", help = "Host Server")
        self.parser.add_argument("--port", help = "Host Server Port")
        args = self.parser.parse_args()
        return args

    def run(self):
        if self.arguments.host and self.arguments.port:
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            image_pb2_grpc.add_NLImageServiceServicer_to_server(ImageHandler(), server)
            server.add_insecure_port(f'{self.arguments.host}:{self.arguments.port}')
            server.start()
            server.wait_for_termination()
        else:
            self.parser.print_help()

if __name__ == '__main__':
    server = Server()
    try:
        server.run()
    except Exception as e:
        server.parser.print_help()
        logging.error(f'Error - {e}')
        traceback.print_exception(*sys.exc_info())
