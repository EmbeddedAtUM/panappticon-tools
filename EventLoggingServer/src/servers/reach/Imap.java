/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:09:50 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Imap extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Imap server starts");
			Imap server = new Imap();
			server.listenSocket(Definition.PORT_IMAP);
		}
	}
}
