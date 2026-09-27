template<typename T>
struct wrap {
    void foo() {
        static constexpr T arr[4] = {};
        struct s1_t {
            struct s2_t {
                int dummy { 0 };
                char* ptr { static_cast<char*>(::operator new(sizeof(arr)))};
            } s2;
        } object;
    }
};
int main() { wrap<int> w; w.foo(); }
