#include <cstdio>
#include <cstdlib>

static thread_local int tls_val = 0;

[[gnu::noinline]]
bool test(void* p, int trigger_abort, void** out) noexcept {
    if (!p)
        return false;

    int saved = -1;
    int flag = (trigger_abort * 2);

    asm volatile goto (
        "  movl %[tls], %%eax\n\t"
        "  movl %%eax, %[saved]\n\t"
        "  movl %[flag], %%eax\n\t"
        "  testl %%eax, %%eax\n\t"
        "  je %l[abort_lbl]\n\t"
        : [saved]"+m"(saved), [flag]"+m"(flag)
        : [tls]"m"(tls_val)
        : "eax", "memory"
        : abort_lbl
    );

    if (flag == 0) {
        fprintf(stderr, "flag==0\n");
        abort();
    }

    *out = (saved >= 0) ? p : nullptr;
    return true;

abort_lbl:
    *out = (saved >= 0) ? p : nullptr;
    return false;
}

int main() {
    void* result;
    if (!test((void*)0x1, 0, &result)) {
        fprintf(stderr, "FAIL: expected true from normal path\n");
        return 1;
    }
    printf("Normal path OK: result=%p\n", result);

    fprintf(stderr, "Triggering abort path...\n");
    bool r = test((void*)0x1, 1, &result);
    printf("Abort path returned %d\n", r);
    return 0;
}
