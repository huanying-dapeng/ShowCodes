package com.dapeng.argparse;

import com.dapeng.utils.CommTools;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ArgumentParser {
    private String fqListFile;
    private int threadNumber = 1;
    private int phred33or64 = 33;
    private String outdir;
    private String sampleName;
    private List<String> fileList = new ArrayList<>();
    private List<String> options = new ArrayList<>();

    public ArgumentParser(String... args) {
        List<String> strings = Arrays.asList(args);
        if (strings.size() == 0 || strings.contains("-h")
                || strings.contains("--help")) {
            printUsage();
            System.exit(0);
        }
        final String[] options = {"-f", "-i", "-o", "-t", "-p", "-s"};
        if (! (strings.stream().filter(x -> x.startsWith("-")).allMatch(x -> {
            boolean flag = false;
            for (String option : options) {
                if (x.equals(option)) {
                    flag = true;
                }
            }
            return flag;
        }))) {
            System.err.println("error args! check args options");
            System.err.println("your args: " + String.join(" ", args) + "\n");
            try {
                Thread.currentThread().sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            printUsage();
            System.exit(0);
        }
        parseArgs(args);
    }

    private void parseArgs(String[] args) {
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            if (arg.equals("-f")) {
                fqListFile = args[++i];
                checkFile(fqListFile);
            }
            else if (arg.equals("-i")) {
                fileList.add(args[++i]);
                while (true) {
                    arg = args[++i];
                    if (arg.startsWith("-")) {
                        i--;
                        break;
                    }
                    checkFile(arg);
                    fileList.add(arg);
                }
            }
            else if (arg.equals("-t")) {
                threadNumber = Integer.parseInt(args[++i]);
            }
            else if (arg.equals("-o")) {
                outdir = CommTools.CheckTools.checkAndCreateDir(args[++i]);
            }
            else if (arg.equals("-p")) {
                arg = args[++i];
                if (! (arg.equals("33") || arg.equals("64"))) {
                    System.err.println("phred33or64 must be provided with 33 or 64\n\n");
                }
                phred33or64 = Integer.parseInt(arg);
            }
            else if (arg.equals("-s")) {
                sampleName = args[++i];
            }
        }
        if (fqListFile == null && fileList == null) {
            System.out.println("args must contain -f or -i, and must be one of them.");
            System.exit(0);
        }
    }

    private void checkFile(String file) {
        if (! CommTools.CheckTools.checkFileIsExist(file)) {
            System.err.println(file + " is not exist or can not be read.\n\n");
            printUsage();
            System.exit(0);
        }
    }

    public void printUsage() {
        StringBuffer buffer = new StringBuffer();
        buffer.append("version information\n");
        buffer.append("@author  :     zhipeng.zhao\n");
        buffer.append("@contact :     zhipeng.zhao@majorbio.com\n");
        buffer.append("@version :     1.0\n\n");
        buffer.append("Description:   Statistics of fastq or gz fastq files, \n");
        buffer.append("               the statistical content: \n");
        buffer.append("                   total_reads,    total_bases,     Reads_with_Ns,\n");
        buffer.append("                   N_Reads_Rate,   A_Rate,T_Rate,   C_Rate,G_Rate,\n");
        buffer.append("                   N_Rate,         Error_Rate,      Q20_rate,\n");
        buffer.append("                   Q30_rate,       GC_Rate\n\n");
        buffer.append("Usage:         java -jar FastqStat.jar [-f | -i] [-o] [-t] [-p]\n\n");
        buffer.append("optional arguments:\n");
        buffer.append("    -h, --help       show this help message and exit\n");
        buffer.append("    -f fqListFile    tab-separated file, and its fields are listed below:\n");
        buffer.append("                     'SampleID<TAB>fq1_path<TAB>fq2_path<TAB>...'\n");
        buffer.append("                     Notice: the file don't contain header\n");
        buffer.append("    -i fqFileList    usage: -i fq1_path fq1_path ...\n");
        buffer.append("                     Notice: we can only choose one of -i and -f\n");
        buffer.append("    -s sampleName    if -i is not null, then -s must be provided\n");
        buffer.append("    -o outdir        output path, [default: current dir]\n");
        buffer.append("    -t threadNum     the number of thread\n");
        buffer.append("    -p Phred33or64   Phred qualitiy: 33 or 64, [default: 33]\n");
        System.out.println(buffer);
    }

    public String getFqListFile() {
        return fqListFile;
    }

    public int getThreadNumber() {
        return threadNumber;
    }

    public int getPhred33or64() {
        return phred33or64;
    }

    public String getOutdir() {
        return outdir;
    }

    public List<String> getFileList() {
        return fileList;
    }

    public List<String> getOptions() {
        return options;
    }

    public String getSampleName() {
        return sampleName;
    }
}
