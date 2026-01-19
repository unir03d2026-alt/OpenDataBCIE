# METRICS REQUIREMENT: HDBSCAN (VALOR BCIE / OUTLIERS)

## A) CORE METRICS (Comparison Standard)

_Traditional Silhouette/DBI typically do not apply well to density-based clustering with noise._

## B) MODEL SPECIFIC EXTRAS

- [ ] **Number of Clusters Found**
- [ ] **% Noise / Outliers** (Points classified as -1)
- [ ] **Largest Cluster Size (%)**
- [ ] **Top 10 Outliers** (by outlier_score / probability)
- [ ] **Cluster Persistence / Stability** (e_om) (↑)

## C) DASHBOARD INTEGRATION

- [ ] Display in "Metrics" Modal
- [ ] Specific "Outlier Report" View
