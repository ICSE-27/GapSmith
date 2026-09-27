"""Campaign t1d: GCC nested functions with NEW attribute kinds and flags:
target_clones, ifunc, target("avx"), externally_visible, no_callee_saves,
-fsanitize, -pg, -finstrument-functions, OpenMP simd, cold on the CALLER.
"""

ATTR_SHAPES = [
    ('__attribute__((target_clones("avx2", "default")))', 'target_clones'),
    ('__attribute__((target("avx2")))', 'target_avx'),
    ('__attribute__((target("sse4.2")))', 'target_sse'),
    ('__attribute__((externally_visible))', 'extern_vis'),
    ('__attribute__((no_callee_saves))', 'no_callee_saves'),
    ('__attribute__((interrupt))', 'interrupt'),       # may be invalid usage -> error, fine
    ('__attribute__((noreturn))', 'noreturn'),
    ('__attribute__((warn_unused_result))', 'wur'),
    ('__attribute__((nothrow))', 'nothrow'),
    ('__attribute__((regparm(2)))', 'regparm'),
]

BODIES = [
    # original 2-nested
    '''void outer() {{
    void {a} g() {{}}
    g();
    void h() {{}}
}}''',
    # 3-nested caller (1683 vein)
    '''void outer() {{
    void {a} g() {{}}
    void h() {{}}
    void k() {{ g(); }}
    k();
}}''',
    # caller first
    '''void outer() {{
    void {a} g() {{}}
    void k() {{ g(); }}
    k();
    void h() {{}}
}}''',
]

EXTRA_FLAG_SETS = [
    ["-O1"], ["-O2"],
    ["-O1", "-fsanitize=address"],
    ["-O1", "-pg"],
    ["-O1", "-finstrument-functions"],
    ["-O1", "-fopenmp-simd"],
    ["-O2", "-flto"],
    ["-O1", "-fcf-protection=full"],
]

def generate():
    for bi, body in enumerate(BODIES):
        for ai, (a, an) in enumerate(ATTR_SHAPES):
            src = body.format(a=a) + "\n"
            for fi, fl in enumerate(EXTRA_FLAG_SETS):
                yield {"name": f"t1d_b{bi}_a{ai}_f{fi}",
                       "src": src, "tag": "gcc", "flags": fl, "ext": ".c"}
