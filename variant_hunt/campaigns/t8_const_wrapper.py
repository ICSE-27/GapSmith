"""Campaign t8: mutations of llvm/crash/test8.cpp
Seed: trailing return type instantiating constant-wrapper template ->
segfault in DeduceAutoType while instantiating the wrapper.
Axes: wrapper shape, operator form, value kinds, call nesting.
"""

SHAPES = [
    # original
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Plus {{
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {{
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }}
}};

constexpr auto cwv = ConstantWrapper<Plus{{}}>{{}}(ConstantWrapper<42>{{}}, ConstantWrapper<17>{{}});''',
    # multiply instead of plus
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Times {{
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) * static_cast<U&&>(u)) {{
    return static_cast<T&&>(t) * static_cast<U&&>(u);
  }}
}};

constexpr auto cwv = ConstantWrapper<Times{{}}>{{}}(ConstantWrapper<42>{{}}, ConstantWrapper<17>{{}});''',
    # three args
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Sum3 {{
  template <class T, class U, class V>
  constexpr auto operator()(T&& t, U&& u, V&& v) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u) + static_cast<V&&>(v)) {{
    return static_cast<T&&>(t) + static_cast<U&&>(u) + static_cast<V&&>(v);
  }}
}};

constexpr auto cwv = ConstantWrapper<Sum3{{}}>{{}}(ConstantWrapper<1>{{}}, ConstantWrapper<2>{{}}, ConstantWrapper<3>{{}});''',
    # nested call
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Plus {{
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {{
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }}
}};

constexpr auto inner = ConstantWrapper<Plus{{}}>{{}}(ConstantWrapper<42>{{}}, ConstantWrapper<17>{{}});
constexpr auto cwv = ConstantWrapper<Plus{{}}>{{}}(inner, ConstantWrapper<1>{{}});''',
    # unary negate
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Neg {{
  template <class T>
  constexpr auto operator()(T&& t) const -> decltype(-static_cast<T&&>(t)) {{
    return -static_cast<T&&>(t);
  }}
}};

constexpr auto cwv = ConstantWrapper<Neg{{}}>{{}}(ConstantWrapper<42>{{}});''',
    # double values
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Plus {{
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {{
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }}
}};

constexpr auto cwv = ConstantWrapper<Plus{{}}>{{}}(ConstantWrapper<4.2>{{}}, ConstantWrapper<1.7>{{}});''',
    # used inside function instead of global
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto operator()(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Plus {{
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {{
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }}
}};

int main() {{
  constexpr auto cwv = ConstantWrapper<Plus{{}}>{{}}(ConstantWrapper<42>{{}}, ConstantWrapper<17>{{}});
  return decltype(cwv)::value - 59;
}}''',
    # member function instead of operator()
    '''template <auto V>
struct ConstantWrapper {{
  static constexpr auto value = V;

  template <class... Ts>
  constexpr auto apply(Ts... args) const -> ConstantWrapper<value(Ts::value...)> {{
    return {{}};
  }}
}};

struct Plus {{
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const -> decltype(static_cast<T&&>(t) + static_cast<U&&>(u)) {{
    return static_cast<T&&>(t) + static_cast<U&&>(u);
  }}
}};

constexpr auto cwv = ConstantWrapper<Plus{{}}>{{}}.apply(ConstantWrapper<42>{{}}, ConstantWrapper<17>{{}});''',
]

FLAGS = [["-std=c++20", "-pedantic-errors"], ["-std=c++20"], ["-std=c++20", "-O2"], ["-std=c++23", "-pedantic-errors"]]

def generate():
    for si, shape in enumerate(SHAPES):
        src = shape.replace("{{", "{").replace("}}", "}") + "\n"
        for fi, fl in enumerate(FLAGS):
            yield {"name": f"t8_s{si}_f{fi}", "src": src, "tag": "clangxx",
                   "flags": fl, "ext": ".cpp"}
