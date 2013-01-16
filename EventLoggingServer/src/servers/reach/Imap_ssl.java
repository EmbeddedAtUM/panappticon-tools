/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:15:48 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Imap_ssl extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Imap_ssl server starts");
			Imap_ssl server = new Imap_ssl();
			server.listenSocket(Definition.PORT_IMAP_SSL);
		}
	}
}