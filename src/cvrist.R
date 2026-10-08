library(tidyverse)
library(CVrisk)

data <- read_csv("data/cvrisk.csv") |>
  janitor::clean_names() |>
  mutate(gender = if_else(gender == 1, "male", "female"))
result <- compute_CVrisk(
  data,
  scores = "ascvd_10y_frs",
  age = "age",
  gender = "gender",
  sbp = "sbp",
  bp_med = "bp_med",
  totchol = "totchol",
  hdl = "hdl",
  statin = "statin",
  diabetes = "diabetes",
  smoker = "smoker",
  egfr = "egfr",
  bmi = "bmi"
) |>
  as_tibble() |>
  select(sample_number, endpoint, ascvd_10y_frs) |>
  filter(!is.na(ascvd_10y_frs))

result |>
  mutate(endpoint = factor(endpoint)) |>
  roc_auc(endpoint, ascvd_10y_frs, event_level = "second")

write_csv(result, "results/data/cvrisk.csv")
