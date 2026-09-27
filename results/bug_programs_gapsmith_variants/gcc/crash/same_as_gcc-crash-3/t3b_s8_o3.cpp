struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help { fn_t ptr; };
consteval help make() { return help{static_cast<fn_t>(&Derived::doit)}; }
template <typename T=int> void generate() {
  constexpr help h = make();
}
void f() { generate(); }
