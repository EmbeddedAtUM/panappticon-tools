/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:18:53 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Snmp extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Snmp server starts");
			Snmp server = new Snmp();
			server.listenSocket(Definition.PORT_SNMP);
		}
	}
}