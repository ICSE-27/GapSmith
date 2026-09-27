template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
};
template <typename... Args>
void bar() {
    auto lam = [] static { outer<>(); };
    lam();
}
int main() { bar<int>(); }
