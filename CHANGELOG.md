# Changelog

## 2026-10-21 — English-first documentation, branding and portability audit

- Rewrote `README.md` as **ORBIT — Data Engineering & Business Intelligence**; retained the French overview in `README.fr.md`, five screenshots, architecture, setup and dated verification evidence.
- Documented Compose 2.24.0+, PowerShell equivalents (execution unverified), volume/project-name precautions, dashboard filter scope and date-dependent receivables.
- Added `docs/PORTABILITY_AUDIT.md` with confirmed findings, OS verification boundaries, licensing/dependency/security limits, remaining French material and branding recommendations.
- Read-only GitHub checks confirmed the canonical name `fadel-santiago/orbit`, a remote MIT license missing locally, and the existing successful Ubuntu CI run from 17 October. No repository rename or Git synchronization was performed.
- Corrected the French operations guide's volume-deletion warning, the product document's CI/CD scope and the portfolio screenshot paths.
- Lightweight checks passed: relative links/anchors and image-file existence, fenced blocks, `git diff --check`, and `docker compose --env-file .env.example config --no-env-resolution --quiet` using Compose 5.3.1. The existing public case-study URL returned HTTP 200.
- No application/configuration/dependency changes, new pipeline tests, Docker builds/runs, media generation, commits, pushes or publication. Existing untracked video scripts were preserved.

## 2026-10-17 — Vérification finale O1

- `cp .env.example .env`, `make demo` et `make test` exécutés depuis un clone local propre avec projet Compose, ports et volumes isolés ;
- 4 tests Python, 10 modèles dbt, 23 tests dbt et 5 contrôles métier réussis ;
- second chargement inchangé : 0 ligne ingérée pour chacune des cinq sources ;
- persistance PostgreSQL confirmée après recréation des conteneurs sans suppression des volumes ;
- Streamlit sain (`/_stcore/health` : `ok`) et Dagster accessible (HTTP 200) ;
- génération de démonstration rendue déterministe et affichage des ports corrigé.

## 2026-10-15 — Dépôt portfolio isolé

- copie autonome créée sans modifier le workspace source ;
- caches, artefacts générés, données locales et dépôts étrangers exclus ;
- ports hôte configurables afin de permettre une vérification Docker isolée ;
- présentation technique ajoutée dans `PORTFOLIO.md`.

### Vérification isolée

- reconstruction des images et démarrage sous le projet Compose temporaire `mini-data-platform-verification` : succès ;
- `make test` : 4 tests Python réussis, pipeline chargé avec les cinq sources synthétiques ;
- dbt : 10 modèles construits, 23 tests réussis, 0 avertissement et 0 erreur ;
- contrôles métier : 5 réussis sur 5 ;
- PostgreSQL sain, dashboard Streamlit (`/_stcore/health`) : `ok`, interface Dagster : HTTP 200 ;
- aucun test sur une machine entièrement vierge n'est revendiqué.

## 2026-10-15 — Démonstrateur vérifié

### Modifié

- documentation produit, architecture, apprentissage, exploitation et sécurité ajoutée ;
- README recentré sur la valeur métier et la démonstration ;
- ports Docker liés à `127.0.0.1` pour éviter une exposition réseau par défaut.

### Preuves de vérification

- `make test` : succès ;
- pytest : 4 tests réussis en 0,07 s ;
- dbt : 10 modèles construits, 23 tests réussis, 0 avertissement et 0 erreur ;
- contrôles métier : 5 réussis sur 5 ;
- rejeu incrémental inchangé : 0 ligne ingérée pour chacune des cinq sources ;
- base synthétique : 16 clients, 84 commandes, 64 factures, 12 références ;
- Docker : `warehouse` sain, `orchestrator` et `dashboard` actifs ;
- contrôle visuel : dashboard Streamlit chargé avec KPI ; interface Dagster exposée sur le port local documenté.

### Non vérifié ou non implémenté

- reconstruction sans cache sur une machine vierge ;
- charge, concurrence, reprise après panne et restauration de sauvegarde ;
- authentification, RBAC, TLS, alerting, CI/CD et déploiement cloud ;
- aucune mesure de gain métier ou de performance n'est revendiquée.

## Historique antérieur

L'état antérieur n'était pas suivi par des commits dans le dépôt racine. Cette copie démarre donc un historique Git indépendant.
