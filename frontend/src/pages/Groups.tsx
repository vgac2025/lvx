export function Groups() {
  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Groupes · multijoueur</h1>
      <div className="panel mc-groups-panel">
        <div className="mc-player-row">
          <div className="mc-player-head">🧑</div>
          <div>
            <strong>Fondateur</strong> — rôle immuable
            <p className="mc-muted">Seul le fondateur peut nommer des admins.</p>
          </div>
        </div>
        <div className="mc-player-row">
          <div className="mc-player-head">👤</div>
          <div>
            <strong>Admin</strong> — nommé par le fondateur
          </div>
        </div>
        <div className="mc-player-row">
          <div className="mc-player-head">👥</div>
          <div>
            <strong>Membre</strong>
          </div>
        </div>

        <p className="mc-muted mc-groups-note">
          API /groups en cours d&apos;intégration — voir GROUPES_RESEAUX_ARTCB.md.
          Sélecteur réseau PRIVÉ / GROUPE / PUBLIC disponible dans le footer.
        </p>
      </div>
    </div>
  );
}
