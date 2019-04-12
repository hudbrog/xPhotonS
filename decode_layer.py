def get_len(inp):
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

with open("img2.dat", "rb") as binary_file:
    fo = open('img2.out', 'wb')
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
        num = get_len(byte)
        if byte & 0x01:
            val = 255
        else:
            val = 0
        for i in range(num):
            if byte & 0x01:
                cnt1=cnt1+1
            else:
                cnt0=cnt0+1
            fo.write(bytes([val]))
    # omg.. they actually have a bug, loosing last byte in most cases
    while cnt0+cnt1 < 1440*2560:
        fo.write(bytes([0]))
        cnt0+=1
    fo.close()
    print("num 0: {}\nnum 1: {}".format(cnt0, cnt1))

