/**
 * @author Junxian Huang
 * @date Aug 31, 2009
 * @time 1:18:26 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Smtp  extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Smtp server starts");
			Smtp server = new Smtp();
			server.listenSocket(Definition.PORT_SMTP);
		}
	}
}
