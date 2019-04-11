with open("img.dat", "rb") as binary_file:
    fo = open('img.out', 'wb')
    cnt0 = 0
    cnte0 = 0
    cnt1 = 0
    cnte1 = 0
    while 1:
        byte_s = binary_file.read(1)
        if not byte_s:
            break
        byte = byte_s[0]
        val = (byte & 0x01)<<7
        num = byte >> 1
        if byte & 0x01:
            cnte1=cnte1+1
        else:
            cnte0=cnte0+1
        if cnt1 == 0 and val > 0:
            print(fo.tell())
            print(cnte0)
        for i in range(num):
            if byte & 0x01:
                cnt1=cnt1+1
            else:
                cnt0=cnt0+1
            fo.write(bytes([val]))
    fo.close()
    print("num 0: {}\nnum 1: {}".format(cnte0, cnte1))
    print("num 0: {}\nnum 1: {}".format(cnt0, cnt1))