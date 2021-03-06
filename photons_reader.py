import struct
from PIL.ImageQt import ImageQt
import PIL
import numpy
import itertools

header_info = [
    "XY Pixel Size",     #0
    "Layer thickness",   #1
    "Normal Exposure(s)",#2
    "Off Time(s)",       #3 
    "Bottom Exposure(s)",#4
    "Bottom Layers",     #5
    "Z Lift Distance(mm)",#6
    "Z Lift Speed(mm/s)",#7
    "Z Retract Speed(mm/s)",#8
    "Total volume(ml)",  #9
    "????",
    "????",
    "????",
    "????",
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
        self.layer_data = []
        self.layer_headers = []
        self.preview_image = None

    def format_bytes(self, data):
        return ":".join("{:02x}".format(c) for c in data)
    
    def read_data(self, with_decode=False):
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
            self.layer_data = [None]*self.num_layers
            self.layer_headers = [None]*self.num_layers

            # read layers
            for i in range(self.num_layers):
                self.layer_offsets[i] = binary_file.tell()
                data = binary_file.read(struct.calcsize(layers_header_format))
                self.layer_headers[i] = struct.unpack(layers_header_format, data)
                header_data_len = (self.layer_headers[i][5]>>3)-4
                self.layer_data[i] = binary_file.read(header_data_len)

    def getXYPixelSize(self):
        return self.header[0]
    def getLayerThickness(self):
        return self.header[1]
    def getNormalExposureTime(self):
        return self.header[2]
    def getOffTime(self):
        return self.header[3]
    def getBottomExposureTime(self):
        return self.header[4]
    def getNumBottomLayers(self):
        return self.header[5]
    def getZLiftDistance(self):
        return self.header[6]
    def getZLiftSpeed(self):
        return self.header[7]
    def getZRetractSpeed(self):
        return self.header[8]
    def getTotalVolume(self):
        return self.header[9]
    def getPreviewW(self):
        return self.preview_w
    def getPreviewH(self):
        return self.preview_h
    def getNumLayers(self):
        return self.num_layers

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
        layer_h = self.layer_headers[layerNum][3]
        layer_w = self.layer_headers[layerNum][4]

        decodedLayer = numpy.zeros(layer_h*layer_w, dtype=numpy.byte)
        idx = 0

        for k, g in itertools.groupby(self.layer_data[layerNum]):
            num = rle[k]
            if k & 0x01 == 0:
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
        img = PIL.Image.frombytes("L", [header[3], header[4]], bytes(data))
        # img.show()
        return ImageQt(img)

