package edu.illinois.cs.testrunner.execution;

import edu.illinois.cs.testrunner.agent.Helper;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;
import org.testng.internal.IResultListener2;
import org.testng.reporters.TextReporter;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

public class TestNListener implements IResultListener2 {

    public TestNListener() {
    }

    @Override
    public void onTestStart(ITestResult result) {
        String curDir = new File("").getAbsolutePath();
        writeTo(curDir + "/ASM-LOGS", "Test started: " + result.getTestClass().getName() + "." + result.getMethod().getMethodName() + "\n");


    }

    @Override
    public void onTestSuccess(ITestResult result) {
        String curDir = new File("").getAbsolutePath();
        writeTo(curDir + "/ASM-LOGS", "Test succeed: " + result.getTestClass().getName() + "." + result.getMethod().getMethodName() + "\n");
        Helper helper = new Helper();
        helper.print(result.getTestClass().getName() + "." + result.getMethod().getMethodName());
        helper.clear();
    }

    @Override
    public void onTestFailure(ITestResult result) {
        String curDir = new File("").getAbsolutePath();
        writeTo(curDir + "/ASM-LOGS", "Test failed: " + result.getTestClass().getName() + "." + result.getMethod().getMethodName() + "\n");
        Helper helper = new Helper();
        helper.print(result.getTestClass().getName() + "." + result.getMethod().getMethodName());
        helper.clear();
    }

    @Override
    public void onTestSkipped(ITestResult result) {
        String curDir = new File("").getAbsolutePath();
        writeTo(curDir + "/ASM-LOGS", "Test skipped: " + result.getTestClass().getName() + "." + result.getMethod().getMethodName() + "\n");
        Helper helper = new Helper();
        helper.print(result.getTestClass().getName() + "." + result.getMethod().getMethodName());
        helper.clear();
    }

    @Override
    public void onTestFailedButWithinSuccessPercentage(ITestResult iTestResult) {

    }

    @Override
    public void onStart(ITestContext iTestContext) {

    }

    @Override
    public void onFinish(ITestContext iTestContext) {

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
    public void beforeConfiguration(ITestResult iTestResult) {

    }

    @Override
    public void onConfigurationSuccess(ITestResult iTestResult) {

    }

    @Override
    public void onConfigurationFailure(ITestResult iTestResult) {

    }

    @Override
    public void onConfigurationSkip(ITestResult iTestResult) {

    }
}
