/**
 * @author Junxian Huang
 * @date Aug 30, 2009
 * @time 3:30:27 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;

import common.BaseWorker;
import common.Definition;
import common.PrefixParser;

/**
 * @author Junxian Huang
 * 
 */
public class UplinkWorker extends BaseWorker {
 
	public void run() {

		try {
			
			client.setSoTimeout(Definition.RECV_TIMEOUT);

			// String line = "";
			BufferedReader in = null;
			PrintWriter out = null;
			char buffer[] = new char[20480];

			// //////////////////////////////////////////
			// Common init

			this.id = this.getId();

			System.out.println("<" + id + "> Uplink Thread starts");

			in = new BufferedReader(new InputStreamReader(client
					.getInputStream()));
			out = new PrintWriter(client.getOutputStream(), true);

			// //////////////////////////////////////////
			// Get prefix and start tcpdump

			
			StringBuilder prefix_sb = new StringBuilder("");
			int bytes_read = in.read(buffer);
			prefix_sb.append(buffer, 0, bytes_read);
			String prefix = prefix_sb.toString();
			System.out.println("prefix:" + prefix_sb.toString());

			// String prefix = "<iPhone><device_id><run_id>";

			PrefixParser parser = new PrefixParser();
			String prefix_array_string = parser.parsePrefix(prefix);
			if (prefix_array_string == null) {
				System.out.println("Thread <" + id + ">: Prefix error "
						+ prefix);
				return;
			}
			String[] prefix_array = prefix_array_string.split("@@@HJX@@@");
			type_string = prefix_array[0];
			id_string = prefix_array[1];
			rid_string = prefix_array[2];

			String s = null;
			System.out.println("<Thread " + id + "> bash upinit.sh "
					+ type_string + " " + id_string + " " + rid_string);
			Process p = Runtime.getRuntime().exec(
					"bash upinit.sh " + type_string + " " + id_string + " "
							+ rid_string);
			BufferedReader stdInput = new BufferedReader(new InputStreamReader(
					p.getInputStream()));
			while ((s = stdInput.readLine()) != null) {
				System.out.println(s);
				if (s.startsWith("upinit ok")) {
					break;
				}
			}

			System.out.println("Server received prefix ok, start");


			// //////////////////////////////////////////
			// major part

			
			while((bytes_read = in.read(buffer)) > -1){
				//System.out.println("<Thread " + id + "> received " + bytes_read + " bytes");
			}
			

			in.close();
			out.close();
			client.close();

			// //////////////////////////////////////////
			// Terminate tcpdump

			String s2 = null;
			System.out.println("<Thread " + id + "> bash uprep.sh "
					+ type_string + " " + id_string + " " + rid_string);
			Process p2 = Runtime.getRuntime().exec(
					"bash uprep.sh " + type_string + " " + id_string + " "
							+ rid_string);
			BufferedReader stdInput2 = new BufferedReader(
					new InputStreamReader(p2.getInputStream()));
			while ((s2 = stdInput2.readLine()) != null) {
				System.out.println(s2);
				if (s2.startsWith("uprep ok")) {
					break;
				}
			}

			System.out.println("Server received prefix ok, start");

			System.out.println("<" + id + "> Thread ends");

		} catch (IOException e) {
			e.printStackTrace();
			try {
				Process p2 = Runtime.getRuntime().exec(
						"bash uprep.sh " + type_string + " " + id_string + " "
								+ rid_string);
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
		}
	}

}
