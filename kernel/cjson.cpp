// cjson.cpp -- canonical JSON, written to be the same bytes the Python model
// writes. tests/cjson_cross.py measures the two against each other.

#include "cjson.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace cjson {
namespace {

// Amendment 1 item 17's rule made mechanical. This is the same table
// tests/chain_check.py carries as DECLARED_WIDTH; the checker reads the width,
// not a hand-kept list of which fields happen to be big today.
struct WidthRow { const char *key; Width w; };

const WidthRow kWidths[] = {
    // 64-bit -> canonical decimal string
    { "t_mono_ns", Width::U64 }, { "rev", Width::U64 },
    { "src_rev", Width::U64 },   { "judged_rev", Width::U64 },
    { "id", Width::U64 },        { "party", Width::U64 },
    { "blocked_by", Width::U64 },{ "batch", Width::U64 },
    { "opened_ns", Width::U64 }, { "due_ns", Width::U64 },
    { "horizon_ns", Width::U64 },{ "release_ns", Width::U64 },
    { "amount_fix", Width::I64 },{ "offset", Width::U64 },
    { "generation", Width::U64 },
    // Amendment 4 item 9: the fingerprint's `row` became `row_orig`, the row's
    // index on the UNCOMPACTED tape. Compaction never renumbers.
    { "seg", Width::U64 },       { "row_orig", Width::U64 },
    { "count", Width::U64 },
    // narrower -> JSON number
    { "m_hand", Width::I16 },    { "m_check", Width::I16 },
    { "m_guard", Width::I16 },   { "n_wit", Width::U16 },
    { "n_wait", Width::U16 },    { "tie", Width::U16 },
    { "flags", Width::U16 },     { "pos", Width::U16 },
    { "f", Width::U16 },         { "cls", Width::U32 },
    { "band", Width::U32 },      { "seat", Width::U32 },
    { "unit", Width::U32 },      { "frame_cap", Width::U32 },
    { "lag_ms", Width::U32 },    { "rung", Width::U8 },
};

// Section 12's kinds, with the keys each declares. Unknown keys are fatal, so
// this table is a fence and not documentation.
struct RowKind { const char *kind; const char *keys[20]; };

const RowKind kRowKinds[] = {
    { "verb", { "k", "ms", "t_mono_ns", "id", "judged_rev", "verb", "reason",
                "flags", "band", "rung", "m_hand", "m_check", "m_guard",
                "batch", "pos", "prev", "h", nullptr } },
    { "frame", { "k", "ms", "t_mono_ns", "lane", "generation", "offset",
                 "frame_h", "prev", "h", nullptr } },
    { "fingerprint", { "k", "ms", "head", "seg", "row_orig", "fp_prev", "fp_h",
                       "prev", "h", nullptr } },
    { "tombstone", { "k", "ms", "span_prev", "span_h", "count", "fp_before",
                     "fp_after", "sig", "prev", "h", nullptr } },
};

// Amendment 1 item 16: `ms` is a key on the row that the hashed body excludes.
const char *const kExcludedFromBody[] = { "prev", "h", "ms" };

bool range_of(Width w, std::int64_t *lo, std::int64_t *hi) {
    switch (w) {
    case Width::I16: *lo = -32768;    *hi = 32767;      return true;
    case Width::U16: *lo = 0;         *hi = 65535;      return true;
    case Width::U32: *lo = 0;         *hi = 4294967295LL; return true;
    case Width::U8:  *lo = 0;         *hi = 255;        return true;
    default: return false;
    }
}

bool valid_utf8(const std::string &s, std::string *error) {
    const auto *p = reinterpret_cast<const unsigned char *>(s.data());
    const std::size_t n = s.size();
    std::size_t i = 0;
    while (i < n) {
        const unsigned char c = p[i];
        std::size_t need;
        std::uint32_t cp;
        if (c < 0x80u) { i++; continue; }
        else if ((c & 0xE0u) == 0xC0u) { need = 1; cp = c & 0x1Fu; }
        else if ((c & 0xF0u) == 0xE0u) { need = 2; cp = c & 0x0Fu; }
        else if ((c & 0xF8u) == 0xF0u) { need = 3; cp = c & 0x07u; }
        else { *error = "invalid UTF-8 lead byte"; return false; }

        if (i + need >= n + 0 && i + need > n - 1) {
            *error = "truncated UTF-8 sequence";
            return false;
        }
        for (std::size_t k = 1; k <= need; k++) {
            const unsigned char cc = p[i + k];
            if ((cc & 0xC0u) != 0x80u) {
                *error = "invalid UTF-8 continuation byte";
                return false;
            }
            cp = (cp << 6) | (cc & 0x3Fu);
        }
        // Overlong, surrogate and out-of-range forms are all refused: an
        // encoder with two spellings for one code point is an encoder with two
        // hashes for one row.
        if ((need == 1 && cp < 0x80u) ||
            (need == 2 && cp < 0x800u) ||
            (need == 3 && cp < 0x10000u)) {
            *error = "overlong UTF-8 sequence";
            return false;
        }
        if (cp >= 0xD800u && cp <= 0xDFFFu) {
            *error = "UTF-8 encoded surrogate";
            return false;
        }
        if (cp > 0x10FFFFu) {
            *error = "UTF-8 code point above U+10FFFF";
            return false;
        }
        i += need + 1;
    }
    return true;
}

void escape_into(const std::string &s, std::string *out) {
    // Exactly Python's json.dumps(..., ensure_ascii=False): the two-character
    // escapes for backslash, quote, backspace, formfeed, newline, return and
    // tab; \u00xx with lowercase hex for every other C0 control; everything
    // else, including U+007F and all non-ASCII, passed through raw.
    static const char *const hexdigits = "0123456789abcdef";
    out->push_back('"');
    for (const char ch : s) {
        const auto c = static_cast<unsigned char>(ch);
        switch (c) {
        case '"':  out->append("\\\""); break;
        case '\\': out->append("\\\\"); break;
        case 0x08: out->append("\\b");  break;
        case 0x0C: out->append("\\f");  break;
        case 0x0A: out->append("\\n");  break;
        case 0x0D: out->append("\\r");  break;
        case 0x09: out->append("\\t");  break;
        default:
            if (c < 0x20u) {
                out->append("\\u00");
                out->push_back(hexdigits[(c >> 4) & 0x0Fu]);
                out->push_back(hexdigits[c & 0x0Fu]);
            } else {
                out->push_back(ch);
            }
        }
    }
    out->push_back('"');
}

bool write_value(const Value &v, const std::string &key,
                 std::string *out, std::string *error);

bool write_member(const std::string &key, const Value &v,
                  std::string *out, std::string *error) {
    escape_into(key, out);
    out->push_back(':');
    return write_value(v, key, out, error);
}

bool write_value(const Value &v, const std::string &key,
                 std::string *out, std::string *error) {
    const Width w = width_of(key);

    switch (v.type()) {
    case Value::Type::Null:
        if (w != Width::Unknown) {
            *error = key + " is a declared-width field and cannot be null";
            return false;
        }
        out->append("null");
        return true;

    case Value::Type::Bool:
        if (w != Width::Unknown) {
            *error = key + " is a declared-width field and cannot be a bool";
            return false;
        }
        out->append(v.as_bool() ? "true" : "false");
        return true;

    case Value::Type::Int: {
        if (w == Width::U64 || w == Width::I64) {
            *error = key + " is declared 64-bit and must be a canonical "
                           "decimal string, not a JSON number";
            return false;
        }
        const std::int64_t n = v.as_int();
        std::int64_t lo = 0;
        std::int64_t hi = 0;
        if (range_of(w, &lo, &hi)) {
            if (n < lo || n > hi) {
                char buf[128];
                std::snprintf(buf, sizeof buf,
                              " is declared narrower and %lld does not fit",
                              static_cast<long long>(n));
                *error = key + buf;
                return false;
            }
        } else if (n > kJsSafeInt || n < -kJsSafeInt) {
            // Section 12: a bare integer above 2**53-1 does not survive a
            // reader in another language, which is what the declared-width
            // rule exists to prevent.
            *error = "a bare integer exceeds 2**53-1; every 64-bit integer is "
                     "a decimal string";
            return false;
        }
        char buf[24];
        std::snprintf(buf, sizeof buf, "%lld", static_cast<long long>(n));
        out->append(buf);
        return true;
    }

    case Value::Type::String: {
        const std::string &s = v.as_string();
        if (w == Width::U64 || w == Width::I64) {
            if (!is_canonical_decimal(s, w == Width::I64)) {
                *error = key + " is declared 64-bit and " + s +
                         " is not a canonical decimal string";
                return false;
            }
        } else if (w != Width::Unknown) {
            *error = key + " is declared narrower than 64 bits and must be a "
                           "JSON number, not a string";
            return false;
        }
        if (!valid_utf8(s, error)) {
            *error = key + ": " + *error;
            return false;
        }
        escape_into(s, out);
        return true;
    }

    case Value::Type::Array:
        out->push_back('[');
        for (std::size_t i = 0; i < v.items().size(); i++) {
            if (i > 0) { out->push_back(','); }
            if (!write_value(v.items()[i], std::string(), out, error)) {
                return false;
            }
        }
        out->push_back(']');
        return true;

    case Value::Type::Object:
        out->push_back('{');
        {
            bool first = true;
            // std::map iterates in byte order, which for UTF-8 is code point
            // order. The sort is the container's, not a step to remember.
            for (const auto &kv : v.members()) {
                if (!first) { out->push_back(','); }
                first = false;
                if (!valid_utf8(kv.first, error)) {
                    *error = "object key: " + *error;
                    return false;
                }
                if (!write_member(kv.first, kv.second, out, error)) {
                    return false;
                }
            }
        }
        out->push_back('}');
        return true;
    }
    *error = "unreachable value type";
    return false;
}

// ------------------------------------------------------------ the reader

class Reader {
public:
    Reader(const std::string &text) : s_(text) {}

