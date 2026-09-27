struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct inner { fn_t ptr; };
struct help { inner i; };
template <typename T=int> void generate() {
  constexpr help h{{{static_cast<fn_t>(&Derived::doit)}}};
}
void f() { generate(); }
