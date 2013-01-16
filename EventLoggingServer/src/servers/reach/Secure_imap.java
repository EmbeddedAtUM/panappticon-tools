/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:12:00 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Secure_imap extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Secure_imap server starts");
			Secure_imap server = new Secure_imap();
			server.listenSocket(Definition.PORT_SECURE_IMAP);
		}
	}
}
