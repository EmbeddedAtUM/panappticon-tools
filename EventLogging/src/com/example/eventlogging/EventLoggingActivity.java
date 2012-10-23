package com.example.eventlogging;

import android.os.Bundle;
import android.os.IBinder;
import android.app.Activity;
import android.app.ActivityManager;
import android.app.ActivityManager.RunningServiceInfo;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.graphics.Color;
import android.view.Menu;
import android.view.View;
import android.widget.Button;

public class EventLoggingActivity extends Activity {
	private String TAG = "EventLoggingActivity";

	private ServerService mServerService;
	private Button mServiceStartButton;
	private Intent mServerIntent;
	private boolean mServiceIsRunning;
    private boolean mIsBound;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_event_logging);
        
        mServerIntent = new Intent(this, ServerService.class);
        mServiceStartButton = (Button)findViewById(R.id.serviceStartButton);
        mServiceStartButton.setOnClickListener(serviceStartButtonListener);
        mServiceIsRunning = isMyServiceRunning();
        
        if(!mServiceIsRunning)
        {
        	mServiceStartButton.setBackgroundColor(Color.GREEN);   
        	mServiceStartButton.setText("Start service!");
        }else{
        	 mServiceStartButton.setBackgroundColor(Color.RED);
        	 mServiceStartButton.setText("Stop service!");
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.activity_event_logging, menu);
        return true;
    }
    
    
    private boolean isMyServiceRunning(){
    	ActivityManager manager = (ActivityManager) getSystemService(ACTIVITY_SERVICE);
    	for(RunningServiceInfo service: manager.getRunningServices(Integer.MAX_VALUE)){
    		if(ServerService.class.getName().equals(service.service.getClassName())){
    			return true;
    		}
    	}
    	return false;
    }
    
    private Button.OnClickListener serviceStartButtonListener =
            new Button.OnClickListener() {
    	public void onClick(View v) {
    		//Log.d(TAG,"Button has been clicked "+ mServiceIsRunning);
    		mServiceStartButton.setEnabled(false);
    		if(mServiceIsRunning) {
    			doUnbindService();
    			stopService(mServerIntent);
    			mServiceStartButton.setBackgroundColor(Color.GREEN);  
    			mServiceStartButton.setText("Start service!");
    			mServiceIsRunning = false;
    		} else {
    			startService(mServerIntent);
    			mServiceStartButton.setBackgroundColor(Color.RED);  
    			mServiceStartButton.setText("Stop service!");
    			mServiceIsRunning = true;
    			doBindService();
    		}
    		mServiceStartButton.setEnabled(true);
    	}
    };
          
    private ServiceConnection mConnection = new ServiceConnection() {
    	public void onServiceConnected(ComponentName className, IBinder service) {
    		mServerService = ((ServerService.LocalBinder)service).getService();
    	}

    	public void onServiceDisconnected(ComponentName className) {
    		mServerService = null;
    	}
    };

    void doBindService() {
    	bindService(mServerIntent, mConnection, Context.BIND_AUTO_CREATE);
    	mIsBound = true;
    }

    void doUnbindService() {
    	if (mIsBound) {
    		unbindService(mConnection);
    		mIsBound = false;
    	}
    }
    
}
