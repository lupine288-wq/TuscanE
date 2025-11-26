package edu.illinois.cs.testrunner.execution;

import edu.illinois.cs.testrunner.agent.Helper;
import org.apache.maven.project.MavenProject;
import org.junit.runner.Description;
import org.junit.runner.notification.Failure;
import org.junit.runner.notification.RunListener;

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

public class TestListener extends RunListener {
    private final Map<String, Long> times;
    private final Map<String, Double> testRuntimes;
    private final Set<String> ignoredTests;

    private static Set<String> immutableList;
    public TestListener() {
        testRuntimes = new HashMap<>();
        times = new HashMap<>();
        ignoredTests = new HashSet<>();
    }

    public Set<String> ignored() {
        return ignoredTests;
    }

    public Map<String, Double> runtimes() {
        return testRuntimes;
    }

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


    private boolean isImmutable(Field field) {
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

    @Override
    public void testIgnored(Description description) throws Exception {
        ignoredTests.add(JUnitTestRunner.fullName(description));
    }

    @Override
    public void testStarted(Description description) throws Exception {
        String curDir = new File("").getAbsolutePath();
        writeTo(curDir + "/ASM-LOGS", "Test started: " + description.getClassName() + "." + description.getMethodName() + "\n");
        System.out.println("Test started: " + description.getClassName() + "." + description.getMethodName());
        times.put(JUnitTestRunner.fullName(description), System.nanoTime());
        
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

    @Override
    public void testFailure(Failure failure) throws Exception {
        failure.getException().printStackTrace();
    }

    @Override
    public void testAssumptionFailure(Failure failure) {
        failure.getException().printStackTrace();
    }

    @Override
    public void testFinished(Description description) throws Exception {
        System.out.println("Test finished: " + description.getClassName() + "." + description.getMethodName());
        final String fullTestName = JUnitTestRunner.fullName(description);

        if (times.containsKey(fullTestName)) {
            final long startTime = times.get(fullTestName);
            testRuntimes.put(fullTestName, (System.nanoTime() - startTime) / 1E9);
        } else {
            System.out.println("Test finished but did not start: " + fullTestName);
        }
        Helper helper = new Helper();
        /* List<String> fieldList = helper.getTmp();

        for (String fieldItem: fieldList) {
            try {
                // String
                String className = fieldItem.substring(0, fieldItem.lastIndexOf(".")).replace('/', '.');
                String fieldName = fieldItem.substring(fieldItem.lastIndexOf(".") + 1);
                System.out.println("CLASSNAME: " + className);
                Class clazz = Class.forName(className);

                Field field = clazz.getDeclaredField(fieldName);
                if (isImmutable(field)) {
                    helper.print(description.getClassName() + "." + description.getMethodName(), fieldItem);
                }
            } catch (ClassNotFoundException cnfe) {
                cnfe.printStackTrace();
                // continue;
            }
        } */
        helper.print(description.getClassName() + "." + description.getMethodName());
        helper.clear();
    }
}
