template<typename T>
struct wrap {
    void foo() {
        static constexpr double d[2] = {0.5, 1.5};
        struct s1_t {
            struct s2_t {
                int dummy { 0 };
                char* ptr { static_cast<char*>(::operator new(sizeof(d)))};
            } s2;
        } object;
    }
};
int main() { wrap<int> w; w.foo(); }
