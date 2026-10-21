# Exploitation

## Prérequis et données

- Docker Desktop avec Docker Compose 2.24.0 ou ultérieur (`env_file.required`) ;
- ports locaux 5432, 3000 et 8501 disponibles ;
- aucune donnée réelle : `data/sources` contient uniquement le scénario synthétique.

La configuration directe avec Python sur l'hôte n'est pas le chemin supporté. Toutes les commandes ci-dessous passent par Docker.

## Démarrage reproductible

```bash
cp .env.example .env
make demo
```

`make demo` démarre PostgreSQL, Dagster et Streamlit, régénère le scénario synthétique déterministe puis exécute ingestion, dbt et qualité. La date de référence par défaut est `2026-10-11`, identique aux fixtures versionnées ; utiliser `make demo DEMO_AS_OF=YYYY-MM-DD` pour tester volontairement une autre période.

- dashboard : http://127.0.0.1:8501
- Dagster : http://127.0.0.1:3000
- PostgreSQL : `127.0.0.1:5432`

## Commandes courantes

```bash
make pipeline   # ingestion idempotente + dbt + contrôles métier
make test       # tests Python puis pipeline complet
make logs       # logs Dagster et Streamlit
make down       # arrête les services et conserve les volumes
```

`make clean-data` exécute `docker compose down -v` : il supprime les volumes PostgreSQL **et Dagster** du projet Compose sélectionné. Ne l'utiliser que pour réinitialiser volontairement cet environnement synthétique. `make down` conserve ces volumes.

Un changement de dossier ou de nom de projet Compose peut sélectionner d'autres volumes. Avant de déplacer une installation existante de `mini-data-platform` vers `orbit`, conserver son ancien `COMPOSE_PROJECT_NAME` et vérifier les volumes ; le renommage GitHub ne migre pas les données locales. Les commandes PowerShell et les limites de portabilité sont décrites dans le [README anglais](README.md#quick-start).

## Fournir des données

Chaque CSV doit respecter exactement son contrat défini dans `SOURCES` dans `src/pme_data_stack/ingestion.py`. La clé métier doit être stable et `updated_at` doit être un timestamp ISO 8601 croissant.

Pour recréer le scénario à une date donnée :

```bash
docker compose run --rm orchestrator python scripts/generate_demo_data.py --as-of 2026-10-15
```

Après remplacement complet par des données plus anciennes, réinitialiser la base de démonstration ; sinon les watermarks empêcheront leur rechargement.

## Comprendre les sorties

- Dagster indique quelle étape a échoué et conserve ses logs.
- dbt renvoie un statut par modèle et par test ; tout échec critique interrompt `make test`.
- le dashboard présente KPI, stocks, recouvrement et santé des données à partir des tables `marts`.
- une ingestion à zéro ligne après un rejeu inchangé est le comportement attendu.

## Dépannage

| Symptôme | Vérification | Solution courante |
|---|---|---|
| port déjà utilisé | `docker compose ps` | arrêter le service concurrent ou changer le port local |
| base indisponible | état `warehouse` | attendre le healthcheck puis relancer |
| colonnes CSV invalides | message `Colonnes invalides` | aligner les en-têtes sur le `SourceSpec` |
| données non rechargées | watermark de la source | utiliser un `updated_at` plus récent ou réinitialiser la démo |
| test dbt en échec | nom du test dans la sortie | corriger la donnée ou le modèle, puis relancer `make test` |
| dashboard vide | tables `marts` | exécuter `make pipeline` |

## Maintenance et déploiement client

Mettre à jour une dépendance à la fois, reconstruire les images et exécuter `make test`. Pour un client, remplacer les CSV par des connecteurs authentifiés, PostgreSQL local par une base managée privée, `.env` par un gestionnaire de secrets, puis ajouter TLS, RBAC, sauvegardes testées, alerting, CI/CD et supervision. Les précautions sont détaillées dans [SECURITY.md](SECURITY.md).
