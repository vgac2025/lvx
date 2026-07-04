#ifndef LIBARTCB_CHAIN_H
#define LIBARTCB_CHAIN_H

#include <stddef.h>

#define ARTCB_HASH_HEX_LEN 65
#define ARTCB_MAX_BODY 16384
#define ARTCB_MAX_ERR 512

typedef struct {
    int index;
    char timestamp[33];
    char prev_hash[ARTCB_HASH_HEX_LEN];
    char graph_root[ARTCB_HASH_HEX_LEN];
    char merkle_root[ARTCB_HASH_HEX_LEN];
    double pol_score;
    char canonical[ARTCB_MAX_BODY];
    char hash[ARTCB_HASH_HEX_LEN];
} artcb_block_record_t;

int artcb_sha256_hex(const char *data, size_t len, char *out_hex);

int artcb_build_canonical(
    int index,
    const char *timestamp,
    const char *prev_hash,
    const char *graph_root,
    const char *merkle_root,
    double pol_score,
    char *out_canonical,
    size_t out_len
);

int artcb_hash_canonical(const char *canonical, char *out_hash);

int artcb_verify_chain_file(const char *path, char *error_msg, size_t error_len);

int artcb_count_blocks(const char *path);

#endif
