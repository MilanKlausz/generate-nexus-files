import json
import sys

import numpy as np

CHILDREN = "children"
CONFIG = "config"
NAME = "name"
VALUES = "values"

X_PIXEL_OFFSET = "x_pixel_offset"
Y_PIXEL_OFFSET = "y_pixel_offset"
Z_PIXEL_OFFSET = "z_pixel_offset"
DETECTOR_NUMBER = "detector_number"


def retrieve_data_from_json(data, data_name, data_array):
    for item in data[CHILDREN]:
        if CONFIG in item and NAME in item[CONFIG]:
            if item[CONFIG][NAME] == data_name:
                for val in item[CONFIG][VALUES]:
                    data_array.append(val)
        if CHILDREN in item:
            retrieve_data_from_json(item, data_name, data_array)


class BaseDetectorGeometry:

    def __init__(self, file_name, debug = False, fatal = True):
        self.debug = debug  # enable debug print
        self.fatal = fatal  # terminate on first error
        data: dict
        with open(file_name, 'r') as json_file:
            data = json.load(json_file)

        x, y, z, pixel_ids = [], [], [], []
        retrieve_data_from_json(data, X_PIXEL_OFFSET, x)
        retrieve_data_from_json(data, Y_PIXEL_OFFSET, y)
        retrieve_data_from_json(data, Z_PIXEL_OFFSET, z)
        retrieve_data_from_json(data, DETECTOR_NUMBER, pixel_ids)
        self.id_dict = dict(zip(pixel_ids, zip(x, y, z)))

    # pixel to coord
    def p2c(self, pixel):
        return np.asarray(self.id_dict[pixel])

    # return vector from two pixels
    def p2v(self, pix1, pix2):
        c1 = self.p2c(pix1)
        c2 = self.p2c(pix2)
        return c2 - c1

    # distance between two pixels
    def dist(self, pix1, pix2):
        c1 = self.p2c(pix1)
        c2 = self.p2c(pix2)
        return np.linalg.norm(c2 - c1)

    # Angle in radians
    def angle(self, v1, v2):
        uv1 = v1 / np.linalg.norm(v1)
        uv2 = v2 / np.linalg.norm(v2)
        return np.arccos(np.dot(uv1, uv2))

    # radians to degrees
    def r2d(self, radians):
        return radians * 360.0 / (np.pi * 2)

    def mprint(self, str):
        if (self.debug):
            print(str)

    def expect(self, val, expect, precision):
        if abs(val - expect) > precision:
            print("value error: {} - {} ({}) > {}".format(val, expect, abs(val - expect), precision))
            if self.fatal:
                sys.exit(0)


if __name__ == '__main__':
    ag = BaseDetectorGeometry("AMOR_nexus_structure.json")