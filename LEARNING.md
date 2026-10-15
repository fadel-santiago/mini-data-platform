# Parcours d'apprentissage

Ce guide explique comment reproduire le système. Exécuter les exercices uniquement avec les données synthétiques. Les procédures complètes sont dans [OPERATIONS.md](OPERATIONS.md).

## 1. Conteneurs et services

Docker Compose lance trois processus isolés : PostgreSQL conserve les données, Dagster orchestre, Streamlit restitue. Les noms de services deviennent des noms DNS sur le réseau interne ; `POSTGRES_HOST=warehouse` relie donc Python à la base.

Pourquoi Docker : mêmes versions et mêmes commandes sur chaque machine. Alternative : environnement Python local, plus léger mais plus sensible aux différences de versions.

```bash
docker compose up -d
docker compose ps
docker compose logs dashboard
```

**Exercice :** identifiez dans `docker-compose.yml` les dépendances et expliquez pourquoi le healthcheck précède l'orchestrateur.

## 2. Ingestion incrémentale

Un `SourceSpec` décrit fichier, table, clé, colonnes et conversions. Au premier chargement toutes les lignes sont insérées. Ensuite, seules les lignes dont `updated_at` dépasse le watermark sont sélectionnées. `ON CONFLICT DO UPDATE` rend le rejeu idempotent.

Alternative : rechargement complet, plus simple mais coûteux et risqué sur de gros volumes. En production, CDC ou API incrémentale peut remplacer les CSV.

```bash
docker compose run --rm orchestrator python -m pme_data_stack.cli ingest
```

**Exercice :** ajoutez une copie d'une commande avec la même clé et un `updated_at` plus récent, puis prédisez le nombre de lignes avant d'exécuter l'ingestion.

## 3. Entrepôt et dbt

`raw` conserve la forme source. Les vues `staging` normalisent noms, types et valeurs. Les tables `marts` correspondent à des questions métier. dbt résout les dépendances créées par `ref()`, construit dans l'ordre et associe tests et documentation aux modèles.

Pourquoi PostgreSQL + dbt : SQL portable, contraintes et lineage lisible. DuckDB serait plus simple pour un fichier local ; un entrepôt cloud serait préférable à grande échelle.

```bash
docker compose run --rm orchestrator dbt build --project-dir /app --profiles-dir /app
```

**Exercice :** ajoutez un KPI `average_order_value` à `executive_kpis.sql`, puis ajoutez un test `not_null`.

## 4. Orchestration Dagster

Les opérations forment un graphe : ingestion → dbt → qualité. Une erreur lève une exception et empêche l'étape suivante d'être considérée comme réussie. La planification est fixée à 06:00, fuseau Europe/Paris.

Alternative : cron convient à une commande simple ; Airflow offre un vaste écosystème mais davantage d'administration.

**Exercice :** ouvrez Dagster, lancez le job manuellement et retrouvez dans les logs le nombre total de lignes nouvelles.

## 5. Qualité et observabilité

Les tests dbt couvrent unicité, valeurs obligatoires, relations et règles SQL. `quality.py` ajoute des contrôles transverses et écrit chaque résultat dans `observability.quality_results`. `assert_quality` transforme un échec en pipeline échoué.

**Exercice :** dans une copie du jeu synthétique, créez une quantité négative et observez quel test bloque le pipeline.

## 6. Dashboard Streamlit

Streamlit exécute une application Python à chaque interaction. SQLAlchemy lit les marts ; Plotly transforme les résultats en graphiques. Le dashboard ne recalcule pas les règles métier : celles-ci restent centralisées dans dbt.

Alternative : Power BI facilite l'adoption métier ; React offre davantage de contrôle UX. Streamlit optimise ici le délai de démonstration.

**Exercice :** ajoutez un filtre de région à un graphique en conservant les calculs dans le mart.

## 7. Tester, modifier et étendre

Pour toute modification : écrire ou adapter un test, changer un seul composant, exécuter le test ciblé, puis `make test`. Ajouter une nouvelle source exige son contrat, sa table raw, son modèle staging, ses tests et au moins un consommateur métier.

Erreurs fréquentes : port occupé, base pas encore saine, en-têtes CSV divergents, watermark trop récent et relation source manquante. Les solutions sont dans [OPERATIONS.md](OPERATIONS.md#dépannage).

Pour un client, commencer par les décisions à prendre et les KPI, puis cartographier les systèmes sources, leur propriétaire, la fraîcheur, les volumes et la sensibilité. Concevoir ensuite les contrats et seulement après les connecteurs.

## Validation de compréhension

Trois idées essentielles : l'idempotence permet de rejouer sans dupliquer ; les marts portent la définition commune des KPI ; un pipeline fiable échoue explicitement lorsque la qualité est insuffisante.

**Exercice de synthèse :** ajoutez une source synthétique de paiements et exposez un KPI de délai moyen de règlement avec ingestion, staging, mart, tests et dashboard.

**Question technique :** pourquoi une ligne corrigée avec le même `updated_at` ne sera-t-elle pas reprise, et quelles stratégies permettent de gérer ce cas ?

**Cas métier :** une PME veut relancer chaque matin les factures échues et prévenir les ruptures avant la préparation des commandes ; le job quotidien matérialise les deux listes et le dashboard les rend actionnables.
