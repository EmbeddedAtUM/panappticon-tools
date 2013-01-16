/**
 * @author Junxian Huang
 * @date Aug 29, 2009
 * @time 5:39:02 PM
 * @organization University of Michigan, Ann Arbor
 */
package common;

/**
 * @author Junxian Huang
 *
 */
public class PrefixParser {

	public String parsePrefix(String prefix){
		String[] prefix_array = prefix.split("><");
		//<aaa><aaa><aaa>
		//<aaa  aaa  aaa>

		//System.out.println("PrefixParser " + prefix);
		if(prefix_array.length == 3){
			if(prefix_array[0].startsWith("<") && prefix_array[2].endsWith(">")){
				prefix_array[0] = prefix_array[0].substring(1);
				prefix_array[2] = prefix_array[2].substring(0, prefix_array[2].length() - 1);
				//System.out.println(prefix_array[0] + "@@@HJX@@@" + prefix_array[1] + "@@@HJX@@@" + prefix_array[2]);
				return prefix_array[0] + "@@@HJX@@@" + prefix_array[1] + "@@@HJX@@@" + prefix_array[2];
			}
		}

		return null;
	}

}
