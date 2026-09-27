template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        auto get() -> decltype(sizeof...(Args)) { return 0; }
    };
    inner(Args...) -> inner<decltype(sizeof...(Args))>;
};
int main() {
    outer();
}
