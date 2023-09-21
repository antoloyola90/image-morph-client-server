import argparse
import base64
from io import BytesIO

import cv2
import grpc
from PIL import Image, ImageStat

from generated import image_pb2, image_pb2_grpc


class ImageServiceClient(object):

    def __init__(self):
        """Initializer. 
           Creates a gRPC channel for connecting to the server.
           Adds the channel to the generated client stub.
           Sets up the image so that its ready for operations. 
        Arguments:
            None.  
        Returns:
            None.
        """
        self.arguments = self.args_parser()

        options = [] #[('grpc.max_receive_message_length', 100 * 1024 * 1024)]
        self.channel = grpc.insecure_channel(f'{self.arguments.host}:{self.arguments.port}', options = options)
        self.stub = image_pb2_grpc.NLImageServiceStub(self.channel)

        self.nl_image = self.make_nlimage(self.arguments.input)
        self.output_filename = self.arguments.output
        self.do_actions()

    def args_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", help = "Host Server")
        parser.add_argument("--port", help = "Host Server Port")
        parser.add_argument("--input", help = "Input File Location")
        parser.add_argument("--output", help = "Output File Location")
        parser.add_argument("--rotate", help = "Rotate needs arg (NONE, NINETY_DEG, ONE_EIGHTY_DEG, TWO_SEVENTY_DEG)")
        parser.add_argument("--mean", help = "Mean Filter", action="store_true")
        args = parser.parse_args()
        return args

    def do_actions(self):
        if 'rotate' in self.arguments and self.arguments.rotate is not None:
            self.rotate_image(self.arguments.rotate)
        if 'mean' in self.arguments and self.arguments.mean:
            self.mean_filter()
        self.write_image()

    def make_nlimage(self, filename):
        image = open(filename, 'rb')
        image_read = image.read()
        pil_image = Image.open(BytesIO(image_read))
        width, height = pil_image.size
        color = self.is_color_image(pil_image)
        image_64_encode = base64.b64encode(image_read)

        nlimage = image_pb2.NLImage(
            data = image_64_encode,
            color = color,
            width = width,
            height = height
        )
        return nlimage

    def is_color_image(self, pil_image):
        im = pil_image.convert("RGB")
        stat = ImageStat.Stat(im)
        if sum(stat.sum)/3 == stat.sum[0]: #check the avg with any element value
            return False #if grayscale
        else:
            return True #else its colour

    def write_image(self):
        img_b64 = base64.b64decode(self.nl_image.data)
        fh = open(self.output_filename, "wb")
        fh.write(img_b64)
        fh.close()

    def rotate_image(self, rotation):
        """Client side implementation for the calling of Rotate Image
           on the server.
        Arguments:
            rotation - the relevant opencv operation. Lookup done through 
            the enum NLImageRotateRequest_Rotation_enum_conversion at
            constants.py
        Returns:
            None.
        """
        try:
            request = image_pb2.NLImageRotateRequest(
                image = self.nl_image,
                rotation = image_pb2.NLImageRotateRequest.Rotation.Value(rotation)
            )
            response = self.stub.RotateImage(request)
            # print('RotateImage Response...')
            # print(rotation, response.width, response.height, response.color)
            self.nl_image = response
        except grpc.RpcError as err:
            print(err.details()) #pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value)) #pylint: disable=no-member
    
    def mean_filter(self):
        """Client side implementation for the calling of the Mean Filter
           on the server.
        Arguments:
            None
        Returns:
            None.
        """
        try:
            response = self.stub.MeanFilter(self.nl_image)
            # print('MeanFilter Response...')
            # print(response.width, response.height, response.color)
            self.nl_image = response
        except grpc.RpcError as err:
            print(err.details()) #pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value)) #pylint: disable=no-member

if __name__ == '__main__':
    ImageServiceClient()
