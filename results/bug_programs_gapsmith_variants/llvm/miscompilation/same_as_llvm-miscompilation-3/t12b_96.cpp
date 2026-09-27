#include <stdio.h>
unsigned int acc = 0;
unsigned short a[6][6];
short b[6];

__attribute__((noinline)) void test() {
    for (long long i = 0; i < 6; i += 2)
        for (long long j = 0; j < 6; j += 2)
            acc += a[j][i] & (a[j][i] > b[j]);
}

/* scalar reference: same loop with volatile barrier to block SLP */
__attribute__((noinline)) unsigned int ref() {
    unsigned int r = 0;
    for (long long i = 0; i < 6; i += 2)
        for (long long j = 0; j < 6; j += 2) {
            volatile unsigned short va = a[j][i];
            volatile short vb = b[j];
            r += (unsigned int)(va & (va > vb));
        }
    return r;
}

int main() {
    for (int i = 0; i < 6; i++) {
        b[i] = 14288;
        for (int j = 0; j < 6; j++) a[i][j] = 61035;
    }
    test();
    unsigned int e = ref();
    printf("acc=%u ref=%u\n", acc, e);
    return acc != e;
}
