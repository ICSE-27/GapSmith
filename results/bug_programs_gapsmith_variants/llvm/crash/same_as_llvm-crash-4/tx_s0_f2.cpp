template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        using Alias = Type;
        inner(Args...) { }
    };
    inner(Args...) -> inner<int>;
};
template <typename... Args>
outer<Args...>::inner<int>::Alias helper(outer<Args...> o) { return {}; }
int main() {
    outer();
}
