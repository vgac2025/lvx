"""Tests politique sécurité pool."""

from __future__ import annotations

import pytest

from artcb.pool.policy import PoolPolicyError, validate_pool_options


def test_local_mining_no_policy_block() -> None:
    validate_pool_options(
        use_distributed=False,
        encrypt_transport=False,
        visibility="private",
    )


def test_distributed_requires_encryption() -> None:
    with pytest.raises(PoolPolicyError, match="chiffrement"):
        validate_pool_options(
            use_distributed=True,
            encrypt_transport=False,
            visibility="private",
        )


def test_group_requires_group_id() -> None:
    with pytest.raises(PoolPolicyError, match="group_id"):
        validate_pool_options(
            use_distributed=True,
            encrypt_transport=True,
            visibility="group",
            actor_address="artcb1test",
        )


def test_all_visibilities_accepted_local() -> None:
    for vis in ("private", "public", "group"):
        validate_pool_options(
            use_distributed=False,
            encrypt_transport=False,
            visibility=vis,
            group_id="grp_test" if vis == "group" else None,
        )
