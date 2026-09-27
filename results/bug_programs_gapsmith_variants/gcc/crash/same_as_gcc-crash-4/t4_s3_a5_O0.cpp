template<typename T>
void foo() {
    static constexpr unsigned arr[8] = {};
    struct s1_t {
        struct s2_t {
            struct s3_t {
                int dummy { 0 };
                char* ptr { static_cast<char*>(::operator new(sizeof(arr)))};
            } s3;
        } s2;
    } object;
};
int main() { foo<void>(); }
