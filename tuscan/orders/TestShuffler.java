package tuscan.orders;

import java.util.*;


public class TestShuffler {
    public static String className(final String testName) {
        return testName.substring(0, testName.lastIndexOf('.'));
    }

    private final HashMap<String, List<String>> classToMethods;
    // For tuscanInterClass (existing implementation)
    private static int interClassRound = 0; // which class permutation to choose
    private static int interCurrentMethodRound = 0; // first class of pair
    private static int interNextMethodRound = 0; // second class of pair
    private static int i1 = 0; // current class
    private static int i2 = 1; // next class
    private static boolean isNewOrdering = false; // To change the permutation of classes

    public TestShuffler(final List<String> tests) {
        classToMethods = new HashMap<>();

        for (final String test : tests) {
            final String className = className(test);

            if (!classToMethods.containsKey(className)) {
                classToMethods.put(className, new ArrayList<>());
            }

            classToMethods.get(className).add(test);
        }
    }

    public List<String> OriginalAndTuscanOrder(int count, boolean isTuscan) {
        List<String> classes = new ArrayList<>(classToMethods.keySet());
        Collections.sort(classes);
        final List<String> fullTestOrder = new ArrayList<>();
        if (isTuscan) {
            int n = classes.size();
            int[][] res = Tuscan.generateTuscanPermutations(n);
            List<String> permClasses = new ArrayList<String>();
            for (int i = 0; i < res[count].length - 1; i++) {
                permClasses.add(classes.get(res[count][i]));
            }
            for (String className : permClasses) {
                fullTestOrder.addAll(classToMethods.get(className));
            }
        } else {
            for (String className : classes) {
                fullTestOrder.addAll(classToMethods.get(className));
            }
        }
        return fullTestOrder;
    }

    public List<String> tuscanIntraClassOrder(int round) {
        List<String> classes = new ArrayList<>(classToMethods.keySet());
        HashMap<String, int[][]> classToPermutations = new HashMap<String, int[][]>();
        Collections.sort(classes);
        final List<String> fullTestOrder = new ArrayList<>();
        int n = classes.size(); // n is number of classes
        int[][] classOrdering = Tuscan.generateTuscanPermutations(n);
        for (String className : classes) {
            int[][] methodPermuation = Tuscan.generateTuscanPermutations(classToMethods.get(className).size());
            classToPermutations.put(className, methodPermuation);
        }
        HashMap<String, List<String>> newClassToMethods = new HashMap<String, List<String>>();
        List<String> permClasses = new ArrayList<String>();
        int classRound = round;
        classRound = classRound % classOrdering.length;
        for (int i = 0; i < classOrdering[classRound].length - 1; i++) {
            permClasses.add(classes.get(classOrdering[classRound][i]));
        }
        for (String className : permClasses) {
            List<String> methods = classToMethods.get(className);
            List<String> permMethods = new ArrayList<String>();
            int[][] currMethodOrdering = classToPermutations.get(className);
            n = methods.size();
            int methodRound = round;
            methodRound = methodRound % currMethodOrdering.length;
            for (int i = 0; i < currMethodOrdering[methodRound].length - 1; i++) {
                permMethods.add(methods.get(currMethodOrdering[methodRound][i]));
            }
            newClassToMethods.put(className, permMethods);
        }
        for (String className : permClasses) {
            fullTestOrder.addAll(newClassToMethods.get(className));
        }
        return fullTestOrder;
    }

    public List<String> tuscanInterClass(int round) {
        List<String> classes = new ArrayList<>(classToMethods.keySet());
        HashMap<String, int[][]> classToPermutations = new HashMap<String, int[][]>();
        Collections.sort(classes);
        final List<String> fullTestOrder = new ArrayList<>();
        int n = classes.size(); // n is number of classes
        // If we have only one class, return the original order as a single round
        if (n == 1) {
            return OriginalAndTuscanOrder(round, false);
        }
        int[][] classOrdering = Tuscan.generateTuscanPermutations(n);

        for (String className : classes) {
            int methodSize = classToMethods.get(className).size();
            int[][] result;
            if (methodSize == 3) {

                int[][] methodPermuation = {
                        { 1, 0, 2, 0},
                        { 2, 1, 0, 0},
                        { 2, 0, 1, 0}
                };
                result = methodPermuation;

            } else if (methodSize == 5) {

                int[][] methodPermuation = {
                        {0,4,1,3,2, 0},
                        {1,0,2,4,3, 0},
                        {2,0,3,1,4, 0},
                        {3,4,0,2,1, 0},
                        {4,2,1,3,0, 0}
                };
                result = methodPermuation;

            } else {

                int[][] methodPermuation = Tuscan.generateTuscanPermutations(methodSize);
                result = methodPermuation;

            }
            classToPermutations.put(className, result);
        }
        HashMap<String, List<String>> newClassToMethods = new HashMap<String, List<String>>(); // class to permutated methods
        List<String> permClasses = new ArrayList<String>();
        if (isNewOrdering) {
            // When we reach end of a permutation for classes only
            i1 = 0;
            i2 = 1;
            interNextMethodRound = 0;
            interCurrentMethodRound = 0;
            interClassRound++;
            isNewOrdering = false;
        }
        for (int i = 0; i < classOrdering[interClassRound].length - 1; i++) {
            permClasses.add(classes.get(classOrdering[interClassRound][i]));
        }
        String currentClass = permClasses.get(i1), nextClass = permClasses.get(i2);
        int currentClassMethodSize = classToMethods.get(currentClass).size();
        int nextClassMethodSize = classToMethods.get(nextClass).size();
        if (currentClassMethodSize == interCurrentMethodRound && nextClassMethodSize == (interNextMethodRound + 1)) {
            // To change the pair so we change i1 & i2
            i1++;
            i2++;
            interNextMethodRound = 0;
            interCurrentMethodRound = 0;
        }
        else if (currentClassMethodSize == (interCurrentMethodRound)) {
            // To change the *next* class methods
            interNextMethodRound++;
            interCurrentMethodRound = 0;
        }
        int[] currentClassTuscan = classToPermutations.get(currentClass)[interCurrentMethodRound];
        int[] nextClassTuscan = classToPermutations.get(nextClass)[interNextMethodRound];
        for (String className : permClasses) {
            List<String> methods = classToMethods.get(className);
            List<String> permMethods = new ArrayList<String>();
            if (className == currentClass) {
                for (int i = 0; i < currentClassTuscan.length - 1; i++) {
                    permMethods.add(methods.get(currentClassTuscan[i]));
                }
            }
            else if (className == nextClass) {
                for (int i = 0; i < nextClassTuscan.length - 1; i++) {
                    permMethods.add(methods.get(nextClassTuscan[i]));
                }
            } else {
                // For other classes, leave the order unchanged.
                permMethods.addAll(methods);
            }
            newClassToMethods.put(className, permMethods);
        }
        for (String className : permClasses) {
            fullTestOrder.addAll(newClassToMethods.get(className));
        }
        interCurrentMethodRound++;
        if (nextClass == permClasses.get(permClasses.size() - 1) &&
                currentClassMethodSize == interCurrentMethodRound &&
                nextClassMethodSize == (interNextMethodRound + 1)) {
            // if the *next class* is our last class then there is no pair so change to the next order
            isNewOrdering = true;
        }
        return fullTestOrder;
    }





