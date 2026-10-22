# Standard de reporting réutilisable

## Structure de l'export attendu

Chaque snapshot doit contenir `Activity ID`, `Activity Name`, `WBS Code`, `Discipline`, `Area`, `BL Start`, `BL Finish`, `Start`, `Finish`, `Planned Duration`, `Budgeted Labor Units`, `Physical % Complete`, `Activity Status` et `Data Date`.

Le grain attendu est une ligne par activité et par Data Date. Les dates sont au format ISO ou reconnues sans ambiguïté. `Activity ID` est unique dans un snapshot.

## KPI publiés

Le reporting affiche l'avancement baseline, l'avancement physique, l'écart en points, le SPI, le nombre d'activités en retard, les jalons tenus ou glissés et les courbes prévu/réel/recalé. Les agrégations sont pondérées par `Budgeted Labor Units`.

## Seuils d'alerte

Un SPI supérieur ou égal à 1 est vert. Un SPI entre 0,90 et 1 est orange. Un SPI inférieur à 0,90 est rouge. Toute anomalie d'intégrité sur les dates, l'identifiant, la discipline ou l'avancement bloque la publication tant qu'elle n'est pas documentée.

## Cadence

Le snapshot est mis à jour chaque mois. Le nom de fichier recommandé est `p6_export_YYYYMMDD.csv`. Les exports bruts sont conservés, les données propres sont versionnées séparément et le journal de contrôles est archivé avec le rapport.
