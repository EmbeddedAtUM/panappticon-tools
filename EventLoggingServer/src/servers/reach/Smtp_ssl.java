/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:12:58 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Smtp_ssl extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Smtp_ssl server starts");
			Smtp_ssl server = new Smtp_ssl();
			server.listenSocket(Definition.PORT_SMTP_SSL);
		}
	}
}
