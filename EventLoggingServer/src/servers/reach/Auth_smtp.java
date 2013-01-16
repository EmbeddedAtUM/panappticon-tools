/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:08:59 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Auth_smtp extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Auth_smtp server starts");
			Auth_smtp server = new Auth_smtp();
			server.listenSocket(Definition.PORT_AUTHENTICATED_SMTP);
		}
	}
}