    bool parse_document(Value *out, std::string *error) {
        if (!valid_utf8(s_, error)) {
            return false;
        }
        if (!parse_value(out, std::string(), error)) {
            return false;
        }
        if (i_ != s_.size()) {
            *error = "trailing bytes after the value";
            return false;
        }
        return true;
    }

private:
    const std::string &s_;
    std::size_t i_ = 0;

    bool eof() const { return i_ >= s_.size(); }
    char peek() const { return s_[i_]; }

    bool expect(char c, std::string *error) {
        if (eof() || s_[i_] != c) {
            *error = std::string("expected ") + c;
            return false;
        }
        i_++;
        return true;
    }

    bool parse_string(std::string *out, std::string *error) {
        if (!expect('"', error)) { return false; }
        out->clear();
        while (true) {
            if (eof()) { *error = "unterminated string"; return false; }
            const auto c = static_cast<unsigned char>(s_[i_]);
            if (c == '"') { i_++; return true; }
            if (c < 0x20u) {
                *error = "a raw control character in a string";
                return false;
            }
            if (c != '\\') { out->push_back(s_[i_++]); continue; }

            i_++;
            if (eof()) { *error = "a trailing backslash"; return false; }
            const char e = s_[i_++];
            switch (e) {
            case '"':  out->push_back('"');  break;
            case '\\': out->push_back('\\'); break;
            case 'b':  out->push_back('\b'); break;
            case 'f':  out->push_back('\f'); break;
            case 'n':  out->push_back('\n'); break;
            case 'r':  out->push_back('\r'); break;
            case 't':  out->push_back('\t'); break;
            case 'u': {
                // The writer emits \u only for a C0 control with no short
                // form, always as \u00xx with lowercase hex. Anything else is
                // a second spelling and is refused.
                if (i_ + 4 > s_.size()) {
                    *error = "a truncated \\u escape";
                    return false;
                }
                if (s_[i_] != '0' || s_[i_ + 1] != '0') {
                    *error = "a \\u escape outside the C0 range";
                    return false;
                }
                unsigned value = 0;
                for (std::size_t k = 2; k < 4; k++) {
                    const char h = s_[i_ + k];
                    unsigned nib;
                    if (h >= '0' && h <= '9') { nib = static_cast<unsigned>(h - '0'); }
                    else if (h >= 'a' && h <= 'f') { nib = static_cast<unsigned>(h - 'a' + 10); }
                    else {
                        *error = "a \\u escape with non-lowercase-hex digits";
                        return false;
                    }
                    value = (value << 4) | nib;
                }
                if (value >= 0x20u) {
                    *error = "a \\u escape for a character the writer emits raw";
                    return false;
                }
                if (value == 0x08u || value == 0x09u || value == 0x0Au ||
                    value == 0x0Cu || value == 0x0Du) {
                    *error = "a \\u escape for a character with a short form";
                    return false;
                }
                i_ += 4;
                out->push_back(static_cast<char>(value));
                break;
            }
            default:
                *error = std::string("an unsupported escape \\") + e;
                return false;
            }
        }
    }

