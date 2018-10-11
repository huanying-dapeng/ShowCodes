package com.dapeng.fastqstats;

public class Record {
    private String id;
    private String baseSeq;
    private String qualSeq;

    public Record(String id, String baseSeq, String qualSeq) {
        this.id = id;
        this.baseSeq = baseSeq;
        this.qualSeq = qualSeq;
    }

    public String getId() {
        return id;
    }

    public String getBaseSeq() {
        return baseSeq;
    }

    public String getQualSeq() {
        return qualSeq;
    }

    @Override
    public String toString() {
        return "Record{" +
                "id='" + id + '\'' +
                ", baseSeq='" + baseSeq + '\'' +
                ", qualSeq='" + qualSeq + '\'' +
                '}';
    }
}
