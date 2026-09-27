template<int& T>
void FuncTemplate() { (void)T; }

template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) {
            static int InternalVar = 43;
            FuncTemplate<InternalVar>();
        }
    };
    inner(Args...) -> inner<int>;
};
int main() {
    outer();
}
