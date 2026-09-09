/* blake2b.c -- BLAKE2b with keyed mode and personalization.
 *
 * The compression function, the IV, the sigma schedule and the rotation
 * constants are RFC 7693's. The initialisation is the full BLAKE2 parameter
 * block rather than RFC 7693's shortened form, because FACTOR needs `person`
 * and RFC 7693 omits it: section 12 derives one key per chain from one machine
 * secret by personalization, and the spool chain is unkeyed but personalized so
 * a plain unkeyed BLAKE2b elsewhere cannot verify as a spool line.
 *
 * The parameter block, 64 bytes, little-endian, as BLAKE2 defines it:
 *
 *   0  digest_length (1)   1  key_length (1)   2  fanout (1)   3  depth (1)
 *   4  leaf_length (4)     8  node_offset (8)  16 node_depth (1)
 *   17 inner_length (1)   18  reserved (14)    32 salt (16)     48 personal (16)
 *
 * h[i] = IV[i] XOR load64(P + 8*i). Sequential mode is fanout 1, depth 1, and
 * every other field zero. FACTOR pins salt to zero; personalization alone
 * separates the chains.
 */

#include "blake2b.h"

#include <string.h>

#define ROTR64(x, y) (((x) >> (y)) ^ ((x) << (64 - (y))))

static const uint64_t blake2b_iv[8] = {
    0x6A09E667F3BCC908ULL, 0xBB67AE8584CAA73BULL,
    0x3C6EF372FE94F82BULL, 0xA54FF53A5F1D36F1ULL,
    0x510E527FADE682D1ULL, 0x9B05688C2B3E6C1FULL,
    0x1F83D9ABFB41BD6BULL, 0x5BE0CD19137E2179ULL
};

static const uint8_t blake2b_sigma[12][16] = {
    {  0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15 },
    { 14, 10,  4,  8,  9, 15, 13,  6,  1, 12,  0,  2, 11,  7,  5,  3 },
    { 11,  8, 12,  0,  5,  2, 15, 13, 10, 14,  3,  6,  7,  1,  9,  4 },
    {  7,  9,  3,  1, 13, 12, 11, 14,  2,  6,  5, 10,  4,  0, 15,  8 },
    {  9,  0,  5,  7,  2,  4, 10, 15, 14,  1, 11, 12,  6,  8,  3, 13 },
    {  2, 12,  6, 10,  0, 11,  8,  3,  4, 13,  7,  5, 15, 14,  1,  9 },
    { 12,  5,  1, 15, 14, 13,  4, 10,  0,  7,  6,  3,  9,  2,  8, 11 },
    { 13, 11,  7, 14, 12,  1,  3,  9,  5,  0, 15,  4,  8,  6,  2, 10 },
    {  6, 15, 14,  9, 11,  3,  0,  8, 12,  2, 13,  7,  1,  4, 10,  5 },
    { 10,  2,  8,  4,  7,  6,  1,  5, 15, 11,  9, 14,  3, 12, 13,  0 },
    {  0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15 },
    { 14, 10,  4,  8,  9, 15, 13,  6,  1, 12,  0,  2, 11,  7,  5,  3 }
};

static uint64_t load64(const uint8_t *src)
{
    return  (uint64_t)src[0]
         | ((uint64_t)src[1] <<  8)
         | ((uint64_t)src[2] << 16)
         | ((uint64_t)src[3] << 24)
         | ((uint64_t)src[4] << 32)
         | ((uint64_t)src[5] << 40)
         | ((uint64_t)src[6] << 48)
         | ((uint64_t)src[7] << 56);
}

#define B2B_G(a, b, c, d, x, y)          \
    do {                                 \
        v[a] = v[a] + v[b] + (x);        \
        v[d] = ROTR64(v[d] ^ v[a], 32);  \
        v[c] = v[c] + v[d];              \
        v[b] = ROTR64(v[b] ^ v[c], 24);  \
        v[a] = v[a] + v[b] + (y);        \
        v[d] = ROTR64(v[d] ^ v[a], 16);  \
        v[c] = v[c] + v[d];              \
        v[b] = ROTR64(v[b] ^ v[c], 63);  \
    } while (0)

