# Présentation technique

## Vue d'ensemble

Orbit est une mini-plateforme Data destinée aux PME qui consolide des exports CRM, ERP et finance dans un entrepôt PostgreSQL. Elle automatise l'ingestion incrémentale, transforme les données en indicateurs cohérents et bloque le pipeline lorsqu'un contrôle critique échoue. Un dashboard présente chiffre d'affaires, marge, stocks et factures échues, tandis que Dagster rend l'exécution observable. Le dépôt utilise exclusivement des données synthétiques et démontre une architecture reproductible avec Python, dbt, PostgreSQL, Dagster, Streamlit et Docker. Il s'agit d'un démonstrateur professionnel, pas d'un système déclaré prêt pour la production.

## Cinq capacités démontrées

1. Ingestion incrémentale idempotente avec watermarks et upserts.
2. Modélisation SQL en couches raw, staging et marts.
3. Tests dbt et contrôles métier bloquants historisés.
4. Orchestration et planification d'un pipeline observable.
5. Dashboard décisionnel alimenté par des modèles analytiques communs.

## Trois problèmes métier adressés

- réconcilier des chiffres dispersés entre CRM, ERP et finance ;
- détecter les stocks critiques et les factures échues ;
- fiabiliser les KPI grâce à des définitions et contrôles centralisés.

## Parcours de démonstration technique

1. Exécuter `make demo` pour charger les cinq sources synthétiques et construire les modèles.
2. Dans Dagster, inspecter le job et l'enchaînement ingestion, dbt et contrôles qualité.
3. Dans Streamlit, parcourir les KPI de ventes, marge, stocks et recouvrement.
4. Vérifier l'état des contrôles et consulter `CHANGELOG.md` pour les résultats observés.

## Checklist captures

- utiliser uniquement le jeu synthétique et masquer toute notification système ;
- capturer le dashboard en vue large : KPI, stocks, recouvrement et qualité ;
- capturer Dagster sur le job et son graphe d'étapes ;
- réutiliser les fichiers existants `docs/screenshots/dashboard1.png` à `dashboard4.png` et `docs/screenshots/dagster-pipeline.png` ;
- vérifier lisibilité, date de démonstration et absence de données privées avant publication.
