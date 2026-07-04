#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "libartcb_chain.h"

int main(void) {
    char hash[ARTCB_HASH_HEX_LEN];
    char canonical[ARTCB_MAX_BODY];

    assert(artcb_sha256_hex("ARTCB", 5, hash) == 0);
    assert(strlen(hash) == 64);
    printf("sha256 ok: %s\n", hash);

    assert(
        artcb_build_canonical(0, "2026-07-04T23:00:00Z", "", "graph", "merkle", 0.81, canonical, sizeof(canonical))
        == 0
    );
    assert(artcb_hash_canonical(canonical, hash) == 0);
    printf("block hash ok: %s\n", hash);

    printf("all C tests passed\n");
    return 0;
}
