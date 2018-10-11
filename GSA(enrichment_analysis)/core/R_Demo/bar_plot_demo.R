args <- commandArgs(trailingOnly = T)
file_in = args[1]
file_ou = args[2]
method  = args[3]
thresh  = args[4]

getMyColor<-function(col1="#008B45",col2="white",cutn=10010,targets){
    targets=round(targets,4)
    ramp_cc<-colorRamp(as.vector(c(col1,col2)))
    continue_cols<-paste(rgb(ramp_cc(round(seq(0,1,length=cutn),4)),max=255),"E5",sep="")
    num2col<-as.data.frame(cbind(round(seq(0,1,length=cutn),4),continue_cols))
    names(num2col)<-c("number","color")
    targetcolor<-vector()
    for(i in 1:length(targets)){
    targetcolor[i]<-as.character(num2col[which(num2col[[1]]==targets[i]),2])
    }
    return(targetcolor)
}

D <- read.table(file_in,sep = "\t",comment.char = "",quote = "",header = T,row.names=1,check.names=FALSE)
D <- D[order(D$Pvalue),]
D$Description <- substr(x=as.character(D$Description),start=1,stop=40)

# if(method == "fdr"){
# DD <- D[D$FDR<thresh,]
# }else{
# DD <- D[D$Pvalue<thresh,]
# }

if(nrow(D) > 40){
    DD <- D[1:40,]
    A = as.numeric(unlist(strsplit(x=as.character(DD$GeneRatio),split="/",fixed=T)))
    a = A[seq(from=1,to=length(A),by=2)]
    b = A[seq(from=2,to=length(A),by=2)]
    DD$ratio = a/b

    Description<- as.character(DD$Description)
    RichFactor <- round(DD$ratio,2)
    Class      <- as.character(DD$Class)

    if(method == "fdr"){
        Pvalue   <- as.numeric(D$FDR)
    }else{
        Pvalue   <- as.numeric(D$Pvalue)
    }

    ### shortname
    %(class_ab)s
    xlabs      <- paste(Description,Class_ab,sep=" : ")
    %(legend_info)s

    ### significant stars:
    n_3tars<-which(Pvalue<=0.001)
    n_2tars<-setdiff(which(Pvalue<=0.01),n_3tars)
    n_1tars<-setdiff(which(Pvalue<=0.05),c(n_3tars,n_2tars))

    ### color card:
    ramp_cc<-colorRamp(as.vector(c("#008B45","white")))
    continue_cols<-paste(rgb(ramp_cc(round(seq(0,1,length=10010),4)),max=255),"E5",sep="")
    barcols<-getMyColor(targets=Pvalue)


    pdf(file=file_ou,width=16,height=7)
    skip<-max(RichFactor)/50
    par(fig=c(0,0.92,0,1),mar = c(12,6,4,0.1)+0.1,new=F)
    bar<-barplot(RichFactor,col=barcols,horiz=FALSE,ylim=c(0,max(RichFactor)+max(RichFactor)/3),axisnames=FALSE,ylab="Ratio:#de_gene/#all_gene",cex.lab=1,font.lab=1,col.lab="black",border=F)
    text(bar,rep(-max(RichFactor)/20,length(bar)),labels=xlabs,srt=30,adj=1,xpd=T,cex=0.5,font=1)
    #text(bar,rep(-0.01,length(bar)),labels=xlabs,srt=30,adj=1,xpd=T,cex=0.5,font=1)
    if(length(n_3tars)!=0){text(bar[n_3tars],RichFactor[n_3tars]+skip,"***",cex=0.4,col="black")}
    if(length(n_2tars)!=0){text(bar[n_2tars],RichFactor[n_2tars]+skip,"**" ,cex=0.4,col="black")}
    if(length(n_1tars)!=0){text(bar[n_1tars],RichFactor[n_1tars]+skip,"*"  ,cex=0.4,col="black")}
    legend("topleft",legend_info,cex=1,bty="n",inset=0)

    ### legend for bar colors:
    par(fig=c(0.91,1,0,0.9),mar = c(12,0.1,4,4)+0.1,new=T)
    Bars<-barplot(rep(0.5,10000),horiz=T,col=continue_cols[10000:1],border=continue_cols[10000:1],space=0,axes=F,xlim=c(0,1),cex.main=1,font.main=1,ylim=c(0,length(continue_cols)+100))
    text(rep(0.6,5),Bars[c(200,2501,5001,7500,9800)],as.character(c(1,0.75,0.5,0.25,0)),cex=1,adj=0,xpd=T)
    text(0,length(continue_cols)+500, method, adj=0, xpd=T)
    dev.off()
}
