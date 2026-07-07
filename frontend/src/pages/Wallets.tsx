import { useEffect, useState } from "react";
import { fetchWalletBalance, fetchWallets } from "../api/client";

export function Wallets() {
  const [wallets, setWallets] = useState<Array<{ address: string; name: string; balance?: number }>>([]);

  useEffect(() => {
    fetchWallets()
      .then(async (list) => {
        const withBal = await Promise.all(
          list.map(async (w) => {
            try {
              const b = await fetchWalletBalance(w.address);
              return { ...w, balance: b.balance_artcb };
            } catch {
              return { ...w, balance: 0 };
            }
          }),
        );
        setWallets(withBal);
      })
      .catch(() => setWallets([]));
  }, []);

  const slots = Array.from({ length: 27 }, (_, i) => wallets[i] ?? null);

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Wallets · coffre</h1>
      <div className="panel mc-chest">
        <div className="mc-chest-grid">
          {slots.map((w, i) => (
            <div key={i} className={`mc-chest-slot${w ? " mc-chest-filled" : ""}`}>
              {w ? (
                <>
                  <div className="mc-chest-icon">◇</div>
                  <div className="mc-chest-name">{w.name}</div>
                  <div className="mc-gold-text">{(w.balance ?? 0).toFixed(2)} ₳</div>
                  <div className="mc-mono mc-chest-addr">{w.address.slice(0, 8)}…</div>
                </>
              ) : null}
            </div>
          ))}
        </div>
        <p className="mc-muted">{wallets.length} wallet(s) — reward 1 ARTCB / bloc (epoch genesis)</p>
      </div>
    </div>
  );
}
