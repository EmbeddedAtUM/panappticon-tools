package com.example.eventlogging;

import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import android.os.BatteryManager;

public class ServerService extends Service{
	private final String TAG = "ServerService";
	
	private UserSpaceServer mUserServer;
	private KernelEventServer mKernelServer;
	private Writer mWriter;
	private BufferQueue mBufferQueue;
	 @Override
	public void onCreate() {
	     mUserServer = new UserSpaceServer();
	     mKernelServer = new KernelEventServer(this);
	     mWriter = Writer.getInstance();  
	     mBufferQueue = BufferQueue.getInstance();
	     
	     IntentFilter filter = new IntentFilter();
	     filter.addAction(Intent.ACTION_BATTERY_CHANGED);
	     registerReceiver(broadcastIntentReceiver, filter);
	 }
	
	public int onStartCommand(Intent intent, int flags, int startId) {
	        mWriter.initialize(this);
	        mBufferQueue.initialize(this);
	        Thread t1 = new Thread(mUserServer);
	        t1.start();
	        Thread t2 = new Thread(mKernelServer);
	        t2.start();
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
	 mUserServer.stop();
	 mKernelServer.stop();
	 //mWriter.close();
	 unregisterReceiver(broadcastIntentReceiver);
    }

	BroadcastReceiver broadcastIntentReceiver = new BroadcastReceiver() {
		@Override
		public void onReceive(Context context, Intent intent) {
			int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
			boolean isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
								status == BatteryManager.BATTERY_STATUS_FULL;
			Log.d(TAG,"Phone is charging " +isCharging);
			SendFiles mSender = new SendFiles(context);
			Thread t = new Thread(mSender);
			t.start();
	    };

		/*@Override
		public void onReceive(Context arg0, Intent arg1) {
			// TODO Auto-generated method stub
			
		};*/
	  };

    public class LocalBinder extends Binder {
        ServerService getService() {
            return ServerService.this;
        }
    }
}