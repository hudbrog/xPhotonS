import photohs_reader
import numpy 
import time
import itertools


def get_layer_decoded_data(reader, layerNum):
    layer_h = reader.layer_headers[layerNum][3]
    layer_w = reader.layer_headers[layerNum][4]

    decodedLayer = list()
    dLen = len(reader.layer_data[layerNum])
    for i in range(dLen):
        num = photohs_reader.rle[reader.layer_data[layerNum][i]]
        val = (reader.layer_data[layerNum][i] & 0x01) * 255
        decodedLayer.extend([val]*num)
    decodedLayer.extend([0]*(layer_w*layer_h-len(decodedLayer)))

    return decodedLayer

def with_groupby(reader, layerNum):
    layer_h = reader.layer_headers[layerNum][3]
    layer_w = reader.layer_headers[layerNum][4]

    decodedLayer = list()
    for k, g in itertools.groupby(reader.layer_data[layerNum]):
        num = photohs_reader.rle[k]
        val = (k & 0x01) * 255
        decodedLayer.extend([val]*num*sum(1 for x in g))
    decodedLayer.extend([0]*(layer_w*layer_h-len(decodedLayer)))

    return decodedLayer

def numpy1(reader, layerNum):
    layer_h = reader.layer_headers[layerNum][3]
    layer_w = reader.layer_headers[layerNum][4]

    decodedLayer = numpy.zeros(layer_h*layer_w, dtype=numpy.byte)
    idx = 0

    for k, g in itertools.groupby(reader.layer_data[layerNum]):
        num = photohs_reader.rle[k]
        if k & 0x01 == 0:
            idx += num*sum(1 for x in g)
        else:
            decodedLayer[idx:(idx+num*sum(1 for x in g))] = 255
    decodedLayer[idx:len(decodedLayer)] = 0

    return decodedLayer

reader = photohs_reader.PhotonSReader("test.photons")
reader.read_data()

num_iter = 3
start = time.time()
for i in range(num_iter):
    get_layer_decoded_data(reader, 2)
end = time.time()
print("default: {}".format(end - start))

start = time.time()
for i in range(num_iter):
    with_groupby(reader, 2)
end = time.time()
print("with_groupby: {}".format(end - start))

start = time.time()
for i in range(num_iter):
    numpy1(reader, 2)
end = time.time()
print("numpy1: {}".format(end - start))
