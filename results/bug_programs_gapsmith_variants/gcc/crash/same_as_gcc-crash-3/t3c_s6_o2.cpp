struct Base { virtual void doit(int) const noexcept; int val; };
struct Derived : Base { void doit(int) const noexcept; };
typedef void (Base::*fn_t)(int) const noexcept;
struct help { fn_t ptr; };
template <typename T=int> void generate() {
  constexpr help h{static_cast<fn_t>(&Derived::doit)};
}
void f() { generate(); }
