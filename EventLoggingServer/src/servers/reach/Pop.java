/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:16:20 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Pop extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Pop server starts");
			Pop server = new Pop();
			server.listenSocket(Definition.PORT_POP);
		}
	}
}
