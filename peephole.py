from __future__ import print_function
import sys

start = 0x8000
image = bytearray(open(sys.argv[1], "rb").read())

opcode_jmp_abs = 0x4c

for i in range(0, len(image)):
    if image[i] == opcode_jmp_abs:
        target = image[i + 1] + (image[i + 2] << 8)
        # If we replace this JMP with BRA, its displacement will be calculated
        # from this point.
        branch_base = start + i + 2
        branch_displacement = target - branch_base
        if branch_displacement >= -128 and branch_displacement <= 127:
            print("%s JMP &%s -> BRA (%d)" % (hex(start + i), hex(target), branch_displacement))
