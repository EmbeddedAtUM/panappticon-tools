/**
 * @author Junxian Huang, Mark Gordon
 * @date Aug 30, 2009
 * @time 4:05:55 PM
 * @organization University of Michigan, Ann Arbor
 */
package servers;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.zip.InflaterInputStream;
import java.net.InetSocketAddress;

import common.BaseWorker;
import common.Definition;

/**
 * @author Junxian Huang, Mark Gordon
 *
 */
public class CollectorWorker extends BaseWorker {
  private String sanitize(String s) {
    StringBuffer buf = new StringBuffer();
    for(int i = 0; i < s.length(); i++) {
      char ch = s.charAt(i);
      if('a' <= ch && ch <= 'z' ||
         'A' <= ch && ch <= 'Z' ||
         '0' <= ch && ch <= '9' ||
         "_-.".indexOf(ch) != -1) {
        /* Don't allow for hidden files or .. in path names. */
        if(buf.length() != 0 || ch != '.') {
          buf.append(ch);
        }
      }
    }
    return buf.toString();
  }

	public void run() {
		System.out.println("<Thread " + getId() + "> Collector Thread starts");
    File logFile = null;
    File logFileInf = null;
		byte buffer[] = new byte[20480];
		try {
			client.setSoTimeout(Definition.RECV_TIMEOUT);

      InputStream sin = new BufferedInputStream(client.getInputStream());

      int pos = 0;
      for(int b = sin.read(); b != -1 && b != 0; b = sin.read()) {
        if(pos >= 200 || pos >= buffer.length) {
          /* The header data is too large. */
          client.getOutputStream().write(5);
          client.close();
          return;
        }
        buffer[pos++] = (byte)b;
      }
      String[] headers = new String(buffer, 0, pos).split("\\|");
     
	
      /* Sanitize the data so that it can be used safetly as folder paths. */
      for(int i = 0; i < headers.length; i++) {
        headers[i] = sanitize(headers[i]);
      //Lide added
      System.out.println("Header is " + headers[i]); 
      }
      /* We will enforce that logs must be stored at least three folders deep.
         It would be annoying if buggy/adversarial clients tried to store logs
         in the root of our log folder.
       */
      //if(headers.length < 4) {
      //Lide changed
      if(headers.length < 2) {
        /* Send back a failure code and close. */
        client.getOutputStream().write(1);
        client.close();
        return;
      }

      /* Compute the log folder and create the directory to hold it. */
      StringBuffer directory = new StringBuffer();
      for(int i = 0; i + 2 < headers.length; i++) {
        if(i != 0) directory.append('/');
        directory.append(headers[i]);
      }
      File logFolder = new File(directory.toString());
      if(!logFolder.exists() && !logFolder.mkdirs()) {
        /* Send back a failure code and close. */
        client.getOutputStream().write(2);
        client.close();
        return;
      }
      System.out.println("Thread <" + getId() + "> Created directory: " +
                         directory.toString());
			
      long payloadLength;
      try {
        payloadLength = Long.parseLong(headers[headers.length - 1]);
      } catch(NumberFormatException e) {
        throw new IOException("Invalid header format");
      }
      String timestamp = headers[headers.length - 2];
      //long timestamp = System.currentTimeMillis();
      logFile = new File(logFolder, "" + timestamp +
                         ".deflate");
      //logFileInf = new File(logFolder, "" + timestamp + ".enflate");
      if(logFile.createNewFile()) {
        System.out.println("Thread <" + getId() + "> Writting log file: " +
                           logFile.getName());
        OutputStream fout = new BufferedOutputStream(new FileOutputStream(
                                logFile));
        while(payloadLength > 0) {
          int sz = sin.read(buffer, 0,
                            (int)Math.min(buffer.length, payloadLength));
          if(sz == -1) {
            throw new IOException("Unexpected end of file");
          }
          fout.write(buffer, 0, sz);
          payloadLength -= sz;
        }
        fout.close();

        InetSocketAddress remoteAddr =
            (client.getRemoteSocketAddress() instanceof InetSocketAddress) ?
            (InetSocketAddress)client.getRemoteSocketAddress() : null;
            
        System.out.println("Thread <" + getId() + "> Wrote log file: " +
                           logFile.getName());

        client.getOutputStream().write(0);
        client.close();
	// Lide commented out
        /*System.out.println("Thread <" + getId() + "> Inflating log file: " +
                           logFile.getName());
        InflaterInputStream logIn = new InflaterInputStream(new FileInputStream(
                                                            logFile));
        OutputStream logOut = new BufferedOutputStream(
                                         new FileOutputStream(logFileInf));
        if(remoteAddr != null) {
          logOut.write(
              ("remote_ip " + remoteAddr.getAddress().getHostAddress() +
               "\n").getBytes());
          logOut.write(("remote_host " + remoteAddr.getHostName() +
                        "\n").getBytes());
        }
        try {
          while(true) {
            int sz = logIn.read(buffer, 0, buffer.length);
            if(sz == -1) break;
            logOut.write(buffer, 0, sz);
          }
        } catch(java.io.EOFException e) {
        }
        logIn.close();
        logOut.close();
        logFile.delete();*/

        //logFileInf.renameTo(new File(logFolder, "" + timestamp));
        logFile.renameTo(new File(logFolder, "" + timestamp));
      } else {
        /* Log data with same headers already exists or we couldn't create the
         * file for some reason.
         */
        client.getOutputStream().write(3);
        client.close();
      }
		} catch (IOException e) {
      if(logFile != null) {
        logFile.delete();
      }
      if(logFileInf != null) {
        logFile.delete();
      }
      try {
	if(client != null) {
        /* Send back an error message to the client if they are still alive.
        */
        client.getOutputStream().write(4);
	client.close();
        }
      } catch (IOException e1) {
				e1.printStackTrace();
			}
			e.printStackTrace();
		}
		System.out.println("<" + getId() + "> Thread ends");
	}
}
