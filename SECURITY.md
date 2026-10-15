# Sécurité

## Statut

Ce dépôt est un démonstrateur local avec données synthétiques. Il n'est pas validé pour traiter des données personnelles, financières réelles ou confidentielles.

## Mesures présentes

- aucun secret versionné ; `.env` est ignoré et `.env.example` ne contient que des valeurs de démonstration ;
- ports PostgreSQL, Dagster et Streamlit liés à `127.0.0.1` ;
- valeurs SQL transmises par paramètres et identifiants construits avec `psycopg.sql` ;
- contrats stricts sur les colonnes CSV et conversions de types ;
- contraintes de clés et tests d'intégrité référentielle ;
- séparation des schémas `raw`, `metadata`, `staging`, `marts` et `observability` ;
- images et versions Python épinglées pour la reproductibilité.

## Menaces et limites connues

| Risque | Situation actuelle | Exigence de production |
|---|---|---|
| accès non autorisé | aucune authentification applicative | SSO, RBAC et moindre privilège |
| interception | HTTP local, pas de TLS | TLS de bout en bout |
| secret compromis | mot de passe de démonstration par défaut | gestionnaire de secrets et rotation |
| perte de données | aucune sauvegarde automatisée | sauvegardes chiffrées et restauration testée |
| fichier malveillant | CSV de démonstration seulement | zone d'arrivée isolée, limites et validation renforcée |
| dépendance vulnérable | aucun scan automatisé | SCA, mises à jour et politique de correctifs |
| exposition réseau | loopback local uniquement | sous-réseaux privés, pare-feu et aucune base publique |
| actions non traçables | logs techniques locaux | journal centralisé, rétention et alertes |

Dagster et Streamlit ne doivent pas être exposés directement à Internet. Les comptes base de données doivent être séparés par rôle en production ; le dashboard ne doit disposer que d'un accès en lecture aux marts.

## Données client

Avant toute mission : inventorier les données, définir finalité et rétention, minimiser les colonnes, anonymiser les jeux de développement et obtenir l'accord du responsable de traitement. Ne jamais copier un export client dans ce dépôt public.

## Signalement

Ne pas publier de secret dans une issue. Révoquer immédiatement tout identifiant exposé, retirer la donnée de l'historique avec une procédure coordonnée, puis documenter l'incident sans reproduire le secret.
