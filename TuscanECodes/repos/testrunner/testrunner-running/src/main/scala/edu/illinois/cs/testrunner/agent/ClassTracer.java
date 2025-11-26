package edu.illinois.cs.testrunner.agent;

import org.objectweb.asm.*;

public class ClassTracer extends ClassVisitor {
    private String cn;

    public ClassTracer(ClassVisitor cv) {
        super(Opcodes.ASM9, cv);
    }

    @Override
    public void visit(int version, int access, String name, String signature, String superName, String[] interfaces) {
        this.cn = name;
        super.visit(version, access, name, signature, superName, interfaces);
    }

    @Override
    public MethodVisitor visitMethod(int access, String name, String desc, String signature, String[] exceptions) {
        final String methodId = this.cn + "." + name;
        return new MethodTracer(Opcodes.ASM9, super.visitMethod(access, name, desc, signature, exceptions), methodId);
    }
}