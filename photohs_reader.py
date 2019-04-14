import struct
from PIL.ImageQt import ImageQt
import PIL
import numpy as np

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

header_format_string = ">5di4diiii"
layers_header_format = '>IIIII IHH'
header_signature = b'\x00\x00\x00\x02\x00\x31'
rle = [1, 1, 65, 65, 33, 33, 97, 97, 17, 17, 81, 81, 49, 49, 113, 113, 9, 9, 73, 73, 41, 41, 105, 105, 25, 25, 89, 89, 57, 57, 121, 121, 5, 5, 69, 69, 37, 37, 101, 101, 21, 21, 85, 85, 53, 53, 117, 117, 13, 13, 77, 77, 45, 45, 109, 109, 29, 29, 93, 93, 61, 61, 125, 125, 3, 3, 67, 67, 35, 35, 99, 99, 19, 19, 83, 83, 51, 51, 115, 115, 11, 11, 75, 75, 43, 43, 107, 107, 27, 27, 91, 91, 59, 59, 123, 123, 7, 7, 71, 71, 39, 39, 103, 103, 23, 23, 87, 87, 55, 55, 119, 119, 15, 15, 79, 79, 47, 47, 111, 111, 31, 31, 95, 95, 63, 63, 127, 127, 2, 2, 66, 66, 34, 34, 98, 98, 18, 18, 82, 82, 50, 50, 114, 114, 10, 10, 74, 74, 42, 42, 106, 106, 26, 26, 90, 90, 58, 58, 122, 122, 6, 6, 70, 70, 38, 38, 102, 102, 22, 22, 86, 86, 54, 54, 118, 118, 14, 14, 78, 78, 46, 46, 110, 110, 30, 30, 94, 94, 62, 62, 126, 126, 4, 4, 68, 68, 36, 36, 100, 100, 20, 20, 84, 84, 52, 52, 116, 116, 12, 12, 76, 76, 44, 44, 108, 108, 28, 28, 92, 92, 60, 60, 124, 124, 8, 8, 72, 72, 40, 40, 104, 104, 24, 24, 88, 88, 56, 56, 120, 120, 16, 16, 80, 80, 48, 48, 112, 112, 32, 32, 96, 96, 64, 64, 128, 128]

class PhotonSReader():
    def __init__(self, filename):
        self.filename = filename
        self.header = tuple()
        self.num_layers = 0
        self.preview_w = 0
        self.preview_h = 0
        self.layer_offsets = list()
        self.preview_image = None

    def format_bytes(self, data):
        return ":".join("{:02x}".format(c) for c in data)
    
    def read_data(self):
        with open(self.filename, "rb") as binary_file:
            # read and check file signature
            signature = binary_file.read(6)
            if signature != header_signature:
                raise Exception('File has unknown signature. First 6 bytes are "{}" instead of "{}"'.format(self.format_bytes(signature), self.format_bytes(header_signature)))

            # read header
            data = binary_file.read(struct.calcsize(header_format_string))
            self.header = struct.unpack(header_format_string, data)

            # read preview image
            self.preview_w, self.preview_h = self.header[10], self.header[12]
            img_format = "<{}h".format(self.preview_w*self.preview_h)
            data = binary_file.read(struct.calcsize(img_format))
            img = struct.unpack(img_format, data)
            self.preview_image = img

            # read number of layers
            num_layers_header_format = '>I'
            data = binary_file.read(struct.calcsize(num_layers_header_format))
            tuple_of_data = struct.unpack(num_layers_header_format, data)
            self.num_layers = tuple_of_data[0]
            self.layer_offsets = [None]*self.num_layers

            # read layers
            for i in range(tuple_of_data[0]):
                self.layer_offsets[i] = binary_file.tell()
                data = binary_file.read(struct.calcsize(layers_header_format))
                tuple_of_data = struct.unpack(layers_header_format, data)
                header_data_len = (tuple_of_data[5]>>3)-4
                binary_file.seek(header_data_len, 1)

    def get_preview_qtimage(self):
        img_data = [b'\0'] * self.preview_w*self.preview_h*3
        for i in range(len(self.preview_image)):
            j = self.preview_image[i]
            img_data[i*3+0] = ((j >> 11) & 0x1F) << 3
            img_data[i*3+1] = ((j >> 5)  & 0x3F) << 2
            img_data[i*3+2] = ((j >> 0)  & 0x1F) << 3
        img = PIL.Image.frombytes("RGB", [self.preview_w, self.preview_h], bytes(img_data))
        return ImageQt(img)
        
    def get_rle_len(self, inp):
        i = 0; j = 7
        num = inp&0xFE
        while i<j:
            # Get the bits from both end iteratively
            if (num>>i)&1 != (num>>j)&1:
                # if the bits don't match swap them by creating a bit mask
                # and XOR it with the number 
                mask = (1<<i) | (1<<j)
                num ^= mask
            i += 1; j -= 1
        return num+1

    def get_layer_raw_data(self, layerNum):
        if layerNum > self.num_layers:
            raise Exception('Invalid layer requested: {} (number of layers loaded: {}'.format(layerNum, self.num_layers))
        with open(self.filename, "rb") as binary_file:
            binary_file.seek(self.layer_offsets[layerNum])
            data = binary_file.read(struct.calcsize(layers_header_format))
            tuple_of_data = struct.unpack(layers_header_format, data)
            header_data_len = (tuple_of_data[5]>>3)-4
            layerData = binary_file.read(header_data_len)
        return (tuple_of_data, layerData)

    def get_layer_decoded_data(self, layerNum):
        tuple_of_data, layerData = self.get_layer_raw_data(layerNum)
        layer_h = tuple_of_data[3]
        layer_w = tuple_of_data[4]
        # decodedLayer = [None]*layer_w*layer_h
        # idx = 0
        # print("W: {}, H: {}, data_len: {}".format(layer_w, layer_h, len(layerData)))
        # for i in range(len(layerData)):
        #     num = rle[layerData[i]]
        #     val = (layerData[i] & 0x01) * 255
        #     for _ in range(num):
        #         decodedLayer[idx] = val
        #         idx+=1
        # # omg.. they actually have a bug, loosing last byte in most cases
        # while idx < layer_w*layer_h:
        #     decodedLayer[idx] = 0
        #     idx+=1

        decodedLayer = list()
        for i in range(len(layerData)):
            num = rle[layerData[i]]
            val = (layerData[i] & 0x01) * 255
            decodedLayer.extend([val]*num)
        decodedLayer.extend([0]*(layer_w*layer_h-len(decodedLayer)))

        return (tuple_of_data, decodedLayer)

    def get_layer_qtimage(self, layerNum):
        header, data = self.get_layer_decoded_data(layerNum)
        img = PIL.Image.frombytes("L", [header[3], header[4]], bytes(data))
        # img.show()
        return ImageQt(img)

