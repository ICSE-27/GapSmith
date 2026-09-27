struct Base { virtual void doit(int) const; virtual void doit(double) const; int val; };
struct Derived : Base { void doit(int) const; void doit(double) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{static_cast<fn_t>(&Derived::doit)};
}
void f() { generate(); }
