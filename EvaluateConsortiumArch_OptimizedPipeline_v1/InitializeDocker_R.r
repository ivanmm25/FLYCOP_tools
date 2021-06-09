#!/usr/bin/env Rscript

# Install needed R packages
suppressMessages(install.packages("stringr",repos = "http://cran.us.r-project.org"))
suppressMessages(install.packages("dplyr",repos = "http://cran.us.r-project.org"))

# These packages are not installed, so it is not needed to check it
# If we did not know whether they were installed or not, we should check it in advance

#if(!require(stringr)) suppressMessages(install.packages("stringr",repos = "http://cran.us.r-project.org"))
#if(!require(dplyr)) suppressMessages(install.packages("dplyr",repos = "http://cran.us.r-project.org"))