    public java.util.Map.Entry<List<List<String>>, List<String[]>> tuscanInterClassNewOrders() {
        // Sort classes by descending number of methods (unchanged)
        List<String> sortedClasses = new ArrayList<>(classToMethods.keySet());
        Collections.sort(sortedClasses, (a, b) -> classToMethods.get(b).size() - classToMethods.get(a).size());

        // Build permutation matrices for each class
        HashMap<String, int[][]> classToPermutationsNew = new HashMap<>();
        for (String className : sortedClasses) {
            int methodSize = classToMethods.get(className).size();
            int[][] result;
            if (methodSize == 3) {
                // KEEP method rows pattern:
                // A B C
                // B A C
                // C A
                // C B
                result = new int[][]{
                        {0, 1, 2, 0}, // A B C
                        {1, 0, 2, 0}, // B A C
                        {2, 0, 0},    // C A
                        {2, 1, 1}     // C B
                };
            } else if (methodSize == 5) {
                // MINIMAL CHANGE: hard-code rows to match
                // AEBDC
                // BACED
                // CADBE
                // EABCD
                // DECB
                // DA
                // (add a trailing duplicate element so we still "drop the last" with length-1 logic)
                result = new int[][]{
                        {0, 4, 1, 3, 2, 0}, // AEBDC
                        {1, 0, 2, 4, 3, 1}, // BACED
                        {2, 0, 3, 1, 4, 2}, // CADBE
                        {4, 0, 1, 2, 3, 4}, // EABCD
                        {3, 4, 2, 1, 3},    // DECB
                        {3, 0, 3}           // DA
                };
            } else {
                result = Tuscan.generateTuscanPermutations(methodSize);
            }
            classToPermutationsNew.put(className, result);
        }

        // Determine number of orders from the first (largest) class (unchanged)
        String firstClass = sortedClasses.get(0);
        int[][] firstMatrix = classToPermutationsNew.get(firstClass);
        int totalOrders = firstMatrix.length;

        // Tuscan square over CLASSES (default)
        int n = sortedClasses.size();
        int[][] classTuscan = Tuscan.generateTuscanPermutations(n);
        int classRows = classTuscan.length;

        List<List<String>> newOrders = new ArrayList<>();
        List<String[]> interClassPairs = new ArrayList<>();

        // Generate each new order (row)
        for (int orderIndex = 0; orderIndex < totalOrders; orderIndex++) {
            List<String> order = new ArrayList<>();

            // For CLASS rows when n==3, use:
            // A B C
            // B A C
            // C A B
            // C B A
            int[] classRow;
            int usableLen;
            if (n == 3) {
                int[][] customClassRows = new int[][]{
                        {0, 1, 2}, // A B C
                        {1, 0, 2}, // B A C
                        {2, 0, 1}, // C A B
                        {2, 1, 0}  // C B A
                };
                classRow = customClassRows[orderIndex % customClassRows.length];
                usableLen = classRow.length;
            } else {
                classRow = classTuscan[orderIndex % classRows];
                usableLen = Math.max(0, classRow.length - 1); // drop duplicated last cell
            }

            // Process each class in the chosen order
            for (int k = 0; k < usableLen; k++) {
                int classIdx = classRow[k];
                if (classIdx < 0 || classIdx >= n) continue;

                String className = sortedClasses.get(classIdx);
                List<String> methods = classToMethods.get(className);
                if (methods == null || methods.isEmpty()) continue;

                int[][] matrix = classToPermutationsNew.get(className);
                int rows = matrix.length;

                // do NOT wrap: if this class exhausted its method rows, skip it
                if (orderIndex >= rows) continue;
                int rowToUse = orderIndex;

                int[] permutation = matrix[rowToUse];
                // Take only the first (permutation.length - 1) entries (drop trailing duplicate)
                for (int m = 0; m < permutation.length - 1; m++) {
                    order.add(methods.get(permutation[m]));
                }
            }

            // collect INTER-CLASS adjacent pairs from this order
            for (int i = 0; i + 1 < order.size(); i++) {
                String left = order.get(i);
                String right = order.get(i + 1);
                String leftCls  = left.substring(0, left.lastIndexOf('.'));
                String rightCls = right.substring(0, right.lastIndexOf('.'));
                if (!leftCls.equals(rightCls)) {
                    interClassPairs.add(new String[]{left, right});
                }
            }

            newOrders.add(order);
        }

        return new java.util.AbstractMap.SimpleEntry<>(newOrders, interClassPairs);
    }

