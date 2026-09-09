/* blake2b.h -- BLAKE2b-512/256 with keyed mode and personalization.
 *
 * Vendored from the RFC 7693 reference construction, extended to the full
 * BLAKE2 parameter block so that `key` and `person` are available, because
 * BLUEPRINT_v0.2.md Amendment 1 item 15 pins six personalization strings and
 * section 12 keys the tape and the dossier:
 *
 *     K_chain = BLAKE2b-256( machine_secret, person = the pinned string )
 *     h       = BLAKE2b-256-keyed( K_tape ; prev_hex || u64le(len(body)) || body )
 *
 * Personalization gives each chain an independent key from one secret, so a row
 * lifted from one chain cannot verify in another. The spool chain is unkeyed
 * and personalized `FCTR-spool-v1`, so a spool verifies alone and a plain
 * unkeyed BLAKE2b elsewhere does not verify as a spool line.
 *
 * The reference for what these functions must produce is Python's
 * `hashlib.blake2b(data, digest_size=n, key=k, person=p)`, which is what
 * tests/chain_check.py and tests/frame_roundtrip.py compute. tests/hash_cross.py
 * measures the two against each other over a corpus; a one-byte disagreement is
 * a finding, not a rounding.
 *
 * No allocation. No I/O. No global state.
 */
#ifndef FACTOR_BLAKE2B_H
#define FACTOR_BLAKE2B_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FACTOR_BLAKE2B_BLOCKBYTES 128
#define FACTOR_BLAKE2B_OUTBYTES    64
#define FACTOR_BLAKE2B_KEYBYTES    64
#define FACTOR_BLAKE2B_SALTBYTES   16
#define FACTOR_BLAKE2B_PERSONBYTES 16

typedef struct {
    uint8_t  b[FACTOR_BLAKE2B_BLOCKBYTES]; /* the block being filled          */
    uint64_t h[8];                         /* the chaining state              */
    uint64_t t[2];                         /* bytes compressed, 128-bit       */
    size_t   c;                            /* bytes already in b              */
    size_t   outlen;                       /* digest length, 1..64            */
} factor_blake2b_ctx;

/* Returns 0 on success, -1 on a refused parameter. A refused parameter is a
 * caller defect: outlen outside 1..64, keylen above 64, personlen above 16, or
 * a null key/person with a nonzero length. Nothing here saturates or clamps. */
int factor_blake2b_init(factor_blake2b_ctx *ctx,
                        size_t outlen,
                        const void *key, size_t keylen,
                        const void *person, size_t personlen);

void factor_blake2b_update(factor_blake2b_ctx *ctx,
                           const void *in, size_t inlen);

/* Writes ctx->outlen bytes to out. The context is spent afterwards. */
void factor_blake2b_final(factor_blake2b_ctx *ctx, void *out);

/* One shot. Same return contract as init. */
int factor_blake2b(void *out, size_t outlen,
                   const void *key, size_t keylen,
                   const void *person, size_t personlen,
                   const void *in, size_t inlen);

/* Lowercase hex of a digest. `out` must hold 2*len+1 bytes; NUL terminated. */
void factor_hex(char *out, const void *digest, size_t len);

/* Parses 2*len lowercase hex characters into len bytes.
 * Returns 0 on success, -1 if any character is not [0-9a-f]. Uppercase is
 * refused: the tape's hex has one spelling. */
int factor_unhex(void *out, size_t len, const char *hex);

/* The known-answer vectors, asserted at boot beside the serve bytes (section 12).
 * Returns 0 when every vector matches, and the count of failures otherwise. */
int factor_blake2b_kat(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* FACTOR_BLAKE2B_H */
