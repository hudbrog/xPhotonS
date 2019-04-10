import struct
from matplotlib import pyplot as plt
import numpy as np

#Normal Exposure(s):12
#Off Time(s):1
#Bottom Exposure(s):80
#Bottom Layers:6
#Z Lift Distance(mm):4
#Z Lift Speed(mm/s):3
#Z Retract Speed(mm/s):3
#thickness: 0.05
#XYPixel: 47.25
#total layers: 345
#volume: 0.14ml

# 6 - header
# 8d - XY Pixel Size
# 8d - Layer
# 8d - normal exposure
# 8d - off time
# 8d - bottom exposure
# 4i - number of bottom layers
# 8d - Z Lift distance
# 8d - Z lift speed (??)
# 8d - Z Retract speed
# 8d - volume
# 4x4i - some ints ???

header_info = [
    "XY Pixel Size",
    "Layer thickness",
    "Normal Exposure(s)",
    "Off Time(s)",
    "Bottom Exposure(s)",
    "Bottom Layers",
    "Z Lift Distance(mm)",
    "Z Lift Speed(mm/s)",
    "Z Retract Speed(mm/s)",
    "Total volume(ml)",
]

layers_header_info = [
    "Total number of layers",
    # doesn't depend on pixel size
    # does depend on screen resolution
    "????(depends on layer thikness or count)",
    "????",
    "????",
    "Screen Width Resolution",
    "Screen Length Resolution",
    "??",
    "??",
    "??",
    "??"    
]

layers2_header_info = [
    # doesn't depend on pixel size
    # does depend on screen resolution
    "????(depends on layer thikness or count)",
    "????",
    "????",
    "Screen Width Resolution",
    "Screen Length Resolution",
    "??",
    "??",
    "??",
    "??",
]

def print_header(header_desc, data):
    for k, v in enumerate(header_desc):
        print("{}: {}".format(v, data[k]))

format_string = ">5di4diiii"
with open("c.photons", "rb") as binary_file:
    # 6 + 8 + 8 + 8 == 30
    binary_file.seek(6)
    data = binary_file.read(struct.calcsize(format_string))
    print("Structure size: {} ({:02X})".format(struct.calcsize(format_string), struct.calcsize(format_string)))
    tuple_of_data = struct.unpack(format_string, data)
    print_header(header_info, tuple_of_data)
    w, h = tuple_of_data[10], tuple_of_data[12]
    np_image = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(tuple_of_data[12]):
        img_format = "<{}h".format(tuple_of_data[10])
        data = binary_file.read(struct.calcsize(img_format))
        img_line = struct.unpack(img_format, data)
        for k, j in enumerate(img_line):
            np_image[i][k][0] = ((j >> 11) & 0x1F) << 3
            np_image[i][k][1] = ((j >> 5)  & 0x3F) << 2
            np_image[i][k][2] = ((j >> 0)  & 0x1F) << 3
    # plt.imshow(np_image, interpolation='nearest')
    # for test.photons: pos = 0x12662, next around 0x19fa7, next 0x2196f (diff 79C8), next 0x2937c (diff 7A0D), next 0x30E3A (7ABE), next 0x3881E (79E4), next 0x40012 (77F4)
    # for c.photons: pos = 0x12662, next around 0x1994A, next 0x20D9F
    # 29456 bytes per layer
    # 32 byte header
    # at some point layer header becomes 28 bytes
    # 29424 for layer data
    print(binary_file.tell())
    # layers_header_format = '>IIIIIIHHHH'
    layers_header_format = '>IIIIIIHHHH'
    data = binary_file.read(struct.calcsize(layers_header_format))
    print(struct.calcsize(layers_header_format))
    tuple_of_data = struct.unpack(layers_header_format, data)
    print_header(layers_header_info, tuple_of_data)
    binary_file.seek(0x1994A, 0)
    layers_header_format = '>IIIIIHHHH'
    data = binary_file.read(struct.calcsize(layers_header_format))
    print(struct.calcsize(layers_header_format))
    tuple_of_data = struct.unpack(layers_header_format, data)
    print_header(layers2_header_info, tuple_of_data)
    binary_file.seek(0x20D9F, 0)
    layers_header_format = '>IIIIIHHHH'
    data = binary_file.read(struct.calcsize(layers_header_format))
    print(struct.calcsize(layers_header_format))
    tuple_of_data = struct.unpack(layers_header_format, data)
    print_header(layers2_header_info, tuple_of_data)
    # for i in range(tuple_of_data[5]):
    #     img_format = "<{}h".format(tuple_of_data[4])
    #     data = binary_file.read(struct.calcsize(img_format))
    #     img_line = struct.unpack(img_format, data)
    #     print(img_line)

