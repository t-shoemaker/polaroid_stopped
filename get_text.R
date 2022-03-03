library(pdftools)
library(stringr)

pdf <- "Polaroid.pdf"
data <- pdf_data(pdf)

output <- list()
for (i in 1:length(data)) {
  d <- data[i][[1]]
  if (nrow(d) != 0) {
    output <- append(output, list(d))
  }
}

for (i in 1:length(output)) {
  num <- str_pad(as.character(i), 4, 'left', 0)
  fname <- paste0("pages/page-", num, ".csv")
  write.csv(output[i], fname)
}
