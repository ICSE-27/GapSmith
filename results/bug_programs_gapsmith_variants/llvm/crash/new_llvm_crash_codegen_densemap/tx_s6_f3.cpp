template <auto V>
struct CW { static constexpr auto value = V; };
template<int& T>
void FuncTemplate() { (void)T; }
template<int i> class A {};
template<int i> void g(A<i> &) {
    []()
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
        constexpr auto w = CW<42>{};
        (void)w;
    }();
}
int main() {
  A<1> a;
  g(a);
}
