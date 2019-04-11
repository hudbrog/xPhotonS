with open("c.photons", "rb") as binary_file:
    binary_file.seek(0x19C16+28)
    buf = binary_file.read(0x75b0-28)
    fo = open('img.dat', 'wb')
    fo.write(buf)
    fo.close()

# 3 686 400 pixels
# 460 800 bytes    

# 1A09 to first different - 6665
# D08EF in bmp (actually maybe 1000 less) ~850k