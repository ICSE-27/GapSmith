#include <stdio.h>
unsigned int acc = 0;
unsigned short a[6][6];
short b[6];

__attribute__((noinline)) void test() {
    for (long long i = 0; i < 6; i += 2)
        for (long long j = 0; j < 6; j += 1)
            acc += a[j][i] & (a[j][i] >= b[j]);
}

int main() {
    for (int i = 0; i < 6; i++) {
        b[i] = 14288;
        for (int j = 0; j < 6; j++) a[i][j] = 61035;
    }
    test();
    printf("acc=%u (expected 2)\n", acc);
    return acc != 2;
}
