-- Remplacer PROJECT.DATASET par le projet et dataset BigQuery.
CREATE OR REPLACE VIEW `PROJECT.DATASET.v_kpi_discipline` AS
SELECT Discipline,
       COUNT(*) AS activities,
       SUM(`Budgeted Labor Units`) AS budgeted_units,
       SAFE_DIVIDE(SUM(`Budgeted Labor Units` * `Physical % Complete`), SUM(`Budgeted Labor Units`)) AS actual_progress,
       SAFE_DIVIDE(SUM(`Budgeted Labor Units` * `Planned %`), SUM(`Budgeted Labor Units`)) AS planned_progress,
       SAFE_DIVIDE(SUM(`Budgeted Labor Units` * `Physical % Complete`), SUM(`Budgeted Labor Units` * `Planned %`)) AS spi
FROM `PROJECT.DATASET.activities_clean`
GROUP BY Discipline;

CREATE OR REPLACE VIEW `PROJECT.DATASET.v_late_activities` AS
SELECT *
FROM `PROJECT.DATASET.activities_clean`
WHERE `Activity Status` <> 'Complete'
  AND `BL Finish` < `Data Date`;

CREATE OR REPLACE VIEW `PROJECT.DATASET.v_s_curve` AS
SELECT Week, `Planned Cum %`, `Actual Cum %`, `Forecast Cum %`
FROM `PROJECT.DATASET.s_curve_weekly`
ORDER BY Week;
