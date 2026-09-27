int main() {
    auto lam = []<typename T>() {
        static constexpr char string[] = "mew";
        struct s1_t {
            struct s2_t {
                int dummy { 0 };
                char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
            } s2;
        } object;
    };
    lam.template operator()<int>();
}
