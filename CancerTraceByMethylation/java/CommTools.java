package com.dapeng.utils;

import com.dapeng.exceptions.DirectoryNotExists;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Arrays;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class CommTools {
    private CommTools() {}

    public static class CheckTool {
        public static boolean isExecFile(String filePath)
                throws FileNotFoundException {

            if (isFile(filePath) && new File(filePath).canExecute()) {
                return true;
            }

            return false;
        }

        public static boolean isFile(String filePath)
                throws FileNotFoundException {

            if (filePath == null) {
                throw new FileNotFoundException("the path is null");
            }

            File file = new File(filePath);
            if (! file.isFile() && ! file.canRead()) {
                throw new FileNotFoundException(filePath + " is not exist");
            }

            return false;
        }

        public static boolean checkAndCreateDirectory(String dir, boolean isExists)
                throws DirectoryNotExists, Exception {

            File file = new File(dir);
            if (isExists && ! file.isDirectory()) {
                throw new DirectoryNotExists(
                        "the param isExists is true, but \"" + dir +  "\" is not exits, " +
                                "so you check the directory or the params");
            } else if (! file.isFile() && ! file.isDirectory()) {
                return file.mkdirs();
            } else if (file.isDirectory()) {
                return true;
            } else {
                String s = file.getName() + " already exist";
                throw new Exception(s);
            }
        }

        public static boolean checkAndGetBoolean(String bool) throws Exception {
            int len;
            if (((len = bool.length()) != 4) && len != 5 ) {
                return false;
            } else {
                if (bool.equals("true") || bool.contains("true")) {
                    return true;
                }
                else if (bool.equals("false") || bool.contains("flase")) {
                    return false;
                }
                else {
                    throw new Exception("the param is \"" + bool + "\", you should check it.");
                }
            }
        }
    }

    public static class TransTool {
        public static int str2int(String str, int def) {
            try {
                return Integer.parseInt(str);
            } catch (NumberFormatException e) {
                return def;
            }
        }

        public static double str2double(String str, int def) {
            try {
                return Double.parseDouble(str);
            } catch (NumberFormatException e) {
                return def;
            }
        }

        public static Number str2T(String str, Number def, Function<String, Number> mapper) {
            try {
                return mapper.apply(str);
            } catch (Exception e) {
                return def;
            }
        }
    }

    public static class JoinTools {
        public static String stringsJOin(String delimiter, String ... strings) {
            return Stream.of(strings).collect(Collectors.joining(delimiter));
        }

        public static String intJoin(String delimiter, int ... values) {
            return Arrays.stream(values)
                    .mapToObj(x -> String.valueOf(x))
                    .collect(Collectors.joining(delimiter));
        }

        public static String doubleJoin(String delimiter, int decimalNumber, double ... values) {
            StringBuffer buf = new StringBuffer();

            int flag = 0;
            for (double value : values) {
                if (flag != 0) {
                    buf.append(delimiter);
                }
                buf.append(String.valueOf(value));
                flag++;
            }
            return buf.toString();
        }
    }

}
