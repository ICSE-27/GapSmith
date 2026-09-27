template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        int dummy { 0 };
        void method() requires (sizeof(string) > 1) {}
    } object;
    object.method();
};
int main() { foo<void>(); }
