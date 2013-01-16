/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:17:01 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Sip extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Sip server starts");
			Sip server = new Sip();
			server.listenSocket(Definition.PORT_SIP);
		}
	}
}
