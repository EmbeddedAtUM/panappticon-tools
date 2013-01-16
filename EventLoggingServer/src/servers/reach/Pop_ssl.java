/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:11:28 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Pop_ssl extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Pop_ssl server starts");
			Pop_ssl server = new Pop_ssl();
			server.listenSocket(Definition.PORT_POP_SSL);
		}
	}
}
