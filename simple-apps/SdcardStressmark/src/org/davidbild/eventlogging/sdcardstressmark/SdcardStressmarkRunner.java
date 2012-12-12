package org.davidbild.eventlogging.sdcardstressmark;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Random;

import android.content.Context;

public class SdcardStressmarkRunner {

	private static final int SIZE = 16777216;

	private static final int SEED = 1;

	private byte[] data;

	private File cacheDir;

	public SdcardStressmarkRunner(Context context) {
		this.cacheDir = context.getExternalCacheDir();
		initData();
	}

	private void initData() {
		data = new byte[SIZE];
		new Random(SEED).nextBytes(data);
	}

	public void stress() {
		try {
			File file = File.createTempFile("stress", "tmp", cacheDir);
			FileOutputStream stream = new FileOutputStream(file);
			stream.write(data);
		} catch (IOException e) {
			throw new RuntimeException("Failed to stress sdcard.", e);
		}
	}

}
