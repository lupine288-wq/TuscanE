package edu.illinois.cs.testrunner.agent;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;

import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.Instrumentation;
import java.lang.invoke.MethodHandle;
import java.security.ProtectionDomain;

public class MainAgent {
    private static Instrumentation inst;

    public static Instrumentation getInstrumentation() { return inst; }

    public static void premain(String agentArgs, Instrumentation inst) {
        MainAgent.inst = inst;

        inst.addTransformer(new ClassFileTransformer() {
            @Override
            public byte[] transform(ClassLoader l, String name, Class c,
                                    ProtectionDomain d, byte[] b) {
                ClassReader cr = new ClassReader(b);
                ClassWriter cw = new ClassWriter(cr, 0);
                ClassTracer cv = new ClassTracer(cw);
                cr.accept(cv, 0);
                return cw.toByteArray();
            }
        }, true);
    }
}
