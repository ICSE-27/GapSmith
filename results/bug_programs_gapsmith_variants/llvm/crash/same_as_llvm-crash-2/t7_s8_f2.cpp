template<int (&T)[3]>
void FuncTemplate() { (void)T[0]; }

template<int i> class A {};
template<int i> void g(A<i> &) {
    static int InternalVar[3] = {4,3,2};
    FuncTemplate<InternalVar>();
}

int main()
{
  A<1> a;
  g(a);
}
