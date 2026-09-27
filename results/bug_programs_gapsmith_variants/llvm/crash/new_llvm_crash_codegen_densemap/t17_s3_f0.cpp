template<int& T> void FuncTemplate() { (void)T; }
struct M {
    template<typename... I>
    int operator[](I... i) {
        static int InternalVar = 43;
        FuncTemplate<InternalVar>();
        return 0;
    }
};
int main() { M m; m[1, 2]; }
