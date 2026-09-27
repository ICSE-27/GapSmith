template<int& T> void FuncTemplate() { (void)T; }
struct S {
    template<typename Self>
    void f(this Self&& self, int n) {
        if (n <= 0) {
            static int InternalVar = 43;
            FuncTemplate<InternalVar>();
            return;
        }
        self.f(n - 1);
    }
};
int main() { S s; s.f(1); }
