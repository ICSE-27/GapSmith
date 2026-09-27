#include <cstdio>
#include <cstdlib>

static thread_local int tls_val = 0;

[[gnu::noinline]]
int test(int trigger_abort) noexcept {
    int saved = -1;
    int flag = (trigger_abort * 2);

    asm volatile goto (
        "  movl %[tls], %%eax\n\t"
        "  movl %%eax, %[saved]\n\t"
        "  movl %[flag], %%eax\n\t"
        "  testl %%eax, %%eax\n\t"
        "  je %l[abort_lbl]\n\t"
        "  jmp %l[ok_lbl]\n\t"
        : [saved]"+m"(saved), [flag]"+m"(flag)
        : [tls]"m"(tls_val)
        : "eax", "memory"
        : abort_lbl, ok_lbl
    );

ok_lbl:
    if (flag == 0) {
        abort();
    }
    return saved + 1;

abort_lbl:
    return saved - 1;
}

int main() {
    int a = test(0);
    printf("normal=%d\n", a);
    int b = test(1);
    printf("abort=%d\n", b);
    return 0;
}
