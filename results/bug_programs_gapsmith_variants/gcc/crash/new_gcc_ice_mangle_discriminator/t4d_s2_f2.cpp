template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            s2_t() requires (sizeof(string) > 1) {}
        } s2;
    } object;
};
int main() { foo<void>(); }
