template <typename... Args>
struct outer {
    template <typename Type>
    struct inner {
        inner(Args...) { }
        template <typename U>
        struct innermost {
            innermost(U, Args...) { }
        };
        template <typename U>
        innermost(U, Args...) -> innermost<U>;
    };

    inner(Args...) -> inner<int>;
};

int main() {
    outer();
}