    bool parse_number(Value *out, std::string *error) {
        const std::size_t start = i_;
        if (!eof() && s_[i_] == '-') { i_++; }
        if (eof() || s_[i_] < '0' || s_[i_] > '9') {
            *error = "a number with no digits";
            return false;
        }
        const std::size_t digits_start = i_;
        while (!eof() && s_[i_] >= '0' && s_[i_] <= '9') { i_++; }
        const std::size_t digits = i_ - digits_start;
        if (digits > 1 && s_[digits_start] == '0') {
            *error = "a number with a leading zero";
            return false;
        }
        if (!eof() && (s_[i_] == '.' || s_[i_] == 'e' || s_[i_] == 'E')) {
            *error = "a fraction or an exponent: section 12 forbids bare floats";
            return false;
        }
        const std::string text = s_.substr(start, i_ - start);
        errno = 0;
        char *end = nullptr;
        const long long v = std::strtoll(text.c_str(), &end, 10);
        if (errno != 0 || end == nullptr || *end != '\0') {
            *error = "a number outside int64";
            return false;
        }
        *out = Value::integer(v);
        return true;
    }

    bool parse_value(Value *out, const std::string &key, std::string *error) {
        if (eof()) { *error = "an empty document"; return false; }
        const char c = peek();

        if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
            *error = "whitespace: the canonical form has none";
            return false;
        }
        if (c == '{') { return parse_object(out, error); }
        if (c == '[') { return parse_array(out, error); }
        if (c == '"') {
            std::string s;
            if (!parse_string(&s, error)) { return false; }
            const Width w = width_of(key);
            if ((w == Width::U64 || w == Width::I64) &&
                !is_canonical_decimal(s, w == Width::I64)) {
                *error = key + " is declared 64-bit and " + s +
                         " is not a canonical decimal string";
                return false;
            }
            if (w != Width::Unknown && w != Width::U64 && w != Width::I64) {
                *error = key + " is declared narrower than 64 bits and must be "
                               "a JSON number";
                return false;
            }
            *out = Value::string(s);
            return true;
        }
        if (c == '-' || (c >= '0' && c <= '9')) {
            if (!parse_number(out, error)) { return false; }
            const Width w = width_of(key);
            if (w == Width::U64 || w == Width::I64) {
                *error = key + " is declared 64-bit and must be a canonical "
                               "decimal string, not a JSON number";
                return false;
            }
            std::int64_t lo = 0;
            std::int64_t hi = 0;
            if (range_of(w, &lo, &hi)) {
                if (out->as_int() < lo || out->as_int() > hi) {
                    *error = key + " does not fit its declared width";
                    return false;
                }
            } else if (out->as_int() > kJsSafeInt || out->as_int() < -kJsSafeInt) {
                *error = "a bare integer exceeds 2**53-1";
                return false;
            }
            return true;
        }
        if (s_.compare(i_, 4, "true") == 0)  { i_ += 4; *out = Value::boolean(true);  return true; }
        if (s_.compare(i_, 5, "false") == 0) { i_ += 5; *out = Value::boolean(false); return true; }
        if (s_.compare(i_, 4, "null") == 0)  { i_ += 4; *out = Value::null();         return true; }
        *error = "an unrecognised token";
        return false;
    }

