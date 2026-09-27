"""Campaign t3b: wave-2 for gcc test3.cpp (constexpr ptr conversion ICE).
Wave 1 only reproduced fold_convert_loc@2757. Try harder:
conversions in constexpr: derived->base member ptr, member ptr to const,
nullptr folds, virtual inheritance, function ptr arrays, templates over member ptr.
"""

SHAPES = [
    # constexpr static_assert comparing member ptr
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
constexpr fn_t p = static_cast<fn_t>(&Derived::doit);
static_assert(p == &Derived::doit, "");''',
    # constexpr member ptr in template arg
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
template <fn_t P> struct X { int v = 1; };
X<static_cast<fn_t>(&Derived::doit)> x;''',
    # constexpr array of member ptrs
    '''struct Base { virtual void doit(int) const; virtual void other() const; int val; };
struct Derived : Base { void doit(int) const; void other() const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
constexpr help hs[2] = {{static_cast<fn_t>(&Derived::doit)}, {nullptr}};''',
    # constexpr member DATA ptr
    '''struct Base { int val; };
struct Derived : Base { int extra; };
typedef int Base::*mp_t;
struct help { mp_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{static_cast<mp_t>(&Derived::val)};
}
void f() { generate(); }''',
    # constexpr conversion via const object
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
constexpr fn_t raw = &Derived::doit;
constexpr help h{raw};''',
    # virtual inheritance
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : virtual Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{static_cast<fn_t>(&Derived::doit)};
}
void f() { generate(); }''',
    # conditional in constexpr initializer
    '''struct Base { virtual void doit(int) const; virtual void other(int) const; int val; };
struct Derived : Base { void doit(int) const; void other(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{sizeof(T) > 0 ? static_cast<fn_t>(&Derived::doit) : static_cast<fn_t>(&Derived::other)};
}
void f() { generate(); }''',
    # nested constexpr struct
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct inner { fn_t ptr; };
struct help { inner i; };
template <typename T=int> void generate() {
  constexpr help h{{{static_cast<fn_t>(&Derived::doit)}}};
}
void f() { generate(); }''',
    # consteval function returning it (C++20)
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
consteval help make() { return help{static_cast<fn_t>(&Derived::doit)}; }
template <typename T=int> void generate() {
  constexpr help h = make();
}
void f() { generate(); }''',
    # constexpr constructor
    '''struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help {
  fn_t ptr;
  constexpr help(fn_t p) : ptr(p) {}
};
template <typename T=int> void generate() {
  constexpr help h(static_cast<fn_t>(&Derived::doit));
}
void f() { generate(); }''',
]

OPTS = [["-O0"], ["-O1"], ["-O2"], ["-std=c++20"], ["-std=c++17", "-O1"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape + "\n"
        for oi, o in enumerate(OPTS):
            yield {"name": f"t3b_s{si}_o{oi}", "src": src, "tag": "gxx",
                   "flags": o, "ext": ".cpp"}
