template<int& T> void FuncTemplate() { (void)T; }
struct S {
    template<typename Self>
    void f(this Self&& self) {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
    }
};
int main() { S s; s.f(); }
