// main.cpp -- the kernel's verbs.
//
// Every verb is a subcommand of one binary so the pins are asserted once, in
// one place, before anything else runs (KICKOFF_M0.md section 6). Nothing here
// opens a socket, spawns a process, writes the writ or writes the switch.
//
// M0 build order (HANDOFF section 5), and where this file stands in it:
//
//   1. BLAKE2b, keyed and personalized, against the known-answer vector   DONE
//   2. canonical JSON, writer and strict reader
//   3. the frame codec
//   4. the 128-byte record
//   5. the tape
//   6. the spool reader, the ring, the cursor
//   7. the ledger fold
//   8. the writ and switch parsers
//   9. the pill
//  10. about, boot, verify, spool-verify, spool-seal, ledger-digest, selftest
//  11. the launcher, with the AFD_CONNECT IOCTL driven
//  12. gate.cmd, then the receipt
//
// A verb that is not built yet refuses with a typed reason and a nonzero exit.
// Nothing is dropped silently and nothing returns a stale value.

#include "blake2b.h"
#include "cjson.h"
#include "../seam/seam.h"

#include <windows.h>

#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

namespace {

// The organ contract's exit codes (section 16), which the kernel's own verbs
// answer with too: 0 done, 2 refused, 3 empty, 4 stale, 5 not found,
// 6 degraded.
enum Exit : int {
    kDone      = 0,
    kRefused   = 2,
    kEmpty     = 3,
    kStale     = 4,
    kNotFound  = 5,
    kDegraded  = 6,
};

// Amendment 2 measured the mechanism on this machine. The word on the header
// row is one of `os-enforced`, `wfp-installed`, `lint-only`; the build is
// configured for the first and says so, and separately reports whether the
// running process is actually inside the container, which is a measurement
// rather than a claim.
const char *kSandboxMechanism = "os-enforced";

bool running_in_appcontainer(bool *known) {
    HANDLE token = nullptr;
    DWORD is_container = 0;
    DWORD returned = 0;
    bool result = false;

    *known = false;
    if (OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token) == 0) {
        return false;
    }
    if (GetTokenInformation(token, TokenIsAppContainer, &is_container,
                            static_cast<DWORD>(sizeof is_container),
                            &returned) != 0) {
        *known = true;
        result = (is_container != 0);
    }
    CloseHandle(token);
    return result;
}

int verb_about() {
    const int kat = factor_blake2b_kat();
    bool known = false;
    const bool inside = running_in_appcontainer(&known);

    // The header row proper is canonical JSON assembled by the writer that
    // arrives in step 2. This is the step-1 form: everything printed here is
    // measured, and every member the pin tuple will carry that does not exist
    // yet is named as absent rather than defaulted.
    std::printf("factor about\n");
    std::printf("  build_id            %s\n", FACTOR_BUILD_ID);
    std::printf("  seam_hash           %s\n", seam::seam_hash());
    std::printf("  seam                %s\n", seam::seam_about());
    std::printf("  hash                blake2b-256, keyed, personalized\n");
    std::printf("  hash_kat            %s (%d of %d vectors failed)\n",
                (kat == 0) ? "PASS" : "FAIL", kat, kat);
    std::printf("  record_layout       v0.2 (128 bytes) -- not yet compiled in\n");
    std::printf("  sandbox_mechanism   %s\n", kSandboxMechanism);
    std::printf("  sandbox_in_force    %s\n",
                known ? (inside ? "yes" : "no") : "unknown");
    std::printf("  module_gate         run by build.cmd, not by this binary\n");
    std::printf("  pin_tuple           absent -- serve bytes, weights, maps,\n");
    std::printf("                      runtime, context and environment arrive\n");
    std::printf("                      with M1; M0 is model-free\n");
    return (kat == 0) ? kDone : kRefused;
}

