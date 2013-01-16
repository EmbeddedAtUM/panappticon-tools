/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:10:48 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Netbios extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Netbios server starts");
			Netbios server = new Netbios();
			server.listenSocket(Definition.PORT_NETBIOS);
		}
	}
}