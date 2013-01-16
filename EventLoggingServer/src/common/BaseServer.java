/**
 * @author Junxian Huang
 * @date Aug 29, 2009
 * @time 2:04:36 PM
 * @organization University of Michigan, Ann Arbor
 */
package common;

import java.io.IOException;
import java.net.ServerSocket;

import servers.*;

/**
 * @author Junxian Huang
 * 
 * Description: This is the base class for a multi-threaded server
 *
 */
public class BaseServer {
	
	public ServerSocket server;
	
	public void listenSocket(int port){
		try{
			server = new ServerSocket(port);
		} catch (IOException e) {
			try {
				Thread.sleep(1000);
			} catch (InterruptedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		    System.out.println("Could not listen on port " + port);
		    
			return;
		}
		while(true){
			
		    try{
		    	//server.accept returns a client connection
		    	switch(port){
		    	
		    	case Definition.PORT_USER_STAT:
		    		UserStateWorker us_worker = new UserStateWorker();
		    		us_worker.setSocket(server.accept());
		    		us_worker.start();
		    		break;
		    	
		    	case Definition.PORT_HTTP:
		    		HttpWorker http_worker = new HttpWorker();
		    		http_worker.setSocket(server.accept());
		    		http_worker.start();
		    		break;
		    	
		    	case Definition.PORT_BT_RANDOM:
		    		BtNondftWorker btnondft_worker = new BtNondftWorker();
		    		btnondft_worker.setSocket(server.accept());
		    		btnondft_worker.start();
		    		break;
		    	
		    	
		    	case Definition.PORT_BT:
		    		BtWorker bt_worker = new BtWorker();
		    		bt_worker.setSocket(server.accept());
		    		bt_worker.start();
		    		break;
		    	
		    	
		    	
		    	case Definition.PORT_WHOAMI:
		    		WhoamiWorker whoami_worker = new WhoamiWorker();
		    		whoami_worker.setSocket(server.accept());
		    		whoami_worker.start();
		    		break;
		    	
		    	case Definition.PORT_VERSION:
		    		VersionWorker version_worker = new VersionWorker();
		    		version_worker.setSocket(server.accept());
		    		version_worker.start();
		    		break;
		    	
		    	case Definition.PORT_REPORT:
		    		CollectorWorker collector_worker = new CollectorWorker();
		    		collector_worker.setSocket(server.accept());
		    		collector_worker.start();
		    		break;
		    	
		    	
		    	case Definition.PORT_DOWN_THRU:
		    		//downlink server
		    		DownlinkWorker downlink_worker = new DownlinkWorker();
		    		downlink_worker.setSocket(server.accept());
		    		downlink_worker.start();
		    		break;
		    		
		    	case Definition.PORT_UP_THRU:
		    		UplinkWorker uplink_worker = new UplinkWorker();
		    		uplink_worker.setSocket(server.accept());
		    		uplink_worker.start();
		    		break;
		    		
		    	//Reach start
		    		
		    	case Definition.PORT_AUTHENTICATED_SMTP:
		    		BaseWorker auth_smtp_worker = new BaseWorker();
		    		auth_smtp_worker.setSocket(server.accept());
		    		auth_smtp_worker.start();
		    		break;
		    		
		    	case Definition.PORT_DNS:
		    		BaseWorker dns_worker = new BaseWorker();
		    		dns_worker.setSocket(server.accept());
		    		dns_worker.start();
		    		break;
		    		
		    	case Definition.PORT_FTP:
		    		BaseWorker ftp_worker = new BaseWorker();
		    		ftp_worker.setSocket(server.accept());
		    		ftp_worker.start();
		    		break;	
		    		
		    	case Definition.PORT_HTTPS:
		    		BaseWorker https_worker = new BaseWorker();
		    		https_worker.setSocket(server.accept());
		    		https_worker.start();
		    		break;
		    		
		    	case Definition.PORT_IMAP_SSL:
		    		BaseWorker imap_ssl_worker = new BaseWorker();
		    		imap_ssl_worker.setSocket(server.accept());
		    		imap_ssl_worker.start();
		    		break;
		    	
		    	case Definition.PORT_IMAP:
		    		BaseWorker imap_worker = new BaseWorker();
		    		imap_worker.setSocket(server.accept());
		    		imap_worker.start();
		    		break;
		    		
		    	case Definition.PORT_NETBIOS:
		    		BaseWorker netbios_worker = new BaseWorker();
		    		netbios_worker.setSocket(server.accept());
		    		netbios_worker.start();
		    		break;
		    		
		    	case Definition.PORT_POP_SSL:
		    		BaseWorker pop_ssl_worker = new BaseWorker();
		    		pop_ssl_worker.setSocket(server.accept());
		    		pop_ssl_worker.start();
		    		break;
		    	
		    	case Definition.PORT_POP:
		    		BaseWorker pop_worker = new BaseWorker();
		    		pop_worker.setSocket(server.accept());
		    		pop_worker.start();
		    		break;
		    		
		    	case Definition.PORT_RPC:
		    		BaseWorker rpc_worker = new BaseWorker();
		    		rpc_worker.setSocket(server.accept());
		    		rpc_worker.start();
		    		break;
		    		
		    	case Definition.PORT_SECURE_IMAP:
		    		BaseWorker secure_imap_worker = new BaseWorker();
		    		secure_imap_worker.setSocket(server.accept());
		    		secure_imap_worker.start();
		    		break;
		    		
		    	case Definition.PORT_SIP:
		    		BaseWorker sip_worker = new BaseWorker();
		    		sip_worker.setSocket(server.accept());
		    		sip_worker.start();
		    		break;
		    		
		    	case Definition.PORT_SMB:
		    		BaseWorker smb_worker = new BaseWorker();
		    		smb_worker.setSocket(server.accept());
		    		smb_worker.start();
		    		break;
		    		
		    	case Definition.PORT_SMTP_SSL:
		    		BaseWorker smtp_ssl_worker = new BaseWorker();
		    		smtp_ssl_worker.setSocket(server.accept());
		    		smtp_ssl_worker.start();
		    		break;
		    		
		    	case Definition.PORT_SMTP:
		    		BaseWorker smtp_worker = new BaseWorker();
		    		smtp_worker.setSocket(server.accept());
		    		smtp_worker.start();
		    		break;
		    		
		    	case Definition.PORT_SNMP:
		    		BaseWorker snmp_worker = new BaseWorker();
		    		snmp_worker.setSocket(server.accept());
		    		snmp_worker.start();
		    		break;
		    	//Reach end
		    	default:
		    		System.out.println("Port " + port + " is not currently supported by BaseServer");
			    	break;
		    		
		    	}
		    	
		    } catch (IOException e) {
		    	System.out.println("Server failed: port <" + port + ">");
		    	return;
		    }
		}
	}


}