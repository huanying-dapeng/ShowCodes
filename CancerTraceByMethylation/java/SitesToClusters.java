package com.dapeng.sites2clusters;

import com.dapeng.clusters.ClustersMap;
import com.dapeng.conf.ConfigInfo;
import com.dapeng.utils.CommTools;
import com.dapeng.utils.ReaderFactory;
import com.dapeng.utils.WriteFactor;
import com.dapeng.utils.readers.BaseFileReader;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Stream;

public class SitesToClusters {
    private AtomicInteger threadNumber;
    private ConfigInfo conf;
    private List<FileInfo> fileInfosList;

    public SitesToClusters() {
        conf = ConfigInfo.getInstance();
        threadNumber = new AtomicInteger(conf.getThreadNumber());
        fileInfosList = getFilesInfoList(conf.getSitesFilesList());
    }

    public static void main(String[] args) {
        long l = System.currentTimeMillis();
        SitesToClusters stc = new SitesToClusters();

        // create a data queue
        ArrayBlockingQueue<String> arrayBlockingQueue =
                new ArrayBlockingQueue<String>(10000);

        // output data
        WriteFactor.TextWriter textWriter =null;

        int flag = 100;
        String flagString;
        for (FileInfo fileInfo : stc.fileInfosList) {
            flag++;
            flagString = "flag_" + flag;

            // clusters map object
            ClustersMap clustersMap = ClustersMap.getInstance(true);
            // read cpgSitesFile handler
            boolean header = fileInfo.isIs_multi_samples() ? true : ! fileInfo.has_header;
            BaseFileReader fr = ReaderFactory.getFileReader(fileInfo.getPath(), header);
            // set sample name
            if (fileInfo.isIs_multi_samples()) {
                String[] items = fr.nextItems();
                System.out.println(Arrays.toString(items));
                items = Arrays.copyOfRange(items, 2, items.length);
                clustersMap.bindSamples(items);
            } else {
                String sample_name = fileInfo.sample_name;
                clustersMap.bindSamples(sample_name.length() > 0 ? sample_name : "sites2clusters");
            }

            if (stc.conf.getThreadNumber() > 1) {// create threads
                ArrayList<STCRunner> threads = stc.createThreads(
                        stc.conf, arrayBlockingQueue, clustersMap, !fileInfo.isIs_multi_samples());
                // add record line to queue
                String line;
                try {
                    while ((line = fr.nextLine()) != null) {
                        arrayBlockingQueue.put(line);
                    }
                    arrayBlockingQueue.put("<--null-->");
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                for (STCRunner runner : threads) {
                    try {
                        runner.join();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
            else {
                // add record line to queue
                String line;
                STCRunner runner = new STCRunner(
                        clustersMap, null, !fileInfo.isIs_multi_samples());
                if (fileInfo.isIs_multi_samples()) {
                    while ((line = fr.nextLine()) != null) {
                        runner.multiSamplesRun(line);
                    }
                }
                else {
                    while ((line = fr.nextLine()) != null) {
                        runner.oneSampleRun(line);
                    }
                }
            }

            String[] filePath = {fileInfo.class_name, fileInfo.sample_name, "cluster.txt"};

            WriteFactor.TextWriter writer = WriteFactor.getTextwriter(
                    flagString, stc.conf.getOutdir(), String.join("_", filePath));
            String clustersString = clustersMap.getClustersString();
            String result = clustersMap.getResult();
            // out to per file
            // System.out.println(clustersString);
            writer.writeLine(clustersString);
            writer.writeLine(result);

            if (stc.conf.isMerging()) {
                if (textWriter == null) {
                    String time = String.valueOf(System.currentTimeMillis());
                    time = time.substring(time.length() - 3, time.length());
                    File file = new File(stc.conf.getOutdir(), time + "_" + "merged_clusters.txt");
                    textWriter = WriteFactor.getTextwriter("merger", file);
                    // output to clusters index to file
                    textWriter.writeLine(clustersString);
                }
                // output to mergre
                textWriter.writeLine(result);
            }

            // System.out.println(result);
            // clear the arrayBlockingQueue
            arrayBlockingQueue.clear();
        }
        System.out.println(System.currentTimeMillis() - l);
        textWriter.close();
    }

    private ArrayList<STCRunner> createThreads(ConfigInfo conf, ArrayBlockingQueue<String> queue,
                               ClustersMap clustersMap, boolean isOneSample) {
        int threadNumber = conf.getThreadNumber();
        ArrayList<STCRunner> threadList = new ArrayList<>();
        for (int i = 0; i < threadNumber; i++) {
            STCRunner runner = new STCRunner(clustersMap, queue, isOneSample);
            runner.start();
            threadList.add(runner);
        }
        return threadList;
    }

    /**
     * files infomation
     * header: class_name  sample_name  is_multi_samples  has_header  file_abspath
     */
    private List<FileInfo> getFilesInfoList(String path) {
        ArrayList<FileInfo> arr = new ArrayList<>();
        BaseFileReader fr = ReaderFactory.getFileReader(path, false);
        HashMap<String, String> map;
        while ((map = fr.nextLineMap()) != null) {
            String class_name = map.get("class_name");
            String sample_name = map.get("sample_name");
            boolean is_multi_samples = false;
            boolean has_header = false;
            try {
                is_multi_samples = CommTools.CheckTool.checkAndGetBoolean(map.get("is_multi_samples"));
                has_header = CommTools.CheckTool.checkAndGetBoolean(map.get("has_header"));
            } catch (Exception e) {
                e.printStackTrace();
            }
            String file_abspath = map.get("file_abspath");
            // System.out.println(class_name + "--" + sample_name + "--" + is_multi_samples + "--"
            //         + has_header + "--" + file_abspath);
            arr.add(new FileInfo(class_name, sample_name, is_multi_samples, has_header, file_abspath));
        }
        return arr;
    }

    /**
     * files infomation
     * header: class_name  sample_name  is_multi_samples  has_header  file_abspath
     */
    private static class FileInfo {
        private String class_name;
        private String sample_name;
        private boolean is_multi_samples;
        private boolean has_header;
        private String path;

        public FileInfo(String class_name, String sample_name, boolean is_multi_samples,
                        boolean has_header, String path) {
            this.class_name = class_name;
            this.sample_name = sample_name;
            this.is_multi_samples = is_multi_samples;
            this.has_header = has_header;
            this.path = path;
        }

        public String getClass_name() {
            return class_name;
        }

        public String getSample_name() {
            return sample_name;
        }

        public boolean isIs_multi_samples() {
            return is_multi_samples;
        }

        public boolean isHas_header() {
            return has_header;
        }

        public String getPath() {
            return path;
        }
    }
}

class STCRunner extends Thread {
    private ClustersMap clustersMap;
    private ArrayBlockingQueue<String> recoredDataqueue;
    private static Pattern pattern = Pattern.compile("\t");
    private boolean isOneSample;

    public STCRunner() {
    }

    public STCRunner(ClustersMap clustersMap, ArrayBlockingQueue recoredDataqueue,
                     boolean isOneSample) {
        this.clustersMap = clustersMap;
        this.recoredDataqueue = recoredDataqueue;
        this.isOneSample = isOneSample;
    }

    @Override
    public void run() {
        if (isOneSample) {
            oneSampleRun();
        } else {
            multiSamplesRun();
        }
    }

    public void multiSamplesRun() {
        while (true) {
            try {
                String s = recoredDataqueue.take();

                if (s.equals("<--null-->")) {
                    recoredDataqueue.put("<--null-->");
                    break;
                }

                String[] sArr = pattern.split(s, 3);

                if (sArr.length < 3) continue;

                int site = Integer.parseInt(sArr[0]);
                String chr = sArr[1].toLowerCase().replace("chr", "");
                Stream<String> stream = Stream.of(sArr[2]);
                double[] dArr = stream.mapToDouble(x -> CommTools.TransTool.str2double(x, 0))
                        .toArray();
                clustersMap.addCpgSiteToClusters(chr, site, dArr);

            } catch (InterruptedException e) {
                e.printStackTrace();
            }

        }
    }

    public void multiSamplesRun(String line) {

        String[] sArr = pattern.split(line, 3);

        int site = Integer.parseInt(sArr[0]);
        String chr = sArr[1].toLowerCase().replace("chr", "");
        Stream<String> stream = Stream.of(sArr[2]);
        double[] dArr = stream.mapToDouble(x -> CommTools.TransTool.str2double(x, 0))
                .toArray();
        clustersMap.addCpgSiteToClusters(chr, site, dArr);

    }

    public void oneSampleRun() {
        while (true) {
            try {
                String s = recoredDataqueue.take();

                if (s.equals("<--null-->")) {
                    recoredDataqueue.put("<--null-->");
                    break;
                }

                String[] sArr = pattern.split(s);
                if (sArr.length < 5) continue;

                String chr = sArr[0].toLowerCase().replace("chr", "");
                int site = Integer.parseInt(sArr[1]);
                int methyNum = Integer.parseInt(sArr[3]);
                int nonMethyNum = Integer.parseInt(sArr[4]);

                clustersMap.addCpgSiteToClusters(chr, site, methyNum, nonMethyNum);

            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public void oneSampleRun(String line) {
        try {
            String[] sArr = pattern.split(line);
            String chr = sArr[0].toLowerCase().replace("chr", "");
            int site = Integer.parseInt(sArr[1]);
            int methyNum = Integer.parseInt(sArr[3]);
            int nonMethyNum = Integer.parseInt(sArr[4]);
            clustersMap.addCpgSiteToClusters(chr, site, methyNum, nonMethyNum);
        } catch (IndexOutOfBoundsException e) {
            System.out.println(line);
            System.out.println(Arrays.toString(pattern.split(line)));
            e.printStackTrace();
            System.exit(0);
        }

    }


    public void setClustersMap(ClustersMap clustersMap) {
        this.clustersMap = clustersMap;
    }

    public void setRecoredDataqueue(ArrayBlockingQueue recoredDataqueue) {
        this.recoredDataqueue = recoredDataqueue;
    }
}
