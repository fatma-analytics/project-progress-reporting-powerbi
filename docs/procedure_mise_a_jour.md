# Procédure mensuelle

1. Exporter depuis Primavera P6 les activités du projet avec la baseline, l'avancement physique et le Data Date.
2. Déposer le CSV dans le dossier d'import en respectant le nom `p6_export_YYYYMMDD.csv`.
3. Actualiser Power Query ou exécuter le script Python de préparation. Le classeur Excel met à jour les onglets Import, Contrôles, Données propres, KPI discipline et Courbe S.
4. Lire les contrôles qualité. Corriger dans P6 toute anomalie de date, d'identifiant, de discipline ou de pourcentage avant publication.
5. Publier le rapport Power BI ou l'export PDF, en archivant le snapshot source et le journal de contrôles.

Le délai cible est inférieur à deux minutes sur le périmètre de démonstration. Cette cible dépendra du volume réel et du mode d'actualisation Power BI.