int verb_selftest() {
    int failures = 0;
    int checks = 0;

    std::printf("factor selftest\n");

    // 1 -- the hash. Asserted at boot beside the serve bytes (section 12).
    {
        const int kat = factor_blake2b_kat();
        checks++;
        if (kat != 0) {
            failures++;
        }
        std::printf("  [1] blake2b known-answer vectors        %s  "
                    "(%d failures)\n",
                    (kat == 0) ? "PASS" : "FAIL", kat);
    }

    // 2 -- the seam's closed sets round trip by name and by number.
    {
        int bad = 0;
        for (std::uint8_t i = 0; i < seam::kVerbCount; ++i) {
            const auto v = static_cast<seam::Verb>(i);
            const char *name = seam::verb_name(v);
            seam::Verb back{};
            if (name == nullptr || !seam::verb_from_name(name, &back) ||
                back != v) {
                bad++;
            }
        }
        for (std::uint8_t i = 0; i < seam::kReasonCount; ++i) {
            const auto r = static_cast<seam::Reason>(i);
            const char *name = seam::reason_name(r);
            seam::Reason back{};
            if (name == nullptr || !seam::reason_from_name(name, &back) ||
                back != r) {
                bad++;
            }
        }
        // A name outside the closed set is refused, never defaulted.
        seam::Verb v{};
        seam::Reason r{};
        if (seam::verb_from_name("EXECUTE", &v)) { bad++; }
        if (seam::reason_from_name("because", &r)) { bad++; }
        checks++;
        if (bad != 0) {
            failures++;
        }
        std::printf("  [2] seam closed sets, %u verbs %u reasons   %s  "
                    "(%d failures)\n",
                    static_cast<unsigned>(seam::kVerbCount),
                    static_cast<unsigned>(seam::kReasonCount),
                    (bad == 0) ? "PASS" : "FAIL", bad);
    }

    // 3 -- canonical JSON, the writer and the strict reader.
    {
        const int bad = cjson::cjson_selftest();
        checks++;
        if (bad != 0) {
            failures++;
        }
    }

    std::printf("  ---\n");
    std::printf("  %d of %d checks passed\n", checks - failures, checks);
    std::printf("  not yet compiled in: the frame codec, the 128-byte record,\n");
    std::printf("  the chain. They arrive in build order.\n");
    return (failures == 0) ? kDone : kRefused;
}

// `factor hash --batch` -- the cross-check surface.
//
// A model in Python cannot check a C hash by reading it. tests/hash_cross.py
// drives this instead: one line in, one digest out, one process for the whole
// corpus. Each line is four whitespace-separated fields
//
//     <outlen> <person_hex|-> <key_hex|-> <input_hex|->
//
// and each answer is the lowercase hex digest, or `REFUSED` when the parameters
// are ones factor_blake2b_init refuses. Hex in and hex out, so nothing depends
// on an encoding or a shell.
bool parse_hex_field(const std::string &tok, std::vector<unsigned char> *out) {
    out->clear();
    if (tok == "-") {
        return true;
    }
    if ((tok.size() % 2) != 0) {
        return false;
    }
    out->resize(tok.size() / 2);
    if (out->empty()) {
        return true;
    }
    return factor_unhex(out->data(), out->size(), tok.c_str()) == 0;
}

int verb_hash_batch() {
    std::string line;
    std::size_t lines = 0;

    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) {
            line.pop_back();
        }
        if (line.empty()) {
            continue;
        }

        std::string tok[4];
        std::size_t n = 0;
        std::size_t i = 0;
        while (i < line.size() && n < 4) {
            while (i < line.size() && line[i] == ' ') { ++i; }
            const std::size_t start = i;
            while (i < line.size() && line[i] != ' ') { ++i; }
            if (i > start) {
                tok[n++] = line.substr(start, i - start);
            }
        }
        if (n != 4) {
            std::printf("REFUSED\n");
            continue;
        }

        const long outlen = std::strtol(tok[0].c_str(), nullptr, 10);
        std::vector<unsigned char> person;
        std::vector<unsigned char> key;
        std::vector<unsigned char> input;
        if (!parse_hex_field(tok[1], &person) ||
            !parse_hex_field(tok[2], &key) ||
            !parse_hex_field(tok[3], &input) ||
            outlen < 0 || outlen > FACTOR_BLAKE2B_OUTBYTES) {
            std::printf("REFUSED\n");
            continue;
        }

        unsigned char digest[FACTOR_BLAKE2B_OUTBYTES];
        char hex[2 * FACTOR_BLAKE2B_OUTBYTES + 1];
        const int rc = factor_blake2b(digest, static_cast<std::size_t>(outlen),
                                      key.empty() ? nullptr : key.data(),
                                      key.size(),
                                      person.empty() ? nullptr : person.data(),
                                      person.size(),
                                      input.data(), input.size());
        if (rc != 0) {
            std::printf("REFUSED\n");
        } else {
            factor_hex(hex, digest, static_cast<std::size_t>(outlen));
            std::printf("%s\n", hex);
        }
        lines++;
    }

    std::fflush(stdout);
    return (lines > 0) ? kDone : kEmpty;
}

