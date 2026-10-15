# Orbit — Mini-plateforme Data pour PME

Orbit consolide des exports CRM, ERP et finance dans un entrepôt contrôlé, puis transforme ces données en indicateurs de ventes, marge, stock et recouvrement. Ce dépôt démontre une chaîne Data Engineering et BI complète, reproductible localement avec des données synthétiques.

> Statut : démonstrateur de portfolio vérifié le 15 octobre 2026. Il n'est pas présenté comme prêt pour une production client.

## Problème et résultat

Les PME pilotent souvent leur activité avec des exports séparés et des définitions de KPI incohérentes. Orbit fournit une source analytique commune, des contrôles bloquants et un dashboard permettant de repérer les tensions opérationnelles.

Le démonstrateur répond à cinq questions :

1. Quel chiffre d'affaires et quelle marge ont été générés ?
2. Quels canaux et régions contribuent aux ventes ?
3. Quels produits sont sous leur seuil de stock ?
4. Quelles factures échues doivent être relancées ?
5. Les données servant ces décisions sont-elles fiables et fraîches ?

## Capacités démontrées

| Couche | Implémentation vérifiée |
|---|---|
| Sources | cinq CSV synthétiques CRM, ERP et finance |
| Ingestion | Python, contrats de colonnes, watermarks et upserts idempotents |
| Entrepôt | PostgreSQL, schémas raw, metadata, staging, marts, observability |
| Transformation | cinq vues staging et cinq tables métier avec dbt |
| Qualité | 23 tests dbt et cinq contrôles métier bloquants |
| Orchestration | job Dagster et planification quotidienne à 06:00 Europe/Paris |
| Restitution | dashboard Streamlit/Plotly et suivi de la santé des données |

~~~mermaid
flowchart LR
    A[CRM / ERP / Finance] --> B[Ingestion Python]
    B --> C[(PostgreSQL)]
    C --> D[dbt staging + marts]
    D --> E[Tests et contrôles]
    D --> F[Dashboard Streamlit]
    G[Dagster] --> B
    G --> D
    G --> E
~~~

L'architecture détaillée est dans [ARCHITECTURE.md](ARCHITECTURE.md).

## Démarrage

Prérequis : Docker Desktop avec Docker Compose.

~~~bash
cp .env.example .env
make demo
~~~

- dashboard : http://127.0.0.1:8501
- orchestration Dagster : http://127.0.0.1:3000
- PostgreSQL : 127.0.0.1:5432

Les services ne sont exposés que sur la machine locale. Les identifiants par défaut sont réservés à cette démonstration synthétique.

## Vérification

~~~bash
make test
~~~

Résultat observé le 15 octobre 2026 :

- 4 tests Python réussis ;
- 10 modèles dbt construits et 23 tests dbt réussis ;
- cinq contrôles métier réussis ;
- second chargement inchangé : zéro ligne nouvelle sur les cinq sources ;
- 16 clients, 84 commandes, 64 factures et 12 références synthétiques.

Les preuves et limites de cette exécution sont consignées dans [CHANGELOG.md](CHANGELOG.md).

## Démonstration technique

Après `make demo`, ouvrir Dagster pour inspecter le job d'ingestion, de transformation et de qualité, puis ouvrir Streamlit pour parcourir les KPI, les alertes de stock, le recouvrement et l'état des contrôles. Le parcours détaillé et la checklist de captures sont dans [PORTFOLIO.md](PORTFOLIO.md).

## Documentation

- [PRODUCT.md](PRODUCT.md) — utilisateurs, exigences et valeur métier ;
- [ARCHITECTURE.md](ARCHITECTURE.md) — composants, flux et compromis ;
- [LEARNING.md](LEARNING.md) — parcours pour comprendre et reproduire ;
- [OPERATIONS.md](OPERATIONS.md) — lancement, usage, maintenance et dépannage ;
- [SECURITY.md](SECURITY.md) — mesures, menaces et exigences de production ;
- [CHANGELOG.md](CHANGELOG.md) — changements et preuves de vérification ;
- [PORTFOLIO.md](PORTFOLIO.md) — synthèse et démonstration techniques.

## Limites

Les sources sont des fichiers locaux et le déploiement utilise une seule machine. Authentification, RBAC, TLS, sauvegardes, alerting, CI/CD, connecteurs réels et haute disponibilité restent à implémenter avant toute production. Aucun gain de productivité ou résultat client n'est revendiqué.

## Checklist de publication GitHub

- [x] données de démonstration synthétiques ;
- [x] secrets exclus et configuration d'exemple fournie ;
- [x] démarrage, exploitation, architecture et sécurité documentés ;
- [x] tests et pipeline exécutés avec succès ;
- [ ] enregistrer une capture du dashboard dans le dépôt ;
- [ ] choisir et ajouter une licence ;
- [x] isoler ce projet dans son propre dépôt sans les autres projets du workspace ;
- [x] vérifier le statut Git et exclure les artefacts générés ;
- [ ] ajouter une CI exécutant les tests sur une base éphémère ;
- [ ] refaire le démarrage sur une machine ou un environnement vierge ;
- [ ] publier seulement après une dernière recherche de secrets.

### Isolation du dépôt

Cette copie est un dépôt autonome. L'espace parent et ses dépôts imbriqués ne font pas partie de son contenu ni de son historique.
