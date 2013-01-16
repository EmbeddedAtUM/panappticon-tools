/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:15:20 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Https extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Https server starts");
			Https server = new Https();
			server.listenSocket(Definition.PORT_HTTPS);
		}
	}
}