static void blake2b_compress(factor_blake2b_ctx *ctx, int last)
{
    uint64_t v[16];
    uint64_t m[16];
    size_t i;

    for (i = 0; i < 8; i++) {
        v[i] = ctx->h[i];
        v[i + 8] = blake2b_iv[i];
    }

    v[12] ^= ctx->t[0];
    v[13] ^= ctx->t[1];
    if (last) {
        v[14] = ~v[14];
    }

    for (i = 0; i < 16; i++) {
        m[i] = load64(&ctx->b[8 * i]);
    }

    for (i = 0; i < 12; i++) {
        const uint8_t *s = blake2b_sigma[i];
        B2B_G(0, 4,  8, 12, m[s[ 0]], m[s[ 1]]);
        B2B_G(1, 5,  9, 13, m[s[ 2]], m[s[ 3]]);
        B2B_G(2, 6, 10, 14, m[s[ 4]], m[s[ 5]]);
        B2B_G(3, 7, 11, 15, m[s[ 6]], m[s[ 7]]);
        B2B_G(0, 5, 10, 15, m[s[ 8]], m[s[ 9]]);
        B2B_G(1, 6, 11, 12, m[s[10]], m[s[11]]);
        B2B_G(2, 7,  8, 13, m[s[12]], m[s[13]]);
        B2B_G(3, 4,  9, 14, m[s[14]], m[s[15]]);
    }

    for (i = 0; i < 8; i++) {
        ctx->h[i] ^= v[i] ^ v[i + 8];
    }
}

int factor_blake2b_init(factor_blake2b_ctx *ctx,
                        size_t outlen,
                        const void *key, size_t keylen,
                        const void *person, size_t personlen)
{
    uint8_t p[64];
    size_t i;

    if (ctx == NULL) {
        return -1;
    }
    if (outlen == 0 || outlen > FACTOR_BLAKE2B_OUTBYTES) {
        return -1;
    }
    if (keylen > FACTOR_BLAKE2B_KEYBYTES) {
        return -1;
    }
    if (personlen > FACTOR_BLAKE2B_PERSONBYTES) {
        return -1;
    }
    if ((keylen > 0 && key == NULL) || (personlen > 0 && person == NULL)) {
        return -1;
    }

    memset(p, 0, sizeof p);
    p[0] = (uint8_t)outlen;
    p[1] = (uint8_t)keylen;
    p[2] = 1;                      /* fanout, sequential          */
    p[3] = 1;                      /* depth, sequential           */
    /* leaf_length, node_offset, node_depth, inner_length, reserved, salt: 0 */
    if (personlen > 0) {
        memcpy(p + 48, person, personlen);   /* zero padded to 16 */
    }

    for (i = 0; i < 8; i++) {
        ctx->h[i] = blake2b_iv[i] ^ load64(p + 8 * i);
    }
    ctx->t[0] = 0;
    ctx->t[1] = 0;
    ctx->c = 0;
    ctx->outlen = outlen;
    memset(ctx->b, 0, sizeof ctx->b);

    if (keylen > 0) {
        /* The key is the first data block, zero padded to 128 bytes. When it
         * is also the last block, the final call marks it last -- which is why
         * the padding is written here and not counted twice. */
        uint8_t block[FACTOR_BLAKE2B_BLOCKBYTES];
        memset(block, 0, sizeof block);
        memcpy(block, key, keylen);
        factor_blake2b_update(ctx, block, sizeof block);
        memset(block, 0, sizeof block);
    }

    return 0;
}

