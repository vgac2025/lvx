import { useEffect, useState } from "react";
import { fetchRtlegEvents } from "../api/client";

export function Logs() {
  const [events, setEvents] = useState<
    Array<{
      event_id: string;
      timestamp: string;
      agent: string;
      event_type: string;
      session_id: string;
    }>
  >([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRtlegEvents()
      .then(setEvents)
      .catch((e) => setError(e instanceof Error ? e.message : "Erreur chargement"));
  }, []);

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Logs · chat MC</h1>
      <div className="panel mc-chat-log">
        {error && <p className="mc-error">{error}</p>}
        {!events.length && !error && <p className="mc-muted">Aucun événement RT-LEG pour l&apos;instant.</p>}
        <ul className="mc-chat-list">
          {[...events].reverse().map((ev) => (
            <li key={ev.event_id}>
              <span className="mc-chat-ts">[{ev.timestamp}]</span>{" "}
              <span className="mc-chat-event">{ev.agent}</span>{" "}
              <span>{ev.event_type}</span>
              <span className="mc-muted"> · {ev.session_id}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