    public List<List<String>> tuscanInterClassLexOrders(java.util.Set<String> alreadyCovered) {
        List<List<String>> allOrders = new ArrayList<>();

        // Get sorted list of classes.
        List<String> sortedClasses = new ArrayList<>(classToMethods.keySet());
        Collections.sort(sortedClasses);
        int n = sortedClasses.size();
        if (n == 0) return allOrders;
        if (n == 1) {
            List<String> singleOrder = new ArrayList<>();
            List<String> methods = classToMethods.get(sortedClasses.get(0));
            String m1 = methods.get(0);
            String m2 = methods.size() > 1 ? methods.get(1) : m1;
            if (m1.equals(m2)) { singleOrder.add(m1); } else { singleOrder.add(m1); singleOrder.add(m2); }

            // Trim ends if same class (unchanged)
            if (singleOrder.size() >= 2 && singleOrder.get(0).split("\\.")[0].equals(singleOrder.get(1).split("\\.")[0])) {
                singleOrder.remove(0);
            }
            int sz1 = singleOrder.size();
            if (sz1 >= 2 && singleOrder.get(sz1 - 2).split("\\.")[0].equals(singleOrder.get(sz1 - 1).split("\\.")[0])) {
                singleOrder.remove(sz1 - 1);
            }
            // Ensure at least one inter-class adjacency
            if (singleOrder.size() >= 2) allOrders.add(singleOrder);
            return allOrders;
        }

        // Build class rows with custom sequences for n=3 and n=5; otherwise use Tuscan with last cell dropped
        int[][] classOrdering = Tuscan.generateTuscanPermutations(n);
        List<int[]> classRows = new ArrayList<>();
        if (n == 3) {
            // A B C ; B A C ; C A ; C B
            classRows.add(new int[]{0, 1, 2});
            classRows.add(new int[]{1, 0, 2});
            classRows.add(new int[]{2, 0});
            classRows.add(new int[]{2, 1});
        } else if (n == 5) {
            // AEBDC ; BACED ; CADBE ; EABCD ; DECB ; DA
            classRows.add(new int[]{0, 4, 1, 3, 2}); // A E B D C
            classRows.add(new int[]{1, 0, 2, 4, 3}); // B A C E D
            classRows.add(new int[]{2, 0, 3, 1, 4}); // C A D B E
            classRows.add(new int[]{4, 0, 1, 2, 3}); // E A B C D
            classRows.add(new int[]{3, 4, 2, 1});    // D E C B
            classRows.add(new int[]{3, 0});          // D A
        } else {
            // Default: use Tuscan rows, dropping duplicated last cell
            for (int r = 0; r < classOrdering.length; r++) {
                int[] row = classOrdering[r];
                if (row.length > 0) {
                    classRows.add(java.util.Arrays.copyOf(row, row.length - 1));
                } else {
                    classRows.add(row);
                }
            }
        }

        for (int r = 0; r < classRows.size(); r++) {
            // Per-class-row accumulator that RESETS for each row
            java.util.Set<String> rowCovered = new java.util.HashSet<>();

            int[] classRow = classRows.get(r);
            List<String> orderedClasses = new ArrayList<>(classRow.length);
            for (int idx : classRow) {
                if (idx >= 0 && idx < n) orderedClasses.add(sortedClasses.get(idx));
            }

            List<List<int[]>> lexList = new ArrayList<>();
            List<Integer> universeSizes = new ArrayList<>();
            for (int i = 0; i < orderedClasses.size() - 1; i++) {
                String leftClass = orderedClasses.get(i);
                String rightClass = orderedClasses.get(i + 1);
                int leftCount = classToMethods.get(leftClass).size();
                int rightCount = classToMethods.get(rightClass).size();
                List<int[]> pairList = new ArrayList<>();
                for (int x = 1; x <= leftCount; x++) {
                    for (int y = 1; y <= rightCount; y++) {
                        pairList.add(new int[]{x, y});
                    }
                }
                lexList.add(pairList);
                universeSizes.add(pairList.size());
            }

            int T = 0;
            for (int size : universeSizes) if (size > T) T = size;

            for (int k = 0; k < T; k++) {
                List<String> order = new ArrayList<>();

                // First class
                String firstClass = orderedClasses.get(0);
                List<String> methodsFirst = classToMethods.get(firstClass);
                int fixedF = 1;
                int[] pairFirst = lexList.get(0).get(k % lexList.get(0).size());
                int g_first = pairFirst[0];
                String m1 = methodsFirst.get(fixedF - 1);
                String m2 = methodsFirst.get(g_first - 1);
                if (m1.equals(m2)) { order.add(m1); } else { order.add(m1); order.add(m2); }

                // Middle classes
                for (int i = 1; i < orderedClasses.size() - 1; i++) {
                    String currentClass = orderedClasses.get(i);
                    List<String> methodsCurrent = classToMethods.get(currentClass);
                    int[] prevPair = lexList.get(i - 1).get(k % lexList.get(i - 1).size());
                    int f_current = prevPair[1];
                    int[] currPair = lexList.get(i).get(k % lexList.get(i).size());
                    int g_current = currPair[0];
                    String m3 = methodsCurrent.get(f_current - 1);
                    String m4 = methodsCurrent.get(g_current - 1);
                    if (m3.equals(m4)) { order.add(m3); } else { order.add(m3); order.add(m4); }
                }

                // Last class
                String lastClass = orderedClasses.get(orderedClasses.size() - 1);
                List<String> methodsLast = classToMethods.get(lastClass);
                int[] lastPair = lexList.get(lexList.size() - 1).get(k % lexList.get(lexList.size() - 1).size());
                int f_last = lastPair[1];
                int fixedG2 = 1;
                String m5 = methodsLast.get(f_last - 1);
                String m6 = methodsLast.get(fixedG2 - 1);
                if (m5.equals(m6)) { order.add(m5); } else { order.add(m5); order.add(m6); }

                // Trim ends if same class
                if (order.size() >= 2 && order.get(0).split("\\.")[0].equals(order.get(1).split("\\.")[0])) {
                    order.remove(0);
                }
                int sz = order.size();
                if (sz >= 2 && order.get(sz - 2).split("\\.")[0].equals(order.get(sz - 1).split("\\.")[0])) {
                    order.remove(sz - 1);
                }

                // === unified one-pass removal based on "both hands free" ===
                if (!order.isEmpty()) {
                    int m = order.size();
                    boolean[] remove = new boolean[m];

                    java.util.function.Function<String,String> cls = s -> s.substring(0, s.lastIndexOf('.'));
                    java.util.function.BiFunction<String,String,Boolean> inter = (a,b) -> !cls.apply(a).equals(cls.apply(b));
                    java.util.function.BiFunction<String,String,Boolean> covered =
                            (a,b) -> {
                                String key = a + "||" + b;
                                return (alreadyCovered != null && alreadyCovered.contains(key)) || rowCovered.contains(key);
                            };

                    for (int i = 0; i < m; i++) {
                        // LEFT hand
                        boolean leftFree = true; // ends are open -> free
                        if (i - 1 >= 0) {
                            String L = order.get(i - 1), X = order.get(i);
                            if (inter.apply(L, X)) {
                                leftFree = covered.apply(L, X); // inter-class but covered => free; otherwise tied
                            } else {
                                leftFree = true; // intra-class => free
                            }
                        }

                        if (!leftFree) {
                            // already tied on the left; no need to check right
                            continue;
                        }

                        // RIGHT hand
                        boolean rightFree = true; // ends are open -> free
                        if (i + 1 < m) {
                            String X = order.get(i), R = order.get(i + 1);
                            if (inter.apply(X, R)) {
                                rightFree = covered.apply(X, R); // inter-class but covered => free; otherwise tied
                            } else {
                                rightFree = true; // intra-class => free
                            }
                        }

                        if (leftFree && rightFree) {
                            remove[i] = true; // both hands free -> removable
                        }
                    }

                    // NOTE: fix for boolean[] stream — use a simple loop instead
                    boolean hasAny = false;
                    for (boolean b : remove) { if (b) { hasAny = true; break; } }
                    if (hasAny) {
                        List<String> kept = new ArrayList<>(m);
                        for (int i = 0; i < m; i++) {
                            if (!remove[i]) kept.add(order.get(i));
                        }
                        order = kept;
                    }
                }
                // === END unified one-pass removal ===

                // final guard — require at least one inter-class adjacency
                if (order.size() < 2) {
                    continue; // drop singleton/empty orders
                } else {
                    boolean hasInter = false;
                    for (int i = 0; i + 1 < order.size(); i++) {
                        String a = order.get(i), b = order.get(i + 1);
                        String ca = a.substring(0, a.lastIndexOf('.'));
                        String cb = b.substring(0, b.lastIndexOf('.'));
                        if (!ca.equals(cb)) { hasInter = true; break; }
                    }
                    if (!hasInter) continue;
                }

                // After finalizing this order, add its inter-class pairs to rowCovered
                for (int i = 0; i + 1 < order.size(); i++) {
                    String a = order.get(i), b = order.get(i + 1);
                    String ca = a.substring(0, a.lastIndexOf('.'));
                    String cb = b.substring(0, b.lastIndexOf('.'));
                    if (!ca.equals(cb)) {
                        rowCovered.add(a + "||" + b);
                    }
                }

                // collapse consecutive duplicates AT THE VERY END
                if (!order.isEmpty()) {
                    List<String> merged = new ArrayList<>();
                    for (String t : order) {
                        if (merged.isEmpty() || !merged.get(merged.size() - 1).equals(t)) {
                            merged.add(t);
                        }
                    }
                    order = merged;
                }

                allOrders.add(order);
            }
        }
        return allOrders;
    }