void factor_blake2b_update(factor_blake2b_ctx *ctx, const void *in, size_t inlen)
{
    const uint8_t *p = (const uint8_t *)in;
    size_t left;
    size_t fill;

    if (inlen == 0) {
        return;
    }

    left = ctx->c;
    fill = FACTOR_BLAKE2B_BLOCKBYTES - left;

    if (inlen > fill) {
        /* Complete the pending block and compress it, then whole blocks, and
         * keep the tail. A block is compressed only once it is known not to be
         * the last one, which is what the trailing `>` rather than `>=` buys. */
        ctx->c = 0;
        memcpy(&ctx->b[left], p, fill);
        ctx->t[0] += FACTOR_BLAKE2B_BLOCKBYTES;
        if (ctx->t[0] < FACTOR_BLAKE2B_BLOCKBYTES) {
            ctx->t[1]++;
        }
        blake2b_compress(ctx, 0);
        p += fill;
        inlen -= fill;

        while (inlen > FACTOR_BLAKE2B_BLOCKBYTES) {
            memcpy(ctx->b, p, FACTOR_BLAKE2B_BLOCKBYTES);
            ctx->t[0] += FACTOR_BLAKE2B_BLOCKBYTES;
            if (ctx->t[0] < FACTOR_BLAKE2B_BLOCKBYTES) {
                ctx->t[1]++;
            }
            blake2b_compress(ctx, 0);
            p += FACTOR_BLAKE2B_BLOCKBYTES;
            inlen -= FACTOR_BLAKE2B_BLOCKBYTES;
        }
        left = 0;
    }

    memcpy(&ctx->b[left], p, inlen);
    ctx->c = left + inlen;
}

void factor_blake2b_final(factor_blake2b_ctx *ctx, void *out)
{
    uint8_t *o = (uint8_t *)out;
    size_t i;

    ctx->t[0] += ctx->c;
    if (ctx->t[0] < ctx->c) {
        ctx->t[1]++;
    }

    while (ctx->c < FACTOR_BLAKE2B_BLOCKBYTES) {
        ctx->b[ctx->c++] = 0;
    }
    blake2b_compress(ctx, 1);

    for (i = 0; i < ctx->outlen; i++) {
        o[i] = (uint8_t)((ctx->h[i >> 3] >> (8 * (i & 7))) & 0xFF);
    }
}

int factor_blake2b(void *out, size_t outlen,
                   const void *key, size_t keylen,
                   const void *person, size_t personlen,
                   const void *in, size_t inlen)
{
    factor_blake2b_ctx ctx;
    if (factor_blake2b_init(&ctx, outlen, key, keylen, person, personlen) != 0) {
        return -1;
    }
    factor_blake2b_update(&ctx, in, inlen);
    factor_blake2b_final(&ctx, out);
    memset(&ctx, 0, sizeof ctx);
    return 0;
}

void factor_hex(char *out, const void *digest, size_t len)
{
    static const char hexdigits[] = "0123456789abcdef";
    const uint8_t *d = (const uint8_t *)digest;
    size_t i;
    for (i = 0; i < len; i++) {
        out[2 * i]     = hexdigits[(d[i] >> 4) & 0x0F];
        out[2 * i + 1] = hexdigits[d[i] & 0x0F];
    }
    out[2 * len] = '\0';
}

int factor_unhex(void *out, size_t len, const char *hex)
{
    uint8_t *o = (uint8_t *)out;
    size_t i;
    for (i = 0; i < len; i++) {
        uint8_t byte = 0;
        size_t half;
        for (half = 0; half < 2; half++) {
            char ch = hex[2 * i + half];
            uint8_t nib;
            if (ch >= '0' && ch <= '9') {
                nib = (uint8_t)(ch - '0');
            } else if (ch >= 'a' && ch <= 'f') {
                nib = (uint8_t)(ch - 'a' + 10);
            } else {
                return -1;      /* uppercase included: the hex has one spelling */
            }
            byte = (uint8_t)((byte << 4) | nib);
        }
        o[i] = byte;
    }
    return 0;
}

/* ------------------------------------------------------------------ the KAT */

/* The independent anchor: RFC 7693 Appendix A, BLAKE2b-512 of "abc". Every
 * other vector below is the value Python's hashlib computes, which is the model
 * tests/chain_check.py and tests/frame_roundtrip.py compute the tape and the
 * spool with. tests/hash_cross.py recomputes all of them against hashlib on
 * every run, so this table is a boot assertion and not the only witness. */
