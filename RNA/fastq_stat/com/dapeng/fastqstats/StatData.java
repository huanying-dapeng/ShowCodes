package com.dapeng.fastqstats;

/**
 * stat key words:
 *     total_reads,    total_bases,    Reads_with_Ns,
 *     N_Reads_Rate,   A_Rate,         T_Rate,
 *     C_Rate,         G_RateN_Rate,   Error_Rate,
 *     Q20_rate,       Q30_rate,       GC_Rate
 */
public class StatData {
    private String sample;
    private volatile long totalReadNum;
    private volatile long totalBaseNum;
    private volatile long containNReadNum;
    private volatile long qualScoreSum;
    private volatile long aNum;
    private volatile long tNum;
    private volatile long cNum;
    private volatile long gNum;
    private volatile long nNum;
    private volatile long q20Num;
    private volatile long q30Num;

    public StatData() {
    }

    public StatData(String sample) {
        this.sample = sample;
    }

    public StatData(String sample, long totalReadNum, long totalBaseNum,
                    long containNReadNum, long qualScoreSum, long aNum,
                    long tNum, long cNum, long gNum, long nNum, long q20Num,
                    long q30Num) {
        this.sample = sample;
        this.totalReadNum = totalReadNum;
        this.totalBaseNum = totalBaseNum;
        this.containNReadNum = containNReadNum;
        this.qualScoreSum = qualScoreSum;
        this.aNum = aNum;
        this.tNum = tNum;
        this.cNum = cNum;
        this.gNum = gNum;
        this.nNum = nNum;
        this.q20Num = q20Num;
        this.q30Num = q30Num;
    }

    public synchronized void updateData(
            long totalReadNum, long totalBaseNum, long containNReadNum,
            long qualScoreSum, long aNum, long tNum, long cNum, long gNum,
            long nNum, long q20Num, long q30Num) {
        // System.out.println(getDataLine());
        this.totalReadNum += totalReadNum;
        this.totalBaseNum += totalBaseNum;
        this.containNReadNum += containNReadNum;
        this.qualScoreSum += qualScoreSum;
        this.aNum += aNum;
        this.tNum += tNum;
        this.cNum += cNum;
        this.gNum += gNum;
        this.nNum += nNum;
        this.q20Num += q20Num;
        this.q30Num += q30Num;
        // System.out.println(getDataLine());
    }

    /**
     * read number operation
     */
    public long getTotalReadNum() {
        return totalReadNum;
    }

    public synchronized void addTotalReadNum(long totalReadNum) {
        this.totalReadNum += totalReadNum;
    }

    /**
     * base number operation
     */
    public long getTotalBaseNum() {
        return totalBaseNum;
    }

    public synchronized void addTotalBaseNum(long totalBaseNum) {
        this.totalBaseNum += totalBaseNum;
    }

    /**
     * read containing N number operation
     */
    public long getContainNReadNum() {
        return containNReadNum;
    }

    public double getNReadsRatio() {
        return ((containNReadNum + 0.0) / totalReadNum) * 100;
    }

    public synchronized void addContainNReadNum(long containNReadNum) {
        this.containNReadNum += containNReadNum;
    }

    /**
     * base quality operation
     */
    public long getQualScoreSum() {
        return qualScoreSum;
    }

    public synchronized void addQualScoreSum(long qualScoreSum) {
        this.qualScoreSum += qualScoreSum;
    }

    /**
     * base A number operation
     */
    public long getaNum() {
        return aNum;
    }

    public synchronized void addaNum(long aNum) {
        this.aNum += aNum;
    }

    public double getARatio() {
        return ((aNum + 0.0) / totalBaseNum) * 100;
    }

    /**
     * base T number operation
     */
    public long gettNum() {
        return tNum;
    }

    public double getTRatio() {
        return ((tNum + 0.0) / totalBaseNum) * 100;
    }

    public synchronized void addtNum(long tNum) {
        this.tNum += tNum;
    }

