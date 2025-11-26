package edu.illinois.cs.testrunner.agent;

import org.apache.maven.project.MavenProject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class Helper {
    private final static Map<String, String> tmp = new ConcurrentHashMap<>();;

    private static Set<String> immutableList;

    private void getImmutableList() {
        if (immutableList == null) {
            immutableList = new HashSet<>();

            immutableList.add("java.lang.String");
            immutableList.add("java.lang.Enum");
            immutableList.add("java.lang.StackTraceElement");
            immutableList.add("java.math.BigInteger");
            immutableList.add("java.math.BigDecimal");
            immutableList.add("java.io.File");
            immutableList.add("java.awt.Font");
            immutableList.add("java.awt.BasicStroke");
            immutableList.add("java.awt.Color");
            immutableList.add("java.awt.GradientPaint");
            immutableList.add("java.awt.LinearGradientPaint");
            immutableList.add("java.awt.RadialGradientPaint");
            immutableList.add("java.awt.Cursor");
            immutableList.add("java.util.Locale");
            immutableList.add("java.util.UUID");
            immutableList.add("java.util.Collections");
            immutableList.add("java.net.URL");
            immutableList.add("java.net.URI");
            immutableList.add("java.net.Inet4Address");
            immutableList.add("java.net.Inet6Address");
            immutableList.add("java.net.InetSocketAddress");
            immutableList.add("java.awt.BasicStroke");
            immutableList.add("java.awt.Color");
            immutableList.add("java.awt.GradientPaint");
            immutableList.add("java.awt.LinearGradientPaint");
            immutableList.add("java.awt.RadialGradientPaint");
            immutableList.add("java.awt.Cursor");
            immutableList.add("java.util.regex.Pattern");
        }
    }


    private static boolean isImmutable(Field field) {
        boolean isFinal = false;
        if (Modifier.isFinal(field.getModifiers())) {
            isFinal = true;
        }

        if ((field.getType().isPrimitive() || field.getDeclaringClass().isEnum()) && isFinal) {
            return true;
        }

        for (String immutableTypeName : immutableList) {
            if ((field.getType().getName().equals(immutableTypeName)) && isFinal) {
                return true;
            }
        }
        return false;
    }


    public static void store(String str) {
        // try {
            String fieldItem = str;
            String className = str; // fieldItem.substring(0, fieldItem.lastIndexOf(".")).replace('/', '.');
            // String fieldName = fieldItem.substring(fieldItem.lastIndexOf(".") + 1);
            // System.out.println("CLASSNAME: " + className);
            // Class clazz = Class.forName(className);

            // Field field = clazz.getDeclaredField(fieldName);
            // if (!isImmutable(field)) {
                tmp.put(str, str);
            // }
        // } catch (ClassNotFoundException cnfe) { // | NoSuchFieldException
            // cnfe.printStackTrace();
            // continue;
        // }
    }

    public static void dummy() {
        tmp.put("dummy", "dummy");
    }

    public void writeTo(final String outputPath, String output) {
        if (!Files.exists(Paths.get(outputPath))) {
            try {
                Files.createFile(Paths.get(outputPath));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        try {
            Files.write(Paths.get(outputPath), output.getBytes(StandardCharsets.UTF_8),
                    StandardOpenOption.APPEND);
        } catch (IOException e) {
            e.printStackTrace(System.err);
        }
    }

    public void print(String testName) {
        String curDir = new File("").getAbsolutePath();
        for (String fieldItem : tmp.keySet()) {
            writeTo(curDir + "/ASM-LOGS", "PAIR: " + testName + "," + fieldItem + "\n");
            System.out.println("PAIR: " + testName + "," + fieldItem);
        }
    }

    public List<String> getTmp() {
        List<String> fieldList  = new LinkedList<>();
        for (String item : tmp.keySet()) {
            fieldList.add(item);
        }
        return fieldList;
    }

    public void clear() {
        tmp.clear();
    }


}
