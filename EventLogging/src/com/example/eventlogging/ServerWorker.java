package com.example.eventlogging;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.net.Socket;

import android.util.Log;


public class ServerWorker implements Runnable{
	private final String TAG = "ServerWorker";

	private Socket mySocket;
	
	public ServerWorker(Socket socket){
		mySocket = socket;
	}
	
	@Override
	public void run() {
		byte buffer[] = new byte[1024*24];
		//TODO: consider changes it into 24*5000 due to the framework parameter
		try {
			//Get the header first
			mySocket.setSoTimeout(30000);
			BufferedInputStream in = new BufferedInputStream(mySocket.getInputStream());
			
			int pos = 0;
			for(int cur = in.read(); cur!=-1 && cur!=0; cur = in.read()){
				buffer[pos++] = (byte)cur;
			}
			String headers = new String(buffer,0, pos);
			Log.d(TAG,"header is"+ headers + ":"+pos);
			
			Long payLoadLength = (long) 0;
			try{
				payLoadLength= Long.parseLong(headers);
			}catch(NumberFormatException e){
				mySocket.getOutputStream().write(1);
				mySocket.close();
				return;
			}
			//DataBuffer myBuffer = DataBuffer.getInstance();
			BufferQueue myBuffer = BufferQueue.getInstance();
			while(payLoadLength > 0){
				int size = in.read(buffer,0,(int)Math.min(buffer.length, payLoadLength));
				if(size == -1){
					mySocket.getOutputStream().write(2);
					mySocket.close();
					return;
				}
				payLoadLength -= size;
				myBuffer.WriteToBuffer(buffer, size, BufferQueue.USER_MODE);
				//myBuffer.WriteToBuffer(buffer, size);	
			}
			mySocket.getOutputStream().write(0);
		
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	

}