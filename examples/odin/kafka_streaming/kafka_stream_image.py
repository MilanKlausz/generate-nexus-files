from kafka import KafkaProducer
import os
from PIL import Image
import numpy as np
from streaming_data_types.area_detector_ADAr import serialise_ADAr
from streaming_data_types.logdata_f142 import serialise_f142
from datetime import datetime
import time

projection = 0
flat_field = 1
dark_field = 2
invalid = 3

if __name__ == '__main__':
    kafka_producer = KafkaProducer(bootstrap_servers='localhost:9092')
    idx = 150
    for i in range(1, 201):
        idx += 1
        nbr_str = str(i)
        nbr_zeros = 4 - len(nbr_str)
        first_zeros = '0' * nbr_zeros
        path_to_image = os.path.join('..', 'Lego1',
                                     f'tomo_{first_zeros}{nbr_str}.tif')
        image = Image.open(path_to_image)
        img_array = np.array(image)
        serialized_output = serialise_ADAr('image_source', idx, datetime.now(),
                                                          img_array)
        rotation_angle = serialise_f142(i, 'rotation_angle', time.time_ns())
        image_key = serialise_f142(projection, 'image_key', time.time_ns())
        kafka_producer.send('odin_topic', serialized_output)
        kafka_producer.send('odin_topic', rotation_angle)
        kafka_producer.send('odin_topic', image_key)
        time.sleep(0.1)

