// seam.cpp -- the closed sets and the seam's hash.
//
// This translation unit includes exactly two headers of its own and nothing
// learned. The blake2b include is the kernel's vendored hash; it is arithmetic,
// not a model.

#include "seam.h"

#include "../kernel/blake2b.h"

#include <cstring>

namespace seam {
namespace {

// Indexed by the pinned number. A gap here would be a defect, so the arrays are
// sized by the counts and checked at compile time below.
const char *const kVerbNames[kVerbCount] = {
    "HOLD", "LOOK", "FETCH", "WAIT", "DRAFT", "DO", "ASK", "CONSULT", "PASS"
};

const char *const kReasonNames[kReasonCount] = {
    "ok", "margin", "blocked", "thin-evidence", "uncalibrated", "contradicted",
    "irreversible", "budget-human", "budget-deep", "budget-self", "capacity",
    "jury-dissent", "window-open", "expired", "demoted", "shadow", "canary",
    "degraded", "out-of-domain", "unstanding", "jury-stale", "presence", "tie",
    "repeat", "terminal", "front", "cap"
};

static_assert(sizeof(kVerbNames) / sizeof(kVerbNames[0]) == kVerbCount,
              "the verb table and section 5's pinned encoding disagree");
static_assert(sizeof(kReasonNames) / sizeof(kReasonNames[0]) == kReasonCount,
              "the reason table and section 8's numbering disagree");

// The canonical description the hash covers: every verb and every reason with
// its pinned number, in number order, one per line, `n\tname\n`. Written by
// code so the hash cannot drift from the tables it is supposed to cover.
struct Description {
    char text[1024];
    std::size_t len;
};

void append(Description &d, const char *s) {
    const std::size_t n = std::strlen(s);
    if (d.len + n < sizeof d.text) {
        std::memcpy(d.text + d.len, s, n);
        d.len += n;
    }
}

void append_number(Description &d, unsigned n) {
    char buf[4];
    std::size_t i = 0;
    if (n == 0) {
        buf[i++] = '0';
    }
    while (n > 0 && i < sizeof buf) {
        buf[i++] = static_cast<char>('0' + (n % 10));
        n /= 10;
    }
    while (i > 0) {
        const char c = buf[--i];
        if (d.len + 1 < sizeof d.text) {
            d.text[d.len++] = c;
        }
    }
}

Description describe() {
    Description d;
    d.len = 0;
    append(d, "FACTOR seam v1\nverbs\n");
    for (unsigned i = 0; i < kVerbCount; ++i) {
        append_number(d, i);
        append(d, "\t");
        append(d, kVerbNames[i]);
        append(d, "\n");
    }
    append(d, "reasons\n");
    for (unsigned i = 0; i < kReasonCount; ++i) {
        append_number(d, i);
        append(d, "\t");
        append(d, kReasonNames[i]);
        append(d, "\n");
    }
    return d;
}

} // namespace

const char *verb_name(Verb v) {
    const auto i = static_cast<std::uint8_t>(v);
    return (i < kVerbCount) ? kVerbNames[i] : nullptr;
}

const char *reason_name(Reason r) {
    const auto i = static_cast<std::uint8_t>(r);
    return (i < kReasonCount) ? kReasonNames[i] : nullptr;
}

bool verb_from_name(const char *name, Verb *out) {
    if (name == nullptr || out == nullptr) {
        return false;
    }
    for (std::uint8_t i = 0; i < kVerbCount; ++i) {
        if (std::strcmp(name, kVerbNames[i]) == 0) {
            *out = static_cast<Verb>(i);
            return true;
        }
    }
    return false;
}

bool reason_from_name(const char *name, Reason *out) {
    if (name == nullptr || out == nullptr) {
        return false;
    }
    for (std::uint8_t i = 0; i < kReasonCount; ++i) {
        if (std::strcmp(name, kReasonNames[i]) == 0) {
            *out = static_cast<Reason>(i);
            return true;
        }
    }
    return false;
}

const char *seam_hash() {
    static char hex[65];
    static bool computed = false;
    if (!computed) {
        const Description d = describe();
        unsigned char digest[32];
        factor_blake2b(digest, sizeof digest, nullptr, 0,
                       "FCTR-tape-v1", 12, d.text, d.len);
        factor_hex(hex, digest, sizeof digest);
        computed = true;
    }
    return hex;
}

const char *seam_about() {
    return "seam: the deterministic component that alone authors verbs; "
           "links no model, no planner, no runtime; "
           "9 verbs and 27 reasons, both closed";
}

} // namespace seam
