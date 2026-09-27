template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };
    inner(Args...) -> inner<decltype((Args{}, ...))>;
};
int main() {
    outer();
}
