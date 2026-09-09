// layout_check.cpp -- FACTOR tests, BLUEPRINT_v0.2.md section 5 ledger record.
//
// Compile-time proof of the Obligation record's size, alignment, every field
// offset, and the absence of implicit padding anywhere in it.
//
//   cl  /std:c++20 /EHsc /W4 layout_check.cpp
//   g++ -std=c++20 -Wall -Wextra -o layout_check layout_check.cpp
//
// Two structs are declared:
//
//   Obligation      -- BLUEPRINT_v0.2.md section 5, verbatim: nine uint64, one
//                      int64, uint32 seq, three int16 margins, three uint16
//                      counters, four uint32, uint16 flags, six uint8 enums,
//                      uint8 _pad[8]. 128 bytes, two whole cache lines, every
//                      one of them a byte the declaration named.
//
//   ObligationV01   -- the superseded v0.1 record (float margins, no
//                      release_ns / seq / n_wit / n_wait / tie / unit, and
//                      _pad[14]). Its static_assert records the size it
//                      ACTUALLY has, 120, not the 128 v0.1 claimed.
//                      Compiling with -DPROVE_SPEC_FAILS turns v0.1's own claim
//                      into a static_assert; THAT BUILD MUST FAIL. It is the
//                      planted lie for this check, and it is exactly the lie
//                      section 21's F-LAYOUT row names: "the v0.1 claim
//                      asserted".

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <type_traits>

// ---------------------------------------------------------------- v0.2, live

struct Obligation {          // 128 bytes; asserted below; no implicit padding
  uint64_t id;               //   0  BLAKE2b-64 of (source, table, key)
  uint64_t party;            //   8  counterparty id; 0 = self
  uint64_t opened_ns;        //  16  wall
  uint64_t due_ns;           //  24  wall; 0 = no deadline
  uint64_t horizon_ns;       //  32  wall; horizon of the standing verb
  uint64_t blocked_by;       //  40  id that must close first; 0 = none
  uint64_t src_rev;          //  48  deposit clock of the last row that touched it
  uint64_t judged_rev;       //  56  deposit clock of the standing margins
  uint64_t release_ns;       //  64  wall; outbox release or ask deadline
  int64_t  amount_fix;       //  72  1/65536 of `unit`; never float
  uint32_t seq;              //  80  seqlock: odd while being written
  int16_t  m_hand;           //  84  1/1024 logit, quantized; readiness margin
  int16_t  m_check;          //  86  contradiction margin
  int16_t  m_guard;          //  88  hazard margin
  uint16_t n_wit;            //  90  independent witnesses, per provenance root
  uint16_t n_wait;           //  92  consecutive WAITs at one revision
  uint16_t tie;              //  94  times a margin landed inside the tie band
  uint32_t cls;              //  96  decision class, interned by the writ
  uint32_t band;             // 100  margin band index at the standing judgment
  uint32_t seat;             // 104  worker pool, human seat, or 0 unassigned
  uint32_t unit;             // 108  ISO 4217 numeric for money, else interned
  uint16_t flags;            // 112
  uint8_t  state;            // 114
  uint8_t  verb;             // 115
  uint8_t  reason;           // 116
  uint8_t  gear;             // 117
  uint8_t  kind;             // 118
  uint8_t  rung;             // 119  rung the standing judgment ran under
  uint8_t  _pad[8];          // 120  zeroed on every write
};

// -- size and alignment -------------------------------------------------------
static_assert(sizeof(Obligation) == 128, "the ledger record must be 128 bytes");
static_assert(alignof(Obligation) == 8, "the ledger record must be 8-byte aligned");
static_assert(128 % 64 == 0, "128 is exactly two 64-byte cache lines");

