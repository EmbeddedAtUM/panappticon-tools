package com.example.eventlogging;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

import android.util.Log;


public class UserSpaceServer implements Runnable{
	private final String TAG = "UserSpaceServer";
	private final int COLLECTOR_PORT = 1234;
	
	private ServerSocket mySocket;
	private boolean mActive;
	
	public UserSpaceServer(){
		mActive = true;
		try {
			mySocket = new ServerSocket(COLLECTOR_PORT);
		} catch (IOException e) {
			// TODO Fill in the right handling
			e.printStackTrace();
		}
	}
	public void run(){
		while(mActive){
			Socket connectionSocket;			
			try {
				Log.d(TAG,"accepting...");
				connectionSocket = mySocket.accept();
				ServerWorker myWorker = new ServerWorker(connectionSocket);
				Thread workerThread = new Thread(myWorker);
				workerThread.start();
			} catch (IOException e) {
				// TODO Fill in the right handling
				e.printStackTrace();
			}	
		}
	}
	
	public void stop(){
		mActive = false;
		try {
			mySocket.close();
		} catch (IOException e) {
			// TODO Fill in the right handling
			e.printStackTrace();
		}
	}
	
	
	
	
}

