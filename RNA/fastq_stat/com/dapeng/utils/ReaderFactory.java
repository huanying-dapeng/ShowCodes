package com.dapeng.utils;

import com.dapeng.fastqstats.Record;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import java.util.zip.GZIPInputStream;

public class ReaderFactory {
    private ReaderFactory() {}

    public static class BaseReader {
        private FileInputStream fis;
        private BufferedReader br;
        private String nextLine;
        private Pattern pattern = Pattern.compile("\t");


        public BaseReader(String file) {
            setReader(file, file.endsWith(".gz"));
        }

        public BaseReader(File file) {
            this(file.getPath());
        }

        public String nextLine() {
            String tmpLine = nextLine;
            next();
            return tmpLine;
        }

        public String[] nextLineItems() {
            String line = nextLine();
            if (line == null) return null;
            return pattern.split(line);
        }

        private void next() {
            try {
                String line = br.readLine();
                if (line != null) {
                    nextLine = line;
                    return;
                }
                nextLine = null;
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        public boolean hasNext() {
            return nextLine != null;
        }

        private void setReader(String file, boolean isGZFile) {
            try {
                fis = new FileInputStream(file);
                InputStream ism = fis;
                if (isGZFile) {
                    ism = new GZIPInputStream(fis);
                }
                br = new BufferedReader(new InputStreamReader(ism));
            } catch (IOException e) {
                e.printStackTrace();
            }
            next();
        }

        public void close() {
            try {
                if (fis != null) {
                    fis.close();
                }
                if (br != null) {
                    br.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public static class FQSeqRecoredReader {
        private List<BaseReader> baseReaderList = new ArrayList<>();
        private BaseReader baseReader;
        private Record nextRecord;
        private volatile AtomicInteger fNum = new AtomicInteger(0);

        public FQSeqRecoredReader(String ... files) {
            for (String file : files) {
                baseReaderList.add(new BaseReader(file));
            }
            baseReader = baseReaderList.get(0);
            getNext(0);
        }

        public FQSeqRecoredReader(File ... files) {
            this((String[]) Stream.of(files).map(x -> x.getPath()).toArray());
        }

        public synchronized Record nextRecord() {
            Record tmp = nextRecord;
            if (tmp != null) { getNext(1); }
            return tmp;
        }

        private void getNext(int flag) {
            while ((fNum.get() + 1) < baseReaderList.size() && ! baseReader.hasNext()) {
                fNum.getAndIncrement();
                System.out.println(fNum.get());
                baseReader = this.baseReaderList.get(fNum.get());
            }
            String id = baseReader.nextLine();
            if (id == null) {
                nextRecord = null;
                baseReader.close();
                return;
            }

            if (! id.startsWith("@")) {
                System.err.println("fq file data error, the first line of file do not start with @");
                System.exit(0);
            }
            String seq = baseReader.nextLine();
            String secName = baseReader.nextLine();
            if (! secName.startsWith("+")) {
                System.err.println("fq file data error, the third line of file do not start with '+'");
                System.exit(0);
            }
            String qual = baseReader.nextLine();
            nextRecord = new Record(id, seq, qual);
        }
    }

    public static class DictReader {
        private BaseReader baseReader;
        private String[] header;

        public DictReader(String file) {
            baseReader = new BaseReader(file);
            header = baseReader.nextLineItems();
        }

        public DictReader(File file) {
            this(file.toString());
        }

        public HashMap<String, String> nextLineDict() {
            HashMap<String, String> map = new HashMap<>();
            String[] items = baseReader.nextLineItems();

            if (items == null) {
                close();
                return null;
            }

            for (int i = 0; i < items.length; i++) {
                map.put(header[i], items[i]);
            }
            return map;
        }

        public boolean hasNext() {
            return baseReader.hasNext();
        }

        public void close() {
            baseReader.close();
        }
    }
}

