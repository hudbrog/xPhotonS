def get_rle_len(inp):
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


res = [None]*256
for i in range(256):
    res[i] = get_rle_len(i)
print(", ".join("{}".format(c) for c in res))