#!/usr/bin/env Rscript

# FLYCOP 
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018 // Modification: June 2021

#install.packages("stringr")  # Already installed from the outside of FLYCOP execution!
suppressMessages(library(stringr))
#install.packages("dplyr")  # Already installed from the outside of FLYCOP execution!
suppressMessages(library(dplyr))


# PREPROCESSING OF COMMAND LINE ARGUMENTS
args = commandArgs(trailingOnly=TRUE)
if (length(args)<10) {
  stop("At least 17 arguments must be supplied: <input_file.txt> <output_file.pdf> <met1_ID> <met2_ID> <met3_ID> <met4_ID> <met5_ID> <met6_ID> <endCycle> <title> <colSubs1> <colSubs2> <colSubs3> <colSubs4> <colSubs5> <colSubs6> [<strain_list>]", call.=FALSE)
} else {
  inputFile=args[1]
  outFile=args[2]
  met1=args[3]
  met2=args[4]
  met3=args[5]
  met4=args[6]
  met5=args[7]
  met6=args[8]
  endCycle=as.numeric(args[9])
  title=args[10]
  color1=args[11]
  color2=args[12]
  color3=args[13]
  color4=args[14]
  color5=args[15]
  color6=args[16]
  strain_list=args[17]  # List of strains
}

# MAX value for x
xMax=endCycle

# STRAINS
# ----------------------------------------------------------------
strain_list <- as.list(strsplit(strain_list, split=" ")[[1]])  # Character to list
names(strain_list) <- strain_list  # Name of elements in the list = its own value
strain_list <- as.vector(strain_list)  # as vector
n_strains <- as.numeric(length(strain_list))  # Number of strains
# ----------------------------------------------------------------

# READ COMETS FILE (format: columns)
# --------------------------------------------------------------------
# DATAFRAME		
df=read.csv(inputFile,sep='\t',header=FALSE,col.names=c('sub1','sub2','sub3','sub4', 'sub5', 'sub6', 'sub7', 'hours', strain_list)) 
# MAX value for biomass
biomass_df <- df %>% select(paste(strain_list))  # Fraction of 'df' dataframe with initial biomass values: 1 row, as many columns as strains in 'strain_list'
yMax=max(biomass_df)
# --------------------------------------------------------------------

# PLOT FILE
# --------------------------------------------------------------------
pdf(outFile,pointsize=20)

# BIOMASS
# =======
n_iter <- 0
for (strain in strain_list){
	biomass <- select(df, paste(strain))
	plot(df$hours*0.1, biomass[,1], xlab='time(h)', ylab='biomass (gr/L)', type='l', lty=2, lwd=3, col=colors()[99+n_iter], ylim=c(0,yMax))
	n_iter <- n_iter + 1
	par(new=TRUE)}

# Check biomass plotting colors: colors()[99:(98+n_strains)]
# lty: (0=blank, 1=solid (default), 2=dashed, 3=dotted, 4=dotdash, 5=longdash, 6=twodash)

# METABOLITES
# ===========

# MAX value for substrates
y2Max=max(df$sub1,df$sub2,df$sub3,df$sub4,df$sub5,df$sub6)

par(new=TRUE,lwd=2)
plot(df$hours*0.1,df$sub1,type='l',col=color1,axes=FALSE,xlab="",ylab="",lwd=4,ylim=c(0,y2Max))
par(new=TRUE)
plot(df$hours*0.1,df$sub2,type='l',col=color2,axes=FALSE,xlab="",ylab="",lwd=4,ylim=c(0,y2Max))
par(new=TRUE)
plot(df$hours*0.1,df$sub3,type='l',col=color3,axes=FALSE,xlab="",ylab="",lwd=4,ylim=c(0,y2Max))
par(new=TRUE)
plot(df$hours*0.1,df$sub4,type='l',col=color4,axes=FALSE,xlab="",ylab="",lwd=4,ylim=c(0,y2Max))
par(new=TRUE)
plot(df$hours*0.1,df$sub5,type='l',col=color5,axes=FALSE,xlab="",ylab="",lwd=4,ylim=c(0,y2Max))
par(new=TRUE)
plot(df$hours*0.1,df$sub6,type='l',col=color6,axes=FALSE,xlab="",ylab="",lwd=4,ylim=c(0,y2Max))

axis(side=4)
mtext('metabolite Conc. (mM)',side=4,cex=par("cex.lab"))
par(lty=1)
# --------------------------------------------------------------------

# LEGEND AND TITLE FOR THE PLOT
# --------------------------------------------------------------------
biomass_plot_colors <- as.vector(colors()[99:(98+n_strains)])
legend(x="left", legend=c(met1,met2,met3,met4,met5,met6,strain_list), lty=c(1,1,1,1,1,1,rep(2, each=n_strains)), lwd=c(4,4,4,4,4,4,rep(3, each=n_strains)), col=c(color1,color2,color3,color4,color5,color6,biomass_plot_colors),cex=0.45)
title(main=title, cex.main=0.75)
invisible(dev.off())
# --------------------------------------------------------------------












