import { useEffect, useState } from "react";
import {
  deleteConnector,
  fetchConnectors,
  learnFromSource,
  saveConnector,
  testConnector,
} from "../api/client";

type ConnectorItem = {
  connector_id: string;
  provider: string;
  label: string;
  config: Record<string, string>;
  api_key_masked?: string;
  kind: string;
  last_test_ok?: boolean | null;
  last_test_message?: string | null;
};

const LLM_PROVIDERS = [
  { id: "openai", name: "ChatGPT (OpenAI)", model: "gpt-4o-mini" },
  { id: "anthropic", name: "Claude (Anthropic)", model: "claude-3-5-haiku-20241022" },
  { id: "bob", name: "IBM Bob", model: "ibm/granite-3-8b-instruct" },
];

const DATA_PROVIDERS = [
  { id: "supabase", name: "Supabase (lecture table client)" },
  { id: "sqlite", name: "SQLite (fichier local)" },
  { id: "postgres", name: "PostgreSQL" },
  { id: "mysql", name: "MySQL" },
];

export function Integrations() {
  const [connectors, setConnectors] = useState<ConnectorItem[]>([]);
  const [llmProviders, setLlmProviders] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [provider, setProvider] = useState("openai");
  const [label, setLabel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [projectUrl, setProjectUrl] = useState("");
  const [table, setTable] = useState("");
  const [dbPath, setDbPath] = useState("");
  const [model, setModel] = useState("gpt-4o-mini");
  const [learnLlm, setLearnLlm] = useState("openai");

  const reload = async () => {
    const data = await fetchConnectors();
    setConnectors(data.connectors);
    setLlmProviders(data.llm_providers);
  };

  useEffect(() => {
    reload().catch((e) => setError(String(e)));
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const config: Record<string, string> = {};
      if (LLM_PROVIDERS.some((p) => p.id === provider)) {
        config.model = model;
      }
      if (provider === "supabase") {
        config.project_url = projectUrl;
        config.table = table;
      }
      if (provider === "sqlite") {
        config.database_path = dbPath;
        config.table = table;
        config.text_column = "content";
      }
      if (provider === "postgres" || provider === "mysql") {
        config.table = table;
        config.text_column = "content";
      }
      await saveConnector({ provider, label: label || provider, api_key: apiKey, config });
      setApiKey("");
      setSuccess("Connecteur enregistré — clé chiffrée localement sur votre machine");
      await reload();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async (id: string) => {
    setLoading(true);
    try {
      const r = await testConnector(id);
      setSuccess(r.ok ? `Test OK: ${r.message}` : `Test échoué: ${r.message}`);
      await reload();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const handleLearn = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const r = await learnFromSource(id, {
        use_llm: !!learnLlm,
        llm_provider: learnLlm || undefined,
      });
      setSuccess(
        `Apprentissage OK — ${r.node_count} nœuds, ${r.chars_ingested} caractères. ` +
          "Allez sur Mémoriser → Graver pour écrire sur la blockchain.",
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    await deleteConnector(id);
    await reload();
  };

  const isLlm = LLM_PROVIDERS.some((p) => p.id === provider);

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Intégrations · Clés API apprentissage</h1>
      <p className="mc-hint">
        Connectez <strong>votre</strong> IA (ChatGPT, Claude…) et <strong>vos</strong> sources de données.
        Les clés restent chiffrées sur <strong>votre machine</strong> — jamais sur un cloud ARTCB.
        La blockchain ARTCB reste en JSON local ; vos bases servent uniquement de <em>source d&apos;apprentissage</em>.
      </p>

      {error && <p className="mc-error">{error}</p>}
      {success && <p className="mc-success">{success}</p>}

      <section className="mc-card">
        <h2>Nouveau connecteur</h2>
        <label>
          Type
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <optgroup label="IA (enrichissement)">
              {LLM_PROVIDERS.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </optgroup>
            <optgroup label="Source de données (apprentissage)">
              {DATA_PROVIDERS.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </optgroup>
          </select>
        </label>
        <label>
          Nom affiché
          <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Mon ChatGPT perso" />
        </label>
        {isLlm && (
          <label>
            Modèle
            <input value={model} onChange={(e) => setModel(e.target.value)} />
          </label>
        )}
        {provider === "supabase" && (
          <>
            <label>
              URL projet Supabase
              <input value={projectUrl} onChange={(e) => setProjectUrl(e.target.value)} placeholder="https://xxx.supabase.co" />
            </label>
            <label>
              Table à lire
              <input value={table} onChange={(e) => setTable(e.target.value)} placeholder="documents" />
            </label>
          </>
        )}
        {provider === "sqlite" && (
          <>
            <label>
              Chemin fichier .db
              <input value={dbPath} onChange={(e) => setDbPath(e.target.value)} placeholder="/chemin/ma_base.db" />
            </label>
            <label>
              Table
              <input value={table} onChange={(e) => setTable(e.target.value)} placeholder="docs" />
            </label>
          </>
        )}
        {(provider === "postgres" || provider === "mysql") && (
          <label>
            Table
            <input value={table} onChange={(e) => setTable(e.target.value)} />
          </label>
        )}
        <label>
          {provider === "postgres" || provider === "mysql"
            ? "Chaîne de connexion (stockée chiffrée localement)"
            : "Clé API (stockée chiffrée localement)"}
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={isLlm ? "sk-… ou clé fournie par la plateforme" : "clé ou connection string"}
            autoComplete="off"
          />
        </label>
        <button type="button" className="mc-btn" disabled={loading || apiKey.length < 8} onClick={handleSave}>
          Connecter
        </button>
      </section>

      <section className="mc-card">
        <h2>Connecteurs actifs ({connectors.length})</h2>
        {connectors.length === 0 && <p>Aucun — ajoutez votre clé ChatGPT, Claude ou source de données.</p>}
        <ul className="mc-connector-list">
          {connectors.map((c) => (
            <li key={c.connector_id} className="mc-connector-item">
              <strong>{c.label}</strong> — {c.provider} ({c.kind})
              {c.api_key_masked && <span> · {c.api_key_masked}</span>}
              {c.last_test_ok != null && (
                <span> · test {c.last_test_ok ? "✓" : "✕"} {c.last_test_message}</span>
              )}
              <div className="mc-connector-actions">
                <button type="button" className="mc-btn-sm" onClick={() => handleTest(c.connector_id)}>Tester</button>
                {c.kind === "data_source" && (
                  <>
                    <select value={learnLlm} onChange={(e) => setLearnLlm(e.target.value)}>
                      <option value="">Apprendre sans IA</option>
                      {llmProviders.map((p) => (
                        <option key={p} value={p}>+ IA {p}</option>
                      ))}
                    </select>
                    <button type="button" className="mc-btn-sm" onClick={() => handleLearn(c.connector_id)}>
                      Apprendre cette source
                    </button>
                  </>
                )}
                <button type="button" className="mc-btn-sm mc-btn-danger" onClick={() => handleDelete(c.connector_id)}>
                  Déconnecter
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
