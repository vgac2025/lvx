"""ARTCB tokenomics constants — single source of truth."""

# 1 ARTCB = 10^8 satoshi (like Bitcoin)
SATOSHI_PER_ARTCB = 100_000_000

# Block reward at genesis (halving every HALVING_INTERVAL blocks)
INITIAL_BLOCK_REWARD_ARTCB = 1.0
INITIAL_BLOCK_REWARD_SATOSHI = int(INITIAL_BLOCK_REWARD_ARTCB * SATOSHI_PER_ARTCB)

HALVING_INTERVAL = 210_000
MAX_HALVINGS = 64
