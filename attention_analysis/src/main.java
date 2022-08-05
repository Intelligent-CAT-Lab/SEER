import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;

public class main {

    public static void main(String[] args){
        String path = System.getProperty("user.dir")+"/TNs_attn_weights";
        File files = new File(path);
        double averagePercentage = 0.0;
        int attendedStatement = 0;
        int allStatements = 0;
        int count = 0;
        int threshold = 5;
        for(File file: files.listFiles()){
            if(file.getName().startsWith("test")){
                try {
                    BufferedReader bf = new BufferedReader(new FileReader(file.getAbsolutePath()));
                    String line = bf.readLine();
                    List<String> CMinusDiffs = new ArrayList<>();
                    List<String> tokens = new ArrayList<>();
                    List<List<Double>> attentionWeights = new ArrayList<>();
                    while (line != null) {
                        // Get tokens of the code
                        if (!line.startsWith("diff") && !line.startsWith("[") && !line.startsWith(
                                " ") && !line.startsWith("*") && line.length() > 0) {
                            tokens = Arrays.asList(line.split(" "));
                        }

                        // Get the diffs and populate non-empty diffs into an array (CMinusDiffs)
                        if (line.startsWith("diff_C-:")) {
                            line = bf.readLine();
                            line = line.substring(1, line.length() - 1);
                            String[] diffs = line.split("', ");
                            for (String diff : diffs) {
                                if (!diff.equals("''")) {
                                    if (diff.startsWith("'"))
                                        diff = diff.substring(1);
                                    if (diff.endsWith("'"))
                                        diff = diff.substring(0, diff.length() - 1);
                                    if (diff.length() > 2)
                                        CMinusDiffs.add(diff);
                                }
                            }
                        }
                        // Get attention matrix
                        if (line.startsWith("[[0")) {
                            //beginning of the matrix
                            String matrix = "";
                            String matrixRow = line.substring(2);
                            boolean terminate = true;
                            while (terminate) {
                                line = bf.readLine();
                                if (line.startsWith("  0")) {
                                    if (line.endsWith("]")) {
                                        line = line.substring(0, line.length() - 1);
                                    }
                                    matrixRow = matrixRow + " " + line.substring(2);
                                } else
                                    terminate = false;
                            }
                            matrix = matrixRow + "\n";
                            while (line != null) {
                                matrixRow = line.substring(2);
                                terminate = true;
                                while (terminate) {
                                    line = bf.readLine();
                                    if (line == null)
                                        break;
                                    if (line.startsWith("  0")) {
                                        if (line.endsWith("]"))
                                            line = line.substring(0, line.length() - 1);
                                        matrixRow = matrixRow + " " + line.substring(2);
                                    } else
                                        terminate = false;
                                }
                                matrix = matrix + matrixRow + "\n";
                            }
                            matrix = matrix.substring(0, matrix.length() - 2);
                            matrix = matrix.replace("    ", " ");
                            matrix = matrix.replace("   ", " ");
                            matrix = matrix.replace("  ", " ");
                            // Transform matrix from string values to double values
                            String[] rows = matrix.split("\n");
                            for (String row : rows) {
                                List<Double> weightRow = new ArrayList<>();
                                for (String item : row.split(" ")) {
                                    Double weight = Double.parseDouble(item);
                                    weightRow.add(weight);
                                }
                                attentionWeights.add(weightRow);
                            }
                        }
                        line = bf.readLine();
                    }

                    // Start the attention analysis
                    int rowCount = 0;
                    List<String> allAttended = new ArrayList<>();
                    List<Integer> allAttendedIndex = new ArrayList<>();
                    for (List<Double> attRow : attentionWeights){
                        // get the mostly attended tokens per each row
                        List<String> rowAttendedTokens = getMostAttended(threshold, rowCount, attRow,
                                tokens);
                        List<Integer> rowAttendedIndices = getMostAttendedIndex(threshold, rowCount,
                                attRow,
                                tokens);
                        // merge them into a single list
                        for(int i=0; i<rowAttendedTokens.size(); i++){
                            String s = rowAttendedTokens.get(i);
                            int index = rowAttendedIndices.get(i);
                            if(!allAttended.contains(s)) {
                                allAttended.add(s);
                                allAttendedIndex.add(index);
                            }
                            else{
                                boolean add = true;
                                for(int j=0; j<allAttended.size(); j++){
                                    if(allAttended.get(j).equals(s)){
                                        if(allAttendedIndex.get(j) == index){
                                            add = false;
                                            break;
                                        }
                                    }
                                }
                                if(add){
                                    allAttended.add(s);
                                    allAttendedIndex.add(index);
                                }
                            }
                        }
                        for(String s:rowAttendedTokens){
                            if(!allAttended.contains(s))
                                allAttended.add(s);
                        }
                        rowCount++;
                    }
                    // remove single tokens in attention
                    /*for(int i=0; i<allAttended.size(); i++){
                        String s = allAttended.get(i);
                        if(s.equals("{") || s.equals("}")){
                            allAttended.remove(i);
                            allAttendedIndex.remove(i);
                        }
                    }*/
                    // computing the contribution
                    int[] contribution = new int[CMinusDiffs.size()];
                    List<Double> contributionPercent = new ArrayList<>();
                    List<Integer> contributionCount = new ArrayList<>();
                    int index = 0;
                    //System.out.println(file.getAbsolutePath());
                    Map<String,Map<String,Integer>> allMaps = new HashMap<>();
                    for(String statement:CMinusDiffs){
                        Map<String,Integer> map = new HashMap<>();
                        for(String token:allAttended) {
                            if(statement.contains(token)) {
                                // get the frequency of token in the code
                                int freq = 0;
                                for(String s:statement.split(" ")){
                                    if(s.equals(token))
                                        freq++;
                                }
                                if(!map.containsKey(token)){
                                    map.put(token,freq);
                                }
                            }
                        }
                        //System.out.println(statement);
                        //System.out.println(allAttended);
                        //System.out.println(map);
                        allMaps.put(statement,map);
                    }
                    List<String> statementAttended = new ArrayList<>();
                    for(String statement:allMaps.keySet()){
                        Map<String,Integer> map = allMaps.get(statement);
                        contribution[index] += map.keySet().size();
                        for(String token:map.keySet()){
                            //System.out.println(statement+" : "+token+" : "+map.get(token));
                            //contribution[index] += map.get(token);
                        }
                        contributionCount.add(contribution[index]);
                        double x = (double) Math.min(100.0,
                                ((contribution[index]*100)/ statement.split(" ").length));
                        contributionPercent.add(x);
                        if(x>=threshold)
                            statementAttended.add("true");
                        else
                            statementAttended.add("false");
                        index++;
                    }

                    if(CMinusDiffs.size()>0 && statementAttended.size()>1){
                        System.out.println(file.getAbsolutePath());
                        System.out.println("Attended Tokens: "+allAttended.toString());
                        System.out.println(CMinusDiffs);
                        System.out.println(contributionPercent);
                        System.out.println(statementAttended);
                        System.out.println(tokens.size());
                        //System.out.println((tokens.size()*threshold/100)
                        // +"->"+contributionCount);
                        for(int i=0; i<contributionPercent.size(); i++){
                            String attended = statementAttended.get(i);
                            allStatements++;
                            if(attended.equals("true"))
                                attendedStatement++;
                            double d = contributionPercent.get(i);
                            averagePercentage += d;
                            count++;
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
        System.out.println("average percentage of tokens attended per statements: "+(averagePercentage/count));
        System.out.println("average attended statements: "+attendedStatement+" from total "+allStatements+"->"+(attendedStatement*100/allStatements));
    }

    private static List<String> getMostAttended(int threshold, int rowCount, List<Double> row,
                                                List<String> tokens){
        List<String> output = new ArrayList<>();
        List<Double> tmp = new ArrayList<>(row);
        int count = (Integer) (row.size()/(100/threshold));
        for(int i=0; i<count; i++){
            int index = getMax(tmp);
            if(index != rowCount)
                output.add(tokens.get(index));
        }
        return output;
    }

    private static List<Integer> getMostAttendedIndex(int threshold, int rowCount, List<Double> row,
                                                List<String> tokens){
        List<Integer> output = new ArrayList<>();
        List<Double> tmp = new ArrayList<>(row);
        int count = (Integer) (row.size()/(100/threshold));
        for(int i=0; i<count; i++){
            int index = getMax(tmp);
            if(index != rowCount)
                output.add(index);
        }
        return output;
    }

    private static int getMax(List<Double> input){
        double max = input.get(0);
        int index = 0;
        for(int i=1; i<input.size();i++){
            if(input.get(i) > max) {
                max = input.get(i);
                index = i;
            }
        }
        input.remove(index);
        input.add(index,-1.0);
        return index;
    }
}

