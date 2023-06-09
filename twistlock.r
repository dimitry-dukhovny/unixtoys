#!/usr/bin/env Rscript

#---
#title: "Twistlock Report"
#output: html_document
#author: "Dimitry Dukhovny"
#date: "2023-05-31"
#purpose: "Tediously process Twistlock output into something reportable to an ISSO.  Run your scan and run this against the CSV output."
#---

# Library import
print("### Begin noisy library imports")
options(tidyverse.quiet = TRUE)
library(tidyverse)
library(janitor)
library(xlsx)
library(dplyr)
library(stringr)
print("### End   noisy library imports")

# Hardcoded values
kev <- "https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv"

# file reading
print("### Begin startup check")
args = commandArgs(trailingOnly=T)
if (length(args)==0) {
  stop("
    First arg is Twistlock output.
    Second arg is CSV list to ignore.")
} else if (length(args)==1) {
  ignored <- c()
} else {
  ignored <- read.csv(args[2])
  ignored <- ignored$cve
}
infile <- args[1]
outfile <- str_replace(infile, 'csv$', 'xlsx')
# Read Known Exploited Vulnerabilities (KEV)
kev <- read.csv(kev)
tldf <- read.csv(infile)
print("### End   startup check")

# file prep
print("### Begin dataframe massage")
severities <- c("", "low", "moderate", "medium",
  "important", "high", "critical")
tldf$Severity <- factor(
  tldf$Severity, 
  ordered=1, 
  levels=severities
  )

# sort by severity then CVSS
tldf <- tldf %>%
  arrange(desc(Severity), desc(CVSS))

# enumerate repositories, count vulns
prepos <- unique(tldf$Repository)
## scrape out anything in the CSV of ignored vulns
tldf <- tldf[!tldf$CVE.ID %in% ignored, ] 

vulnrep <- tldf %>%
  count(Repository, Severity) %>%
  filter(!is.na(Severity)) %>%
  filter(Severity!="") %>%
  pivot_wider(names_from=Severity, values_from = n) %>%
  #mutate(Total=rowSums(.[, sapply(., is.numeric)])) %>%
  adorn_totals(c("row", "col"))
vulnrep <- data.frame(vulnrep)
rownames(vulnrep) <- vulnrep[,1]
vulnrep
print("### End   dataframe massage")

paste("### Begin data write to", outfile)
# start the workbook with the report
print(vulnrep)
write.xlsx2(vulnrep, file=outfile, sheetName="ALL",
  row.names=FALSE, append = F)
vulnrep <- NULL

# add high and critical across the repos in a separate sheet
bigvulns <- tldf %>%
  filter(Severity=="high"| Severity=="critical") %>%
  select(Repository, Distro, CVE.ID, Type, Severity, Package.Name,
    Package.Version, Vendor.Status, Description)

# save a worksheet per repository in /tmp/out.xlsx, matching against the KEV
# ignore Twistlock's own peccadillos
prepos <- prepos[!prepos=="twistlock/private"]

gc(reset = FALSE, full = TRUE) # memory leak in xlsx
print("#### Begin making a worksheet per repo or image")
for (prepo in prepos) {
  print(prepo)
  tldfsub <- tldf %>%
    filter(Repository == prepo) %>%
    select(Repository, Distro, CVE.ID, Type, Severity, Package.Name,
      Package.Version, Vendor.Status, Description) %>%
    mutate(KEV=(CVE.ID %in% kev$cveID))
  write.xlsx2(tldfsub, outfile, sheetName = prepo, col.names = T,
    row.names = F, append = T, widths=20)
  tldfsub <- NULL
  gc(reset = FALSE, full = TRUE) # memory leak in xlsx
}
print("#### End   making a worksheet per repo or image")
write.xlsx2(bigvulns, outfile, sheetName = "Highlights", col.names = T,
    row.names = F, append = T, widths=20)
paste("### End   data write to", outfile)

# Beautification is separate, so we have a functioning Excel file even if that
#  crappy `xlsx` module spills memory like a toddler with a martini glass
paste("### Begin beatification of", outfile)
wb <- loadWorkbook(outfile)
headerstyle <- CellStyle(wb) + Font(wb, isBold=TRUE)
wrapstyle <- CellStyle(wb) + Alignment(horizontal="ALIGN_LEFT", vertical="VERTICAL_TOP", wrapText=TRUE)
sheets <- getSheets(wb)
for (x in sheets) {
  autoSizeColumn(x, colIndex=1:8)
  toprow <- getRows(x, 1)
  cells <- getCells(toprow)
  lapply(cells, setCellStyle, cellStyle=headerstyle)
  if (x$getSheetName() != "ALL") {
    setColumnWidth(x, 9, 70)
    filledrows=getRows(x, 2:x$getPhysicalNumberOfRows())
    cells <- getCells(row=filledrows, colIndex=c(9))
    lapply(cells, setCellStyle, cellStyle=wrapstyle)
    setRowHeight(filledrows, multiplier=4)
  }
}
saveWorkbook(wb, outfile)
paste("### End   beatification of", outfile)

