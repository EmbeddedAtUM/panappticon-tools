/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:16:40 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Rpc extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Rpc server starts");
			Rpc server = new Rpc();
			server.listenSocket(Definition.PORT_RPC);
		}
	}
}
