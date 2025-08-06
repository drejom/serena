# Data Analysis Module
# A comprehensive R script for statistical analysis

library(stats)

#' Calculate descriptive statistics for a dataset
#' @param data A numeric vector
#' @return A list containing mean, median, sd, min, max
calculate_descriptive_stats <- function(data) {
  if (!is.numeric(data)) {
    stop("Input must be numeric")
  }
  
  stats_list <- list(
    mean = mean(data, na.rm = TRUE),
    median = median(data, na.rm = TRUE),
    sd = sd(data, na.rm = TRUE),
    min = min(data, na.rm = TRUE),
    max = max(data, na.rm = TRUE),
    n = length(data[!is.na(data)])
  )
  
  return(stats_list)
}

#' Perform linear regression analysis
#' @param x Independent variable
#' @param y Dependent variable
#' @return Linear model object
perform_regression <- function(x, y) {
  if (length(x) != length(y)) {
    stop("x and y must have the same length")
  }
  
  model <- lm(y ~ x)
  return(model)
}

#' DataProcessor S3 class for data transformation
#' @param data Input data frame
DataProcessor <- function(data) {
  if (!is.data.frame(data)) {
    stop("Input must be a data frame")
  }
  
  structure(
    list(
      data = data,
      original_dim = dim(data),
      processed = FALSE
    ),
    class = "DataProcessor"
  )
}

#' Normalize numeric columns in DataProcessor
#' @param obj DataProcessor object
normalize_data <- function(obj) {
  UseMethod("normalize_data")
}

normalize_data.DataProcessor <- function(obj) {
  numeric_cols <- sapply(obj$data, is.numeric)
  
  obj$data[numeric_cols] <- lapply(obj$data[numeric_cols], function(x) {
    (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)
  })
  
  obj$processed <- TRUE
  return(obj)
}

#' Print method for DataProcessor
print.DataProcessor <- function(x, ...) {
  cat("DataProcessor object\n")
  cat("Original dimensions:", x$original_dim[1], "rows,", x$original_dim[2], "columns\n")
  cat("Processed:", x$processed, "\n")
  if (x$processed) {
    cat("Current dimensions:", nrow(x$data), "rows,", ncol(x$data), "columns\n")
  }
}

#' Generate summary report
#' @param data Input data frame
#' @param output_file Optional file path to save report
generate_report <- function(data, output_file = NULL) {
  report <- list()
  
  # Summary statistics for numeric columns
  numeric_cols <- names(data)[sapply(data, is.numeric)]
  
  for (col in numeric_cols) {
    report[[col]] <- calculate_descriptive_stats(data[[col]])
  }
  
  if (!is.null(output_file)) {
    sink(output_file)
    print(report)
    sink()
    cat("Report saved to", output_file, "\n")
  }
  
  return(report)
}

# Example usage function
run_example <- function() {
  # Create sample data
  set.seed(123)
  sample_data <- data.frame(
    x = rnorm(100, mean = 10, sd = 2),
    y = rnorm(100, mean = 15, sd = 3),
    z = rnorm(100, mean = 20, sd = 4)
  )
  
  # Calculate statistics
  stats_x <- calculate_descriptive_stats(sample_data$x)
  print(stats_x)
  
  # Perform regression
  model <- perform_regression(sample_data$x, sample_data$y)
  print(summary(model))
  
  # Use DataProcessor
  processor <- DataProcessor(sample_data)
  processor <- normalize_data(processor)
  print(processor)
  
  # Generate report
  report <- generate_report(sample_data)
  
  return(list(stats = stats_x, model = model, processor = processor, report = report))
}