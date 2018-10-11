library("ggplot2")
args <- commandArgs(trailingOnly = T)
file_in = args[1]
file_ou = args[2]
method  = args[3]
thresh  = args[4]

D <- read.table(file_in,sep = "\t",comment.char = "",quote = "",header = T)
D <- D[order(D$Pvalue),]
D$Description <- paste(as.character(D$ID), as.character(D$Description),sep=" ")
D$Description <- substr(x=as.character(D$Description),start=1,stop=40)

if(method == "fdr"){
    DD <- D[D$FDR<thresh,]
    if(nrow(DD)>0){
        if(nrow(DD) > 30){
            DD <- DD[1:30,]
        }
        D$Description <- factor(D$Description,levels=as.character(D$Description))
        p <- ggplot(data = DD, mapping = aes(x=Enrich_factor,y=Description,size=GeneCount,color=FDR,shape=Class)) + theme_classic(base_family ="Times")
        p <- p + geom_point()
        p <- p + scale_color_continuous(low = "red", high = "yellow",space = "Lab")
        p <- p + theme(panel.border = element_rect(colour = "black", fill=NA, size=1))
        pdf(file = file_ou,width = 10,height = 10)
        print(p)
        dev.off()
    }
}else{
    DD <- D[D$Pvalue<thresh,]
    if(nrow(DD)>0){
        if(nrow(DD) > 30){
            DD <- DD[1:30,]
        }
        DD$Description <- factor(DD$Description,levels=as.character(DD$Description))
        p <- ggplot(data = DD, mapping = aes(x=Enrich_factor,y=Description,size=GeneCount,color=Pvalue,shape=Class)) + theme_classic(base_family ="Times")
        p <- p + geom_point()
        p <- p + scale_color_continuous(low = "red", high = "yellow",space = "Lab")
        p <- p + theme(panel.border = element_rect(colour = "black", fill=NA, size=1))
        pdf(file = file_ou,width = 10,height = 10)
        print(p)
        dev.off()
    }
}