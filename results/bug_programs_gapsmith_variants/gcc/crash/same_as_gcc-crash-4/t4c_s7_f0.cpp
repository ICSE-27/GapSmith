template<typename T>
void foo() {
    static constexpr char string[] = "mew";
    struct s1_t {
        struct s2_t {
            int dummy { 0 };
            char* ptr { static_cast<char*>(::operator new(sizeof(string)))};
        } s2;
    } object;
};
template void foo<int>();
template void foo<long>();
int main() { foo<void>(); }
