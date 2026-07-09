import { useEffect, useState } from "react";
import {
  addP2PPeer,
  fetchNotificationChannels,
  fetchP2PStatus,
  fetchP2PPeers,
  saveNotificationChannel,
  syncP2PAll,
} from "../api/client";

export function Network() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [peers, setPeers] = useState<Array<Record<string, unknown>>>([]);
  const [channels, setChannels] = useState<Array<Record<string, unknown>>>([]);
  const [host, setHost] = useState("127.0.0.1");
  const [port, setPort] = useState("8000");
  const [peerKem, setPeerKem] = useState("");
  const [notifLabel, setNotifLabel] = useState("");
  const [notifSecret, setNotifSecret] = useState("");
  const [chatId, setChatId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const reload = async () => {
    setStatus(await fetchP2PStatus());
    setPeers((await fetchP2PPeers()).peers);
    setChannels((await fetchNotificationChannels()).channels);
  };

  useEffect(() => {
    reload().catch((e) => setError(String(e)));
  }, []);

  const handleAddPeer = async () => {
    try {
      await addP2PPeer({ host, port: parseInt(port, 10), kem_public_key_hex: peerKem, label: `${host}:${port}` });
      setSuccess("Pair P2P ajouté");
      await reload();
    } catch (e) {
      setError(String(e));
    }
  };

  const handleSync = async () => {
    try {
      const r = await syncP2PAll();
      setSuccess(`Sync terminée — ${r.peer_count} pair(s)`);
      await reload();
    } catch (e) {
      setError(String(e));
    }
  };

  const handleSaveNotif = async () => {
    try {
      await saveNotificationChannel({
        channel_type: "telegram",
        label: notifLabel || "Telegram",
        secret: notifSecret,
        config: { chat_id: chatId },
      });
      setSuccess("Canal Telegram enregistré (local chiffré)");
      await reload();
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Réseau P2P · artcb-devnet</h1>
      <p className="mc-hint">
        <strong>Calcul local</strong> — pas de pool distribué. Sync P2P = blocs <strong>publics</strong> uniquement,
        transport chiffré <strong>ML-KEM-768</strong>. Les blocs privés ne quittent jamais votre machine.
      </p>
      {error && <p className="mc-error">{error}</p>}
      {success && <p className="mc-success">{success}</p>}

      {status && (
        <section className="mc-card">
          <h2>Nœud local</h2>
          <p>Network: {String(status.network_id)} · Node: {String(status.node_id)}</p>
          <p>ML-KEM pub: {String(status.kem_public_key_hex).slice(0, 32)}…</p>
          <p>Blocs publics locaux: {String(status.public_blocks_local)} · reçus P2P: {String(status.public_blocks_incoming)}</p>
          <button type="button" className="mc-btn" onClick={handleSync}>Synchroniser tous les pairs</button>
        </section>
      )}

      <section className="mc-card">
        <h2>Ajouter un pair</h2>
        <label>Host<input value={host} onChange={(e) => setHost(e.target.value)} /></label>
        <label>Port API<input value={port} onChange={(e) => setPort(e.target.value)} /></label>
        <label>Clé publique ML-KEM du pair (hex)<textarea value={peerKem} onChange={(e) => setPeerKem(e.target.value)} rows={2} /></label>
        <button type="button" className="mc-btn" onClick={handleAddPeer} disabled={peerKem.length < 32}>Ajouter</button>
      </section>

      <section className="mc-card">
        <h2>Pairs ({peers.length})</h2>
        <ul className="mc-connector-list">
          {peers.map((p) => (
            <li key={String(p.peer_id)} className="mc-connector-item">
              {String(p.label || p.peer_id)} — {String(p.base_url)}
              {p.last_sync_ok != null && <span> · sync {p.last_sync_ok ? "✓" : "✕"}</span>}
            </li>
          ))}
        </ul>
      </section>

      <section className="mc-card">
        <h2>Alertes Telegram</h2>
        <p className="mc-hint">
          Notifications à chaque bloc gravé. Créez un bot via @BotFather, récupérez le token et votre chat_id.
          Gmail retiré — OAuth Google trop complexe pour cette release.
        </p>
        <label>Nom<input value={notifLabel} onChange={(e) => setNotifLabel(e.target.value)} placeholder="Mon bot ARTCB" /></label>
        <label>Chat ID<input value={chatId} onChange={(e) => setChatId(e.target.value)} placeholder="123456789" /></label>
        <label>
          Bot token
          <input type="password" value={notifSecret} onChange={(e) => setNotifSecret(e.target.value)} />
        </label>
        <button type="button" className="mc-btn" onClick={handleSaveNotif} disabled={notifSecret.length < 8 || !chatId}>Enregistrer</button>
        <p>Canaux actifs: {channels.length}</p>
      </section>
    </div>
  );
}
