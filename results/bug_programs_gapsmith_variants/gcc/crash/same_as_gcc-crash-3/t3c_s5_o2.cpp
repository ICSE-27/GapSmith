struct Base { virtual void doit(int) const; int val; };
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
void f() { generate(); }
