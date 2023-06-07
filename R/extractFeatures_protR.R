library("protr")


myprops <- data.frame(
  AccNo = c("TOP-IDP", "B-value", "FoldUnfold","Net Charge","DisProt"),
  A = c(0.06,0.994,19.89,0,0.042), R = c(0.18,1.026,21.03,1,0.211),
  N = c(0.007,1.022,18.49,0,-0.106), D = c(0.192,1.022,17.41,-1,0.127),
  C = c(0.02,0.939,23.52,0,-0.546), E = c(0.736,1.052,17.46,-1,0.469),
  Q = c(0.318,1.041,19.23,0,0.381), G = c(0.166,1.018,17.11,0,0.095),
  H = c(0.303,0.967,21.72,0,-0.127), I = c(-0.486, 0.977,25.71,0,-393),
  L = c(-0.326,0.982, 25.36,0,-0.26), K = c(0.586,1.029,18.19,1,0.37),
  M = c(-0.397, 0.963,24.82,0,0.197), F = c(-0.697, 0.934, 27.18,0,-0.381),
  P = c(0.987,1.05,17.43,0,0.419), S = c(0.341,1.025,17.67,0,0.201),
  T = c(0.059,0.998,19.81,0,-0.116), W = c(-0.884, 0.938, 28.48,0,-0.465),
  Y = c(-0.51, 0.981,25.93,0,-0.427), V = c(-0.121,0.968,23.93,0,-0.302))



main <- function() {
  
  args= commandArgs(trailingOnly = TRUE)
  filename <- args[1]
  filename_2 <- args[2]
  
  
  ##import IDR sequences
  sequences <- readFASTA(file = filename)
  
  #program only works with proteins with IDR sequences larger than 15 aas
  ifelse(any(nchar(sequences)<16), "you have a sequence that has an IDR shorter than 16, they will be removed" , "all sequences are larger than 15 sequences, proceeding" )
  
  x=sequences[(which(lapply(sequences,nchar)>6))]
  
  
  PAAC=sapply(x,extractPAAC,customprops = myprops, props = c("TOP-IDP", "B-value", "FoldUnfold","Net Charge","DisProt"),lambda=5)
  
  DC=sapply(x,extractDC)
  
  MB_autocorr=sapply(x,extractMoreauBroto,customprops = myprops, props = c("TOP-IDP", "B-value", "FoldUnfold","Net Charge","DisProt",    "CIDH920105", "BHAR880101","CHAM820101", "CHAM820102"),nlag=5)
  
  CTDC=sapply(x,extractCTDC)
  
  
  QSO=sapply(x,extractQSO,nlag=5)
  
  final_feature_matrix <- cbind(t(QSO), t(CTDC),t(MB_autocorr),t(PAAC),t(DC))
  

  write.table(final_feature_matrix,file=filename_2,quote = FALSE,sep="\t") # keeps the rownames
  
  
}

main()
