z_test_from_data <- function(data,col1,col2,sub1,sub2) {
 data <- as.data.frame(data)
 V1<-data[,col1]
 V2<-data[,col2]
 #data clean and subset, either
 X <- subset(data, V1 == sub2)
 Y <- subset(data, V1 == sub1)
 x <- X[,col2]
 y <- Y[,col2]
 #z score
 zeta<-(mean(x)-mean(y))/(sqrt(sd(x)^2/length(x) +sd(y)^2/length(y)))
 print(paste(zeta," is the z-value"))
 #plot red line
 r <- max(zeta+0.5, 5)
 plot(x=seq(from = -r, to= r, by=0.1),y=dnorm(seq(from = -r, to= r,  by=0.1),mean=0),type='l',xlab = 'mean difference',  ylab='possibility')
 abline(v=zeta, col='red')
 #get p
 p = 1-pnorm(zeta)
 print(paste(p, " is the p-value"))
 return(p)
}

z_test_from_agg<-function(mean_a,mean_b,sd_a,sd_b, n_a, n_b){
 zeta<-(mean_b-mean_a)/(sqrt(sd_a^2/n_a + sd_b^2/n_b))
 print(paste(zeta," is the z-value"))
 #plot red line
 r <- max(zeta+0.5, 5)
 plot(x=seq(from = -r, to= r, by=0.1),y=dnorm(seq(from = -r, to= r,  by=0.1),mean=0),type='l',xlab = 'mean difference',  ylab='possibility')
 abline(v=zeta, col='red')
 #get p
 p = 1-pnorm(zeta)
 print(paste(p, " is the p-value"))
 return(p)
}

permutation_test <- function(df1,c1,c2,n,w1,w2){
  df <- as.data.frame(df1)
  D_null<-c()
  V1<-df[,c1]
  V2<-df[,c2]
  sub.value1 <- df[df[, c1] == w1, c2]
  sub.value2 <- df[df[, c1] == w2, c2]
  D <-  mean(sub.value2, na.rm=TRUE) - mean(sub.value1, na.rm=TRUE)
  m=length(V1)
  l=length(V1[V1==w2])
  for(jj in 1:n){
    null <- rep(w1,length(V1))
    null[sample(m,l)] <- w2
    nf <- data.frame(Key=null, Value=V2)
    names(nf) <- c("Key","Value")
    w1_null <- nf[nf$Key == w1,2]
    w2_null <- nf[nf$Key == w2,2]
    D_null <- c(D_null,mean(w2_null, na.rm=TRUE) - mean(w1_null, na.rm=TRUE))
  }
  myhist<-hist(D_null, prob=TRUE)
  multiplier <- myhist$counts / myhist$density
  mydensity <- density(D_null, adjust=2)
  mydensity$y <- mydensity$y * multiplier[1]
  plot(myhist)
  lines(mydensity, col='blue')
  abline(v=D, col='red')
  M <- (sum(D_null >= D) + 1) / (length(D_null) + 1)
  return(M)
}