    bool parse_array(Value *out, std::string *error) {
        if (!expect('[', error)) { return false; }
        *out = Value::array();
        if (!eof() && peek() == ']') { i_++; return true; }
        while (true) {
            Value item;
            if (!parse_value(&item, std::string(), error)) { return false; }
            out->push(item);
            if (eof()) { *error = "an unterminated array"; return false; }
            if (peek() == ',') { i_++; continue; }
            if (peek() == ']') { i_++; return true; }
            *error = "expected , or ] in an array";
            return false;
        }
    }

    bool parse_object(Value *out, std::string *error) {
        if (!expect('{', error)) { return false; }
        *out = Value::object();
        if (!eof() && peek() == '}') { i_++; return true; }
        std::string previous_key;
        bool have_previous = false;
        while (true) {
            std::string key;
            if (eof() || peek() != '"') {
                *error = "expected a quoted key";
                return false;
            }
            if (!parse_string(&key, error)) { return false; }
            if (have_previous && !(previous_key < key)) {
                // Strictly increasing catches an unsorted key and a duplicate
                // key with one comparison, and both are the same defect: a
                // second spelling of one object.
                *error = (previous_key == key)
                             ? ("a duplicate key " + key)
                             : ("keys out of code point order at " + key);
                return false;
            }
            previous_key = key;
            have_previous = true;

            if (!expect(':', error)) { return false; }
            Value v;
            if (!parse_value(&v, key, error)) { return false; }
            out->set(key, v);

            if (eof()) { *error = "an unterminated object"; return false; }
            if (peek() == ',') { i_++; continue; }
            if (peek() == '}') { i_++; return true; }
            *error = "expected , or } in an object";
            return false;
        }
    }
};

} // namespace

