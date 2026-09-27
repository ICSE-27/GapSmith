template <typename... Args>
template <typename... BArgs>
struct outer_two;

template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args..., Type) { }
    };

    inner(Args..., int) -> inner<int>;
};

int main() {
    outer();
}
