package org.davidbild.eventlogging.sdcardstressmark;

import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import android.os.SystemClock;
import android.util.Log;

public class DvfsStressmarkRunner {
	private static String TAG = "DvfsStressmark";

	private boolean fixedDuration;

	private int cycles;
	private int sleep;

	private double period;
	private double dutyCycle;
	private int count;

	private MessageDigest digest;
	private byte[] data;

	public DvfsStressmarkRunner(double period, double dutyCycle, int count) {
		this.period = period;
		this.dutyCycle = dutyCycle;
		this.count = count;
		this.fixedDuration = true;
		setupWork();
	}

	public DvfsStressmarkRunner(int cycles, int sleep, int count) {
		this.fixedDuration = false;
		this.cycles = cycles;
		this.sleep = sleep;
		this.count = count;
		setupWork();
	}

	public void stress() {
		warmUp();

		if (fixedDuration)
			fixedDurationStress();
		else
			fixedWorkStress();
	}

	public void warmUp() {
		long start = SystemClock.elapsedRealtime();
		do {
			doWork();
		} while (SystemClock.elapsedRealtime() - start < 45);
	}

	public void fixedWorkStress() {
		for (int i = 0; i < count; ++i) {

			for (int j = 0; j < cycles; ++j) {
				doWork();
			}

			try {
				Thread.sleep(sleep);
			} catch (InterruptedException e) {
				throw new RuntimeException("Should not have been interrupted",
						e);
			}
		}
	}

	public void fixedDurationStress() {
		long active = (long) (dutyCycle * (double) period);
		long inactive = (long) ((1 - dutyCycle) * (double) period);

		for (int i = 0; i < count; ++i) {
			long start = SystemClock.elapsedRealtime();
			int cnt = 0;
			do {
				cnt++;
				doWork();
			} while (SystemClock.elapsedRealtime() - start < active);
			Log.v(TAG,
					String.format("Did %d loops in %d ms", cnt,
							SystemClock.elapsedRealtime() - start));

			try {
				Thread.sleep(inactive);
			} catch (InterruptedException e) {
				throw new RuntimeException("Should not have been interrupted",
						e);
			}
		}
	}

	private void setupWork() {
		data = new byte[1000 * 4];
		ByteBuffer buff = ByteBuffer.wrap(data);
		for (int i = 0; i < 1000; ++i) {
			buff.putInt(i);
		}

		try {
			digest = MessageDigest.getInstance("SHA-1");
			digest.reset();
		} catch (NoSuchAlgorithmException e) {
			// Should never happen
			throw new RuntimeException(e);
		}
	}

	private void doWork() {
		digest.update(data);
	}

};
