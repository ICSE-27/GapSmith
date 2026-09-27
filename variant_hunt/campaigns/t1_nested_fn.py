"""Campaign t1: mutations of gcc/crash/test1.c
Seed: two nested functions, first carries section attribute -> ICE segfault in
tree-nested.cc at -O1/-O2 (clean at -O0).
Axes: attribute kind x attribute target x structure x opt level.
"""

ATTRS = [
    '__attribute__((section(".text")))',
    '__attribute__((section(".text.hot")))',
    '__attribute__((section("foo")))',
    '__attribute__((used))',
    '__attribute__((noinline))',
    '__attribute__((noclone))',
    '__attribute__((cold))',
    '__attribute__((hot))',
    '__attribute__((aligned(64)))',
    '__attribute__((visibility("hidden")))',
    '__attribute__((weak))',
    '__attribute__((always_inline))',
    '__attribute__((optimize("O0")))',
    '__attribute__((optimize("O3")))',
    '__attribute__((noipa))',
    '__attribute__((noinstrument_function))',
    '__attribute__((constructor))',
    '__attribute__((destructor))',
    '__attribute__((pure))',
    '__attribute__((const))',
    '__attribute__((flatten))',
    '__attribute__((section(".text"), used))',
    '__attribute__((section(".text"), noinline))',
    '__attribute__((used, noinline))',
    '__attribute__((cold, noinline))',
    '__attribute__((section(".text"), aligned(32)))',
]

# structure templates: {A} = attribute placed on g, {B} = optional attr on h
BODIES = [
    # original shape
    lambda a, b: f'''void outer() {{
    void {a} g() {{}}
    g();
    void {b} h() {{}}
}}''',
    # no call to g
    lambda a, b: f'''void outer() {{
    void {a} g() {{}}
    void {b} h() {{}}
}}''',
    # call both
    lambda a, b: f'''void outer() {{
    void {a} g() {{}}
    void {b} h() {{}}
    g(); h();
}}''',
    # g calls h (h declared after g -> forward use inside g needs decl)
    lambda a, b: f'''void outer() {{
    void {b} h() {{}}
    void {a} g() {{ h(); }}
    g();
}}''',
    # three nested
    lambda a, b: f'''void outer() {{
    void {a} g() {{}}
    g();
    void {b} h() {{}}
    void k() {{ g(); }}
    k();
}}''',
    # nested-in-nested
    lambda a, b: f'''void outer() {{
    void {a} g() {{
        void inner() {{}}
        inner();
    }}
    g();
    void {b} h() {{}}
}}''',
    # returning int, with args
    lambda a, b: f'''int outer(int x) {{
    int {a} g(int y) {{ return y + 1; }}
    int r = g(x);
    int {b} h(int y) {{ return y * 2; }}
    return r + h(x);
}}''',
    # attribute on h only (swapped)
    lambda a, b: f'''void outer() {{
    void {b} g() {{}}
    g();
    void {a} h() {{}}
}}''',
    # static-ish chain with static var inside
    lambda a, b: f'''void outer() {{
    static int cnt;
    void {a} g() {{ cnt++; }}
    g();
    void {b} h() {{ cnt--; }}
    h();
}}''',
    # trampolines: address taken
    lambda a, b: f'''void (*fp)();
void outer() {{
    void {a} g() {{}}
    fp = g;
    void {b} h() {{}}
}}''',
]

OPTS = ["-O1", "-O2", "-O3", "-Os", "-Og"]

def generate():
    i = 0
    for bi, body in enumerate(BODIES):
        for ai, a in enumerate(ATTRS):
            for b in ['', '__attribute__((noinline))']:
                src = body(a, b) + "\n"
                for o in OPTS:
                    yield {
                        "name": f"t1_b{bi}_a{ai}{'_b' if b else ''}_{o[1:]}",
                        "src": src,
                        "tag": "gcc",
                        "flags": [o],
                        "ext": ".c",
                    }
                    i += 1