// -- every field offset, exactly as section 5 pins it in its own comments ------
static_assert(offsetof(Obligation, id)         ==   0, "id @ 0");
static_assert(offsetof(Obligation, party)      ==   8, "party @ 8");
static_assert(offsetof(Obligation, opened_ns)  ==  16, "opened_ns @ 16");
static_assert(offsetof(Obligation, due_ns)     ==  24, "due_ns @ 24");
static_assert(offsetof(Obligation, horizon_ns) ==  32, "horizon_ns @ 32");
static_assert(offsetof(Obligation, blocked_by) ==  40, "blocked_by @ 40");
static_assert(offsetof(Obligation, src_rev)    ==  48, "src_rev @ 48");
static_assert(offsetof(Obligation, judged_rev) ==  56, "judged_rev @ 56");
static_assert(offsetof(Obligation, release_ns) ==  64, "release_ns @ 64");
static_assert(offsetof(Obligation, amount_fix) ==  72, "amount_fix @ 72");
static_assert(offsetof(Obligation, seq)        ==  80, "seq @ 80");
static_assert(offsetof(Obligation, m_hand)     ==  84, "m_hand @ 84");
static_assert(offsetof(Obligation, m_check)    ==  86, "m_check @ 86");
static_assert(offsetof(Obligation, m_guard)    ==  88, "m_guard @ 88");
static_assert(offsetof(Obligation, n_wit)      ==  90, "n_wit @ 90");
static_assert(offsetof(Obligation, n_wait)     ==  92, "n_wait @ 92");
static_assert(offsetof(Obligation, tie)        ==  94, "tie @ 94");
static_assert(offsetof(Obligation, cls)        ==  96, "cls @ 96");
static_assert(offsetof(Obligation, band)       == 100, "band @ 100");
static_assert(offsetof(Obligation, seat)       == 104, "seat @ 104");
static_assert(offsetof(Obligation, unit)       == 108, "unit @ 108");
static_assert(offsetof(Obligation, flags)      == 112, "flags @ 112");
static_assert(offsetof(Obligation, state)      == 114, "state @ 114");
static_assert(offsetof(Obligation, verb)       == 115, "verb @ 115");
static_assert(offsetof(Obligation, reason)     == 116, "reason @ 116");
static_assert(offsetof(Obligation, gear)       == 117, "gear @ 117");
static_assert(offsetof(Obligation, kind)       == 118, "kind @ 118");
static_assert(offsetof(Obligation, rung)       == 119, "rung @ 119");
static_assert(offsetof(Obligation, _pad)       == 120, "_pad @ 120");

// -- no implicit padding ANYWHERE ---------------------------------------------
// Two independent proofs, because they fail in different ways.
//
// (1) The sum of every member's own size equals sizeof. If the compiler had
//     inserted one alignment hole anywhere between two fields, or one byte of
//     trailing ABI pad, this sum would be smaller than sizeof.
// (2) The last member ends exactly at sizeof, which pins the trailing case on
//     its own and gives a clearer diagnostic when only the pad is wrong.
//
// This matters because the record is memory-mapped and, per F-REPLAY, digested:
// implicit padding is uninitialised memory that would land in the file and make
// the digest depend on whatever the allocator last left there.
constexpr std::size_t kNamedBytes =
      sizeof(Obligation::id) + sizeof(Obligation::party)
    + sizeof(Obligation::opened_ns) + sizeof(Obligation::due_ns)
    + sizeof(Obligation::horizon_ns) + sizeof(Obligation::blocked_by)
    + sizeof(Obligation::src_rev) + sizeof(Obligation::judged_rev)
    + sizeof(Obligation::release_ns) + sizeof(Obligation::amount_fix)
    + sizeof(Obligation::seq)
    + sizeof(Obligation::m_hand) + sizeof(Obligation::m_check)
    + sizeof(Obligation::m_guard)
    + sizeof(Obligation::n_wit) + sizeof(Obligation::n_wait)
    + sizeof(Obligation::tie)
    + sizeof(Obligation::cls) + sizeof(Obligation::band)
    + sizeof(Obligation::seat) + sizeof(Obligation::unit)
    + sizeof(Obligation::flags)
    + sizeof(Obligation::state) + sizeof(Obligation::verb)
    + sizeof(Obligation::reason) + sizeof(Obligation::gear)
    + sizeof(Obligation::kind) + sizeof(Obligation::rung)
    + sizeof(Obligation::_pad);

static_assert(kNamedBytes == sizeof(Obligation),
              "no implicit padding anywhere: every byte is a declared byte");
static_assert(offsetof(Obligation, _pad) + sizeof(Obligation::_pad)
                  == sizeof(Obligation),
              "no implicit TRAILING padding");
static_assert(kNamedBytes == 128, "the named bytes come to 128");