// ------------------------------------------------------------------ Value

Value Value::boolean(bool b) { Value v; v.type_ = Type::Bool; v.bool_ = b; return v; }
Value Value::integer(std::int64_t n) { Value v; v.type_ = Type::Int; v.int_ = n; return v; }
Value Value::string(std::string s) { Value v; v.type_ = Type::String; v.str_ = std::move(s); return v; }
Value Value::array() { Value v; v.type_ = Type::Array; return v; }
Value Value::object() { Value v; v.type_ = Type::Object; return v; }

Value Value::wide(std::int64_t n) {
    char buf[24];
    std::snprintf(buf, sizeof buf, "%lld", static_cast<long long>(n));
    return Value::string(std::string(buf));
}

void Value::push(Value v) { arr_.push_back(std::move(v)); }
void Value::set(const std::string &k, Value v) { obj_[k] = std::move(v); }

const Value *Value::find(const std::string &k) const {
    const auto it = obj_.find(k);
    return (it == obj_.end()) ? nullptr : &it->second;
}

// ------------------------------------------------------------------ API

Width width_of(const std::string &key) {
    for (const WidthRow &row : kWidths) {
        if (key == row.key) { return row.w; }
    }
    return Width::Unknown;
}

bool is_canonical_decimal(const std::string &s, bool signed_ok) {
    if (s.empty()) { return false; }
    std::size_t i = 0;
    if (s[0] == '-') {
        if (!signed_ok) { return false; }
        i = 1;
    }
    if (i >= s.size()) { return false; }
    for (std::size_t k = i; k < s.size(); k++) {
        if (s[k] < '0' || s[k] > '9') { return false; }
    }
    const std::size_t digits = s.size() - i;
    if (digits > 1 && s[i] == '0') { return false; }
    return true;
}

