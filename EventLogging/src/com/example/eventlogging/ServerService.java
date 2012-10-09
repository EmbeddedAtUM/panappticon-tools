package com.example.eventlogging;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;

public class ServerService extends Service{
	private final String TAG = "ServerService";
	
	private UserSpaceServer mServer;
	private Writer mWriter;
	private DataBuffer mDataBuffer;
	 @Override
	public void onCreate() {
	     mServer = new UserSpaceServer();
	     mWriter = Writer.getInstance();  
	     mDataBuffer = DataBuffer.getInstance();
	 }
	
	public int onStartCommand(Intent intent, int flags, int startId) {
	        mWriter.initialize(this);
	        mDataBuffer.initialize(this);
	        Thread t1 = new Thread(mServer);
	        t1.start();
		    int START_STICKY = 1;
	        return START_STICKY;
	    }
	 
	@Override
	public IBinder onBind(Intent intent) {
		return null;
	}

	@Override
    public void onDestroy() {
	 Log.d(TAG,"Service on destroy");
	 mServer.stop();
	 mWriter.close();
    }

    public class LocalBinder extends Binder {
        ServerService getService() {
            return ServerService.this;
        }
    }
}