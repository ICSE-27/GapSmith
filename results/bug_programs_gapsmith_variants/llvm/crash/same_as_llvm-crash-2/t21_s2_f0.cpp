template<int& T> void FuncTemplate() { (void)T; }
struct S { int a; int b; };
struct W {
    template<typename Self>
    void f(this Self&& self) {
        static S InternalVar = {1, 43};
        FuncTemplate<InternalVar.b>();
    }
};
int main() { W w; w.f(); }
