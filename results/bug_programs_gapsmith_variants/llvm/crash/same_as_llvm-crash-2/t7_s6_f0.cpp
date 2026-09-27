template<const int& T>
void FuncTemplate() { (void)T; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static const int InternalVar = 43;
    FuncTemplate<InternalVar>();
}

int main()
{
  A<1> a;
  g(a);
}
