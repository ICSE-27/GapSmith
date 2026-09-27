"""Campaign t5b: asm goto NEW axes: register outputs ("+r"), asm goto in loops,
two sequential asm gotos, noreturn caller, -flto, -fpic, output only on some
paths, fallthrough attribute. Run-mode: divergence across -O0..-O2 = hit.
"""

SHAPES = [
    # register outputs instead of memory
    '''#include <stdio.h>
__attribute__((noinline))
int test(int t) {
    int saved = -1;
    int flag = t ? 0 : 1;
    asm volatile goto (
        "  movl $0, %%eax\\n\\t"
        "  movl %%eax, %[saved]\\n\\t"
        "  movl %[flag], %%eax\\n\\t"
        "  testl %%eax, %%eax\\n\\t"
        "  je %l[abort_lbl]\\n\\t"
        : [saved]"+r"(saved), [flag]"+r"(flag)
        :
        : "eax"
        : abort_lbl
    );
    if (flag == 0) __builtin_abort();
    return saved + 1;
abort_lbl:
    return saved - 1;
}
int main() {
    printf("normal=%d\\n", test(0));
    printf("abort=%d\\n", test(1));
    return 0;
}''',
    # asm goto inside a loop
    '''#include <stdio.h>
int total = 0;
__attribute__((noinline))
int test(int n) {
    int saved = -1;
    for (int i = 0; i < n; i++) {
        int flag = (i == n - 1) ? 0 : 1;
        asm volatile goto (
            "  movl $0, %%eax\\n\\t"
            "  movl %%eax, %[saved]\\n\\t"
            "  movl %[flag], %%eax\\n\\t"
            "  testl %%eax, %%eax\\n\\t"
            "  je %l[abort_lbl]\\n\\t"
            : [saved]"+m"(saved), [flag]"+m"(flag)
            :
            : "eax", "memory"
            : abort_lbl
        );
        if (flag == 0) __builtin_abort();
        total += saved + 1;
        continue;
abort_lbl:
        total += saved - 1;
    }
    return total;
}
int main() {
    printf("r=%d\\n", test(4));
    return 0;
}''',
    # two sequential asm gotos
    '''#include <stdio.h>
__attribute__((noinline))
int test(int t) {
    int s1 = -1, s2 = -1;
    int flag = t ? 0 : 1;
    asm volatile goto (
        "  movl $0, %%eax\\n\\t  movl %%eax, %[s1]\\n\\t"
        "  movl %[flag], %%eax\\n\\t  testl %%eax, %%eax\\n\\t  je %l[ab]\\n\\t"
        : [s1]"+m"(s1), [flag]"+m"(flag)
        :
        : "eax", "memory"
        : ab
    );
    if (flag == 0) __builtin_abort();
    asm volatile goto (
        "  movl $2, %%eax\\n\\t  movl %%eax, %[s2]\\n\\t  jmp %l[ok]\\n\\t"
        : [s2]"+m"(s2)
        :
        : "eax", "memory"
        : ok
    );
    return s1 + s2;
ok:
    return s1 + s2 + 10;
ab:
    return s1 - 1;
}
int main() {
    printf("n=%d\\n", test(0));
    printf("a=%d\\n", test(1));
    return 0;
}''',
    # asm goto in a noreturn-attributed function
    '''#include <stdio.h>
#include <stdlib.h>
int saved_g;
__attribute__((noinline))
void die(int t) {
    int saved = -1;
    int flag = t ? 0 : 1;
    asm volatile goto (
        "  movl $0, %%eax\\n\\t  movl %%eax, %[saved]\\n\\t"
        "  movl %[flag], %%eax\\n\\t  testl %%eax, %%eax\\n\\t  je %l[ab]\\n\\t"
        : [saved]"+m"(saved), [flag]"+m"(flag)
        :
        : "eax", "memory"
        : ab
    );
    if (flag == 0) exit(2);
    saved_g = saved + 1;
    return;
ab:
    saved_g = saved - 1;
}
int main() {
    die(0);
    printf("g=%d\\n", saved_g);
    die(1);
    printf("g2=%d\\n", saved_g);
    return 0;
}''',
    # asm goto with output only meaningful on label path
    '''#include <stdio.h>
__attribute__((noinline))
int test(int t) {
    int out = 42;
    asm volatile goto (
        "  testl %[t], %[t]\\n\\t  je %l[zero]\\n\\t"
        : [out]"+m"(out)
        : [t]"r"(t)
        : "memory"
        : zero
    );
    return out;
zero:
    out = 7;
    return out;
}
int main() {
    printf("%d %d\\n", test(1), test(0));
    return 0;
}''',
]

CFLAGS = [[], ["-flto"], ["-fpic"], ["-fomit-frame-pointer"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for fi, fl in enumerate(CFLAGS):
            yield {"name": f"t5b_s{si}_f{fi}", "src": src, "tag": "gxx" if si in (0,) else "gcc",
                   "flags": fl, "mode": "run",
                   "optlevels": ["-O0", "-O1", "-O2"],
                   "ext": ".cpp" if si == 0 else ".c"}
