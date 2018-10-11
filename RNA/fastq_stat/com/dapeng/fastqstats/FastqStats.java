package com.dapeng.fastqstats;

import com.dapeng.argparse.ArgumentParser;
import com.dapeng.utils.ReaderFactory;

import java.util.*;
import java.util.concurrent.ArrayBlockingQueue;

public class FastqStats {
    public static void main(String[] args) {
        long l = System.currentTimeMillis();
        FastqStats fastqStats = new FastqStats();
        fastqStats.start(args);
        System.out.println(System.currentTimeMillis() - l);

    }

    private void start(String ... args) {
        ArgumentParser parser = new ArgumentParser(args);

        // get the samples and its absolute paths
        List<String> fileList = parser.getFileList();

        // get the temp file info hashmap object
        HashMap<String, String[]> fqFileInfo = getFQFileInfo(parser);

        // collect the result data objects
        List<StatData> resList = new ArrayList<>();

        // analyze data
        Set<Map.Entry<String, String[]>> entrySet = fqFileInfo.entrySet();
        ArrayBlockingQueue<Record> queue = new ArrayBlockingQueue<Record>(500000);
        long l = System.currentTimeMillis();
        for (Map.Entry<String, String[]> entry : entrySet) {
            String sample = entry.getKey();
            String[] files = entry.getValue();

            // create shared data object
            ReaderFactory.FQSeqRecoredReader fqReader =
                    new ReaderFactory.FQSeqRecoredReader(files);
            StatData statData = new StatData(sample);

            if (parser.getThreadNumber() == 1) {
                // main thread start analysis
                new ThreadRunner(fqReader, statData, parser.getPhred33or64()).run();

            } else {
                Thread[] threads = new Thread[parser.getThreadNumber()];

                // start other threads to analysis
                for (int i = 0; i < parser.getThreadNumber(); i++) {
                    threads[i] = new ThreadRunner(queue, statData, parser.getPhred33or64());
                    threads[i].start();
                }

                try {
                    Record record;
                    while ((record = fqReader.nextRecord()) != null) {
                            queue.put(record);
                    }
                    queue.put(new Record(null, null, null));
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                // join all threads
                for (Thread thread : threads) {
                    try {
                        thread.join();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
            System.out.println(System.currentTimeMillis() - l + " " + Thread.currentThread().getName() + "  所有线程用时");

            resList.add(statData);

            queue.clear();
        }

        stdout(resList);
    }

    /**
     * print the result to screen
     * @param resList  List<StatData>
     */
    private void stdout(List<StatData> resList) {
        String title = resList.get(0).getDataTitleLine();
        System.out.println(title);
        for (StatData statData : resList) {
            System.out.println(statData.getDataLine());
        }
    }

    private static HashMap<String, String[]> getFQFileInfo(ArgumentParser parser) {
        HashMap<String, String[]> map = new HashMap<>();
        // get the samples and its absolute paths

        List<String> fileList = parser.getFileList();
        if (fileList.size() > 0) {
            map.put(parser.getSampleName(), fileList.toArray(new String[0]));
        } else if (parser.getFqListFile() != null) {
            ReaderFactory.BaseReader reader = new ReaderFactory.BaseReader(parser.getFqListFile());
            String[] lineItems;
            while ((lineItems = reader.nextLineItems()) != null) {
                map.put(lineItems[0], Arrays.copyOfRange(lineItems, 1, lineItems.length));
            }
        } else {
            System.err.println("args error, lack of -i or -f option");
            parser.printUsage();
        }
        return map;
    }
}
