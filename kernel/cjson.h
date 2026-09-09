// cjson.h -- canonical JSON: the writer, and a strict reader.
//
// BLUEPRINT_v0.2.md section 12: "UTF-8; keys sorted by code point; separators
// `,` and `:` with no spaces; no ASCII escaping of non-ASCII; no NaN, no
// Infinity, no bare floats; every 64-bit integer written as a decimal string;
// unknown keys are `fatal`."
//
// Written here and not vendored, because the canonical form IS the contract:
// the row's hash is taken over these exact bytes, and a library that pretty
// prints, reorders, or writes 1e+16 for an integer produces a second head for
// one tape. Section 12 records the measurement that forced this: the same
// double serializes as `1e+16` in one language and `10000000000000000` in
// another.
//
// Amendment 1 item 17 decides string-versus-number by DECLARED WIDTH, not by
// magnitude: every field declared 64-bit -- amount_fix, t_mono_ns, rev, and
// every id -- is a canonical decimal string; int16 margins and small counters
// are JSON numbers. The table lives in cjson.cpp and is the same table
// tests/chain_check.py carries.
//
// Amendment 1 item 16: `ms` is a key on the row that the hashed body excludes.
// It is not a sidecar. body() is what the chain covers: the row minus `prev`,
// `h` and `ms`.
//
// Nothing here allocates a float, converts to one, or accepts one. A double
// cannot be constructed through this interface, so a float cannot reach a
// canonical form by accident.

#ifndef FACTOR_CJSON_H
#define FACTOR_CJSON_H

#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace cjson {

// The declared width of a field, from Amendment 1 item 17's rule.
enum class Width {
    Unknown,   // not in the table: a string, an object, an array, or a bool
    U64, I64,  // -> canonical decimal STRING
    U32, U16, I16, U8,  // -> JSON number, range checked
};

Width width_of(const std::string &key);

// The largest integer a JSON reader in another language can be trusted with.
// A bare integer above this is fatal; that is what the declared-width rule is
// protecting, and section 12 says so.
inline constexpr std::int64_t kJsSafeInt = 9007199254740991LL;  // 2**53 - 1

class Value {
public:
    enum class Type { Null, Bool, Int, String, Array, Object };

    Value() : type_(Type::Null) {}
    static Value null() { return Value(); }
    static Value boolean(bool b);
    static Value integer(std::int64_t v);   // a JSON number; for a field the
                                            // width table declares narrower
                                            // than 64 bits
    // A field declared 64-bit. Formatted here to its canonical decimal
    // spelling and carried as a string, which is what the tape holds and what
    // tests/chain_check.py's model holds. There is no path by which a 64-bit
    // field becomes a bare JSON number.
    static Value wide(std::int64_t v);
    static Value string(std::string s);
    static Value array();
    static Value object();

    Type type() const { return type_; }
    bool is_null() const { return type_ == Type::Null; }

    bool as_bool() const { return bool_; }
    std::int64_t as_int() const { return int_; }
    const std::string &as_string() const { return str_; }
    const std::vector<Value> &items() const { return arr_; }
    const std::map<std::string, Value> &members() const { return obj_; }

    void push(Value v);                       // array
    void set(const std::string &k, Value v);  // object
    const Value *find(const std::string &k) const;
    bool has(const std::string &k) const { return find(k) != nullptr; }

private:
    Type type_;
    bool bool_ = false;
    std::int64_t int_ = 0;
    std::string str_;
    std::vector<Value> arr_;
    // std::map keeps the keys sorted by byte order, which for UTF-8 is code
    // point order -- so the canonical key order is a property of the container
    // rather than a sort somebody can forget to call.
    std::map<std::string, Value> obj_;
};

// Canonical bytes. Returns false and fills `error` when the value cannot be
// written canonically: a 64-bit-declared field holding something other than a
// canonical decimal string, a narrow field out of its range, a bare integer
// above 2**53-1, or a non-UTF-8 string. Nothing is coerced.
bool write(const Value &v, std::string *out, std::string *error);

// The bytes the row's hash covers: the row minus `prev`, `h` and `ms`.
bool body(const Value &row, std::string *out, std::string *error);

// A strict reader. It accepts exactly what write() emits and refuses
// everything else -- any whitespace, keys out of order, a duplicate key, a
// leading zero, a plus sign, an exponent, a fraction, a literal other than
// true/false/null, a lone surrogate, trailing bytes. A reader that is more
// permissive than its writer is a reader that accepts two spellings of one
// tape.
bool parse(const std::string &text, Value *out, std::string *error);

// Section 12: unknown keys are fatal. `kind` is the row's `k`. Returns false
// with the offending key named when the row carries a key its kind does not
// declare, or when the kind itself is unknown.
bool validate_row_keys(const Value &row, std::string *error);

// The canonical decimal spelling rule for a 64-bit field: an optional minus
// only when signed, then digits, with no leading zero unless the value is
// exactly "0".
bool is_canonical_decimal(const std::string &s, bool signed_ok);

// The self-check compiled into `factor selftest`. Returns the number of
// failures; 0 is green.
int cjson_selftest();

} // namespace cjson

#endif // FACTOR_CJSON_H
