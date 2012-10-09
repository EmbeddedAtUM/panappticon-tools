package www.EventLoggingTest;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.os.Process;

public class EventLoggingTestActivity extends Activity {
	
	private String TAG = "EventLoggingTestActivity";
	
	private Button mThreadStartButton;
	private CpuExerciser mCpuExerciser;
	
	 final Runnable mUpdateButton = new Runnable() {
	        public void run() {
	        	Log.d(TAG,"****In the update runnable");
	            updateButton();
	            Log.d(TAG,"Lide: runnable My pid is" + Process.myPid() + " " + Process.myTid());
	        }
	    };
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        mCpuExerciser = new CpuExerciser(this);
        
        mThreadStartButton = (Button)findViewById(R.id.threadStartButton);
        mThreadStartButton.setOnClickListener(threadStartButtonListener);
        mThreadStartButton.setText("Start CPU exerciser!");
        mThreadStartButton.setBackgroundColor(Color.GREEN);
        
        Log.d(TAG,"Lide: main activity My pid is" + Process.myPid() + " " + Process.myTid());
    }
    
    public void onStart(){
    	super.onStart();
    
    }
    private Button.OnClickListener threadStartButtonListener =
        new Button.OnClickListener() {
          public void onClick(View v) {
            mThreadStartButton.setEnabled(false);
            mThreadStartButton.setText("CPU exerciser working!");
            mThreadStartButton.setBackgroundColor(Color.RED);
            Thread t1 = new Thread(mCpuExerciser);
            t1.start();
            mThreadStartButton.setEnabled(true);
          }
      };
      
      public void updateButton(){
      	mThreadStartButton.setText("CPU exercise has stopped");
  		mThreadStartButton.setBackgroundColor(Color.YELLOW);
      }
    
}