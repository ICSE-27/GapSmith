struct Base { virtual void doit(int) const; int val; };
struct Derived : Base { void doit(int) const; };
typedef void (Base::*fn_t)(int) const;
struct help {
  const fn_t& ref;
};
template <typename T=int> void generate() {
  constexpr fn_t p = static_cast<fn_t>(&Derived::doit);
  constexpr help h{p};
}
void f() { generate(); }
