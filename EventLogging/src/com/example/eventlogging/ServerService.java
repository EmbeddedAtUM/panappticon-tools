package com.example.eventlogging;

import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.ConnectivityManager;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import android.os.BatteryManager;

public class ServerService extends Service{
	private final String TAG = "ServerService";
	
	private UserSpaceServer mUserServer;
	private KernelEventServer mKernelServer;
	private ConfigChange mConfigChange;
	private Writer mWriter;
	private BufferQueue mBufferQueue;
	
	private boolean NetworkListenerRegistered;
	 @Override
	public void onCreate() {
	     mUserServer = new UserSpaceServer();
	     mKernelServer = new KernelEventServer(this);
	     
	     mWriter = Writer.getInstance();  
	     mBufferQueue = BufferQueue.getInstance();
	     
	     IntentFilter filter = new IntentFilter();
	     filter.addAction(Intent.ACTION_BATTERY_CHANGED);
	     registerReceiver(batterybroadcastIntentReceiver, filter);
	     
	     NetworkListenerRegistered = false;
	     
	 }
	
	public int onStartCommand(Intent intent, int flags, int startId) {
	        mWriter.initialize(this);
	        mBufferQueue.initialize(this);
	        mUserServer.start();
	        mKernelServer.start();
	        mConfigChange = new ConfigChange();
	        mConfigChange.start();
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
	 mUserServer.terminate();
	 mKernelServer.terminate();
	 Log.d(TAG,"mConfigChange is " + mConfigChange); 
	 if(mConfigChange != null) 
		mConfigChange.terminate();
	 
	 //mWriter.close();
	 unregisterReceiver(batterybroadcastIntentReceiver);
	 if(NetworkListenerRegistered)
		unregisterReceiver(networkbroadcastReceiver);
    }

	BroadcastReceiver batterybroadcastIntentReceiver = new BroadcastReceiver() {
		@Override
		public void onReceive(Context context, Intent intent) {
			int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
			boolean isCharging = (status == BatteryManager.BATTERY_STATUS_CHARGING) || (status == BatteryManager.BATTERY_STATUS_FULL);
			boolean isDischarging = (status == BatteryManager.BATTERY_STATUS_DISCHARGING);
			Log.d(TAG,"Phone is charging:discharging:registered " +isCharging + " " + isDischarging + " "+NetworkListenerRegistered);
			IntentFilter filter_network = new IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION);
		    if(isCharging){
				registerReceiver(networkbroadcastReceiver, filter_network);	
				NetworkListenerRegistered = true;
		    }
			if(isDischarging){	
				if(NetworkListenerRegistered)
					unregisterReceiver(networkbroadcastReceiver);
				NetworkListenerRegistered = false;
			}		
	    };
	  };

	BroadcastReceiver networkbroadcastReceiver = new BroadcastReceiver(){
		@Override
		public void onReceive(Context context, Intent intent) {
			String action = intent.getAction();
			if(!action.equals(ConnectivityManager.CONNECTIVITY_ACTION))
				return;
			SendFiles mSender = new SendFiles(context);
			if(mSender.shouldUpload())
			{
				Thread t = new Thread(mSender);
				t.start();
			}
			
		}
		
	};
   static {
	System.loadLibrary("get_time");
   }    
   
    public static native long  getCurrentMicroSeconds();
    
    public class LocalBinder extends Binder {
        ServerService getService() {
            return ServerService.this;
        }
    }
}
