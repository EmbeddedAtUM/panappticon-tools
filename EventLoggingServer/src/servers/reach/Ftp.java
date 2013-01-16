/**
 * @author Junxian Huang
 * @date Aug 30, 2009
 * @time 10:23:54 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers.reach;

import servers.Collector;

import common.BaseServer;
import common.Definition;

/**
 * @author Junxian Huang
 *
 */
public class Ftp extends BaseServer {
	
	public static void main(String[] argv){
		while(true){
			System.out.println("Ftp server starts");
			Ftp server = new Ftp();
			server.listenSocket(Definition.PORT_FTP);
		}
	}
}
