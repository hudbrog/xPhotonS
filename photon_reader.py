import struct
from PIL.ImageQt import ImageQt
import PIL
import numpy
import itertools

header_info = [
    "Format Version", #0
    "Bed X(mm)",      #1
    "Bed Y(mm)",      #2
    "Bed Z(mm)",      #3
    "???",
    "???",
    "???",
    "Layer Height(mm)", #7
    "Exposure Time(s)", #8
    "Bottom Time(s)",   #9
    "Off Time(s)",      #10
    "Bottom Layers",    #11
    "Resolution X",     #12
    "Resolution Y",     #13
    "PreviewOffset",    #14
    "LayersDataOffset", #15
    "Number Of Layers", #16
    "PreviewOffset2",   #17
    "Print time (s)",   #18
    "???",   
    "paramOffset",      #20
    "paramSize",        #21
    "AA Level",         #22
    "Exposure PWM",     #23
    "Bottom Exposure PWM",  #24
    "???",
    "???",
]

layer_header_info = [
    "Layer Z",
    "Exposure Time(s)",
    "Off Time(s)",
    "Data Address",
    "Data Size",
    "????",
    "????",
    "????",
    "????",
]

header_format_string = "<i3f3i4f3i9i2h"
preview_header_format = "<8i"
layers_header_format = '<fff2i4i'
header_signature = b'\x19\x00\xFD\x12'
rle = [1, 1, 65, 65, 33, 33, 97, 97, 17, 17, 81, 81, 49, 49, 113, 113, 9, 9, 73, 73, 41, 41, 105, 105, 25, 25, 89, 89, 57, 57, 121, 121, 5, 5, 69, 69, 37, 37, 101, 101, 21, 21, 85, 85, 53, 53, 117, 117, 13, 13, 77, 77, 45, 45, 109, 109, 29, 29, 93, 93, 61, 61, 125, 125, 3, 3, 67, 67, 35, 35, 99, 99, 19, 19, 83, 83, 51, 51, 115, 115, 11, 11, 75, 75, 43, 43, 107, 107, 27, 27, 91, 91, 59, 59, 123, 123, 7, 7, 71, 71, 39, 39, 103, 103, 23, 23, 87, 87, 55, 55, 119, 119, 15, 15, 79, 79, 47, 47, 111, 111, 31, 31, 95, 95, 63, 63, 127, 127, 2, 2, 66, 66, 34, 34, 98, 98, 18, 18, 82, 82, 50, 50, 114, 114, 10, 10, 74, 74, 42, 42, 106, 106, 26, 26, 90, 90, 58, 58, 122, 122, 6, 6, 70, 70, 38, 38, 102, 102, 22, 22, 86, 86, 54, 54, 118, 118, 14, 14, 78, 78, 46, 46, 110, 110, 30, 30, 94, 94, 62, 62, 126, 126, 4, 4, 68, 68, 36, 36, 100, 100, 20, 20, 84, 84, 52, 52, 116, 116, 12, 12, 76, 76, 44, 44, 108, 108, 28, 28, 92, 92, 60, 60, 124, 124, 8, 8, 72, 72, 40, 40, 104, 104, 24, 24, 88, 88, 56, 56, 120, 120, 16, 16, 80, 80, 48, 48, 112, 112, 32, 32, 96, 96, 64, 64, 128, 128]