    public List<List<String>> tuscanInterClassLexOrdersworks(java.util.Set<String> alreadyCovered) {
        List<List<String>> allOrders = new ArrayList<>();

        // Get sorted list of classes.
        List<String> sortedClasses = new ArrayList<>(classToMethods.keySet());
        Collections.sort(sortedClasses);
        int n = sortedClasses.size();
        if (n == 0) return allOrders;
        if (n == 1) {
            List<String> singleOrder = new ArrayList<>();
            List<String> methods = classToMethods.get(sortedClasses.get(0));
            String m1 = methods.get(0);
            String m2 = methods.size() > 1 ? methods.get(1) : m1;
            if (m1.equals(m2)) { singleOrder.add(m1); } else { singleOrder.add(m1); singleOrder.add(m2); }

            // Trim ends if same class (unchanged)
            if (singleOrder.size() >= 2 && singleOrder.get(0).split("\\.")[0].equals(singleOrder.get(1).split("\\.")[0])) {
                singleOrder.remove(0);
            }
            int sz1 = singleOrder.size();
            if (sz1 >= 2 && singleOrder.get(sz1 - 2).split("\\.")[0].equals(singleOrder.get(sz1 - 1).split("\\.")[0])) {
                singleOrder.remove(sz1 - 1);
            }
            allOrders.add(singleOrder);
            return allOrders;
        }

        // Build class rows with custom sequences for n=3 and n=5; otherwise use Tuscan with last cell dropped
        int[][] classOrdering = Tuscan.generateTuscanPermutations(n);
        List<int[]> classRows = new ArrayList<>();
        if (n == 3) {
            // A B C ; B A C ; C A ; C B
            classRows.add(new int[]{0, 1, 2});
            classRows.add(new int[]{1, 0, 2});
            classRows.add(new int[]{2, 0});
            classRows.add(new int[]{2, 1});
        } else if (n == 5) {
            // AEBDC ; BACED ; CADBE ; EABCD ; DECB ; DA
            classRows.add(new int[]{0, 4, 1, 3, 2}); // A E B D C
            classRows.add(new int[]{1, 0, 2, 4, 3}); // B A C E D
            classRows.add(new int[]{2, 0, 3, 1, 4}); // C A D B E
            classRows.add(new int[]{4, 0, 1, 2, 3}); // E A B C D
            classRows.add(new int[]{3, 4, 2, 1});    // D E C B
            classRows.add(new int[]{3, 0});          // D A
        } else {
            // Default: use Tuscan rows, dropping duplicated last cell
            for (int r = 0; r < classOrdering.length; r++) {
                int[] row = classOrdering[r];
                if (row.length > 0) {
                    classRows.add(java.util.Arrays.copyOf(row, row.length - 1));
                } else {
                    classRows.add(row);
                }
            }
        }

        for (int r = 0; r < classRows.size(); r++) {
            // Per-class-row accumulator that RESETS for each row
            java.util.Set<String> rowCovered = new java.util.HashSet<>();

            int[] classRow = classRows.get(r);
            List<String> orderedClasses = new ArrayList<>(classRow.length);
            for (int idx : classRow) {
                if (idx >= 0 && idx < n) orderedClasses.add(sortedClasses.get(idx));
            }

            List<List<int[]>> lexList = new ArrayList<>();
            List<Integer> universeSizes = new ArrayList<>();
            for (int i = 0; i < orderedClasses.size() - 1; i++) {
                String leftClass = orderedClasses.get(i);
                String rightClass = orderedClasses.get(i + 1);
                int leftCount = classToMethods.get(leftClass).size();
                int rightCount = classToMethods.get(rightClass).size();
                List<int[]> pairList = new ArrayList<>();
                for (int x = 1; x <= leftCount; x++) {
                    for (int y = 1; y <= rightCount; y++) {
                        pairList.add(new int[]{x, y});
                    }
                }
                lexList.add(pairList);
                universeSizes.add(pairList.size());
            }

            int T = 0;
            for (int size : universeSizes) if (size > T) T = size;

            for (int k = 0; k < T; k++) {
                List<String> order = new ArrayList<>();

                // First class
                String firstClass = orderedClasses.get(0);
                List<String> methodsFirst = classToMethods.get(firstClass);
                int fixedF = 1;
                int[] pairFirst = lexList.get(0).get(k % lexList.get(0).size());
                int g_first = pairFirst[0];
                String m1 = methodsFirst.get(fixedF - 1);
                String m2 = methodsFirst.get(g_first - 1);
                if (m1.equals(m2)) { order.add(m1); } else { order.add(m1); order.add(m2); }

                // Middle classes
                for (int i = 1; i < orderedClasses.size() - 1; i++) {
                    String currentClass = orderedClasses.get(i);
                    List<String> methodsCurrent = classToMethods.get(currentClass);
                    int[] prevPair = lexList.get(i - 1).get(k % lexList.get(i - 1).size());
                    int f_current = prevPair[1];
                    int[] currPair = lexList.get(i).get(k % lexList.get(i).size());
                    int g_current = currPair[0];
                    String m3 = methodsCurrent.get(f_current - 1);
                    String m4 = methodsCurrent.get(g_current - 1);
                    if (m3.equals(m4)) { order.add(m3); } else { order.add(m3); order.add(m4); }
                }

                // Last class
                String lastClass = orderedClasses.get(orderedClasses.size() - 1);
                List<String> methodsLast = classToMethods.get(lastClass);
                int[] lastPair = lexList.get(lexList.size() - 1).get(k % lexList.get(lexList.size() - 1).size());
                int f_last = lastPair[1];
                int fixedG2 = 1;
                String m5 = methodsLast.get(f_last - 1);
                String m6 = methodsLast.get(fixedG2 - 1);
                if (m5.equals(m6)) { order.add(m5); } else { order.add(m5); order.add(m6); }

                // Trim ends if same class
                if (order.size() >= 2 && order.get(0).split("\\.")[0].equals(order.get(1).split("\\.")[0])) {
                    order.remove(0);
                }
                int sz = order.size();
                if (sz >= 2 && order.get(sz - 2).split("\\.")[0].equals(order.get(sz - 1).split("\\.")[0])) {
                    order.remove(sz - 1);
                }

                // Filter covered inter-class pairs using (alreadyCovered ∪ rowCovered)
                if (order.size() >= 2) {
                    boolean changed = true;
                    while (changed && order.size() >= 2) {
                        changed = false;

                        int hit = -1;
                        for (int i = 0; i + 1 < order.size(); i++) {
                            String x = order.get(i), y = order.get(i + 1);
                            String cx = x.substring(0, x.lastIndexOf('.'));
                            String cy = y.substring(0, y.lastIndexOf('.'));
                            if (!cx.equals(cy)) {
                                String key = x + "||" + y;
                                if ((alreadyCovered != null && alreadyCovered.contains(key)) || rowCovered.contains(key)) {
                                    hit = i; break;
                                }
                            }
                        }
                        if (hit == -1) break;

                        String x = order.get(hit);
                        String y = order.get(hit + 1);

                        boolean leftShared = false, rightShared = false;
                        boolean leftCovered = false, rightCovered = false;

                        if (hit - 1 >= 0) {
                            String w = order.get(hit - 1);
                            String cw = w.substring(0, w.lastIndexOf('.'));
                            String cx = x.substring(0, x.lastIndexOf('.'));
                            if (!cw.equals(cx)) {
                                leftShared = true;
                                String kL = w + "||" + x;
                                leftCovered = (alreadyCovered != null && alreadyCovered.contains(kL)) || rowCovered.contains(kL);
                            }
                        }
                        if (hit + 2 < order.size()) {
                            String z = order.get(hit + 2);
                            String cy = y.substring(0, y.lastIndexOf('.'));
                            String cz = z.substring(0, z.lastIndexOf('.'));
                            if (!cy.equals(cz)) {
                                rightShared = true;
                                String kR = y + "||" + z;
                                rightCovered = (alreadyCovered != null && alreadyCovered.contains(kR)) || rowCovered.contains(kR);
                            }
                        }

                        if (!leftShared && !rightShared) {
                            // pair not shared -> remove BOTH x and y
                            order.remove(hit + 1);
                            order.remove(hit);
                            changed = true;
                            continue;
                        }
                        if (rightShared && !leftShared) {
                            // shared only on right -> remove x to keep (y,z)
                            order.remove(hit);
                            changed = true;
                            continue;
                        }
                        if (leftShared && !rightShared) {
                            // shared only on left -> remove y to keep (w,x)
                            order.remove(hit + 1);
                            changed = true;
                            continue;
                        }

                        // both sides shared
                        if (leftCovered && rightCovered) {
                            // both adjacent inter-class neighbors are also covered -> drop whole order
                            order.clear();
                            changed = true;
                            break;
                        } else if (!rightCovered && leftCovered) {
                            // keep uncovered (y,z) -> remove x
                            order.remove(hit);
                            changed = true;
                            continue;
                        } else if (!leftCovered && rightCovered) {
                            // keep uncovered (w,x) -> remove y
                            order.remove(hit + 1);
                            changed = true;
                            continue;
                        } else {
                            // both neighbors inter-class but both NOT covered -> keep order as-is
                            break;
                        }
                    }
                }

                // --- POST-PASS: keep only elements that belong to an inter-class adjacency ---
                if (order.size() >= 1) {
                    int m = order.size();
                    boolean[] keep = new boolean[m];

                    java.util.function.BiFunction<String,String,Boolean> diffClass = (a,b) -> {
                        String ca = a.substring(0, a.lastIndexOf('.'));
                        String cb = b.substring(0, b.lastIndexOf('.'));
                        return !ca.equals(cb);
                    };

                    // mark items that are part of at least one inter-class pair
                    for (int i = 0; i < m - 1; i++) {
                        if (diffClass.apply(order.get(i), order.get(i + 1))) {
                            keep[i] = true;
                            keep[i + 1] = true;
                        }
                    }

                    // rebuild compacted order
                    List<String> compact = new ArrayList<>();
                    for (int i = 0; i < m; i++) {
                        if (keep[i]) compact.add(order.get(i));
                    }
                    order = compact;

                    // second edge trim for any remaining same-class ends
                    if (order.size() >= 2) {
                        String c0a = order.get(0).substring(0, order.get(0).lastIndexOf('.'));
                        String c0b = order.get(1).substring(0, order.get(1).lastIndexOf('.'));
                        if (c0a.equals(c0b)) order.remove(0);
                    }
                    int osz = order.size();
                    if (osz >= 2) {
                        String cLa = order.get(osz - 2).substring(0, order.get(osz - 2).lastIndexOf('.'));
                        String cLb = order.get(osz - 1).substring(0, order.get(osz - 1).lastIndexOf('.'));
                        if (cLa.equals(cLb)) order.remove(osz - 1);
                    }

                    // if no inter-class adjacency remains, drop the order
                    boolean hasInter = false;
                    for (int i = 0; i + 1 < order.size(); i++) {
                        if (diffClass.apply(order.get(i), order.get(i + 1))) { hasInter = true; break; }
                    }
                    if (!hasInter) {
                        order.clear();
                    }
                }
                // --- END POST-PASS ---

                if (!order.isEmpty()) {
                    // After finalizing this order, add its inter-class pairs to rowCovered (so later orders in this row see them)
                    for (int i = 0; i + 1 < order.size(); i++) {
                        String a = order.get(i), b = order.get(i + 1);
                        String ca = a.substring(0, a.lastIndexOf('.'));
                        String cb = b.substring(0, b.lastIndexOf('.'));
                        if (!ca.equals(cb)) {
                            rowCovered.add(a + "||" + b);
                        }
                    }
                    allOrders.add(order);
                }
            }
        }
        return allOrders;
    }







