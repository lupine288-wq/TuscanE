import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import org.json.simple.parser.JSONParser;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import tuscan.orders.TestShuffler;
import tuscan.orders.Tuscan;



public class GetTuscanOrders {

    public static void main(String [] args) {
        String project = args[0];
        String sha = args[1]; // Short sha
        String module = args[2];
        String method = args[3];
        // All original rounds should be in ./original-rounds
        String pathToOrders = "simplified_original_test_orders/";
        File folder = new File(pathToOrders);
        System.out.println(folder);
        File[] listOfFiles = folder.listFiles();

        try {
	    String cproject = project.replace("/", "_");
	    String cmodule = module.replace("/", "_");
	    System.out.println(cproject);
	    String originalOrderStr = pathToOrders + cproject + "-" + cmodule + "-" + sha + "-original_order";
            Path originalOrderPath = Paths.get(originalOrderStr);
	    List<String> tests = Files.readAllLines(originalOrderPath); 

	    // We have orders generate its tuscan orders and get the list
            TestShuffler testShuffler = new TestShuffler(tests);
            
            String outputPathPrefix = "outputs/" + method + "/" + project + "/" + module + "/" + sha + "/";

            switch (method) {
                case "only":
                    generateClassOnly(outputPathPrefix, testShuffler, tests);
                    break;
                case "intra":
                    generateIntraClass(outputPathPrefix, testShuffler, tests);
                    break;
                case "inter":
                    generateInterClass(outputPathPrefix, testShuffler, tests);
                    break;
                // Case for target pairs method
                // case "":
                //     break;
                default:
                    System.out.println("WRONG METHOD");
                    break;
            }
        } catch(Exception e) {
            e.printStackTrace();
        }
    }

    public static int getClassesSize(List<String> tests) {
        List<String> classes = new ArrayList<String>();        
        for (final String test : tests) {
            final String className = TestShuffler.className(test);
            if (!classes.contains(className)) {
                classes.add(className);
            }
        }
        return classes.size();
    }

    public static void makeJSON(String prefix, int i, List<String> testOrder) {
        JSONObject jsonObject = new JSONObject();
        // System.out.println(i + " | " + testOrder.size());
        jsonObject.put("testOrder", testOrder);
        // String outFile = String.format("outputs/round%d.json", i);
        String outFile = prefix + "round" + i + ".json";
        try {
            FileWriter file = new FileWriter(outFile);
            file.write(jsonObject.toJSONString());
            file.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static HashMap<String, List<String>> generateClassToMethods (List<String> tests) {
        HashMap<String, List<String>> classToMethods = new HashMap<>();
        for (final String test : tests) {
            final String className = TestShuffler.className(test);
            if (!classToMethods.containsKey(className)) {
                classToMethods.put(className, new ArrayList<>());
            }
            classToMethods.get(className).add(test);
        }
        return classToMethods;
    }

    public static int findNumberOfRoundsInterClass (HashMap<String, List<String>> classToMethods) {
        int classSize = classToMethods.keySet().size();
        if (classSize == 1) {
            // If there is only one class, just run one round
            return 1;
        }
        List<String> classes = new ArrayList<>(classToMethods.keySet());
        Collections.sort(classes);
        int[][] classPermutations = Tuscan.generateTuscanPermutations(classSize);
        HashMap<String, Integer> classToSize = new HashMap<>();
        for (String className : classToMethods.keySet()) {
            classToSize.put(className, classToMethods.get(className).size());
        }
        int tempRounds = 0;
        for (int i = 0; i < classPermutations.length; i++) {
            int methodSize = 0;
            for (int j = 0; j < classPermutations[i].length - 2; j++) {
                String current = classes.get(classPermutations[i][j]);
                String next = classes.get(classPermutations[i][j + 1]);
                int size1 = classToMethods.get(current).size();
                int size2 = classToMethods.get(next).size();
                if (size1 == 3 || size1 == 5) {
                    size1++;
                }
                if (size2 == 3 || size2 == 5) {
                    size2++;
                }
                methodSize += (size1 * size2);
            }
            tempRounds += methodSize;
        }
        return tempRounds;
    }
    

    public static int findMaxMethodSize(HashMap<String, List<String>> classToMethods) {
        int maxMethodSize = 0;
        for (String className : classToMethods.keySet()) {
            int nn = classToMethods.get(className).size();
            if (maxMethodSize < nn) {
                maxMethodSize = nn;
            }
        }
        return maxMethodSize;
    }

    public static void generateClassOnly(String prefix, TestShuffler testShuffler, List<String> tests) {
        int n = getClassesSize(tests);
        int rounds = n;
        if (n == 3 || n == 5) {
            rounds++;
        }
        System.out.println(rounds);
        for (int i = 0; i < rounds; i++) {
            List<String> currentRoundPermutation = testShuffler.OriginalAndTuscanOrder(i, true);
            makeJSON(prefix, i, currentRoundPermutation);
            // System.out.println(currentRoundPermutation);
        }
    }

    public static void generateIntraClass(String prefix, TestShuffler testShuffler, List<String> tests) {
        HashMap<String, List<String>> classToMethods = generateClassToMethods(tests);
        int maxMethodSize = findMaxMethodSize(classToMethods);
        if (maxMethodSize == 3 || maxMethodSize == 5) {
            maxMethodSize++;
        }
        int rounds;
        int classSize = classToMethods.keySet().size();
        if (classSize == 3 || classSize == 5) {
            classSize++;
        }
        if (classSize > maxMethodSize) {
            rounds = classSize;
        } else {
            rounds = maxMethodSize;
        }
        // int rounds = 230;
        System.out.println(rounds);
        for (int i = 0; i < rounds; i++) {
            List<String> currentRoundPermutation = testShuffler.tuscanIntraClassOrder(i);
            makeJSON(prefix, i, currentRoundPermutation);
            // System.out.println(currentRoundPermutation);
        }
    }


    public static void generateInterClass(String prefix, TestShuffler testShuffler, List<String> tests) {
        // First: generate orders using the new method (returns orders + inter-class pairs)
        java.util.Map.Entry<List<List<String>>, List<String[]>> res = testShuffler.tuscanInterClassNewOrders();
        List<List<String>> newOrders = res.getKey();
        List<String[]> interPairs = res.getValue();

        int newRounds = newOrders.size();
        System.out.println("New Orders Rounds: " + newRounds);
        for (int i = 0; i < newRounds; i++) {
            makeJSON(prefix, i, newOrders.get(i));
        }
        System.out.println("Inter-class adjacent pairs covered (from new orders): " + interPairs.size());

        // Build covered set "left||right"
        java.util.Set<String> covered = new java.util.HashSet<>();
        for (String[] p : interPairs) {
            if (p != null && p.length == 2) covered.add(p[0] + "||" + p[1]);
        }

        // Then: generate lexicographic orders, filtering already-covered inter-class pairs per the new rule
        List<List<String>> lexOrders = testShuffler.tuscanInterClassLexOrders(covered);
        int lexRounds = lexOrders.size();
        System.out.println("Lex Orders Rounds (after filtering): " + lexRounds);
        for (int i = 0; i < lexRounds; i++) {
            makeJSON(prefix, i + newRounds, lexOrders.get(i));
        }
    }

    




}
 