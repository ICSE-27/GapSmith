template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            void method() requires (sizeof(string) > 1) {}
        } s2;
    } object;
    object.s2.method();
};
int main() { foo<void>(); }