    public List<List<String>> tuscanInterClassLexOrdersBackup2(java.util.Set<String> alreadyCovered) {
        List<List<String>> allOrders = new ArrayList<>();

        // Get sorted list of classes.
        List<String> sortedClasses = new ArrayList<>(classToMethods.keySet());
        Collections.sort(sortedClasses);
        int n = sortedClasses.size();
        if (n == 0) return allOrders;
        if (n == 1) {
            List<String> singleOrder = new ArrayList<>();
            List<String> methods = classToMethods.get(sortedClasses.get(0));
            String m1 = methods.get(0);
            String m2 = methods.size() > 1 ? methods.get(1) : m1;
            if(m1.equals(m2)) { singleOrder.add(m1); } else { singleOrder.add(m1); singleOrder.add(m2); }

            // Trim ends if same class (unchanged)
            if (singleOrder.size() >= 2 && singleOrder.get(0).split("\\.")[0].equals(singleOrder.get(1).split("\\.")[0])) {
                singleOrder.remove(0);
            }
            int sz1 = singleOrder.size();
            if (sz1 >= 2 && singleOrder.get(sz1 - 2).split("\\.")[0].equals(singleOrder.get(sz1 - 1).split("\\.")[0])) {
                singleOrder.remove(sz1 - 1);
            }
            allOrders.add(singleOrder);
            return allOrders;
        }

        int[][] classOrdering = Tuscan.generateTuscanPermutations(n);

        for (int r = 0; r < classOrdering.length; r++) {
            // New per-row accumulator that RESETS for each Tuscan class row
            java.util.Set<String> rowCovered = new java.util.HashSet<>();

            List<String> orderedClasses = new ArrayList<>();
            for (int i = 0; i < classOrdering[r].length - 1; i++) {
                orderedClasses.add(sortedClasses.get(classOrdering[r][i]));
            }

            List<List<int[]>> lexList = new ArrayList<>();
            List<Integer> universeSizes = new ArrayList<>();
            for (int i = 0; i < orderedClasses.size() - 1; i++) {
                String leftClass = orderedClasses.get(i);
                String rightClass = orderedClasses.get(i + 1);
                int leftCount = classToMethods.get(leftClass).size();
                int rightCount = classToMethods.get(rightClass).size();
                List<int[]> pairList = new ArrayList<>();
                for (int x = 1; x <= leftCount; x++) {
                    for (int y = 1; y <= rightCount; y++) {
                        pairList.add(new int[]{x, y});
                    }
                }
                lexList.add(pairList);
                universeSizes.add(pairList.size());
            }

            int T = 0;
            for (int size : universeSizes) if (size > T) T = size;

            for (int k = 0; k < T; k++) {
                List<String> order = new ArrayList<>();

                // First class
                String firstClass = orderedClasses.get(0);
                List<String> methodsFirst = classToMethods.get(firstClass);
                int fixedF = 1;
                int[] pairFirst = lexList.get(0).get(k % lexList.get(0).size());
                int g_first = pairFirst[0];
                String m1 = methodsFirst.get(fixedF - 1);
                String m2 = methodsFirst.get(g_first - 1);
                if(m1.equals(m2)) { order.add(m1); } else { order.add(m1); order.add(m2); }

                // Middle classes
                for (int i = 1; i < orderedClasses.size() - 1; i++) {
                    String currentClass = orderedClasses.get(i);
                    List<String> methodsCurrent = classToMethods.get(currentClass);
                    int[] prevPair = lexList.get(i - 1).get(k % lexList.get(i - 1).size());
                    int f_current = prevPair[1];
                    int[] currPair = lexList.get(i).get(k % lexList.get(i).size());
                    int g_current = currPair[0];
                    String m3 = methodsCurrent.get(f_current - 1);
                    String m4 = methodsCurrent.get(g_current - 1);
                    if(m3.equals(m4)) { order.add(m3); } else { order.add(m3); order.add(m4); }
                }

                // Last class
                String lastClass = orderedClasses.get(orderedClasses.size() - 1);
                List<String> methodsLast = classToMethods.get(lastClass);
                int[] lastPair = lexList.get(lexList.size() - 1).get(k % lexList.get(lexList.size() - 1).size());
                int f_last = lastPair[1];
                int fixedG = 1;
                String m5 = methodsLast.get(f_last - 1);
                String m6 = methodsLast.get(fixedG - 1);
                if(m5.equals(m6)) { order.add(m5); } else { order.add(m5); order.add(m6); }

                // Trim ends if same class (unchanged)
                if (order.size() >= 2 && order.get(0).split("\\.")[0].equals(order.get(1).split("\\.")[0])) {
                    order.remove(0);
                }
                int sz = order.size();
                if (sz >= 2 && order.get(sz - 2).split("\\.")[0].equals(order.get(sz - 1).split("\\.")[0])) {
                    order.remove(sz - 1);
                }

                // ====== NEW: filter covered inter-class pairs using (alreadyCovered U rowCovered) ======
                if (order.size() >= 2) {
                    boolean changed = true;
                    while (changed && order.size() >= 2) {
                        changed = false;

                        int hit = -1;
                        // find first covered adjacent inter-class pair (x,y)
                        for (int i = 0; i + 1 < order.size(); i++) {
                            String x = order.get(i), y = order.get(i + 1);
                            String cx = x.substring(0, x.lastIndexOf('.'));
                            String cy = y.substring(0, y.lastIndexOf('.'));
                            if (!cx.equals(cy)) {
                                String key = x + "||" + y;
                                if ((alreadyCovered != null && alreadyCovered.contains(key)) || rowCovered.contains(key)) {
                                    hit = i; break;
                                }
                            }
                        }
                        if (hit == -1) break;

                        String x = order.get(hit);
                        String y = order.get(hit + 1);

                        // check shared neighbors (inter-class) and whether those neighbors are covered in union
                        boolean leftShared = false, rightShared = false;
                        boolean leftCovered = false, rightCovered = false;

                        if (hit - 1 >= 0) {
                            String w = order.get(hit - 1);
                            String cw = w.substring(0, w.lastIndexOf('.'));
                            String cx = x.substring(0, x.lastIndexOf('.'));
                            if (!cw.equals(cx)) {
                                leftShared = true;
                                String kL = w + "||" + x;
                                leftCovered = (alreadyCovered != null && alreadyCovered.contains(kL)) || rowCovered.contains(kL);
                            }
                        }
                        if (hit + 2 < order.size()) {
                            String z = order.get(hit + 2);
                            String cy = y.substring(0, y.lastIndexOf('.'));
                            String cz = z.substring(0, z.lastIndexOf('.'));
                            if (!cy.equals(cz)) {
                                rightShared = true;
                                String kR = y + "||" + z;
                                rightCovered = (alreadyCovered != null && alreadyCovered.contains(kR)) || rowCovered.contains(kR);
                            }
                        }

                        if (!leftShared && !rightShared) {
                            // pair not shared -> remove BOTH x and y
                            order.remove(hit + 1);
                            order.remove(hit);
                            changed = true;
                            continue;
                        }

                        if (rightShared && !leftShared) {
                            // shared only on right -> remove x to keep (y,z)
                            order.remove(hit);
                            changed = true;
                            continue;
                        }

                        if (leftShared && !rightShared) {
                            // shared only on left -> remove y to keep (w,x)
                            order.remove(hit + 1);
                            changed = true;
                            continue;
                        }

                        // both sides shared
                        if (leftCovered && rightCovered) {
                            // both adjacent inter-class neighbors are also covered -> drop whole order
                            order.clear();
                            changed = true;
                            break;
                        } else if (!rightCovered && leftCovered) {
                            // keep uncovered (y,z) -> remove x
                            order.remove(hit);
                            changed = true;
                            continue;
                        } else if (!leftCovered && rightCovered) {
                            // keep uncovered (w,x) -> remove y
                            order.remove(hit + 1);
                            changed = true;
                            continue;
                        } else {
                            // both neighbors inter-class but both NOT covered -> keep order as-is
                            break;
                        }
                    }
                }
                // ====== end filtering ======

                if (!order.isEmpty()) {
                    // After finalizing this order, add its inter-class pairs to rowCovered (so later orders in this row see them)
                    for (int i = 0; i + 1 < order.size(); i++) {
                        String a = order.get(i), b = order.get(i + 1);
                        String ca = a.substring(0, a.lastIndexOf('.'));
                        String cb = b.substring(0, b.lastIndexOf('.'));
                        if (!ca.equals(cb)) {
                            rowCovered.add(a + "||" + b);
                        }
                    }
                    allOrders.add(order);
                }
            }
        }
        return allOrders;
    }








   
    public List<List<String>> tuscanInterClassMethodOrder() {
        List<List<String>> allOrders = new ArrayList<>();

        // Get sorted list of classes.
        List<String> sortedClasses = new ArrayList<>(classToMethods.keySet());
        Collections.sort(sortedClasses);
        int n = sortedClasses.size();
        if (n == 0) return allOrders;

        // If only one class, simply use its method Tuscan square (dropping duplicate last element).
        if (n == 1) {
            List<String> methods = classToMethods.get(sortedClasses.get(0));
            int[][] methodTuscan = Tuscan.generateTuscanPermutations(methods.size());
            for (int r = 0; r < methodTuscan.length; r++) {
                List<String> order = new ArrayList<>();
                int[] row = methodTuscan[r];
                // Use indices 0 to (row.length - 1) to get distinct methods.
                for (int j = 0; j < row.length - 1; j++) {
                    order.add(methods.get(row[j]));
                }
                allOrders.add(order);
            }
            return allOrders;
        }

        // Generate the Tuscan square for classes.
        int[][] classOrdering = Tuscan.generateTuscanPermutations(n);

        // For each row of the class Tuscan square, use that row (excluding the duplicate last element)
        // as the serial order of classes.
        for (int r = 0; r < classOrdering.length; r++) {
            List<String> orderedClasses = new ArrayList<>();
            for (int i = 0; i < classOrdering[r].length - 1; i++) {
                orderedClasses.add(sortedClasses.get(classOrdering[r][i]));
            }

            // For each class in the ordered list, generate its method Tuscan square
            // and compute the number of distinct methods as (row length - 1).
            List<int[][]> methodTuscanList = new ArrayList<>();
            List<Integer> distinctCountList = new ArrayList<>();
            for (String cls : orderedClasses) {
                int[][] mTuscan = Tuscan.generateTuscanPermutations(classToMethods.get(cls).size());
                methodTuscanList.add(mTuscan);
                distinctCountList.add(mTuscan[0].length - 1);
            }

            // Build lexicographic lists for each adjacent pair using distinct method counts.
            List<List<int[]>> lexList = new ArrayList<>();
            List<Integer> lexSizes = new ArrayList<>();
            for (int i = 0; i < orderedClasses.size() - 1; i++) {
                int leftDistinct = distinctCountList.get(i);
                int rightDistinct = distinctCountList.get(i + 1);
                List<int[]> pairList = new ArrayList<>();
                for (int x = 1; x <= leftDistinct; x++) {
                    for (int y = 1; y <= rightDistinct; y++) {
                        pairList.add(new int[]{x, y});
                    }
                }
                lexList.add(pairList);
                lexSizes.add(pairList.size());
            }

            // Determine T as the LCM of all lex list sizes.
            int T = 1;
            for (int size : lexSizes) {
                T = lcm(T, size);
            }

            // --- Generate Orders Systematically for This Serial Order ---
            // For each order index k (0 <= k < T), determine the lex pair selection for each adjacent pair,
            // then choose a method row for each class and output the entire distinct method row.
            for (int k = 0; k < T; k++) {
                List<String> order = new ArrayList<>();

                // --- First Class ---
                String firstClass = orderedClasses.get(0);
                List<String> methodsFirst = classToMethods.get(firstClass);
                int fixedF = 1; // always fixed at 1
                int[] pairFirst = lexList.get(0).get(k % lexList.get(0).size());
                int g_first = pairFirst[0];
                int firstRowIndex = (fixedF - 1) % methodTuscanList.get(0).length;
                int[] firstMethodRow = methodTuscanList.get(0)[firstRowIndex];
                // Add the entire distinct method row (indices 0 to row.length - 1)
                for (int j = 0; j < firstMethodRow.length - 1; j++) {
                    order.add(methodsFirst.get(firstMethodRow[j]));
                }

                // --- Middle Classes ---
                for (int i = 1; i < orderedClasses.size() - 1; i++) {
                    String currentClass = orderedClasses.get(i);
                    List<String> methodsCurrent = classToMethods.get(currentClass);
                    int[] prevPair = lexList.get(i - 1).get(k % lexList.get(i - 1).size());
                    int f_current = prevPair[1];
                    int[] currPair = lexList.get(i).get(k % lexList.get(i).size());
                    int g_current = currPair[0];
                    int rowIndex = (f_current - 1) % methodTuscanList.get(i).length;
                    int[] methodRow = methodTuscanList.get(i)[rowIndex];
                    for (int j = 0; j < methodRow.length - 1; j++) {
                        order.add(methodsCurrent.get(methodRow[j]));
                    }
                }

                // --- Last Class ---
                int lastIndex = orderedClasses.size() - 1;
                String lastClass = orderedClasses.get(lastIndex);
                List<String> methodsLast = classToMethods.get(lastClass);
                int[] lastPair = lexList.get(lexList.size() - 1).get(k % lexList.get(lexList.size() - 1).size());
                int f_last = lastPair[1];
                int fixedG = 1;
                int lastRowIndex = (f_last - 1) % methodTuscanList.get(lastIndex).length;
                int[] lastMethodRow = methodTuscanList.get(lastIndex)[lastRowIndex];
                for (int j = 0; j < lastMethodRow.length - 1; j++) {
                    order.add(methodsLast.get(lastMethodRow[j]));
                }

                allOrders.add(order);
            }
        }
        return allOrders;
    }
    public List<List<String>> tuscanInterClassLexOrdersNoremoval(java.util.Set<String> alreadyCovered) {
        List<List<String>> allOrders = new ArrayList<>();

        // Get sorted list of classes.
        List<String> sortedClasses = new ArrayList<>(classToMethods.keySet());
        Collections.sort(sortedClasses);
        int n = sortedClasses.size();
        if (n == 0) return allOrders;
        if (n == 1) {
            // Keep simple construction; no trimming/removal.
            List<String> singleOrder = new ArrayList<>();
            List<String> methods = classToMethods.get(sortedClasses.get(0));
            String m1 = methods.get(0);
            String m2 = methods.size() > 1 ? methods.get(1) : m1;
            singleOrder.add(m1);
            if (!m1.equals(m2)) singleOrder.add(m2); else singleOrder.add(m2);
            allOrders.add(singleOrder);
            return allOrders;
        }

        // Build class rows with custom sequences for n=3 and n=5; otherwise use Tuscan with last cell dropped
        int[][] classOrdering = Tuscan.generateTuscanPermutations(n);
        List<int[]> classRows = new ArrayList<>();
        if (n == 3) {
            // A B C ; B A C ; C A ; C B
            classRows.add(new int[]{0, 1, 2});
            classRows.add(new int[]{1, 0, 2});
            classRows.add(new int[]{2, 0});
            classRows.add(new int[]{2, 1});
        } else if (n == 5) {
            // AEBDC ; BACED ; CADBE ; EABCD ; DECB ; DA
            classRows.add(new int[]{0, 4, 1, 3, 2}); // A E B D C
            classRows.add(new int[]{1, 0, 2, 4, 3}); // B A C E D
            classRows.add(new int[]{2, 0, 3, 1, 4}); // C A D B E
            classRows.add(new int[]{4, 0, 1, 2, 3}); // E A B C D
            classRows.add(new int[]{3, 4, 2, 1});    // D E C B
            classRows.add(new int[]{3, 0});          // D A
        } else {
            // Default: use Tuscan rows, dropping duplicated last cell
            for (int r = 0; r < classOrdering.length; r++) {
                int[] row = classOrdering[r];
                if (row.length > 0) {
                    classRows.add(java.util.Arrays.copyOf(row, row.length - 1));
                } else {
                    classRows.add(row);
                }
            }
        }

        // For each class row, generate orders via lexicographic pairing
        for (int r = 0; r < classRows.size(); r++) {
            int[] classRow = classRows.get(r);
            List<String> orderedClasses = new ArrayList<>(classRow.length);
            for (int idx : classRow) {
                if (idx >= 0 && idx < n) orderedClasses.add(sortedClasses.get(idx));
            }

            // Build lexicographic universes between adjacent classes
            List<List<int[]>> lexList = new ArrayList<>();
            List<Integer> universeSizes = new ArrayList<>();
            for (int i = 0; i < orderedClasses.size() - 1; i++) {
                String leftClass = orderedClasses.get(i);
                String rightClass = orderedClasses.get(i + 1);
                int leftCount = classToMethods.get(leftClass).size();
                int rightCount = classToMethods.get(rightClass).size();
                List<int[]> pairList = new ArrayList<>();
                for (int x = 1; x <= leftCount; x++) {
                    for (int y = 1; y <= rightCount; y++) {
                        pairList.add(new int[]{x, y});
                    }
                }
                lexList.add(pairList);
                universeSizes.add(pairList.size());
            }

            int T = 0;
            for (int size : universeSizes) if (size > T) T = size;

            // Emit raw orders (no trimming/removal/merging)
            for (int k = 0; k < T; k++) {
                List<String> order = new ArrayList<>();

                // First class
                String firstClass = orderedClasses.get(0);
                List<String> methodsFirst = classToMethods.get(firstClass);
                int fixedF = 1;
                int[] pairFirst = lexList.get(0).get(k % lexList.get(0).size());
                int g_first = pairFirst[0];
                String m1 = methodsFirst.get(fixedF - 1);
                String m2 = methodsFirst.get(g_first - 1);
                if (m1.equals(m2)) { order.add(m1); } else { order.add(m1); order.add(m2); }

                // Middle classes
                for (int i = 1; i < orderedClasses.size() - 1; i++) {
                    String currentClass = orderedClasses.get(i);
                    List<String> methodsCurrent = classToMethods.get(currentClass);
                    int[] prevPair = lexList.get(i - 1).get(k % lexList.get(i - 1).size());
                    int f_current = prevPair[1];
                    int[] currPair = lexList.get(i).get(k % lexList.get(i).size());
                    int g_current = currPair[0];
                    String m3 = methodsCurrent.get(f_current - 1);
                    String m4 = methodsCurrent.get(g_current - 1);
                    if (m3.equals(m4)) { order.add(m3); } else { order.add(m3); order.add(m4); }
                }

                // Last class
                String lastClass = orderedClasses.get(orderedClasses.size() - 1);
                List<String> methodsLast = classToMethods.get(lastClass);
                int[] lastPair = lexList.get(lexList.size() - 1).get(k % lexList.get(lexList.size() - 1).size());
                int f_last = lastPair[1];
                int fixedG2 = 1;
                String m5 = methodsLast.get(f_last - 1);
                String m6 = methodsLast.get(fixedG2 - 1);
                if (m5.equals(m6)) { order.add(m5); } else { order.add(m5); order.add(m6); }

                // No trimming / no filtering / no duplicate collapsing
                allOrders.add(order);
            }
        }

        return allOrders;
    }


    /* Helper function to compute gcd */
    private int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    /* Helper function to compute lcm */
    private int lcm(int a, int b) {
        return a * (b / gcd(a, b));
    }












}
