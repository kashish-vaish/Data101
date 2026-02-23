z_test_from_data <- function(data,col1,col2,sub1,sub2) {
  data <- as.data.frame(data)
  V1 <- data[,col1]
  V2 <- data[,col2]

  #data clean and subset, either
  X <- subset(data, V1 == sub2)
  Y <- subset(data, V1 == sub1)
  x <- X[,col2]
  y <- Y[,col2]

  # -----------------------------
  # ONE-TAILED TEST ONLY (upper tail)
  # Always tests: mean(high group) > mean(low group)
  # If needed, groups are swapped so z-value is never negative.
  # -----------------------------

  # NA-safe means
  mx <- mean(x, na.rm=TRUE)
  my <- mean(y, na.rm=TRUE)

  # flip so difference is non-negative (no negative z ever)
  if (mx < my) {
    tmp <- x; x <- y; y <- tmp
    tmpm <- mx; mx <- my; my <- tmpm
    print("One-tailed only: swapped groups to keep z >= 0 (H1: higher mean > lower mean).")
  } else {
    print("One-tailed only (upper tail): H1 is higher mean > lower mean.")
  }

  # NA-safe sample sizes and sds
  nx <- sum(!is.na(x))
  ny <- sum(!is.na(y))

  # z score
  zeta <- (mx - my) / (sqrt(sd(x, na.rm=TRUE)^2/nx + sd(y, na.rm=TRUE)^2/ny))
  print(paste(zeta," is the z-value"))

  # plot red line (z on standard normal)
  r <- max(abs(zeta)+0.5, 5)
  grid <- seq(from = -r, to= r, by=0.1)
  plot(x=grid,
       y=dnorm(grid, mean=0),
       type='l',
       xlab = 'z (standardized mean difference)',
       ylab='density')
  abline(v=zeta, col='red')

  # get p (upper-tail one-tailed, consistent after flipping)
  p <- 1 - pnorm(zeta)
  print(paste(p, " is the one-tailed (upper-tail) p-value"))
  return(p)
}

z_test_from_agg <- function(mean_a,mean_b,sd_a,sd_b, n_a, n_b){

  # -----------------------------
  # ONE-TAILED TEST ONLY (upper tail)
  # Always tests: mean(high group) > mean(low group)
  # If needed, inputs are swapped so z-value is never negative.
  # -----------------------------

  # flip so mean_b - mean_a is non-negative (no negative z ever)
  if (mean_b < mean_a) {
    tmp <- mean_a; mean_a <- mean_b; mean_b <- tmp
    tmp <- sd_a;   sd_a   <- sd_b;   sd_b   <- tmp
    tmp <- n_a;    n_a    <- n_b;    n_b    <- tmp
    print("One-tailed only: swapped inputs to keep z >= 0 (H1: higher mean > lower mean).")
  } else {
    print("One-tailed only (upper tail): H1 is higher mean > lower mean.")
  }

  zeta <- (mean_b-mean_a) / (sqrt(sd_a^2/n_a + sd_b^2/n_b))
  print(paste(zeta," is the z-value"))

  # plot red line
  r <- max(abs(zeta)+0.5, 5)
  grid <- seq(from = -r, to= r, by=0.1)
  plot(x=grid,
       y=dnorm(grid, mean=0),
       type='l',
       xlab = 'z (standardized mean difference)',
       ylab='density')
  abline(v=zeta, col='red')

  # get p (upper-tail one-tailed, consistent after flipping)
  p <- 1 - pnorm(zeta)
  print(paste(p, " is the one-tailed (upper-tail) p-value"))
  return(p)
}

permutation_test <- function(df1,c1,c2,n,w1,w2){
  df <- as.data.frame(df1)
  D_null <- c()
  V1 <- df[,c1]
  V2 <- df[,c2]

  sub.value1 <- df[df[, c1] == w1, c2]
  sub.value2 <- df[df[, c1] == w2, c2]
  D <- mean(sub.value2, na.rm=TRUE) - mean(sub.value1, na.rm=TRUE)

  # -----------------------------
  # ONE-TAILED TEST ONLY (upper tail)
  # Always tests: mean(high group) > mean(low group)
  # If needed, labels are swapped so observed D is never negative.
  # -----------------------------

  # flip so D is non-negative (no negative observed diff)
  if (D < 0) {
    tmp <- w1; w1 <- w2; w2 <- tmp
    D <- -D
    print("One-tailed only: swapped groups to keep D >= 0 (H1: higher mean > lower mean).")
  } else {
    print("One-tailed only (upper tail): H1 is higher mean > lower mean.")
  }

  m <- length(V1)
  l <- length(V1[V1==w2])

  for(jj in 1:n){
    null <- rep(w1, length(V1))
    null[sample(m, l)] <- w2
    nf <- data.frame(Key=null, Value=V2)
    names(nf) <- c("Key","Value")
    w1_null <- nf[nf$Key == w1, 2]
    w2_null <- nf[nf$Key == w2, 2]
    D_null <- c(D_null, mean(w2_null, na.rm=TRUE) - mean(w1_null, na.rm=TRUE))
  }

  myhist <- hist(D_null, prob=TRUE)
  multiplier <- myhist$counts / myhist$density
  mydensity <- density(D_null, adjust=2)
  mydensity$y <- mydensity$y * multiplier[1]
  plot(myhist)
  lines(mydensity, col='blue')
  abline(v=D, col='red')

  # one-tailed upper-tail p-value with +1 smoothing
  M <- (sum(D_null >= D) + 1) / (length(D_null) + 1)
  return(M)
}
