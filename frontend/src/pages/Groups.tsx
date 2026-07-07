import { useEffect, useState } from "react";
import {
  createGroup,
  fetchGroupsForAddress,
  fetchWallets,
  inviteGroupMember,
  promoteGroupMember,
} from "../api/client";
import type { GroupData } from "../api/client";
import { useDashboard } from "../context/DashboardContext";

export function Groups() {
  const { actorAddress, setActorAddress, setGroupId } = useDashboard();
  const [wallets, setWallets] = useState<Array<{ address: string; name: string }>>([]);
  const [groups, setGroups] = useState<GroupData[]>([]);
  const [newName, setNewName] = useState("");
  const [inviteAddr, setInviteAddr] = useState("");
  const [selectedGroup, setSelectedGroup] = useState<GroupData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadGroups = async (address: string) => {
    if (!address) return;
    const data = await fetchGroupsForAddress(address);
    setGroups(data.groups);
  };

  useEffect(() => {
    fetchWallets()
      .then((list) => {
        setWallets(list);
        if (list.length && !actorAddress) {
          setActorAddress(list[0].address);
        }
      })
      .catch(() => setWallets([]));
  }, [actorAddress]);

  useEffect(() => {
    if (actorAddress) loadGroups(actorAddress).catch(() => setGroups([]));
  }, [actorAddress]);

  const handleCreate = async () => {
    if (!newName.trim() || !actorAddress) return;
    setLoading(true);
    setError(null);
    try {
      const g = await createGroup(newName.trim(), actorAddress);
      setNewName("");
      setSelectedGroup(g);
      setGroupId(g.group_id);
      await loadGroups(actorAddress);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async () => {
    if (!selectedGroup || !inviteAddr.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const g = await inviteGroupMember(
        selectedGroup.group_id,
        actorAddress,
        inviteAddr.trim(),
        "contributor",
      );
      setSelectedGroup(g);
      setInviteAddr("");
      await loadGroups(actorAddress);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handlePromote = async (target: string) => {
    if (!selectedGroup) return;
    setLoading(true);
    setError(null);
    try {
      const g = await promoteGroupMember(
        selectedGroup.group_id,
        actorAddress,
        target,
        "admin",
      );
      setSelectedGroup(g);
      await loadGroups(actorAddress);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const isFounder = selectedGroup?.founder_address === actorAddress;

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Groupes · multijoueur</h1>

      <div className="panel">
        <h2>Wallet actif</h2>
        {wallets.length ? (
          <select
            value={actorAddress}
            onChange={(e) => {
              setActorAddress(e.target.value);
            }}
          >
            {wallets.map((w) => (
              <option key={w.address} value={w.address}>
                {w.name} — {w.address.slice(0, 12)}…
              </option>
            ))}
          </select>
        ) : (
          <p className="mc-muted">
            Aucun wallet — créez-en un via Console : POST /wallet/create ou API.
          </p>
        )}
      </div>

      <div className="panel mc-groups-panel">
        <h2>Créer un groupe</h2>
        <div className="toolbar">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Nom du groupe"
            aria-label="Nom groupe"
          />
          <button className="primary" onClick={handleCreate} disabled={loading || !actorAddress}>
            Créer
          </button>
        </div>
        {error && <p className="mc-error">{error}</p>}
      </div>

      <div className="panel">
        <h2>Mes groupes ({groups.length})</h2>
        <ul className="mc-checklist-list">
          {groups.map((g) => (
            <li key={g.group_id}>
              <button
                type="button"
                onClick={() => {
                  setSelectedGroup(g);
                  setGroupId(g.group_id);
                }}
              >
                {g.name}
              </button>
              <span className="mc-muted"> · {g.members.length} membres</span>
            </li>
          ))}
        </ul>
      </div>

      {selectedGroup && (
        <div className="panel">
          <h2>{selectedGroup.name}</h2>
          <p className="mc-muted">ID: {selectedGroup.group_id}</p>
          <div className="mc-player-row">
            <div className="mc-player-head">🧑</div>
            <div>
              <strong>Fondateur</strong> — {selectedGroup.founder_address.slice(0, 16)}…
              <p className="mc-muted">Rôle immuable (PROTOCOLE F1–F3)</p>
            </div>
          </div>
          {selectedGroup.members.map((m) => (
            <div key={m.address} className="mc-player-row">
              <div className="mc-player-head">
                {m.role === "founder" ? "🧑" : m.role === "admin" ? "👤" : "👥"}
              </div>
              <div>
                <strong>{m.role}</strong> — {m.address.slice(0, 20)}…
                {isFounder && m.role === "contributor" && m.address !== actorAddress && (
                  <button
                    type="button"
                    style={{ marginLeft: "0.5rem" }}
                    onClick={() => handlePromote(m.address)}
                    disabled={loading}
                  >
                    Nommer admin
                  </button>
                )}
              </div>
            </div>
          ))}

          <h3>Inviter membre</h3>
          <div className="toolbar">
            <input
              value={inviteAddr}
              onChange={(e) => setInviteAddr(e.target.value)}
              placeholder="adresse artcb1…"
            />
            <button onClick={handleInvite} disabled={loading}>
              Inviter
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
