import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.util.*;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class phase3_analysis_main {

    public static void main(String[] args){
        String path = System.getProperty("user.dir")+"/attention_analysis/attn_phase3_no_try_except/attn_weights_matrices_phase3";
        File files = new File(path);
//        File output = new File(path + "../main_analysis.txt");
        double averagePercentage = 0.0;
        int attendedStatement = 0;
        int allStatements = 0;
        int count = 0;
        int threshold = 5;
//        String prevCode = "";
        for(File file: files.listFiles()){
//        	Boolean same = false;
            if(file.getName().startsWith("test")){ // remove 100000 to run on all
                try {
                    BufferedReader bf = new BufferedReader(new FileReader(file.getAbsolutePath()));
                    String line = bf.readLine();
                    List<String> statements = new ArrayList<>();//List<String> CMinusDiffs = new ArrayList<>(); 
                    List<String> tokens = new ArrayList<>();
                    List<List<Double>> attentionWeights = new ArrayList<>();
                    while (line != null) {
//                    	System.out.println("Line: " + line);
                        // Get tokens of the code
                        if (line.startsWith("Code: ") && line.length() > 0) {
                        	String newLine = line.substring(6);
//                        	if(prevCode == newLine) {
//                        		same = true;
//                        		break;
//                        	}
//                        	prevCode = newLine;
                        	
                            tokens = Arrays.asList(newLine.split(" "));
                        }

                        // Get the diffs and populate non-empty diffs into an array (CMinusDiffs)
//                        if (line.startsWith("diff_C-:")) {
//                            line = bf.readLine();
//                            line = line.substring(1, line.length() - 1);
//                            String[] diffs = line.split("', ");
//                            for (String diff : diffs) {
//                                if (!diff.equals("''")) {
//                                    if (diff.startsWith("'"))
//                                        diff = diff.substring(1);
//                                    if (diff.endsWith("'"))
//                                        diff = diff.substring(0, diff.length() - 1);
//                                    if (diff.length() > 2)
//                                        CMinusDiffs.add(diff);
//                                }
//                            }
//                        }
                        // Get the statements rather than the diffs -- Attempt to match Paper's Algorithm
//                        System.out.println("Line: " + line);
//                        if(same == true) {
//                        	
//                        }
                        if (line.startsWith("Code: ") && line.length() > 0) {
                            // Need to figure out how to split up the method into statements
                        	int start = line.indexOf('{');
                        	int end = line.lastIndexOf('}');
                        	// newLine does not include method header, or beginning & ending brackets of the method
//                        	System.out.println(file + " " + line);
                        	String newLine = line.substring(start+1, end);
                        	//statements = Arrays.asList(line.split(";")); //don't want this b/c still want the ; present
//                        	System.out.println(newLine);
                        	Boolean notDone = true;
                        	while(notDone) {
                        		String statement = "";
                        		Boolean construct = false;
                        		String strippedLine = newLine.strip();
//                        		System.out.println("NewLine1: " + newLine);
                        		if(strippedLine.charAt(0) == '}') {
                        			newLine = newLine.substring(1);
                        		}
//                        		System.out.println("NewLine2: " + newLine);
                        		int opening = newLine.indexOf('{');
                        		int closing = newLine.indexOf(';');
//                        		System.out.println("Closing: " + closing);
                        		strippedLine = newLine.strip();
                        		if(strippedLine.startsWith("if ") || strippedLine.startsWith("else ") || strippedLine.startsWith("for ") || strippedLine.startsWith("while ") || strippedLine.startsWith("do ") || strippedLine.startsWith("try ") || strippedLine.startsWith("catch ")) {
                        			statement = newLine.substring(0, opening+1);
                        			construct = true;
                        		}
                        		else if(opening == -1 && closing == -1) {
                        			statement = "";
                        			notDone = false;
                        		}
                        		else if(opening == -1) {
//                        			System.out.println(newLine + " " + closing);
                        			statement = newLine.substring(0, closing+1);
                        		}
                        		else if(closing == -1) {
                        			statement = ""; // this case *shouldn't* happen
                        		}
                        		else if(opening < closing) {
                        			if(newLine.indexOf("try")<closing || newLine.indexOf("catch")<closing) { //no longer necessary, try catch accounted for in constructs
                        				String temp = newLine.substring(opening+1, closing+1);
//                        				System.out.println("Temp: " + temp);
//                        				System.out.println("Length: " + newLine.length() + "\n closing+1 = " + (closing+1));
                        				int t_opening = temp.indexOf('{');
                        				int t_closing = temp.indexOf(';');
//                        				System.out.println("Opening: " + opening);
                        				statement = temp.substring(t_opening+1, t_closing+1);
//                        				System.out.println("St: " + statement);
                        			}
                        			else {
                        				statement = newLine.substring(opening+1, closing+1);
                        			}
                        		}
                        		else if(closing < opening) {
                        			statement = newLine.substring(0, closing+1);
                        		}
                        		if((opening!=-1) && (construct)) {
                        			newLine = newLine.substring(opening+1);
//                        			System.out.println("New Line: " + newLine);
                        		}
                        		else if((closing!=-1) && (closing+1 < newLine.length())) {
                        			newLine = newLine.substring(closing+1);
//                        			System.out.println("New Line: " + newLine);
                        		}else {
                        			notDone = false;
//                        			System.out.println("Length: " + newLine.length() + "\n closing+1 = " + closing+1);
                        		}
                        		if(newLine.length() == 0 || newLine.strip().length() == 0) {
                        			notDone = false;
                        		}
//                        		System.out.println("Statement: " + statement + "\n");
                        		if(statement != "" && statement != ";") {
                        			statement = statement.strip();
                        			if(statement.charAt(0) == '}') {
                            			statement = newLine.substring(1);
                            		}
                        			statements.add(statement.strip());
//                        			System.out.println("Statement: " + statement);
                        		}
//                        		System.out.println("Statement: " + statement);
                        	}
//                        	System.out.println("Done");
                        }
                        
//                        System.out.println("Test, beg of matrix");
                        
                        // Get attention matrix
                        if (line.startsWith("[[0")) {
                            //beginning of the matrix
                            String matrix = "";
                            String matrixRow = line.substring(2);
                            boolean terminate = true;
                            while (terminate) {
                                line = bf.readLine();
//                                System.out.println("matrixRow: " + matrixRow + "line: " + line);
                                if (line.startsWith(" 0")) {
                                    if (line.endsWith("]")) {
                                        line = line.substring(0, line.length() - 1);
                                    }
                                    matrixRow = matrixRow + " " + line.substring(2);
//                                    System.out.println("True. MatrixRow: " + matrixRow);
                                } else
                                    terminate = false;
//                                	System.out.println("False. MatrixRow: " + matrixRow);
                            }
                            matrix = matrixRow + "\n";
                            while (line != null) {
                                matrixRow = line.substring(2);
                                terminate = true;
                                while (terminate) {
                                    line = bf.readLine();
                                    if (line == null)
                                        break;
                                    if (line.startsWith(" 0")) {
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
//                                	if(item.startsWith("nsor(")) {
//                                		item = item.substring(7);
//                                	}
                                	if(item.endsWith(",") || item.endsWith("]")) {
//                                		System.out.println(item + " " + item.substring(0, item.length()-1));
                                		item = item.substring(0, item.length()-1);
                                	}
                                	if(item != "") {
                                		Double weight = Double.parseDouble(item);
                                        weightRow.add(weight);
                                	}
                                }
                                attentionWeights.add(weightRow);
                            }
                        }
                        line = bf.readLine();
                    }

                    // Start the attention analysis
//                    System.out.println("Begin attention analysis for " + file);
                    int rowCount = 0;
                    List<String> allAttended = new ArrayList<>();
                    List<Integer> allAttendedIndex = new ArrayList<>();
                    for (List<Double> attRow : attentionWeights){
                        // get the mostly attended tokens per each row
                        List<String> rowAttendedTokens = getMostAttended(threshold, rowCount, attRow,
                                tokens);
//                        System.out.println("Threshold: " + threshold + "\n rowCount: " + rowCount + "\n attRow: " + attRow + "\n Tokens: " + tokens);
//                        System.out.println("rowAttendedTokens: " + rowAttendedTokens);
//                        System.out.println("attentionWeights: " + attentionWeights);
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
                    int[] contribution = new int[statements.size()];//int[] contribution = new int[CMinusDiffs.size()];
                    List<Double> contributionPercent = new ArrayList<>();
                    List<Integer> contributionCount = new ArrayList<>();
                    int index = 0;
                    //System.out.println(file.getAbsolutePath());
                    Map<String,Map<String,Integer>> allMaps = new HashMap<>();
                    for(String statement:statements){//for(String statement:CMinusDiffs){
                        Map<String,Integer> map = new HashMap<>();
//                        System.out.println("All Attended: " + allAttended);
                        for(String token:allAttended) {
//                        	System.out.println("Token: " + token);
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
//                    System.out.println(allMaps.get("closeable.close();"));
                    for(String statement:allMaps.keySet()){
//                    	System.out.println(statement);
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
//                    System.out.println("Test1 " + statements.size() + statementAttended.size() + file);
                    if(statements.size()>0 && statementAttended.size()>1){//if(CMinusDiffs.size()>0 && statementAttended.size()>1){ 
                    	FileWriter myWriter = null;
                    	BufferedWriter bw = null;
                    	PrintWriter pw = null;
//                    	System.out.println("Test2 " + file);
                    	try {
//                    		System.out.println("Test3 " + file);
                    		myWriter = new FileWriter(System.getProperty("user.dir")+"/attention_analysis/main_analysis.txt", true);
                    		bw = new BufferedWriter(myWriter);
                    		pw = new PrintWriter(bw);
                			pw.println(file.getAbsolutePath());
                			pw.println("Attended Tokens: "+allAttended.toString());
                			pw.println(statements.toString());//pw.println(CMinusDiffs.toString());
                			pw.println(contributionPercent.toString());
                			pw.println(statementAttended.toString());
                			pw.println(tokens.size());
                			pw.flush();
                			System.out.println("Here");
                    	} catch (IOException e) {
                			e.printStackTrace();
                		}
//                		} finally{
//                			try {
////                				System.out.println("Test4 " + file);
//                				myWriter.close();
//                				bw.close();
//                				pw.close();
//                			} catch (IOException e) {
//                    			e.printStackTrace();
//                    		}
//                		}
//                    	System.out.println("Test5 " + file);
                    	System.out.println(file.getAbsolutePath());
                        System.out.println("Attended Tokens: "+allAttended.toString());
                        System.out.println(statements);//System.out.println(CMinusDiffs);
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
//        System.out.println("Test6");
        FileWriter myWriter2 = null;
    	BufferedWriter bw2 = null;
    	PrintWriter pw2 = null;
    	try {
//    		System.out.println("Test7");
    		myWriter2 = new FileWriter(System.getProperty("user.dir")+"/attention_analysis/main_analysis.txt", true);
    		bw2 = new BufferedWriter(myWriter2);
    		pw2 = new PrintWriter(bw2);
			pw2.println("average percentage of tokens attended per statements: "+(averagePercentage/count));
			pw2.println("average attended statements: "+attendedStatement+" from total "+allStatements+"->"+(attendedStatement*100/allStatements));
			pw2.flush();
			System.out.println("Test");
    	} catch (IOException e) {
			e.printStackTrace();
		} finally{
			try {
//				System.out.println("Test8");
				myWriter2.close();
//				bw2.close();
				pw2.close();
			} catch (IOException e) {
    			e.printStackTrace();
    		}
		}
//    	System.out.println("Test9");
        System.out.println("average percentage of tokens attended per statements: "+(averagePercentage/count));
        System.out.println("average attended statements: "+attendedStatement+" from total "+allStatements+"->"+(attendedStatement*100/allStatements));
    }

    private static List<String> getMostAttended(int threshold, int rowCount, List<Double> row,
                                                List<String> tokens){
        List<String> output = new ArrayList<>();
        List<Double> tmp = new ArrayList<>(row);
        int count = (Integer) (row.size()/(100/threshold));
//        System.out.println("count: " + row.size());
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

