with open("test.photons", "rb") as binary_file:
    binary_file.seek(75362+32)
    buf = binary_file.read(0x7945-32)
    fo = open('img2.dat', 'wb')
    fo.write(buf)
    fo.close()

# 3 686 400 pixels
# 460 800 bytes    

# 1A09 to first different - 6665
# D08EF in bmp (actually maybe 1000 less) ~850k


