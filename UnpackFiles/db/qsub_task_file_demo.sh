
#PBS -N 4_uniprot_sprot 
#PBS -l nodes=1:ppn=2
#PBS -l mem=4G
#PBS -q zh
cd /mnt/ilustre/users/zhipeng.zhao/jobs/GPCR2Cancer/PTM/Uniprot

gunzip -c ./uniprot_sprot.dat.gz > ./uniprot_sprot.dat


