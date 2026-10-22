# Méthode de calcul de la courbe en S

Le projet utilise des activités pondérées par leurs unités de travail budgétées. Pour chaque activité, l'avancement prévu à une semaine donnée est calculé par interpolation linéaire entre `BL Start` et `BL Finish`, bornée entre 0 % et 100 %. La courbe baseline est la somme des avancements prévus multipliés par les unités budgétées, divisée par le total budgété.

L'avancement réel est l'avancement physique pondéré observé au dernier Data Date. Pour les semaines antérieures au dernier snapshot, le script applique un profil d'avancement cohérent avec le planning et un facteur de productivité par discipline. Dans un vrai reporting, cette partie est remplacée par l'historique réel des mises à jour P6.

Le recalé conserve le réel au Data Date, puis répartit le reste à faire jusqu'à la fin du projet. Cette projection est volontairement simple et transparente. Un projet réel pourrait utiliser les tendances de production, les contraintes de calendrier, les activités restantes et les dates de fin recalculées par P6.

Le SPI est `Actual % / Planned %`. Un SPI inférieur à 1 indique un retard par rapport à la baseline. Les seuils de lecture du dashboard sont : vert si SPI >= 1, orange entre 0,90 et 1, rouge si SPI < 0,90.
