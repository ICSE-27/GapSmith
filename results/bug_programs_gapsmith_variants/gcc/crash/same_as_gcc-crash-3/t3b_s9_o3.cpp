struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help {
  fn_t ptr;
  constexpr help(fn_t p) : ptr(p) {}
};
template <typename T=int> void generate() {
  constexpr help h(static_cast<fn_t>(&Derived::doit));
}
void f() { generate(); }
