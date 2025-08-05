#' S3 class constructor for LinearModel
#' @param formula model formula
#' @param data data frame
#' @return LinearModel object
create_linear_model <- function(formula, data) {
  model <- lm(formula, data)
  structure(
    list(
      model = model,
      formula = formula,
      data = deparse(substitute(data))
    ),
    class = "LinearModel"
  )
}

#' Print method for LinearModel
print.LinearModel <- function(x, ...) {
  cat("Linear Model:", deparse(x$formula), "\n")
  cat("Data:", x$data, "\n")
  print(summary(x$model))
}