bool write(const Value &v, std::string *out, std::string *error) {
    out->clear();
    error->clear();
    return write_value(v, std::string(), out, error);
}

bool body(const Value &row, std::string *out, std::string *error) {
    if (row.type() != Value::Type::Object) {
        *error = "a row body is taken over an object";
        return false;
    }
    Value stripped = Value::object();
    for (const auto &kv : row.members()) {
        bool excluded = false;
        for (const char *name : kExcludedFromBody) {
            if (kv.first == name) { excluded = true; break; }
        }
        if (!excluded) { stripped.set(kv.first, kv.second); }
    }
    return write(stripped, out, error);
}

bool parse(const std::string &text, Value *out, std::string *error) {
    error->clear();
    Reader r(text);
    return r.parse_document(out, error);
}

bool validate_row_keys(const Value &row, std::string *error) {
    if (row.type() != Value::Type::Object) {
        *error = "a row is an object";
        return false;
    }
    const Value *k = row.find("k");
    if (k == nullptr || k->type() != Value::Type::String) {
        *error = "a row with no string kind `k`";
        return false;
    }
    const RowKind *kind = nullptr;
    for (const RowKind &rk : kRowKinds) {
        if (k->as_string() == rk.kind) { kind = &rk; break; }
    }
    if (kind == nullptr) {
        *error = "unknown row kind " + k->as_string();
        return false;
    }
    for (const auto &kv : row.members()) {
        bool declared = false;
        for (std::size_t i = 0; kind->keys[i] != nullptr; i++) {
            if (kv.first == kind->keys[i]) { declared = true; break; }
        }
        if (!declared) {
            *error = "unknown key " + kv.first + " on a " + k->as_string() +
                     " row -- fatal";
            return false;
        }
    }
    return true;
}

// ------------------------------------------------------------- the selftest

namespace {

int expect_write(const Value &v, const char *want, const char *label,
                 int *checks) {
    std::string out;
    std::string err;
    (*checks)++;
    if (!write(v, &out, &err)) {
        std::printf("      %s: write refused: %s\n", label, err.c_str());
        return 1;
    }
    if (out != want) {
        std::printf("      %s: wrote %s, wanted %s\n", label, out.c_str(), want);
        return 1;
    }
    return 0;
}

int expect_refused(const char *text, const char *label, int *checks) {
    Value v;
    std::string err;
    (*checks)++;
    if (parse(std::string(text), &v, &err)) {
        std::printf("      %s: accepted %s, which is not canonical\n",
                    label, text);
        return 1;
    }
    return 0;
}

} // namespace

