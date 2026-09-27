template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            static void smethod() requires (sizeof(string) > 1) {}
        } s2;
    } object;
    decltype(object)::s2_t::smethod();
};
int main() { foo<void>(); }
