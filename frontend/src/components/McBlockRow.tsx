import type { ChainBlock } from "../types";

function rewardArtcb(block: ChainBlock): string {
  if (block.block_reward != null) {
    return `${(block.block_reward / 1e8).toFixed(block.block_reward % 1e8 === 0 ? 0 : 1)}₳`;
  }
  return "1₳";
}

interface Props {
  blocks: ChainBlock[];
  limit?: number;
  reverse?: boolean;
}

export function McBlockRow({ blocks, limit = 8, reverse = true }: Props) {
  const slice = reverse ? [...blocks].reverse().slice(0, limit) : blocks.slice(0, limit);

  if (!slice.length) {
    return <p className="mc-muted">Aucun bloc miné — mémorisez un graphe puis signez.</p>;
  }

  return (
    <div className="mc-block-row">
      {slice.map((b) => (
        <div
          key={b.index}
          className={`mc-block ${b.signature ? "mc-block-mined" : "mc-block-pending"}`}
          title={`#${b.index} · PoL ${b.pol_score?.toFixed(2) ?? "?"} · ${rewardArtcb(b)}`}
        >
          <div>#{b.index}</div>
          <div className="mc-block-reward">{rewardArtcb(b)}</div>
        </div>
      ))}
    </div>
  );
}
