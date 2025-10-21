#' @title Repeated holdout cross-validation for rpart models
#' @name cross_validate
#' @description Runs `n_iter` random train/validation splits on a data frame and compares
#'
#' Runs n_iter random train/validation splits on a data frame and returns
#' (1) a data frame of per-iteration scores using the subset of predictors in the
#' provided rpart object vs using all predictors, and
#' (2) summary statistics (means/variances) of those scores.
#'
#' @param df data.frame with the full dataset to split repeatedly
#' @param tree an already-fitted \code{rpart} object; its \code{control} and \code{terms()} are reused
#' @param n_iter integer, number of random splits to run
#' @param split_ratio numeric in (0,1), fraction of rows used for training each iteration
#' @param method character, \code{"class"} (default) for classification accuracy or \code{"anova"} for MSE
#'
#' @return A list of length 2:
#' \itemize{
#'   \item \code{[[1]]} data.frame with columns \code{accuracy_subset}, \code{accuracy_all}
#'   \item \code{[[2]]} list with averages and variances for both series
#' }
#'
#' @examples
#' \dontrun{
#'   library(rpart)
#'   fit <- rpart(Species ~ ., data = iris, method = "class")
#'   CVK::cross_validate(iris, fit, n_iter = 5, split_ratio = 0.8)
#' }
#'
#' @import rpart
#' @export
library("rpart")

cross_validate <- function(df, tree, n_iter, split_ratio, method = 'class')
{
  # training data frame df
  df <- as.data.frame(df)

  # mean_subset is a vector of accuracy values generated from the specified features in the tree object
  mean_subset <- c()

  # mean_all is a vector of accuracy values generated from all the available features in the data frame
  mean_all <- c()

  # control parameters for the decision tree
  contro <- tree$control

  # the following snippet will create relations to generate decision trees
  # relation_all will create a decision tree with all the features
  # relation_subset will create a decision tree with only user-specified features in tree
  dep <- all.vars(terms(tree))[1]
  indep <- list()
  relation_all <- as.formula(paste(dep, '.', sep = "~"))
  i <- 1
  while (i < length(all.vars(terms(tree)))) {
    indep[[i]] <- all.vars(terms(tree))[i + 1]
    i <- i + 1
  }
  b <- paste(indep, collapse = "+")
  relation_subset <- as.formula(paste(dep, b, sep = "~"))

  # creating train and test samples with the given split ratio
  # performing cross-validation n_iter times
  for (i in 1:n_iter) {
    sample <-
      sample.int(n = nrow(df),
                 size = floor(split_ratio * nrow(df)),
                 replace = FALSE)
    train <- df[sample,]
    testing  <- df[-sample,]
    type <- typeof(unlist(testing[dep]))

    # decision tree for regression if the method specified is "anova"
    if (method == 'anova') {
      first.tree <-
        rpart(
          relation_subset,
          data = train,
          control = contro,
          method = 'anova'
        )
      second.tree <- rpart(relation_all, data = train, method = 'anova')
      pred1.tree <- predict(first.tree, newdata = testing)
      pred2.tree <- predict(second.tree, newdata = testing)
      mean1 <- mean((as.numeric(pred1.tree) - testing[, dep]) ^ 2)
      mean2 <- mean((as.numeric(pred2.tree) - testing[, dep]) ^ 2)
      mean_subset <- c(mean_subset, mean1)
      mean_all <- c(mean_all, mean2)
    }

    # decision tree for classification
    # if the method specified is not "anova", then this block is executed
    # if the method is not specified by the user, the default option is to perform classification
    else{
      first.tree <-
        rpart(
          relation_subset,
          data = train,
          control = contro,
          method = 'class'
        )
      second.tree <- rpart(relation_all, data = train, method = 'class')
      pred1.tree <- predict(first.tree, newdata = testing, type = 'class')
      pred2.tree <- predict(second.tree, newdata = testing, type = 'class')
      mean1 <- mean(as.character(pred1.tree) == as.character(testing[, dep]))
      mean2 <- mean(as.character(pred2.tree) == as.character(testing[, dep]))
      mean_subset <- c(mean_subset, mean1)
      mean_all <- c(mean_all, mean2)
    }
  }

  # average_accuracy_subset is the average accuracy of n_iter iterations of cross-validation with user-specified features
  # average_acuracy_all is the average accuracy of n_iter iterations of cross-validation with all the available features
  # variance_accuracy_subset is the variance of accuracy of n_iter iterations of cross-validation with user-specified features
  # variance_accuracy_all is the variance of accuracy of n_iter iterations of cross-validation with all the available features
  cross_validation_stats <-
    list(
      "average_accuracy_subset" = mean(mean_subset, na.rm = TRUE),
      "average_accuracy_all" = mean(mean_all, na.rm = TRUE),
      "variance_accuracy_subset" = var(mean_subset, na.rm = TRUE),
      "variance_accuracy_all" = var(mean_all, na.rm = TRUE)
    )

  # creating a data frame of accuracy_subset and accuracy_all
  # accuracy_subset contains n_iter accuracy values on cross-validation with user-specified features
  # accuracy_all contains n_iter accuracy values on cross-validation with all the available features
  cross_validation_df <-
    data.frame(accuracy_subset = mean_subset, accuracy_all = mean_all)
  return(list(cross_validation_df, cross_validation_stats))
}
