#include "libartcb_chain.h"

#include <openssl/evp.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int hex_encode(const unsigned char *in, size_t in_len, char *out_hex) {
    static const char *hex = "0123456789abcdef";
    for (size_t i = 0; i < in_len; i++) {
        out_hex[i * 2] = hex[(in[i] >> 4) & 0xF];
        out_hex[i * 2 + 1] = hex[in[i] & 0xF];
    }
    out_hex[in_len * 2] = '\0';
    return 0;
}

int artcb_sha256_hex(const char *data, size_t len, char *out_hex) {
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len = 0;
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) {
        return -1;
    }
    if (EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) != 1) {
        EVP_MD_CTX_free(ctx);
        return -1;
    }
    if (EVP_DigestUpdate(ctx, data, len) != 1) {
        EVP_MD_CTX_free(ctx);
        return -1;
    }
    if (EVP_DigestFinal_ex(ctx, digest, &digest_len) != 1) {
        EVP_MD_CTX_free(ctx);
        return -1;
    }
    EVP_MD_CTX_free(ctx);
    hex_encode(digest, digest_len, out_hex);
    return 0;
}

int artcb_build_canonical(
    int index,
    const char *timestamp,
    const char *prev_hash,
    const char *graph_root,
    const char *merkle_root,
    double pol_score,
    char *out_canonical,
    size_t out_len
) {
    int written = snprintf(
        out_canonical,
        out_len,
        "%d|%s|%s|%s|%s|%.6f",
        index,
        timestamp ? timestamp : "",
        prev_hash ? prev_hash : "",
        graph_root ? graph_root : "",
        merkle_root ? merkle_root : "",
        pol_score
    );
    if (written < 0 || (size_t)written >= out_len) {
        return -1;
    }
    return 0;
}

int artcb_hash_canonical(const char *canonical, char *out_hash) {
    if (!canonical || !out_hash) {
        return -1;
    }
    return artcb_sha256_hex(canonical, strlen(canonical), out_hash);
}

static int parse_block_line(
    const char *line,
    artcb_block_record_t *record,
    char *error_msg,
    size_t error_len
) {
    char stored_hash[ARTCB_HASH_HEX_LEN];
    char computed[ARTCB_HASH_HEX_LEN];
    char canonical[ARTCB_MAX_BODY];

    if (sscanf(
            line,
            "{\"index\":%d,\"timestamp\":\"%32[^\"]\",\"prev_hash\":\"%64[^\"]\","
            "\"graph_root\":\"%64[^\"]\",\"merkle_root\":\"%64[^\"]\",\"pol_score\":%lf,"
            "\"hash\":\"%64[^\"]\"}",
            &record->index,
            record->timestamp,
            record->prev_hash,
            record->graph_root,
            record->merkle_root,
            &record->pol_score,
            stored_hash
        ) != 7) {
        snprintf(error_msg, error_len, "invalid block json line");
        return -1;
    }

    if (artcb_build_canonical(
            record->index,
            record->timestamp,
            record->prev_hash,
            record->graph_root,
            record->merkle_root,
            record->pol_score,
            canonical,
            sizeof(canonical)
        ) != 0) {
        snprintf(error_msg, error_len, "canonical build failed index=%d", record->index);
        return -1;
    }

    if (artcb_hash_canonical(canonical, computed) != 0) {
        snprintf(error_msg, error_len, "hash compute failed index=%d", record->index);
        return -1;
    }

    if (strncmp(stored_hash, computed, ARTCB_HASH_HEX_LEN) != 0) {
        snprintf(error_msg, error_len, "hash mismatch index=%d", record->index);
        return -1;
    }

    strncpy(record->hash, stored_hash, ARTCB_HASH_HEX_LEN);
    strncpy(record->canonical, canonical, ARTCB_MAX_BODY);
    return 0;
}

int artcb_count_blocks(const char *path) {
    FILE *fp = fopen(path, "r");
    if (!fp) {
        return 0;
    }
    char line[ARTCB_MAX_BODY];
    int count = 0;
    while (fgets(line, sizeof(line), fp)) {
        if (line[0] == '{') {
            count++;
        }
    }
    fclose(fp);
    return count;
}

int artcb_verify_chain_file(const char *path, char *error_msg, size_t error_len) {
    FILE *fp = fopen(path, "r");
    if (!fp) {
        if (error_msg && error_len > 0) {
            snprintf(error_msg, error_len, "chain file not found (empty ok)");
        }
        return 0;
    }

    char line[ARTCB_MAX_BODY];
    char prev_hash[ARTCB_HASH_HEX_LEN] = {0};
    int expected_index = 0;
    int valid = 0;

    while (fgets(line, sizeof(line), fp)) {
        if (line[0] != '{') {
            continue;
        }
        artcb_block_record_t record;
        memset(&record, 0, sizeof(record));
        if (parse_block_line(line, &record, error_msg, error_len) != 0) {
            fclose(fp);
            return -1;
        }
        if (record.index != expected_index) {
            snprintf(error_msg, error_len, "index gap expected=%d got=%d", expected_index, record.index);
            fclose(fp);
            return -1;
        }
        if (expected_index > 0 && strncmp(record.prev_hash, prev_hash, ARTCB_HASH_HEX_LEN) != 0) {
            snprintf(error_msg, error_len, "prev_hash mismatch index=%d", record.index);
            fclose(fp);
            return -1;
        }
        strncpy(prev_hash, record.hash, ARTCB_HASH_HEX_LEN);
        expected_index++;
        valid = 1;
    }

    fclose(fp);
    if (!valid && error_msg && error_len > 0) {
        snprintf(error_msg, error_len, "empty chain valid");
    }
    return 0;
}
