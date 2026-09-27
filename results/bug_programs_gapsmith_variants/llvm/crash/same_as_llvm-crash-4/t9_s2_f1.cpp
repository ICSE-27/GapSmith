template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
    };

    inner(Args...) -> inner<decltype(sizeof...(Args))>;
};

int main() {
    outer();
}
