#include <stdio.h>
unsigned int acc = 0;
unsigned int a[6][6];
int b[6];

__attribute__((noinline)) void test() {
    for (long long i = 0; i < 6; i += 3)
        for (long long j = 0; j < 6; j += 1)
            acc += a[j][i] | (a[j][i] <= b[j]);
}

/* scalar reference: same loop with volatile barrier to block SLP */
__attribute__((noinline)) unsigned int ref() {
    unsigned int r = 0;
    for (long long i = 0; i < 6; i += 3)
        for (long long j = 0; j < 6; j += 1) {
            volatile unsigned int va = a[j][i];
            volatile int vb = b[j];
            r += (unsigned int)(va | (va <= vb));
        }
    return r;
}

int main() {
    for (int i = 0; i < 6; i++) {
        b[i] = -1;
        for (int j = 0; j < 6; j++) a[i][j] = 65535;
    }
    test();
    unsigned int e = ref();
    printf("acc=%u ref=%u\n", acc, e);
    return acc != e;
}
