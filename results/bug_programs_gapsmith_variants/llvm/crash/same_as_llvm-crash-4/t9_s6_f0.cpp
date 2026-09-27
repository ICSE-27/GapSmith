template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        inner(Type, Args...) { }
    };

    inner(Args...) -> inner<int>;
    inner(int, Args...) -> inner<long>;
};

int main() {
    outer();
}
