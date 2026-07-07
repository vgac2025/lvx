"""PoL scorer tests."""

from artcb.agents.critic import DualAgentLoop
from artcb.ir.encoder import IREncoder
from artcb.pol.scorer import PolScorer


def test_pol_score_high_for_valid_graph() -> None:
    encoder = IREncoder()
    graph = encoder.encode("Nous avons décidé d'utiliser FastAPI. Le problème est la perte de contexte.")
    scorer = PolScorer()
    result = scorer.score(graph)
    assert result.validation_rate == 1.0
    assert result.pol_score >= 0.6
    assert result.block_accepted is True


def test_collective_reward_split() -> None:
    rewards = PolScorer.split_reward(
        1.0,
        {"alice": 0.8, "bob": 0.7, "agent": 0.5},
    )
    assert abs(sum(rewards.values()) - 1.0) < 1e-6
    assert rewards["alice"] == 0.4


def test_dual_agent_loop() -> None:
    loop = DualAgentLoop()
    result = loop.run("Observer le monde pour apprendre.")
    assert result.nodes_proposed >= 1
    assert result.pol.pol_score > 0
