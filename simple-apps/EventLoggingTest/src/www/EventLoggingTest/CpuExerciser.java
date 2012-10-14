package www.EventLoggingTest;

import android.os.Handler;
import android.os.Process;
import android.os.SystemClock;
import android.util.Log;

public class CpuExerciser implements Runnable
{
	private static String TAG = "CpuExerciser";
	private int mLoad = 1000 * 10; //ms
	private Handler mHandler = new Handler();
	public boolean active = false;
	public boolean alive = true;
	public EventLoggingTestActivity mActivity;
	
	private int x = 0;
	private int y = 2;
	private int z = 5;
	
	public CpuExerciser(EventLoggingTestActivity m){
		mActivity = m;
	}
	
	public void run() {
		Log.d(TAG,"Lide: cpuexerciser pid is" + Process.myPid() + " " + Process.myTid());
			exerciser(mLoad);
			mHandler.post(mActivity.mUpdateButton);
			Log.d(TAG,"Lide runnable from worker is "+ mActivity.mUpdateButton.hashCode()+" "+mActivity.mUpdateButton.toString());
			return;
	}
	private void exerciser (int mLoad){
		if (mLoad >= 0) {
			// elapsed real time has milliseconds since boot, including deep sleep
			long begin_time = SystemClock.elapsedRealtime();
			long end_time = begin_time;
			while(end_time-begin_time< mLoad) {
			    		x += 5;
			    		y += 3;
			    		z += 7;
			    		x += z;
			    		y += z;
			    		z += 8;
					end_time = SystemClock.elapsedRealtime();		
			}
			//SystemClock.sleep(100-mLoad);
			} 
	}
		
	protected void finalize() {
		mHandler.removeCallbacks(this);
	}
	
	public int getLoad() {
		return mLoad;
	}
	
	public void setLoad(int load) {
		mLoad = load;
	}
};
