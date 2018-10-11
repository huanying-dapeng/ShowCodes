package com.dapeng.utils;

import java.io.File;

public class CommTools {
    public static class CheckTools {
        public static boolean checkFileIsExist(String file) {
            File f = new File(file);
            if (f.isFile() && f.canRead()) {
                return true;
            }
            return false;
        }

        public static String checkAndCreateDir(String dir) {
            File file = new File(dir);
            if (! file.isDirectory()) {
                file.mkdirs();
            }
            return dir;
        }
    }
}
