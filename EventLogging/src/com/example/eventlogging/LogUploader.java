package com.example.eventlogging;

import java.io.BufferedOutputStream;
import java.io.IOException;
import java.math.BigInteger;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
//import java.util.EventLogging;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.telephony.TelephonyManager;
import android.util.Log;


/* This class is responsible for all of the policy decisions on when to actually
 * send log information back to our log collecting servers and is also
 * responsible for actually sending the data should it decide that it is
 * appropriate.
 */
public class LogUploader {
	private final String TAG = "LogUploader";
	public final static int USER_MODE = 0;
	public final static int KERNEL_MODE = 1;
	
	private Thread uploadThread;
	
	public static final int CONNECTION_NONE = 0;
	public static final int CONNECTION_WIFI = 1;
	public static final int CONNECTION_3G = 2;
	
	public static final int UPLOAD_THRESHOLD = 2*1024*1024;//10M 
	
	private static final String SERVER_IP = "gambit.eecs.umich.edu"; 
	private static final int SERVER_PORT = 5204;
	
	private ConnectivityManager connectivityManager;
	private TelephonyManager telephonyManager;
	
	private Writer mWriter;
	
	public LogUploader(Context context){
	    telephonyManager = (TelephonyManager)context.getSystemService(
                Context.TELEPHONY_SERVICE); 
	    connectivityManager = (ConnectivityManager)context.getSystemService(
                    Context.CONNECTIVITY_SERVICE);
	    
	    mWriter = Writer.getInstance();
	}
	
	public int connectionAvailable() {
	    /* TODO: Maybe we should only send data when the device is plugged in.
	     */
	    NetworkInfo info = connectivityManager.getActiveNetworkInfo();
	    if(info == null) {
	      return CONNECTION_NONE;
	    }
	    int netType = info.getType();
	    int netSubtype = info.getSubtype();
	    if (netType == ConnectivityManager.TYPE_WIFI) {
	      return info.isConnected() ? CONNECTION_WIFI : CONNECTION_NONE;
	    } else if (netType == ConnectivityManager.TYPE_MOBILE
	        && (netSubtype == TelephonyManager.NETWORK_TYPE_UMTS || netSubtype == TelephonyManager.NETWORK_TYPE_EDGE)
	        && !telephonyManager.isNetworkRoaming()) {
	      return info.isConnected() ? CONNECTION_3G : CONNECTION_NONE;
	    }
	    return CONNECTION_NONE;
	  }
	
	public void upload(byte [] source, int len, int mode) {
	    uploadThread = new UploadThread(source, len, mode, 0);
	    uploadThread.start();
	  }
	
	public void upload(byte [] source, int len, int mode, long runID){
		  uploadThread = new UploadThread(source, len, mode, runID);
		  uploadThread.start();
	}
	
	private class UploadThread extends Thread{
		private byte [] mSource;
	    private int mLen;
	    private int mMode;
	    private long mRunID;
	    
		public UploadThread(byte [] source, int len, int mode, long runID){
	    	  mSource = source;
	    	  mLen = len;
	    	  mMode = mode;
	    	  mRunID = runID;
	      }
		@Override
		public void run() {
		    int success = 1;
		    long runID = (mRunID == 0)?System.currentTimeMillis(): mRunID;
		    //EventLogging eventLogging = EventLogging.getInstance();
		    for(int iter = 1; !interrupted(); iter++) {
		    	
		    	//eventlogging.addEvent(EventLogging.EVENT_UPLOAD_TRACE);
		    	boolean send_success = send(runID, mSource, mLen, mMode);
		    	//eventlogging.addEvent(EventLogging.EVENT_UPLOAD_DONE);

			if(send(runID, mSource, mLen, mMode)) {
		            break;
		        }
		        if(iter > 4){ 
		        	success = 0;
		        	break; // The max wait is 30 seconds.
		        }
		        Log.i(TAG, "Failed to send log.  Will try again in " + (1 << iter) +
		                     " seconds");
		        try {
		        	//do {
		              sleep(1000 * (1 << iter)); // Sleep for 2^iter seconds.
		              Log.i(TAG, "Failed log sending, sleep for " + (1 << iter) +
		              " seconds");
		            //} while((connectionAvailable() == CONNECTION_NONE)||(connectionAvailable() == CONNECTION_3G));
		         	} catch(InterruptedException e) {
		         		//break;
		         	}
		    }
		    if(success == 0){
		    	//eventlogging.addEvent(EventLogging.EVENT_WRITE_TRACE);    
			mWriter.writeToFile(runID, mSource, mLen, mMode);
		    	//eventlogging.addEvent(EventLogging.EVENT_WRITE_DONE);
		    }
		    	
		}	
	}
		
	public boolean send(long runID, byte[] source, int len, int mode) {
	    Log.i(TAG, "Sending log data " + len + " "+ mode);
	    Socket s = new Socket();
	    try {
	      s.setSoTimeout(4000);
	      s.connect(new InetSocketAddress(SERVER_IP, SERVER_PORT),
	                15000);
	    } catch(IOException e) {
	      /* Failed to connect to server.  Try again later.
	       */
	      return false;
	    }
	    try {
	      BufferedOutputStream sockOut = new BufferedOutputStream(
	                                          s.getOutputStream(), 1024);
	      /* Write the prefix string to the server. */
	      sockOut.write(getPrefix(runID, len, mode));
	      sockOut.write(0);

	      /* Write the array to the server. */
	      int offset = 0;
	      while(true) {
	    	  int sz = (len - offset) > 1024? 1024: (len-offset);
	    	  if(sz <= 0) break;
	    	  sockOut.write(source, offset, sz);
	    	  offset += sz;
	      }
	      sockOut.flush();
	      int response = s.getInputStream().read();
	      s.close();

	      if(response != 0) {
	    	  Log.w(TAG, "Log data not accepted by server");
	      }
	    } catch(SocketTimeoutException e) {
	      /* Connection trouble with server.  Try again later.
	       */
	      return false;
	    } catch(IOException e) {
	    	Log.w(TAG, "Unexpected exception sending log.  Dropping log data");
	    	e.printStackTrace();
	    }
	    return true;
	  }

	  private byte[] getPrefix(long runID, long payloadLength, int mode) {
	    String deviceID = telephonyManager.getDeviceId();
	    String selectMode;
	    if(mode == USER_MODE){
	    	selectMode = "user";
	    	Log.d("Lide","select user mode "+ selectMode);
		    
	    }
	    else{
	    	selectMode = "kernel";
	    	Log.d("Lide","select kernel mode "+ selectMode);
			
	    }
	    return (getMD5(deviceID) + "|"+ selectMode+"|" + payloadLength).getBytes();
	  }
	  
	  private String getMD5(String s){
		    MessageDigest m = null;
		    try {
		      m = MessageDigest.getInstance("MD5");
		    } catch (NoSuchAlgorithmException e) {
		      e.printStackTrace();
		    }
		    m.update(s.getBytes(), 0, s.length());
		    return new BigInteger(1, m.digest()).toString(16);
		  }
}
