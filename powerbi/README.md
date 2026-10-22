# Modèle Power BI prêt à reproduire

Le projet fournit les briques réutilisables nécessaires à un modèle Power BI : `measures.dax`, `power_query_clean.m`, les exports propres, les courbes hebdomadaires et les règles de seuils.

Le modèle contient quatre pages recommandées : Synthèse projet, Par discipline, Activités en retard et Contrôles qualité. La source de démonstration est `data/processed/activities_clean.csv` et la courbe est `data/processed/s_curve_weekly.csv`.

Un fichier binaire `.pbit` doit être généré par Power BI Desktop ou le service Power BI, qui ne sont pas disponibles dans cet environnement Linux. Aucun faux `.pbit` n'est donc publié. Les mesures et la requête Power Query sont prêtes à être collées dans Power BI Desktop pour produire le template réutilisable.
