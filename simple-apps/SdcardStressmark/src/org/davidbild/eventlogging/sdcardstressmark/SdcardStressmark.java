package org.davidbild.eventlogging.sdcardstressmark;

import org.davidbild.eventlogging.sdcardstressmark.R;

import android.os.Bundle;
import android.os.Handler;
import android.os.SystemClock;
import android.app.Activity;
import android.graphics.Color;
import android.view.Menu;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class SdcardStressmark extends Activity {

	private static final String TAG = "SdcardStessmark";

	private Button mButton;
	private TextView mTextView;
	private Handler mHandler;
	private SdcardStressmarkRunner mSdcardExerciser;
	private DvfsStressmarkRunner mCpuExerciser;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		mHandler = new Handler();
		mButton = (Button) findViewById(R.id.threadStartButton);
		mButton.setOnClickListener(mButtonListener);
		mCpuExerciser = new DvfsStressmarkRunner(65, 1, 100);
		mSdcardExerciser = new SdcardStressmarkRunner(this);
		updateButton();
		mTextView = (TextView) findViewById(R.id.textview);
	}

	private Button.OnClickListener mButtonListener = new Button.OnClickListener() {
		public void onClick(View v) {
			mButton.setEnabled(false);
			mButton.setText("Running stressmark");
			mButton.setBackgroundColor(Color.YELLOW);
			new SerialRunner().start();
			//new Thread(new CpuRunner()).start();
			//new Thread(new SdcardRunner()).start();
		}
	};

	public void updateButton() {
		mButton.setText("Start stressmark");
		mButton.setBackgroundColor(Color.GREEN);
		mButton.setEnabled(true);
	}

	private void appendMessageCallback(CharSequence message) {
		mTextView.append(message);
	}

	public void appendMessage(final CharSequence message) {
		mHandler.post(new Runnable() {
			@Override
			public void run() {
				appendMessageCallback(message);
			}
		});
	}

	private final Runnable mUpdateButton = new Runnable() {
		public void run() {
			updateButton();
		}
	};

	private class SdcardRunner extends Thread {
		@Override
		public void run() {
			appendMessage("sdcard: stressing\n");
			mSdcardExerciser.stress();
			appendMessage("sdcard: done\n");
		}
	}

	private class CpuRunner extends Thread {
		@Override
		public void run() {
			appendMessage("Started\n");
			long start = SystemClock.elapsedRealtime();
			mCpuExerciser.stress();
			appendMessage(String.format("Finished. Took %d ms\n",
					SystemClock.elapsedRealtime() - start));
			mHandler.post(mUpdateButton);
		}
	}

	private class SerialRunner extends Thread {
		@Override
		public void run() {
			appendMessage("Started\n");
			long start = SystemClock.elapsedRealtime();
			appendMessage("sdcard: stressing\n");
			mSdcardExerciser.stress();
			appendMessage(String.format("sdcard: done. Took %d ms\n", SystemClock.elapsedRealtime() - start));
			mCpuExerciser.stress();
			appendMessage(String.format("Finished. Took %d ms\n",
					SystemClock.elapsedRealtime() - start));
			mHandler.post(mUpdateButton);
		}
	}
	
}
