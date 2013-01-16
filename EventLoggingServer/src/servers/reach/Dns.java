/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:14:56 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Dns extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Dns server starts");
			Dns server = new Dns();
			server.listenSocket(Definition.PORT_DNS);
		}
	}
}