// -- cache lines --------------------------------------------------------------
// Line 0 is id .. judged_rev. The ripeness walk keys on (cls, due_ns) and
// state: due_ns is on line 0, cls and state on line 1, so a walked record
// touches both lines. No field straddles a line boundary.
static_assert(offsetof(Obligation, judged_rev) + 8 == 64,
              "line 0 ends exactly after judged_rev");
static_assert(offsetof(Obligation, release_ns) == 64, "line 1 starts at release_ns");

// -- the record must be memcpy-able into an mmap ------------------------------
static_assert(std::is_standard_layout<Obligation>::value, "standard layout");
static_assert(std::is_trivially_copyable<Obligation>::value, "trivially copyable");

// -- the widths the ledger header pins ----------------------------------------
// v0.2 replaced the three float margins with int16 quantized logits, so there
// is no IEEE-754 dependency left in the record. What remains to pin is that the
// exact-width types exist and that the signed ones are two's complement, which
// C++20 mandates.
static_assert(sizeof(uint64_t) == 8 && sizeof(int64_t) == 8, "64-bit exact width");
static_assert(sizeof(int16_t) == 2, "int16_t exact width");
static_assert(std::numeric_limits<int16_t>::min() == -32768,
              "int16 margins are two's complement: 1/1024 logit spans +-32 logits");
static_assert(std::numeric_limits<int16_t>::max() == 32767, "int16 max");

// ------------------------------------------------------------ v0.1, the lie

struct ObligationV01 {                // BLUEPRINT.md v0.1 section 5, verbatim
  uint64_t id;
  uint64_t party;
  uint64_t opened_ns;
  uint64_t due_ns;
  uint64_t horizon_ns;
  uint64_t blocked_by;
  uint64_t src_rev;
  uint64_t judged_rev;
  int64_t  amount_fix;
  float    m_hand, m_check, m_guard;
  uint32_t cls;
  uint32_t band;
  uint32_t seat;
  uint16_t flags;
  uint8_t  state;
  uint8_t  verb;
  uint8_t  reason;
  uint8_t  gear;
  uint8_t  kind;
  uint8_t  rung;
  uint8_t  _pad[14];
};

static_assert(sizeof(ObligationV01) == 120,
              "v0.1's record as written was 120 bytes, not the 128 it claimed");
static_assert(sizeof(ObligationV01) != sizeof(Obligation),
              "v0.2 must not be byte-compatible with v0.1; the header refuses it");

#ifdef PROVE_SPEC_FAILS
// THE PLANTED LIE. Section 21 F-LAYOUT: "the v0.1 claim asserted".
// This build MUST fail. If it ever compiles, this file has stopped checking
// anything and the layout gate is blind.
static_assert(sizeof(ObligationV01) == 128,
              "PLANTED LIE: v0.1 claimed 128; the compiler says otherwise");
#endif

// -----------------------------------------------------------------------------

#define ROW(f) std::printf("  %-12s %4zu %4zu\n", #f, \
                           offsetof(Obligation, f), sizeof(Obligation::f))

int main() {
  std::printf("Obligation    (v0.2, _pad[8])  sizeof = %zu  alignof = %zu\n",
              sizeof(Obligation), alignof(Obligation));
  std::printf("ObligationV01 (v0.1, _pad[14]) sizeof = %zu  alignof = %zu\n",
              sizeof(ObligationV01), alignof(ObligationV01));
  std::printf("named bytes summed = %zu   implicit padding = %zu\n",
              kNamedBytes, sizeof(Obligation) - kNamedBytes);
  std::printf("  %-12s %4s %4s\n", "field", "off", "size");
  ROW(id); ROW(party); ROW(opened_ns); ROW(due_ns); ROW(horizon_ns);
  ROW(blocked_by); ROW(src_rev); ROW(judged_rev); ROW(release_ns);
  ROW(amount_fix); ROW(seq);
  ROW(m_hand); ROW(m_check); ROW(m_guard);
  ROW(n_wit); ROW(n_wait); ROW(tie);
  ROW(cls); ROW(band); ROW(seat); ROW(unit);
  ROW(flags);
  ROW(state); ROW(verb); ROW(reason); ROW(gear); ROW(kind); ROW(rung);
  ROW(_pad);
  std::printf("all static_asserts passed at compile time\n");
  return 0;
}
