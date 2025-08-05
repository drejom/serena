#' Calculate mean of numeric vector
#' @param x numeric vector
#' @return mean value
calculate_mean <- function(x) {
  if (!is.numeric(x)) {
    stop("Input must be numeric")
  }
  mean(x, na.rm = TRUE)
}

#' Create data summary
#' @param data data.frame
#' @return summary statistics
summarize_data <- function(data) {
  list(
    rows = nrow(data),
    cols = ncol(data),
    numeric_cols = sum(sapply(data, is.numeric))
  )
}