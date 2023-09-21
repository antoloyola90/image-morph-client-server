import base64
import sys
import traceback

import cv2
import numpy

from generated import image_pb2, image_pb2_grpc
from constants import NLImageRotateRequest_Rotation_enum_conversion, MEAN_FILTER_GRID_SIZE

class ImageHandler(image_pb2_grpc.NLImageServiceServicer):

    def get_image_as_np(self, image):
        image_64_decode = base64.decodebytes(image)
        img_buff = numpy.frombuffer(image_64_decode, dtype=numpy.uint8)
        img_as_np = cv2.imdecode(img_buff, flags=1)
        return img_as_np

    def convert_to_nlimage(self, np_image, color):
        retval, buffer = cv2.imencode('.jpg', np_image)
        img_as_text = base64.b64encode(buffer)
        nl_image = image_pb2.NLImage(
            data = img_as_text,
            color = color,
            width = np_image.shape[1],
            height = np_image.shape[0]
        )
        return nl_image

    def RotateImage(self, request, context):
        """Server side implementation for Rotate Image.
        Arguments:
            request - contains the image + relevant data
            context - unused
        Returns:
            NLImage
        """
        def lookup_NLImageRotateRequest_Rotation(rotation_str):
            if (rotation_str in NLImageRotateRequest_Rotation_enum_conversion):
                return NLImageRotateRequest_Rotation_enum_conversion[rotation_str]
            return None

        try:
            operation_to_do = lookup_NLImageRotateRequest_Rotation(request.rotation)
            if operation_to_do is not None:
                img_as_np = self.get_image_as_np(request.image.data)
                image = cv2.rotate(img_as_np, operation_to_do)
                nl_image = self.convert_to_nlimage(image, request.image.color)
                return nl_image
            else:
                return request.image
        except Exception as e:
            traceback.print_exception(*sys.exc_info())

    def MeanFilter(self, request, context):
        """Server side implementation for the Mean Filter effect
           on an Image.
        Arguments:
            request - contains the image + relevant data
            context - unused
        Returns:
            NLImage
        """
        try:
            img_as_np = self.get_image_as_np(request.data)
            image = cv2.blur(img_as_np, MEAN_FILTER_GRID_SIZE) 
            nl_image = self.convert_to_nlimage(image, request.color)
            return nl_image
        except Exception as e:
            traceback.print_exception(*sys.exc_info())
