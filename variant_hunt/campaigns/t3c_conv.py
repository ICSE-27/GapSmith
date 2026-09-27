"""Campaign t3c: constexpr conversion vein (fold_convert_loc@2757) — new axes:
reinterpret_cast in constexpr, unions holding member ptrs, member ptr
comparisons in constant expressions, function pointers (not member), arrays of
function ptrs in constexpr structs, conversion sequences.
"""

SHAPES = [
    # union holding member ptr in constexpr
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
union help {
  fn_t ptr;
  unsigned long raw;
  constexpr help(fn_t p) : ptr(p) {}
};
template <typename T=int> void generate() {
  constexpr help h(static_cast<fn_t>(&Derived::doit));
}
void f() { generate(); }''',
    # constexpr member ptr comparison
    '''struct Base { virtual void doit(int) const; virtual void other(int) const; int val; };
struct Derived : Base { void doit(int) const; void other(int) const; };
typedef void (Base::*fn_t)(int) const;
constexpr bool same = static_cast<fn_t>(&Derived::doit) == static_cast<fn_t>(&Base::doit);
static_assert(!same, "");''',
    # array of fn ptrs in constexpr struct
    '''struct Base { virtual void doit(int) const; virtual void other(int) const; int val; };
struct Derived : Base { void doit(int) const; void other(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help {
  fn_t ptrs[2];
};
template <typename T=int> void generate() {
  constexpr help h{{static_cast<fn_t>(&Derived::doit), static_cast<fn_t>(&Derived::other)}};
}
void f() { generate(); }''',
    # constexpr reference to member-ptr object
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help {
  const fn_t& ref;
};
template <typename T=int> void generate() {
  constexpr fn_t p = static_cast<fn_t>(&Derived::doit);
  constexpr help h{p};
}
void f() { generate(); }''',
    # plain function pointer (not member) in constexpr
    '''void freefn(int);
struct help {
  void (*ptr)(int);
};
template <typename T=int> void generate() {
  constexpr help h{static_cast<void(*)(int)>(&freefn)};
}
void f() { generate(); }''',
    # member ptr via const object conversion chain
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
typedef void (Derived::*dfn_t)(int) const;
struct help {
  fn_t ptr;
};
template <typename T=int> void generate() {
  constexpr dfn_t dp = &Derived::doit;
  constexpr help h{static_cast<fn_t>(dp)};
}
void f() { generate(); }''',
    # noexcept fn ptr
    '''struct Base { virtual void doit(int) const noexcept; int val; };
struct Derived : Base { void doit(int) const noexcept; };
typedef void (Base::*fn_t)(int) const noexcept;
struct help { fn_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{static_cast<fn_t>(&Derived::doit)};
}
void f() { generate(); }''',
    # overloaded member selection
    '''struct Base { virtual void doit(int) const; virtual void doit(double) const; int val; };
struct Derived : Base { void doit(int) const; void doit(double) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{static_cast<fn_t>(&Derived::doit)};
}
void f() { generate(); }''',
]

OPTS = [["-O0"], ["-O1"], ["-O2"], ["-std=c++20"], ["-std=c++17", "-O1"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for oi, o in enumerate(OPTS):
            yield {"name": f"t3c_s{si}_o{oi}", "src": src, "tag": "gxx",
                   "flags": o, "ext": ".cpp"}
