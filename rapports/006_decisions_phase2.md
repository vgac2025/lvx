# Rapport 006 — Décisions utilisateur Q-002→Q-016 + Phase 2 démarrée

**Horodatage :** 2026-07-04T23:10:00Z

---

## 1. Demande utilisateur

Enregistrer dans le dépôt (pas le chat seul) :

| Question | Réponse |
|----------|---------|
| Q-015 | **C** — deux unités `pARTCB` + `pubARTCB` |
| Q-016 | **C** — mineurs humain + agent IA |
| Q-002 | **Les deux** — rule-based + Bob LLM |
| Q-004 | **Oui** Gradium |
| Q-006 | **Livre Wailly 100 %** (pas exemple CDC) |
| Q-009 | **D** — clés Bob + Gradium |
| OpenRouter | Hackathon **ne fournit pas** — utiliser clé **Bob CLI** |

**Consigne agent :** développer MVP avancé uniquement ; ne pas solliciter Q-010/hors scope.

---

## 2. État d'avancement (%)

| Phase | Avant | Après |
|-------|-------|-------|
| Spec / décisions | 100 % | **100 %** |
| Phase 1 IR | 100 % | 100 % |
| Phase 2 Backend | 0 % | **~40 %** (PoL, agents, RT-LEG, API base) |
| Phase 3 Blockchain | 0 % | 0 % |
| Phase 4 Frontend | 0 % | 0 % |
| **Global MVP** | ~35 % | **~45 %** |

---

## 3. Correction Q-006 (réponses perdues)

**Avant (`rapports/002_decisions_secrets.md`) :**
> Texte démo **exemple CDC** (anglais)

**Après (`DEMO_TEXTE_ARTCB`, D-010) :**
> `data/fixtures/wailly_le_roi_de_l_inconnu.pdf` — **100 % du livre**

---

## 4. OpenRouter / Bob — avant / après

**Avant (`CONFIGURATION_ARTCB`) :**
> `OPENROUTER_API_KEY` — clé LLM OpenRouter

**Après (`DECISIONS D-022`, `config.py`) :**
```python
bob_api_key=os.getenv("BOB_API_KEY") or os.getenv("OPENROUTER_API_KEY") or None
```
> Hackathon ne fournit pas OpenRouter. **`BOB_API_KEY` canonique** ; `OPENROUTER_API_KEY` = alias.

---

## 5. Fichiers créés

| Fichier | Rôle |
|---------|------|
| `DEMO_TEXTE_ARTCB` | Spec démo Wailly 100% |
| `src/artcb/pol/scorer.py` | PoL + split collectif |
| `src/artcb/agents/explorer.py`, `critic.py` | Dual-agent |
| `src/artcb/rtleg/events.py`, `timeline.py` | RT-LEG |
| `src/api/main.py` | FastAPI Phase 2 |
| `tests/test_pol.py` | 3 tests PoL |

---

## 6. Fichiers modifiés

| Fichier | Changement |
|---------|------------|
| `DECISIONS_UTILISATEUR_ARTCB` | D-010 Wailly ; D-019→D-022 |
| `QUESTIONS_OUVERTES_ARTCB` | v4 — tout résolu sauf Q-010 |
| `TOKENOMICS_ARTCB` | pARTCB / pubARTCB |
| `CONFIGURATION_ARTCB` | Bob alias, demo book |
| `.env.example` | Q-006, Q-002, Q-009 |
| `src/artcb/config.py` | demo_book, pol_*, Bob alias |
| `CHECKLIST_PRE_DEV_ARTCB` | Gate 🟢 |

---

## 7. Tests

```bash
python3 -m pytest tests/ -v
# 31 passed in 4.78s
```

Log : `logs/20260704_phase2_decisions.json`

---

## 8. Reste Phase 2

- [ ] Routes API complètes §8 CDC (search, store, chain)
- [ ] WebSocket temps réel
- [ ] LLM path B (Bob client HTTP)
- [ ] Test livre Wailly couverture 100%

---

**Fin rapport 006**