int cjson_selftest() {
    int fails = 0;
    int checks = 0;

    // Keys sort by code point, separators carry no spaces.
    {
        Value o = Value::object();
        o.set("b", Value::integer(2));
        o.set("a", Value::integer(1));
        o.set("A", Value::integer(0));
        fails += expect_write(o, "{\"A\":0,\"a\":1,\"b\":2}", "key order",
                              &checks);
    }
    // A declared 64-bit field is a canonical decimal string.
    {
        Value o = Value::object();
        o.set("t_mono_ns", Value::wide(9007199254740993LL));
        fails += expect_write(o, "{\"t_mono_ns\":\"9007199254740993\"}",
                              "64-bit as a string", &checks);
    }
    // A narrow field is a number.
    {
        Value o = Value::object();
        o.set("m_hand", Value::integer(-32768));
        fails += expect_write(o, "{\"m_hand\":-32768}", "int16 as a number",
                              &checks);
    }
    // Non-ASCII passes through raw; the C0 controls escape as the model does.
    {
        Value o = Value::object();
        o.set("lane", Value::string("caf\xC3\xA9\x01\n"));
        fails += expect_write(o, "{\"lane\":\"caf\xC3\xA9\\u0001\\n\"}",
                              "escaping", &checks);
    }
    // The body excludes prev, h and ms, and nothing else.
    {
        Value row = Value::object();
        row.set("k", Value::string("frame"));
        row.set("ms", Value::integer(17));
        row.set("lane", Value::string("files"));
        row.set("prev", Value::string("00"));
        row.set("h", Value::string("11"));
        std::string out;
        std::string err;
        checks++;
        if (!body(row, &out, &err) ||
            out != "{\"k\":\"frame\",\"lane\":\"files\"}") {
            std::printf("      body: got %s\n", out.c_str());
            fails++;
        }
    }
    // The strict reader refuses every second spelling.
    fails += expect_refused("{\"b\":1,\"a\":2}", "unsorted keys", &checks);
    fails += expect_refused("{\"a\":1,\"a\":2}", "duplicate key", &checks);
    fails += expect_refused("{ \"a\":1}", "leading space", &checks);
    fails += expect_refused("{\"a\": 1}", "space after colon", &checks);
    fails += expect_refused("{\"a\":1.5}", "a fraction", &checks);
    fails += expect_refused("{\"a\":1e3}", "an exponent", &checks);
    fails += expect_refused("{\"a\":01}", "a leading zero", &checks);
    fails += expect_refused("{\"a\":+1}", "a plus sign", &checks);
    fails += expect_refused("{\"a\":\"\\u0041\"}", "a needless \\u", &checks);
    fails += expect_refused("{\"a\":\"\\/\"}", "an escaped solidus", &checks);
    fails += expect_refused("{\"t_mono_ns\":12}", "64-bit as a number", &checks);
    fails += expect_refused("{\"t_mono_ns\":\"012\"}", "a leading zero in a "
                            "64-bit string", &checks);
    fails += expect_refused("{\"m_hand\":\"1\"}", "int16 as a string", &checks);
    fails += expect_refused("{\"m_hand\":32768}", "int16 out of range", &checks);
    fails += expect_refused("{\"a\":1}x", "trailing bytes", &checks);
    fails += expect_refused("{\"a\":9007199254740992}", "a bare integer above "
                            "2**53-1", &checks);

    // Round trip: what the writer emits, the reader accepts and re-emits.
    {
        const char *texts[] = {
            "{}", "[]", "{\"a\":[1,2,3],\"b\":{\"c\":null,\"d\":true}}",
            "{\"h\":\"deadbeef\",\"id\":\"18446744073709551615\"}",
        };
        for (const char *t : texts) {
            Value v;
            std::string err;
            std::string again;
            checks++;
            if (!parse(std::string(t), &v, &err) ||
                !write(v, &again, &err) || again != t) {
                std::printf("      round trip: %s -> %s (%s)\n", t,
                            again.c_str(), err.c_str());
                fails++;
            }
        }
    }
    // Unknown keys are fatal.
    {
        Value row = Value::object();
        row.set("k", Value::string("frame"));
        row.set("lane", Value::string("files"));
        row.set("colour", Value::string("blue"));
        std::string err;
        checks++;
        if (validate_row_keys(row, &err)) {
            std::printf("      unknown key accepted\n");
            fails++;
        }
    }

    std::printf("  [3] canonical JSON, writer and strict reader %s  "
                "(%d of %d)\n",
                (fails == 0) ? "PASS" : "FAIL", checks - fails, checks);
    return fails;
}

} // namespace cjson
