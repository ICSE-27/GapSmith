template <typename... Args>
struct outer {
    template <typename Type = long>
    struct inner {
        inner(Args...) { }
    };

    inner(Args...) -> inner<int>;
};

int main() {
    outer();
}