    /**
     * base C number operation
     */
    public long getcNum() {
        return cNum;
    }

    public double getCRatio() {
        return ((cNum + 0.0) / totalBaseNum) * 100;
    }

    public synchronized void addcNum(long cNum) {
        this.cNum += cNum;
    }

    /**
     * base G number operation
     */
    public long getgNum() {
        return gNum;
    }

    public double getGRatio() {
        return ((gNum + 0.0) / totalBaseNum) * 100;
    }

    public synchronized void addgNum(long gNum) {
        this.gNum += gNum;
    }

    /**
     * base N number operation
     */
    public long getnNum() {
        return nNum;
    }

    public double getNRatio() {
        return ((nNum + 0.0) / totalBaseNum) * 100;
    }

    public synchronized void addnNum(long nNum) {
        this.nNum += nNum;
    }

    /**
     * base Q20 number operation
     */
    public long getQ20Num() {
        return q20Num;
    }

    public double getQ20Ratio() {
        return ((q20Num + 0.0) / totalBaseNum) * 100;
    }

    public synchronized void addQ20Num(long q20Num) {
        this.q20Num += q20Num;
    }

    /**
     * base Q30 number operation
     */
    public long getQ30Num() {
        return q30Num;
    }

    public double getQ30Ratio() {
        return ((q30Num + 0.0) / totalBaseNum) * 100;
    }

    public synchronized void addQ30Num(long q30Num) {
        this.q30Num += q30Num;
    }

    /**
     * base GC number operation
     */
    public double getGCRatio() {
        return getCRatio() + getGRatio();
    }

    // #Sample_ID	Total_Reads	Total_Bases	Total_Reads_with_Ns	N_Reads%
    // A%	T%	C%	G%	N%	Error%	Q20%	Q30%	GC%
    public String getDataLine() {
        StringBuffer buffer = new StringBuffer();
        double errorRatio = Math.pow(10, ((double) qualScoreSum / totalBaseNum) * -0.1) * 100;
        buffer.append(getSample()).append("\t")  // Sample_ID
                .append(getTotalReadNum()).append("\t")  // Total_Reads
                .append(getTotalBaseNum()).append("\t")  // Total_Bases
                .append(getContainNReadNum()).append("\t")  // Total_Reads_with_Ns
                .append(String.format("%.3f", getNRatio())).append("\t")  // N_Reads%
                .append(String.format("%.3f", getARatio())).append("\t")  // A%
                .append(String.format("%.3f", getTRatio())).append("\t")  // T%
                .append(String.format("%.3f", getCRatio())).append("\t")  // C%
                .append(String.format("%.3f", getGRatio())).append("\t")  // G%
                .append(String.format("%.3f", getNRatio())).append("\t")  // N%
                .append(String.format("%.3f", errorRatio)).append("\t")   // Error%
                .append(String.format("%.3f", getQ20Ratio())).append("\t")  // Q20%
                .append(String.format("%.3f", getQ30Ratio())).append("\t")  // Q30%
                .append(String.format("%.3f", getGCRatio()));  // GC%
        return buffer.toString();
    }

    public String getDataTitleLine() {
        StringBuffer buffer = new StringBuffer();
        buffer.append("Sample_ID").append("\t")  // Sample_ID
                .append("Total_Reads").append("\t")  // Total_Reads
                .append("Total_Bases").append("\t")  // Total_Bases
                .append("Total_Reads_with_Ns").append("\t")  // Total_Reads_with_Ns
                .append("N_Reads%").append("\t")  // N_Reads%
                .append("A%").append("\t")  // A%
                .append("T%").append("\t")  // T%
                .append("C%").append("\t")  // C%
                .append("G%").append("\t")  // G%
                .append("N%").append("\t")  // N%
                .append("Error%").append("\t")   // Error%
                .append("Q20%").append("\t")  // Q20%
                .append("Q30%").append("\t")  // Q30%
                .append("GC%");  // GC%
        return buffer.toString();
    }

    private String getSample() {
        return sample;
    }
}