#define KAT_RFC7693_ABC_512 \
    "ba80a53f981c4d0d6a2797b69f12f6e94c212f14685ac4b74b12bb6fdbffa2d1" \
    "7d87c5392aab792dc252d5de4533cc9518d38aa8dbf1925ab92386edd4009923"

#define KAT_EMPTY_256 \
    "0e5751c026e543b2e8ab2eb06099daa1d1e5df47778f7787faab45cdf12fe3a8"

/* tests/frame_roundtrip.py's own KAT preimage: the genesis prev of 64 zeros,
 * u64le(12), and the body "known-answer". */
#define KAT_SPOOL_PERSONALIZED \
    "f682e7d6d8a4c0b0612903ab2672f9f66627e99445fa9a6eced0230dc54b4277"
#define KAT_SPOOL_UNPERSONALIZED \
    "204d715e71bcc3d901f78d44474ee60312c0d026d323cd91f836945b5d45d3d6"

/* Keyed, over "known-answer", with tests/chain_check.py's fixture secret. */
#define KAT_KEYED_256 \
    "6fb6e2d4deff498865cd3f68797ef74be914560697403c7e70d9e2d8cd95920a"

/* The six chain keys derived from that same fixture secret by personalization
 * alone -- Amendment 1 item 15's strings, in CHAIN_ORDER. */
static const char *const kat_chain_keys[6] = {
    "af2328b5890b125c3a999ce2132a92d717585e7486a44d1bd4494b88447eb2d1", /* tape    */
    "c5857cff88cfea29dda2aaa9c72237ff1f0728a5902afad4c817f68e91bdeb28", /* dossier */
    "77163b84200b7a6c7549996e658bdcb177bb7e9a4cfb255044e0d2f9f7214736", /* ledger  */
    "c308afa0890b858f5b41edeabc728eb19b92fa8e99fe719500e0c06e0ea6559a", /* ckpt    */
    "6b568ef89251d46770ca6bdef3b3b05e052e373cf203d043cf3420581344c966", /* spool   */
    "75b91e0fd35bf8c4c620dfafbc1cc0864c0a774bb03deaf6b26931b13245f6d3"  /* fprint  */
};

static const char *const kat_person[6] = {
    "FCTR-tape-v1", "FCTR-dossier-v1", "FCTR-ledger-v1",
    "FCTR-ckpt-v1", "FCTR-spool-v1",   "FCTR-fprint-v1"
};

/* The keyed tape row hash over that preimage, under K_tape. */
#define KAT_TAPE_ROW \
    "2b7721c5ef40c2ab519d7890523f502dc719e1fe6f16fab5835bf84bd27b3445"

static int kat_one(const char *expect_hex,
                   size_t outlen,
                   const void *key, size_t keylen,
                   const void *person, size_t personlen,
                   const void *in, size_t inlen)
{
    uint8_t got[FACTOR_BLAKE2B_OUTBYTES];
    char hex[2 * FACTOR_BLAKE2B_OUTBYTES + 1];

    if (factor_blake2b(got, outlen, key, keylen, person, personlen,
                       in, inlen) != 0) {
        return 1;
    }
    factor_hex(hex, got, outlen);
    return (strcmp(hex, expect_hex) == 0) ? 0 : 1;
}

