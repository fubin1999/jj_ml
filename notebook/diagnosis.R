library(tidyverse)
library(patchwork)

mono_data <- read_csv("data/mono.csv")
multi_data <- read_csv("data/multi.csv")

pep_mono_data <- mono_data |>
  select(Endpoint, A2MG, APOB)
pep_multi_data <- multi_data |>
  select(Endpoint, A2MG, APOB)

pep_data <- bind_rows(
  list(mono_center = pep_mono_data, multi_center = pep_multi_data),
  .id = "cohort"
) |>
  mutate(Endpoint = as.factor(Endpoint))

p1 <- ggplot(pep_data, aes(log2(A2MG), log2(APOB))) +
  geom_point(aes(color = Endpoint)) +
  theme_classic()

p2 <- ggplot(pep_data, aes(log2(A2MG), log2(APOB))) +
  geom_point(aes(color = cohort)) +
  theme_classic()

p1 + p2

ggplot(mono_data, aes(factor(Endpoint), P)) +
  geom_boxplot()
