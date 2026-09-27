"""Campaign t1b: wave-2 around the NEW gimple_call_static_chain_flags@gimple.cc:1683 ICE
found in wave 1: three nested functions where a later nested fn (k) calls an
earlier attribute-carrying fn (g) -> ICE in ealias pass (not the seed's
tree-nested.cc segfault).
Expand: attribute x call graph x arity x types x flags.
"""

ATTRS = [
    '__attribute__((section(".text")))',
    '__attribute__((section(".text.hot")))',
    '__attribute__((section("foo")))',
    '__attribute__((used))',
    '__attribute__((noinline))',
    '__attribute__((cold))',
    '__attribute__((aligned(64)))',
    '__attribute__((visibility("hidden")))',
    '__attribute__((weak))',
    '__attribute__((always_inline))',
    '__attribute__((optimize("O0")))',
    '__attribute__((noipa))',
    '__attribute__((constructor))',
    '__attribute__((pure))',
    '__attribute__((const))',
    '__attribute__((section(".text"), used))',
    '__attribute__((section(".text"), noinline))',
    '__attribute__((section(".text"), aligned(32)))',
]

# {A} on g; bodies differ in who calls g
BODIES = [
    # k calls g (wave-1 winner)
    '''void outer() {{
    void {a} g() {{}}
    g();
    void h() {{}}
    void k() {{ g(); }}
    k();
}}''',
    # k calls g, g not called directly
    '''void outer() {{
    void {a} g() {{}}
    void h() {{}}
    void k() {{ g(); }}
    k();
}}''',
    # two callers of g
    '''void outer() {{
    void {a} g() {{}}
    void h() {{ g(); }}
    void k() {{ g(); }}
    h(); k();
}}''',
    # call chain g<-h<-k
    '''void outer() {{
    void {a} g() {{}}
    void h() {{ g(); }}
    void k() {{ h(); }}
    k();
}}''',
    # mutual-ish (h calls g, g calls nothing), k calls both
    '''void outer() {{
    void {a} g() {{}}
    void h() {{ g(); }}
    void k() {{ g(); h(); }}
    k();
}}''',
    # int-returning, args passed
    '''int outer(int x) {{
    int {a} g(int v) {{ return v + 1; }}
    int h(int v) {{ return v * 2; }}
    int k(int v) {{ return g(v) + h(v); }}
    return k(x);
}}''',
    # g modifies static, k calls g twice
    '''void outer() {{
    static int cnt;
    void {a} g() {{ cnt++; }}
    void h() {{}}
    void k() {{ g(); g(); }}
    k();
}}''',
    # address of g taken in k (trampoline + call)
    '''void (*fp)();
void outer() {{
    void {a} g() {{}}
    void h() {{}}
    void k() {{ fp = g; g(); }}
    k();
}}''',
    # recursion via k
    '''void outer() {{
    void {a} g() {{}}
    void h() {{}}
    void k(int n) {{ if (n) {{ g(); k(n-1); }} }}
    k(2);
}}''',
]

OPTS = [["-O1"], ["-O2"], ["-O3"], ["-Os"], ["-Og"],
        ["-O1", "-fipa-cp"], ["-O2", "-fno-inline"], ["-O1", "-ffunction-sections"]]

def generate():
    for bi, body in enumerate(BODIES):
        for ai, a in enumerate(ATTRS):
            src = body.format(a=a) + "\n"
            for oi, o in enumerate(OPTS):
                yield {"name": f"t1b_b{bi}_a{ai}_o{oi}",
                       "src": src, "tag": "gcc", "flags": o, "ext": ".c"}
