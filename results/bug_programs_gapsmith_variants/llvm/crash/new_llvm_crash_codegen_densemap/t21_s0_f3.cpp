template<int& T> void FuncTemplate() { (void)T; }
template<int i> void g() {
    []()
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }();
}
int main() { g<1>(); }
