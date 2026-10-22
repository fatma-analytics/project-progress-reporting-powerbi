# Données

Les fichiers `data/raw/p6_export_YYYYMMDD.csv` sont des exports simulés au format P6, produits avec une graine aléatoire fixe dans `build_project.py`. Ils contiennent 300 activités, 5 disciplines, 3 zones et 4 Data Dates. Le dernier export contient volontairement cinq types d'anomalies pour tester le dispositif qualité.

Les fichiers `data/processed/` sont les sorties propres utilisées pour les graphiques et le classeur Excel. Les anomalies ne sont pas silencieusement supprimées : elles sont signalées puis corrigées ou bornées dans la table propre, conformément à la procédure documentée.
