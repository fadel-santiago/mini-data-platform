# Produit — Mini-plateforme Data pour PME

## Problème métier

Une PME dispose souvent de données séparées entre CRM, ERP et facturation. Les équipes recopient des chiffres, les indicateurs divergent et les alertes de stock ou de paiement arrivent trop tard. Ce démonstrateur consolide ces sources dans un entrepôt contrôlé et les restitue dans un tableau de bord décisionnel.

Le projet est une référence de portfolio et non un système prêt pour une production client.

## Utilisateurs cibles

- direction : chiffre d'affaires, marge et tendances ;
- responsable commercial : ventes par région, canal et client ;
- finance : factures échues et priorités de relance ;
- opérations : ruptures et besoins de réapprovisionnement ;
- équipe data : exécution, lineage et qualité du pipeline.

## Périmètre démontré

Le jeu synthétique reproductible contient 16 clients, 84 commandes, 64 factures et 12 références de stock. Il alimente dix modèles dbt et cinq contrôles métier complémentaires aux 23 tests dbt.

### Exigences fonctionnelles

1. Charger cinq fichiers sources CRM, ERP et finance sans créer de doublons.
2. Reprendre uniquement les lignes plus récentes que le watermark de chaque source.
3. Produire des modèles analytiques de ventes, marge, stock et recouvrement.
4. Bloquer le pipeline lorsqu'un contrôle critique échoue.
5. Exposer les résultats dans un dashboard et l'exécution dans Dagster.

### Critères de succès du démonstrateur

- `make test` termine sans erreur ;
- un second chargement inchangé ingère zéro ligne ;
- les 23 tests dbt et les cinq contrôles métier passent ;
- le dashboard et Dagster sont accessibles uniquement depuis la machine locale ;
- les limites sont présentées sans revendiquer de gain client non mesuré.

## Indicateurs de valeur à mesurer

Ces indicateurs décrivent la valeur métier à évaluer lors d'une adaptation, pas des résultats obtenus par ce démonstrateur : temps de production du reporting, taux d'erreurs de rapprochement, fraîcheur des KPI, nombre de sources manuelles supprimées et délai de détection des ruptures ou impayés.

## Hors périmètre actuel

Connecteurs SaaS, données temps réel, authentification, RBAC, haute disponibilité, sauvegardes, alerting externe, chiffrement géré, CI/CD et validation réglementaire. Voir [SECURITY.md](SECURITY.md) et [OPERATIONS.md](OPERATIONS.md).
