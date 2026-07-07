interface Props {
  icon: string;
  label: string;
  value: string;
  sub?: string;
  gold?: boolean;
  barPct?: number;
}

export function McKpiSlot({ icon, label, value, sub, gold, barPct }: Props) {
  return (
    <div className={`mc-slot mc-kpi-slot${gold ? " mc-slot-gold" : ""}`}>
      <div className="mc-kpi-icon" aria-hidden>
        {icon}
      </div>
      <div className="mc-kpi-body">
        <div className="mc-kpi-label">{label}</div>
        <div className="mc-kpi-value">{value}</div>
        {sub && <div className="mc-kpi-sub">{sub}</div>}
        {barPct !== undefined && (
          <div className="mc-hp-bar" role="progressbar" aria-valuenow={barPct} aria-valuemin={0} aria-valuemax={100}>
            <div className="mc-hp-fill" style={{ width: `${Math.min(100, barPct)}%` }} />
          </div>
        )}
      </div>
    </div>
  );
}
