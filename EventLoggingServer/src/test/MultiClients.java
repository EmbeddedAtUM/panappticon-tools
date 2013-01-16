/**
 * @author Junxian Huang
 * @date Aug 29, 2009
 * @time 2:27:05 PM
 * @organization University of Michigan, Ann Arbor
 */
package test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

/**
 * @author Junxian Huang
 *
 */

public class MultiClients extends Thread {

	public long id;
	

	@Override
	public void run() {
		// TODO Auto-generated method stub
		Socket socket;
		PrintWriter out;
		BufferedReader in;
		
		this.id = this.getId();
		
		try{
			
			for(int i = 0 ; i < 10 ; i++){
				//Thread.sleep(200);
				//System.out.println("this is " + id);
			}
			//if(1 == 1)return;
			
		    socket = new Socket("141.212.111.182", 5110);
		    out = new PrintWriter(socket.getOutputStream(), 
		                true);
		    in = new BufferedReader(new InputStreamReader(
			       socket.getInputStream()));
		     
		    //for(int i = 0 ; i < 5 ; i++){
		    	out.println("ID<" + id + ">");
		    	//Thread.sleep(1);
		    //}
		    	char cbuf[] = new char[1000];
		    	in.read(cbuf);
		    	StringBuilder sb = new StringBuilder("");
		    	sb.append(cbuf);
		    	System.out.println(sb.toString());
		    in.close();
		    out.close();
		    socket.close();
		     
		} catch (UnknownHostException e) {
		     System.out.println("Unknown host: falcon.eecs.umich.edu");
		     System.exit(1);
		} catch  (IOException e) {
		     System.out.println("No I/O");
		     System.exit(1);
		}
		
	}

	
}
