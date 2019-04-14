import struct
# from matplotlib import pyplot as plt
# import numpy as np

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
        if k >= len(data):
            return
        print("{}: {}".format(v, data[k]))

def read_layer_data(fh):
    buf = []
    temp = ''
    last_sym = 1
    while 1:
        temp = fh.read(1)
        # if not temp:
        #     fh.seek(-3, 1)
        #     return buf
        if (temp[0] == 0x0E or temp[0] == 0x0F or temp[0] == 0x0) and last_sym == 0x0:
            fh.seek(-2, 1)
            del buf[-1]
            return buf
        else:
            buf.extend(temp)
            last_sym = temp[0]

def read_layer(fh):
    layers_header_format = '>IIIII IHH'
    data = fh.read(struct.calcsize(layers_header_format))
    last_pos = binary_file.tell()
    tuple_of_data = struct.unpack(layers_header_format, data)
    print_header(layers2_header_info, tuple_of_data)
    header_data_len = (tuple_of_data[5]>>3)-4
    layer_data = fh.read(header_data_len)
    # layer_data = read_layer_data(fh)
    # print(":".join("{:02x}".format(c) for c in data[20:24]))
    print("Current pos: {}, last pos: {}, data_len: {} -- {} -- {}\n-----".format(hex(binary_file.tell()), hex(last_pos), hex(len(layer_data)), len(layer_data), header_data_len))

format_string = ">5di4diiii"
with open("zzz2.photons", "rb") as binary_file:
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
    # for c.photons: pos = 0x12662, next around 0x19C16, next 0x211C6
    # 29456 bytes per layer
    # 32 byte header
    # at some point layer header becomes 28 bytes
    # 29424 for layer data
    # print(binary_file.tell())
    # layers_header_format = '>IIIIIIHHHH'
    layers_header_format = '>I'
    data = binary_file.read(struct.calcsize(layers_header_format))
    # print(struct.calcsize(layers_header_format))
    tuple_of_data = struct.unpack(layers_header_format, data)
    print("-----------------------------\nNUmber of layers: {}\n-------------------\n".format(tuple_of_data[0]))
    for i in range(tuple_of_data[0]):
        read_layer(binary_file)