int factor_blake2b_kat(void)
{
    /* The preimage tests/frame_roundtrip.py pins: 64 zero characters, u64le of
     * the body length, then the body. Built here rather than pasted, so the
     * shape is visible. */
    static const char body[] = "known-answer";
    uint8_t pre[64 + 8 + 12];
    uint8_t secret[32];
    uint8_t k_tape[32];
    int fails = 0;
    size_t i;

    memset(pre, '0', 64);
    memset(pre + 64, 0, 8);
    pre[64] = (uint8_t)(sizeof body - 1);      /* 12, little-endian u64 */
    memcpy(pre + 72, body, sizeof body - 1);

    for (i = 0; i < sizeof secret; i++) {
        secret[i] = (uint8_t)i;                /* bytes(range(32)) */
    }

    fails += kat_one(KAT_RFC7693_ABC_512, 64, NULL, 0, NULL, 0, "abc", 3);
    fails += kat_one(KAT_EMPTY_256, 32, NULL, 0, NULL, 0, "", 0);
    fails += kat_one(KAT_SPOOL_PERSONALIZED, 32, NULL, 0,
                     "FCTR-spool-v1", 13, pre, sizeof pre);
    fails += kat_one(KAT_SPOOL_UNPERSONALIZED, 32, NULL, 0, NULL, 0,
                     pre, sizeof pre);
    fails += kat_one(KAT_KEYED_256, 32, secret, sizeof secret, NULL, 0,
                     body, sizeof body - 1);

    for (i = 0; i < 6; i++) {
        fails += kat_one(kat_chain_keys[i], 32, NULL, 0,
                         kat_person[i], strlen(kat_person[i]),
                         secret, sizeof secret);
    }

    /* K_tape, then the keyed row hash under it. */
    if (factor_blake2b(k_tape, sizeof k_tape, NULL, 0,
                       "FCTR-tape-v1", 12, secret, sizeof secret) != 0) {
        fails++;
    } else {
        fails += kat_one(KAT_TAPE_ROW, 32, k_tape, sizeof k_tape, NULL, 0,
                         pre, sizeof pre);
    }

    /* The streaming path must equal the one shot, or a tape written in pieces
     * and verified whole would disagree with itself. Split at every offset
     * that crosses a block boundary and at one that does not. */
    {
        static const size_t splits[] = { 1, 63, 64, 127, 128, 129, 200 };
        uint8_t big[600];
        uint8_t whole[32];
        size_t s;
        for (i = 0; i < sizeof big; i++) {
            big[i] = (uint8_t)(i * 7 + 1);
        }
        if (factor_blake2b(whole, sizeof whole, NULL, 0, "FCTR-tape-v1", 12,
                           big, sizeof big) != 0) {
            fails++;
        }
        for (s = 0; s < sizeof splits / sizeof splits[0]; s++) {
            factor_blake2b_ctx ctx;
            uint8_t piecewise[32];
            size_t cut = splits[s];
            if (factor_blake2b_init(&ctx, 32, NULL, 0, "FCTR-tape-v1", 12) != 0) {
                fails++;
                continue;
            }
            factor_blake2b_update(&ctx, big, cut);
            factor_blake2b_update(&ctx, big + cut, sizeof big - cut);
            factor_blake2b_final(&ctx, piecewise);
            if (memcmp(piecewise, whole, sizeof whole) != 0) {
                fails++;
            }
        }
    }

    /* A refused parameter is refused, not clamped. */
    {
        uint8_t out[64];
        uint8_t key65[65];
        uint8_t person17[17];
        memset(key65, 0, sizeof key65);
        memset(person17, 0, sizeof person17);
        if (factor_blake2b(out, 0, NULL, 0, NULL, 0, "", 0) != -1) { fails++; }
        if (factor_blake2b(out, 65, NULL, 0, NULL, 0, "", 0) != -1) { fails++; }
        if (factor_blake2b(out, 32, key65, 65, NULL, 0, "", 0) != -1) { fails++; }
        if (factor_blake2b(out, 32, NULL, 0, person17, 17, "", 0) != -1) { fails++; }
    }

    /* Uppercase hex is refused; lowercase round-trips. */
    {
        uint8_t back[4];
        char hex[9];
        static const uint8_t src[4] = { 0x0f, 0xa0, 0x00, 0xff };
        factor_hex(hex, src, sizeof src);
        if (strcmp(hex, "0fa000ff") != 0) { fails++; }
        if (factor_unhex(back, sizeof back, hex) != 0) { fails++; }
        if (memcmp(back, src, sizeof src) != 0) { fails++; }
        if (factor_unhex(back, sizeof back, "0FA000FF") != -1) { fails++; }
    }

    return fails;
}
