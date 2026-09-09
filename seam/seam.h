// seam.h -- the closed sets, and the component that will alone author verbs.
//
// The seam is its own static library from the first commit, and it links
// nothing learned: no model header, no llama header, no planner header. That is
// BLUEPRINT_v0.2.md section 2 and section 9 as written, and it is the one item
// of PROPOSAL_REV1 section 1.2 that costs nothing now and would be expensive to
// retrofit, so the handoff permits it at M0 without an amendment.
//
// What lives here at M0: the closed verb set, the closed reason set, and the
// hash of both. What does not: any judgment. M0 is model-free, so no verb is
// authored at all -- the loop proves conservation and replay and writes no verb
// row. The gate's refusal order arrives with M1.
//
// The lineage of the law, because merging the judge and the gate is the mistake
// every session that tried it was caught making: the judge returns a float, the
// gate returns a verb, and for a warrant obligation the gate returns before it
// reads the margin at all. They stay in different translation units with
// different hashes.

#ifndef FACTOR_SEAM_H
#define FACTOR_SEAM_H

#include <cstdint>

namespace seam {

// section 5's pinned `verb` encoding, and section 8's table. Nine verbs.
// The numbers are the record's, not a display order; nothing renumbers them.
enum class Verb : std::uint8_t {
    Hold    = 0,
    Look    = 1,
    Fetch   = 2,
    Wait    = 3,
    Draft   = 4,
    Do      = 5,
    Ask     = 6,
    Consult = 7,
    Pass    = 8,
};
inline constexpr std::uint8_t kVerbCount = 9;

// section 8's reasons, closed and numbered. A refusal carries one of these and
// nothing else; there is no free-text reason anywhere in FACTOR.
enum class Reason : std::uint8_t {
    Ok            = 0,
    Margin        = 1,
    Blocked       = 2,
    ThinEvidence  = 3,
    Uncalibrated  = 4,
    Contradicted  = 5,
    Irreversible  = 6,
    BudgetHuman   = 7,
    BudgetDeep    = 8,
    BudgetSelf    = 9,
    Capacity      = 10,
    JuryDissent   = 11,
    WindowOpen    = 12,
    Expired       = 13,
    Demoted       = 14,
    Shadow        = 15,
    Canary        = 16,
    Degraded      = 17,
    OutOfDomain   = 18,
    Unstanding    = 19,
    JuryStale     = 20,
    Presence      = 21,
    Tie           = 22,
    Repeat        = 23,
    Terminal      = 24,
    Front         = 25,
    Cap           = 26,
};
inline constexpr std::uint8_t kReasonCount = 27;

// The wire spelling of each. These are the strings the tape and the account
// print; changing one changes the seam hash, which is the point.
const char *verb_name(Verb v);
const char *reason_name(Reason r);

// Round trips for a reader. Return false when the name is not in the closed
// set; nothing is defaulted, because a name that means two things is a defect.
bool verb_from_name(const char *name, Verb *out);
bool reason_from_name(const char *name, Reason *out);

// The seam's own hash: BLAKE2b-256 over the canonical description of the two
// closed sets, personalized `FCTR-tape-v1`. It goes on the header row beside
// the pin tuple. Add, remove or rename a verb or a reason and this moves.
// Returns a pointer to a static, NUL-terminated, 64-character lowercase hex
// string, computed once.
const char *seam_hash();

// What the seam links, stated for the reader and, at M1, checked by F-VETO.
const char *seam_about();

} // namespace seam

#endif // FACTOR_SEAM_H
