// Copyright (c) 2015 Caleb Jones

#include <stdio.h>
#include <stdint.h>

int main() {
    union {
        uint8_t  c[4];
        uint32_t i;
    } u;

    u.i = 0x01020304;

    if (0x04 == u.c[0])
        printf("Little endian\n");
    else if (0x01 == u.c[0])
        printf("Big endian\n");

    instr a; a.raw = 0;
    a.nibbles.n1 = 1;
    a.nibbles.n2 = 2;
    a.nibbles.n3 = 3;
    a.nibbles.n4 = 4;
    printf("%lu\n", sizeof(instr));
    printf("%04x\n", a.raw);
}
