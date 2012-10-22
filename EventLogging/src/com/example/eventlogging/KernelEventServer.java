package com.example.eventlogging;


import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Array;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import android.content.Context;
import android.util.Log;

/**
 * A utility class for accessing the kernel event logging. Provides methods for
 * reading the event logs and flushing the log buffers. Call {{@link #start()}
 * to begin retrieving the logs and {@link #stop} to quit. Call {@link #queue()}
 * to retrieve the queue of event log buffers.
 * 
 * @author David R. Bild modified by Lide Zhang
 * 
 */
public class KernelEventServer extends Thread{
	private static final String TAG = "KernelEventLog";

	/**
	 * The file exposing the kernel event log
	 */
	private static final String PROC_FILE = "/proc/event_logging";

	private volatile boolean running;

	private Thread thread;
	
	private BufferQueue mBufferQueue;
	

	public KernelEventServer(Context context) {
		running = false;
		mBufferQueue = BufferQueue.getInstance();
		running = true;
	}


	/**
	 * Stops retrieving logs from the kernel.
	 */
	public void terminate() {
		running = false;
		interrupt();
	}

	/**
	 * Retrieves the queue of event log buffers
	 * 
	 * @return the queue of event log buffers
	 */
/*	public BlockingQueue<ByteBuffer> queue() {
		return queue;
	}*/

	private void restartRead() {
		FileOutputStream fwriter = null;
		Log.d(TAG, "Kernel reset read");
		try {
			fwriter = new FileOutputStream(PROC_FILE);
			fwriter.write("restart".getBytes());
			fwriter.close();
		} catch (FileNotFoundException e)  {
			Log.e(TAG, "Failed to open proc file", e);
		} catch (IOException e) {
			Log.e(TAG, "Failed to write to proc file", e);
		}
	}

	public void run() {
		FileInputStream freader = null;
		Log.d("Lide", "Kernel server reads");

		restartRead();

		try {
			freader = new FileInputStream(PROC_FILE);
			Log.d("Lide", "Kernel server starts read");
			while (running) {
				byte[] sizebytes = new byte[4];
				int sz = 0;
				while(sz < 4){
					sz += freader.read(sizebytes,sz,4-sz);
					Log.d("Lide","read bytes "+ sz);
				}
				int size = ByteBuffer.wrap(sizebytes)
						.order(ByteOrder.LITTLE_ENDIAN).getInt();
				Log.d("Lide", "Kernel server starts read "+size);
				byte[] buffer = new byte[size + 4];
				System.arraycopy(sizebytes, 0, buffer, 0, 4);
				int readLen = size;
				int pos = 4;
				while(readLen > 0){
					sz = freader.read(buffer, pos, readLen);
					pos += sz;
					readLen -= sz;
				}
				mBufferQueue.WriteToBuffer(buffer, size+4, BufferQueue.KERNEL_MODE);
			}
		} catch (FileNotFoundException e) {
			Log.e(TAG, "Failed to open proc file", e);
		} catch (IOException e) {
			Log.e(TAG, "Failed while reading proc file", e);
		} finally {
			if (freader != null)
				try {
					freader.close();
				} catch (IOException e) {
					Log.w(TAG, "Error while closing proc file", e);
				}
		}
	}

	/**
	 * Flushes the kernel event log buffers.
	 * 
	 * @throws IOException
	 *             if the buffers could not be flushed
	 */
	public void flush() throws IOException {
		FileWriter fstream = new FileWriter(PROC_FILE);
		try {
			fstream.write("1");
		} finally {
			fstream.close();
		}
	}

}