// `factor cjson --batch` -- the canonical JSON cross-check surface.
//
// One JSON document per line in; per line out either
//
//     OK <the canonical bytes>          the reader accepted it and the writer
//                                       re-emitted exactly these bytes
//     DRIFT <the canonical bytes>       accepted, but re-emitting changed it
//     REFUSED <reason>                  the strict reader refused it
//
// A canonical document is always one line, because every C0 control inside a
// string is escaped, so line-per-document costs nothing. tests/cjson_cross.py
// drives it against Python's canon().
int verb_cjson_batch() {
    std::string line;
    std::size_t lines = 0;

    while (std::getline(std::cin, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n')) {
            line.pop_back();
        }
        if (line.empty()) {
            continue;
        }
        lines++;

        cjson::Value v;
        std::string err;
        if (!cjson::parse(line, &v, &err)) {
            std::printf("REFUSED %s\n", err.c_str());
            continue;
        }
        std::string again;
        if (!cjson::write(v, &again, &err)) {
            std::printf("REFUSED %s\n", err.c_str());
            continue;
        }
        std::printf("%s %s\n", (again == line) ? "OK" : "DRIFT", again.c_str());
    }

    std::fflush(stdout);
    return (lines > 0) ? kDone : kEmpty;
}

int refuse_unbuilt(const char *verb) {
    std::fprintf(stderr,
                 "factor: %s is not built at this point in M0's order.\n"
                 "  reason: out-of-domain\n"
                 "  see: HANDOFF_FOR-THE-IMPLEMENTING-SESSION section 5\n",
                 verb);
    return kRefused;
}

int usage(const char *argv0) {
    std::fprintf(stderr,
        "usage: %s <verb> [options]\n"
        "\n"
        "  about                       the header row\n"
        "  selftest                    the compiled-in checks\n"
        "  hash --batch                stdin: <outlen> <person_hex|-> "
        "<key_hex|-> <input_hex|->\n"
        "  cjson --batch               stdin: one JSON document per line\n"
        "  boot --home <dir>           [not built]\n"
        "  verify --home <dir>         [not built]\n"
        "  spool-verify <spool>        [not built]\n"
        "  spool-seal <lane>           [not built]\n"
        "  ledger-digest --home <dir>  [not built]\n"
        "\n"
        "exit: 0 done, 2 refused, 3 empty, 4 stale, 5 not found, 6 degraded\n",
        argv0);
    return kNotFound;
}

} // namespace

int main(int argc, char **argv) {
    if (argc < 2) {
        return usage(argv[0]);
    }

    const char *verb = argv[1];

    if (std::strcmp(verb, "about") == 0 || std::strcmp(verb, "--about") == 0) {
        return verb_about();
    }
    if (std::strcmp(verb, "selftest") == 0) {
        return verb_selftest();
    }
    if (std::strcmp(verb, "hash") == 0) {
        if (argc >= 3 && std::strcmp(argv[2], "--batch") == 0) {
            return verb_hash_batch();
        }
        std::fprintf(stderr, "factor hash: only --batch is built\n"
                             "  reason: out-of-domain\n");
        return kRefused;
    }
    if (std::strcmp(verb, "cjson") == 0) {
        if (argc >= 3 && std::strcmp(argv[2], "--batch") == 0) {
            return verb_cjson_batch();
        }
        std::fprintf(stderr, "factor cjson: only --batch is built\n"
                             "  reason: out-of-domain\n");
        return kRefused;
    }
    if (std::strcmp(verb, "boot") == 0 ||
        std::strcmp(verb, "verify") == 0 ||
        std::strcmp(verb, "spool-verify") == 0 ||
        std::strcmp(verb, "spool-seal") == 0 ||
        std::strcmp(verb, "ledger-digest") == 0) {
        return refuse_unbuilt(verb);
    }

    std::fprintf(stderr, "factor: unknown verb %s\n  reason: out-of-domain\n",
                 verb);
    return usage(argv[0]);
}
