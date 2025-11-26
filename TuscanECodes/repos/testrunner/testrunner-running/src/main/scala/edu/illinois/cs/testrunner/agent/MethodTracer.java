package edu.illinois.cs.testrunner.agent;

import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.HashSet;
import java.util.Set;

import static org.objectweb.asm.Type.getInternalName;

public class MethodTracer extends MethodVisitor {
    private String methodName;
    private static Set<String> blackList;

    public MethodTracer(int api, MethodVisitor methodVisitor, String methodName) {
        super(api, methodVisitor);
        this.methodName = methodName;
    }

    private Set<String> getBlackList() {
        if (blackList == null) {
            blackList = new HashSet<>();

            blackList.add("java");
            blackList.add("sun");
            blackList.add("edu/illinois/cs/testrunner/agent");
            blackList.add("org/apache/maven");
            blackList.add("com/sun");
            blackList.add("jdk");
            blackList.add("org/junit");
        }
        return blackList;
    }

    @Override
    public void visitFieldInsn(int opcode, String owner, String name, String desc) {
        for (String blackListItem : getBlackList()) {
            if (owner.startsWith(blackListItem)) {
                mv.visitFieldInsn(opcode, owner, name, desc);
                return;
            }
        }
        switch (opcode) {
            case Opcodes.GETSTATIC:
                super.visitLdcInsn(owner.replace("/", ".") + "." + name);
                // super.visitLdcInsn(name);
                super.visitMethodInsn(Opcodes.INVOKESTATIC, getInternalName(Helper.class), "store", "(Ljava/lang/String;)V", false);
                mv.visitFieldInsn(opcode, owner, name, desc);
                break;
            case Opcodes.PUTSTATIC:
                mv.visitFieldInsn(opcode, owner, name, desc);
                super.visitLdcInsn(owner.replace("/", ".") + "." + name);
                // super.visitLdcInsn(name);
                super.visitMethodInsn(Opcodes.INVOKESTATIC, getInternalName(Helper.class), "store", "(Ljava/lang/String;)V", false);
                break;
            default:
                mv.visitFieldInsn(opcode, owner, name, desc);
                break;
        }
    }



}
