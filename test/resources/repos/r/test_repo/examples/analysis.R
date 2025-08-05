# Load required libraries
library(stats)

# Sample data analysis
data <- data.frame(
  x = rnorm(100),
  y = rnorm(100),
  group = sample(c("A", "B"), 100, replace = TRUE)
)

# Use utility functions
mean_x <- calculate_mean(data$x)
summary_stats <- summarize_data(data)

# Create model
model <- create_linear_model(y ~ x + group, data)
print(model)