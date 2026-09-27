"""Campaign t5: mutations of gcc/miscompilation/test5.cpp
Seed: asm goto + thread_local memory input + noreturn-ish branch -> -O1/-O2
emits code whose labels merge before prologue; binary segfaults.
Run-mode: behavior must be identical across opt levels; difference = MISCOMPILE.
"""

import itertools

TLS_KINDS = ["thread_local int tls_val = 0;", "int tls_val = 0;",
             "thread_local long tls_val = 0;", "static thread_local int tls_val = 0;"]

FLAG_EXPR = ["trigger_abort ? 0 : 1", "trigger_abort", "!trigger_abort",
             "trigger_abort & 1", "(trigger_abort * 2)"]

ABORT_CALL = ["abort()", "__builtin_trap()", "exit(3)", "fprintf(stderr, \"x\\n\"), abort()"]

SHAPES = [
    # original-ish
    '''#include <cstdio>
#include <cstdlib>

{tls}

[[gnu::noinline]]
bool test(void* p, int trigger_abort, void** out) noexcept {{
    if (!p)
        return false;

    int saved = -1;
    int flag = {flagexpr};

    asm volatile goto (
        "  movl %[tls], %%eax\\n\\t"
        "  movl %%eax, %[saved]\\n\\t"
        "  movl %[flag], %%eax\\n\\t"
        "  testl %%eax, %%eax\\n\\t"
        "  je %l[abort_lbl]\\n\\t"
        : [saved]"+m"(saved), [flag]"+m"(flag)
        : [tls]"m"(tls_val)
        : "eax", "memory"
        : abort_lbl
    );

    if (flag == 0) {{
        fprintf(stderr, "flag==0\\n");
        {abortcall};
    }}

    *out = (saved >= 0) ? p : nullptr;
    return true;

abort_lbl:
    *out = (saved >= 0) ? p : nullptr;
    return false;
}}

int main() {{
    void* result;
    if (!test((void*)0x1, 0, &result)) {{
        fprintf(stderr, "FAIL: expected true from normal path\\n");
        return 1;
    }}
    printf("Normal path OK: result=%p\\n", result);

    fprintf(stderr, "Triggering abort path...\\n");
    bool r = test((void*)0x1, 1, &result);
    printf("Abort path returned %d\\n", r);
    return 0;
}}''',
    # no early return, simpler control flow
    '''#include <cstdio>
#include <cstdlib>

{tls}

[[gnu::noinline]]
int test(int trigger_abort) noexcept {{
    int saved = -1;
    int flag = {flagexpr};

    asm volatile goto (
        "  movl %[tls], %%eax\\n\\t"
        "  movl %%eax, %[saved]\\n\\t"
        "  movl %[flag], %%eax\\n\\t"
        "  testl %%eax, %%eax\\n\\t"
        "  je %l[abort_lbl]\\n\\t"
        : [saved]"+m"(saved), [flag]"+m"(flag)
        : [tls]"m"(tls_val)
        : "eax", "memory"
        : abort_lbl
    );

    if (flag == 0) {{
        {abortcall};
    }}
    return saved + 1;

abort_lbl:
    return saved - 1;
}}

int main() {{
    int a = test(0);
    printf("normal=%d\\n", a);
    int b = test(1);
    printf("abort=%d\\n", b);
    return 0;
}}''',
    # two asm-goto labels
    '''#include <cstdio>
#include <cstdlib>

{tls}

[[gnu::noinline]]
int test(int trigger_abort) noexcept {{
    int saved = -1;
    int flag = {flagexpr};

    asm volatile goto (
        "  movl %[tls], %%eax\\n\\t"
        "  movl %%eax, %[saved]\\n\\t"
        "  movl %[flag], %%eax\\n\\t"
        "  testl %%eax, %%eax\\n\\t"
        "  je %l[abort_lbl]\\n\\t"
        "  jmp %l[ok_lbl]\\n\\t"
        : [saved]"+m"(saved), [flag]"+m"(flag)
        : [tls]"m"(tls_val)
        : "eax", "memory"
        : abort_lbl, ok_lbl
    );

ok_lbl:
    if (flag == 0) {{
        {abortcall};
    }}
    return saved + 1;

abort_lbl:
    return saved - 1;
}}

int main() {{
    int a = test(0);
    printf("normal=%d\\n", a);
    int b = test(1);
    printf("abort=%d\\n", b);
    return 0;
}}''',
]

def generate():
    for si, shape in enumerate(SHAPES):
        for ti, tls in enumerate(TLS_KINDS):
            for fi, fe in enumerate(FLAG_EXPR):
                for ai, ac in enumerate(ABORT_CALL[:2]):
                    src = shape.format(tls=tls, flagexpr=fe, abortcall=ac) + "\n"
                    yield {"name": f"t5_s{si}_t{ti}_f{fi}_a{ai}",
                           "src": src, "tag": "gxx", "flags": ["-std=c++20"],
                           "mode": "run",
                           "optlevels": ["-O0", "-O1", "-O2"],
                           "ext": ".cpp"}
