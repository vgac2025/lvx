# Rapport 022 — Correction Interface et Ajout Métriques Système

**Date** : 2026-07-05 02:57 CEST  
**Auteur** : Agent Advanced (Bob)  
**Contexte** : Correction accès interface + ajout métriques système/hardware

---

## 🚨 Problème Identifié

### Ce que l'utilisateur voit
```
URL accédée: http://localhost:8000/
Résultat: {"detail":"Introuvable"}
```

### Cause
L'utilisateur accède à l'**API Backend** (port 8000) au lieu du **Frontend React** (port 5174).

- **Port 8000** = API REST (JSON uniquement, pas d'interface visuelle)
- **Port 5174** = Interface web React (interface graphique complète)

---

## ✅ Solution : Accès Correct à l'Interface

### URL Correcte
```
http://localhost:5174
```

**PAS** `http://localhost:8000` (c'est l'API, pas l'interface)

### Vérification
```bash
# API Backend (JSON)
curl http://localhost:8000/api/v1/health
# → {"status":"ok","chain":{"block_count":7}}

# Frontend React (HTML)
curl http://localhost:5174
# → <!DOCTYPE html>... (page web complète)
```

---

## 📊 Métriques Système Manquantes

### Ce que l'utilisateur demande
Afficher en temps réel dans l'interface :
- CPU usage (%)
- RAM usage (MB / GB)
- Disk usage (GB)
- Network I/O
- Température CPU
- Nombre de processus
- Uptime système

### État Actuel
❌ **Aucune métrique système** n'est affichée dans l'interface actuelle

L'interface montre uniquement :
- Graphe IR
- Agents doubles
- PoL score
- Blockchain footer

### Solution Requise
Ajouter un endpoint `/api/v1/metrics` qui retourne :
```json
{
  "system": {
    "cpu_percent": 45.2,
    "ram_used_mb": 2048,
    "ram_total_mb": 8192,
    "disk_used_gb": 120.5,
    "disk_total_gb": 500.0,
    "uptime_seconds": 86400
  },
  "hardware": {
    "cpu_model": "Intel Core i7-9750H",
    "cpu_cores": 6,
    "cpu_threads": 12,
    "cpu_temp_celsius": 65.0
  },
  "network": {
    "bytes_sent": 1024000,
    "bytes_recv": 2048000
  },
  "processes": {
    "total": 245,
    "artcb_api": {
      "pid": 81130,
      "cpu_percent": 2.5,
      "memory_mb": 128
    }
  }
}
```

---

## 🎯 Interface Dynamique Demandée

### Exigences Utilisateur
1. **Tout dans une seule page** — pas de scroll ni clic
2. **Modules internes scrollables** — seuls les modules peuvent scroller
3. **Métriques temps réel** — mise à jour automatique toutes les 2 secondes
4. **Layout compact** — tout visible sans scroll de page

### Architecture Proposée
```
┌─────────────────────────────────────────────────────┐
│ Header: ARTCB — Métriques Système (temps réel)     │
├─────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│ │ CPU: 45%    │ │ RAM: 2/8 GB │ │ Disk: 120GB │   │
│ └─────────────┘ └─────────────┘ └─────────────┘   │
├─────────────────────────────────────────────────────┤
│ ┌───────────────────────┐ ┌───────────────────────┐│
│ │ Graphe IR (scrollable)│ │ Agents (scrollable)   ││
│ │                       │ │                       ││
│ │ [Cytoscape viewer]    │ │ Explorer: ...         ││
│ │                       │ │ Critique: ...         ││
│ └───────────────────────┘ └───────────────────────┘│
├─────────────────────────────────────────────────────┤
│ ┌───────────────────────┐ ┌───────────────────────┐│
│ │ PoL Gauge             │ │ Reconstruction        ││
│ │ [Jauge circulaire]    │ │ [Texte côte à côte]   ││
│ └───────────────────────┘ └───────────────────────┘│
├─────────────────────────────────────────────────────┤
│ Footer: Blockchain — 7 blocs, hash: b9ddf9a8...    │
└─────────────────────────────────────────────────────┘
```

**Hauteur page** : 100vh (pas de scroll vertical de page)  
**Modules internes** : overflow-y: auto (scroll interne uniquement)

---

## 📝 Actions Requises

### 1. Créer Endpoint Métriques
```python
# src/api/routes.py
import psutil
import platform

@router.get("/metrics")
async def get_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    
    return {
        "system": {
            "cpu_percent": cpu_percent,
            "ram_used_mb": ram.used // (1024**2),
            "ram_total_mb": ram.total // (1024**2),
            "disk_used_gb": disk.used // (1024**3),
            "disk_total_gb": disk.total // (1024**3),
            "uptime_seconds": int(time.time() - psutil.boot_time())
        },
        "hardware": {
            "cpu_model": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True)
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv
        }
    }
```

### 2. Ajouter Composant Métriques Frontend
```typescript
// frontend/src/components/SystemMetrics.tsx
import { useEffect, useState } from 'react';

export function SystemMetrics() {
  const [metrics, setMetrics] = useState(null);
  
  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch('/api/v1/metrics');
      const data = await res.json();
      setMetrics(data);
    }, 2000); // Mise à jour toutes les 2 secondes
    
    return () => clearInterval(interval);
  }, []);
  
  if (!metrics) return <div>Chargement métriques...</div>;
  
  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <h3>CPU</h3>
        <div className="value">{metrics.system.cpu_percent}%</div>
      </div>
      <div className="metric-card">
        <h3>RAM</h3>
        <div className="value">
          {metrics.system.ram_used_mb} / {metrics.system.ram_total_mb} MB
        </div>
      </div>
      <div className="metric-card">
        <h3>Disk</h3>
        <div className="value">
          {metrics.system.disk_used_gb} / {metrics.system.disk_total_gb} GB
        </div>
      </div>
    </div>
  );
}
```

### 3. Modifier Layout Page Principale
```typescript
// frontend/src/pages/Demo.tsx
import { SystemMetrics } from '../components/SystemMetrics';

export function Demo() {
  return (
    <div className="demo-container" style={{ height: '100vh', overflow: 'hidden' }}>
      <header>
        <h1>ARTCB — Métriques Système</h1>
        <SystemMetrics />
      </header>
      
      <main className="grid-layout">
        <div className="module" style={{ overflowY: 'auto', maxHeight: '40vh' }}>
          <GraphViewer />
        </div>
        <div className="module" style={{ overflowY: 'auto', maxHeight: '40vh' }}>
          <AgentPanel />
        </div>
        <div className="module">
          <PolGauge />
        </div>
        <div className="module" style={{ overflowY: 'auto', maxHeight: '30vh' }}>
          <Reconstruct />
        </div>
      </main>
      
      <footer>
        <BlockchainFooter />
      </footer>
    </div>
  );
}
```

---

## ✅ Vérification Post-Implémentation

### Tests à Effectuer
```bash
# 1. Vérifier endpoint métriques
curl http://localhost:8000/api/v1/metrics | jq .

# 2. Ouvrir interface dans navigateur
xdg-open http://localhost:5174

# 3. Vérifier mise à jour temps réel
# → Les métriques doivent se rafraîchir toutes les 2 secondes
```

### Critères de Validation
- ✅ Métriques CPU/RAM/Disk affichées
- ✅ Mise à jour automatique toutes les 2 secondes
- ✅ Pas de scroll de page (height: 100vh)
- ✅ Modules internes scrollables uniquement
- ✅ Tout visible sans clic ni scroll de page

---

## 📌 Résumé

| Problème | Solution |
|----------|----------|
| Utilisateur accède à port 8000 | Utiliser port 5174 (frontend) |
| Pas de métriques système | Ajouter endpoint `/api/v1/metrics` |
| Interface nécessite scroll | Layout 100vh avec modules scrollables |
| Métriques statiques | Polling toutes les 2 secondes |

**URL Correcte Interface** : http://localhost:5174  
**URL API Backend** : http://localhost:8000/api/v1/

---

**Fin du Rapport 022**