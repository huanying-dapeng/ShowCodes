package com.dapeng.fastqstats;

import com.dapeng.utils.ReaderFactory;

import java.util.concurrent.ArrayBlockingQueue;

public class ThreadRunner extends Thread {
    private StatData statData;
    private ReaderFactory.FQSeqRecoredReader reader;
    private int phred;
    private ArrayBlockingQueue<Record> queue;

    public ThreadRunner() {}

    public ThreadRunner(ReaderFactory.FQSeqRecoredReader reader,
                        StatData statData, int phred) {
        this.reader = reader;
        this.statData = statData;
        this.phred = phred;
    }

    public ThreadRunner(ArrayBlockingQueue queue,
                        StatData statData, int phred) {
        this.queue = queue;
        this.statData = statData;
        this.phred = phred;
    }

    @Override
    public void run() {
        long l = System.currentTimeMillis();
        stat();
        long es = System.currentTimeMillis();
        System.out.println(es - l + " " + getName());
    }

    private Record nextRecord() {
        Record record;
        if (queue != null) {
            try {
                record = queue.take();
            } catch (InterruptedException e) {
                e.printStackTrace();
                record = null;
            }
            if (record != null && record.getId() == null && record.getBaseSeq() == null) {
                try {
                    queue.put(new Record(null, null, null));
                    record = null;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            return record;
        } else if (reader != null) {
            return reader.nextRecord();
        } else {
            System.out.println("non-data get");
            System.exit(0);
            return null;
        }
    }

    private void stat() {
        long a = 0;
        long t = 0;
        long c = 0;
        long g = 0;
        long n = 0;
        long q20 = 0;
        long q30 = 0;
        long tReads = 0;
        long tBases = 0;
        long tnReads = 0;
        long qSum = 0;

        // while ((record = reader.nextRecord()) != null) {
        while (true) {
            Record record = nextRecord();

            if (record == null) break;

            char[] charArray = record.getBaseSeq().toCharArray();
            int nFlag = 0;
            tReads++;
            tBases += charArray.length;
            for (char ch : charArray) {
                switch (ch) {
                    case 'A': a++; break;
                    case 'T': t++; break;
                    case 'C': c++; break;
                    case 'G': g++; break;
                    case 'N': n++; nFlag++; break;
                }
            }
            tnReads += nFlag > 0 ? 1 : 0;

            char[] qchs = record.getQualSeq().toCharArray();
            for (char q : qchs) {
                int qul = q - phred;
                qSum += qul;
                if (qul >= 20) {
                    q20++;
                    if (qul >= 30) {
                        q30++;
                    }
                }
            }
        }
        statData.updateData(
                tReads, tBases, tnReads, qSum, a, t, c, g, n, q20, q30);
    }

    public void setStatData(StatData statData) {
        this.statData = statData;
    }

    public void setReader(ReaderFactory.FQSeqRecoredReader reader) {
        this.reader = reader;
    }

    public void setPhred(int phred) {
        this.phred = phred;
    }
}
