# Changelog

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
