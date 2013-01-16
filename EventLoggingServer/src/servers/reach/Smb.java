/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:12:29 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Smb extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Smb server starts");
			Smb server = new Smb();
			server.listenSocket(Definition.PORT_SMB);
		}
	}
}
