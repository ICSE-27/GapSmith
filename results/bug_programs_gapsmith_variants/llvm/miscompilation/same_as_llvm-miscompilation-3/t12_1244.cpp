#include <stdio.h>
unsigned int acc = 0;
unsigned char a[8][8];
signed char b[8];

__attribute__((noinline)) void test() {
    for (long long i = 0; i < 8; i += 3)
        for (long long j = 0; j < 8; j += 1)
            acc += a[j][i] & (a[j][i] <= b[j]);
}

int main() {
    for (int i = 0; i < 8; i++) {
        b[i] = -1;
        for (int j = 0; j < 8; j++) a[i][j] = 65535;
    }
    test();
    printf("acc=%u (expected 0)\n", acc);
    return acc != 0;
}
