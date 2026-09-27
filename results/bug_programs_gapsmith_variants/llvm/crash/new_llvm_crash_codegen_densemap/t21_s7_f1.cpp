template<int& T> void FuncTemplate() { (void)T; }
template<int i>
void g(int x = []()
    {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
        return 0;
    }()) {
    (void)x;
}
int main() { g<1>(); }
