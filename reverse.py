inp = 0xFE
i = 0; j = 7
num = inp&0xFE
print(hex(inp))
while i<j:
    # Get the bits from both end iteratively
    if (num>>i)&1 != (num>>j)&1:
        # if the bits don't match swap them by creating a bit mask
        # and XOR it with the number 
        mask = (1<<i) | (1<<j)
        num ^= mask
    i += 1; j -= 1
res = num+1
# print(bin(res))
print(hex(res))
print(res)