class PhotonReader():
    def __init__(self, filename):
        self.filename = filename
        self.header = tuple()
        self.preview_header = tuple()
        self.num_layers = 0
        self.preview_w = 0
        self.preview_h = 0
        self.layer_offsets = list()
        self.layer_data = []
        self.layer_headers = []
        self.preview_image = [None]

    def format_bytes(self, data):
        return ":".join("{:02x}".format(c) for c in data)
    
    def read_data(self, with_decode=False):
        with open(self.filename, "rb") as binary_file:
            # read and check file signature
            signature = binary_file.read(4)
            if signature != header_signature:
                raise Exception('File has unknown signature. First 4 bytes are "{}" instead of "{}"'.format(self.format_bytes(signature), self.format_bytes(header_signature)))

            # read header
            data = binary_file.read(struct.calcsize(header_format_string))
            self.header = struct.unpack(header_format_string, data)
            self.num_layers = self.header[16]

            if self.header[0] != 1:
                raise Exception("Format v2 is not supported yet")

            # read preview image
            binary_file.seek(self.header[14], 0)
            data = binary_file.read(struct.calcsize(preview_header_format))
            self.preview_header = struct.unpack(preview_header_format, data)
            self.preview_w, self.preview_h = self.preview_header[0], self.preview_header[1]
            img_format = "<{}h".format(int(self.preview_header[3]/2))
            data = binary_file.read(struct.calcsize(img_format))
            img = struct.unpack(img_format, data)
            self.preview_image = img

            self.layer_offsets = [None]*self.num_layers
            self.layer_data = [None]*self.num_layers
            self.layer_headers = [None]*self.num_layers

            binary_file.seek(self.header[15], 0)

            for i in range(self.num_layers):
                self.layer_offsets[i] = binary_file.tell()
                data = binary_file.read(struct.calcsize(layers_header_format))
                self.layer_headers[i] = struct.unpack(layers_header_format, data)

            # read layers
            for i in range(self.num_layers):
                header_data_len = self.layer_headers[i][4]
                binary_file.seek(self.layer_headers[i][3])
                self.layer_data[i] = binary_file.read(header_data_len)

    def print_header(self):
        for k, v in enumerate(header_info):
            if k >= len(self.header):
                return
            print("{}: {}".format(v, self.header[k]))

    def print_layer_header(self, layer_header):
        for k, v in enumerate(layer_header_info):
            if k >= len(layer_header):
                return
            print("{}: {}".format(v, layer_header[k]))

    def get_preview_qtimage(self):
        img_data = numpy.zeros(self.preview_h*self.preview_w, numpy.uint32)
        i = 0
        idx = 0        
        data_len = len(self.preview_image)
        while i < data_len:
            j = self.preview_image[i]
            cR = ((j >> 11) & 0x1F) << 3
            cG = ((j >> 5)  & 0x3F) << 2
            cB = ((j >> 0)  & 0x1F) << 3
            val = (cR << 24) | (cG << 16) | ((cB & 0x001F) << 8) | 255
            num = 1
            if (j & 0x0020) == 0x0020:
                num += self.preview_image[i+1] & 0x0FFF
                i+=1
            i+=1
            next_idx = idx + num
            img_data[idx:next_idx] = val
            idx = next_idx

        img = PIL.Image.frombytes("RGBA", [self.preview_w, self.preview_h], bytes(img_data))
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
        layer_h = self.layer_headers[layerNum][3]
        layer_w = self.layer_headers[layerNum][4]

        decodedLayer = list()
        for k, g in itertools.groupby(self.layer_data[layerNum]):
            num = rle[k]
            val = (k & 0x01) * 255
            decodedLayer.extend([val]*num*sum(1 for x in g))
        decodedLayer.extend([0]*(layer_w*layer_h-len(decodedLayer)))

        return decodedLayer

    def get_layer_decoded_data_numpy(self, layerNum):
        layer_h = self.header[12]
        layer_w = self.header[13]

        decodedLayer = numpy.zeros(layer_h*layer_w, dtype=numpy.byte)
        idx = 0

        for k, g in itertools.groupby(self.layer_data[layerNum]):            
            num = k&0x7F
            if k & 0x80 == 0:
                idx += num*sum(1 for x in g)
            else:
                nextIdx = idx + (num*sum(1 for x in g))
                decodedLayer[idx:nextIdx] = 255
                idx = nextIdx
        decodedLayer[idx:len(decodedLayer)] = 0

        return decodedLayer
    
    def get_layer_bits(self, layerNum):
        return numpy.packbits(self.get_layer_decoded_data_numpy(layerNum))


    def get_layer_qtimage(self, layerNum):
        data = self.get_layer_decoded_data_numpy(layerNum)
        header = self.layer_headers[layerNum]
        img = PIL.Image.frombytes("L", [self.header[12], self.header[13]], bytes(data))
        # img.show()
        return ImageQt(img)

