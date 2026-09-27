"""Campaign t3: mutations of gcc/crash/test3.cpp
Seed: constexpr init holding static_cast<ptr-to-member-fn>(&Derived::doit)
-> ICE in fold_convert_loc, fold-const.cc:2757 at every -O.
Axes: member pointer kind, cast kind, constexpr context, inheritance shape.
"""

# member-pointer type + expression pairs
MPTRS = [
    # (typedef decl, expr)
    ("typedef void (Base::*fn_t)(int) const;", "static_cast<fn_t>(&Derived::doit)"),
    ("typedef void (Base::*fn_t)(int);", "static_cast<fn_t>(&Derived::doit)"),
    ("typedef int (Base::*fn_t)();", "static_cast<fn_t>(&Derived::get)"),
    ("typedef int Base::*fn_t;", "static_cast<fn_t>(&Derived::val)"),
    ("typedef void (*fn_t)(int);", "static_cast<fn_t>(&freefn)"),
    ("typedef void (Base::*fn_t)(int) const;", "(fn_t)(&Derived::doit)"),
    ("typedef void (Base::*fn_t)(int) const;", "&Derived::doit"),
    ("typedef void (Base::*fn_t)(int) const;", "static_cast<fn_t>(&Base::doit)"),
]

SHAPES = [
    # original
    '''struct Base {{
  virtual void doit(int) const;
  virtual int get();
  int val;
}};
struct Derived : Base {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
template <typename T=int> void generate() {{
  constexpr help h{{{expr}}};
}}
void f() {{ generate(); }}''',
    # no template, direct constexpr global
    '''struct Base {{
  virtual void doit(int) const;
  virtual int get();
  int val;
}};
struct Derived : Base {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
constexpr help h{{{expr}}};''',
    # constexpr local var in function
    '''struct Base {{
  virtual void doit(int) const;
  virtual int get();
  int val;
}};
struct Derived : Base {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
void f() {{ constexpr help h{{{expr}}}; (void)h; }}''',
    # constinit
    '''struct Base {{
  virtual void doit(int) const;
  virtual int get();
  int val;
}};
struct Derived : Base {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
constinit help h{{{expr}}};''',
    # static_assert / array bound context
    '''struct Base {{
  virtual void doit(int) const;
  virtual int get();
  int val;
}};
struct Derived : Base {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
template <typename T=int> void generate() {{
  constexpr help h{{{expr}}};
  static_assert(sizeof(h) >= 1, "");
}}
void f() {{ generate(); }}''',
    # array of helps
    '''struct Base {{
  virtual void doit(int) const;
  virtual int get();
  int val;
}};
struct Derived : Base {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
template <typename T=int> void generate() {{
  constexpr help h[2] = {{{{{expr}}}, {{{expr}}}}};
}}
void f() {{ generate(); }}''',
    # multi-level inheritance
    '''struct Base {{
  virtual void doit(int) const;
  virtual int get();
  int val;
}};
struct Mid : Base {{}};
struct Derived : Mid {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
template <typename T=int> void generate() {{
  constexpr help h{{{expr}}};
}}
void f() {{ generate(); }}''',
    # non-virtual
    '''struct Base {{
  void doit(int) const;
  int get();
  int val;
}};
struct Derived : Base {{
  void doit(int) const;
  int get();
}};
typedef void (*free_t)(int);
void freefn(int);
{td}
struct help {{
  fn_t ptr;
}};
template <typename T=int> void generate() {{
  constexpr help h{{{expr}}};
}}
void f() {{ generate(); }}''',
]

OPTS = [["-O0"], ["-O1"], ["-O2"]]

def generate():
    for si, shape in enumerate(SHAPES):
        for mi, (td, expr) in enumerate(MPTRS):
            src = shape.format(td=td, expr=expr) + "\n"
            for oi, o in enumerate(OPTS[:1] if (si + mi) % 2 else OPTS):
                yield {"name": f"t3_s{si}_m{mi}_{o[0][1:]}",
                       "src": src, "tag": "gxx", "flags": o, "ext": ".cpp"}
