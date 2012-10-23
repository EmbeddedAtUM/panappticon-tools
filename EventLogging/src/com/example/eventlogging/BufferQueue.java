package com.example.eventlogging;

import java.nio.ByteBuffer;
import java.util.Queue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.EventLogging;

import android.content.Context;
import android.util.Log;

public class BufferQueue {
	private static final String TAG = "BufferQueue";
	private final int BUFFER_SIZE = 1 * 1024*1024;//2M
	
	public static final int USER_MODE = 0;
	public  static final int KERNEL_MODE = 1;
	
	private LinkedBlockingQueue<UnitBuffer> [] mQueues;
	
	private UnitBuffer mUserUnitBuffer;
	private int mQueueIndex = 0;
	private int mCurQueueLen = 0;
	
	private LogUploader mUploader;
	
	private static BufferQueue mBufferQueue = new BufferQueue();
	
	public static BufferQueue getInstance(){
		return mBufferQueue;
	}
	
	private BufferQueue(){
		mQueues = new LinkedBlockingQueue[2];
		mQueues[0] = new LinkedBlockingQueue<UnitBuffer>();
		mQueues[1] = new LinkedBlockingQueue<UnitBuffer>();
		ByteBuffer newByteBuffer = ByteBuffer.allocate(BUFFER_SIZE);
		mUserUnitBuffer = new UnitBuffer(newByteBuffer, USER_MODE, 0);
	}
	
	public void initialize(Context context){
		mUploader = new LogUploader(context);
	}
	
	public synchronized void WriteToBuffer(byte [] input, int length, int mode){
		switch(mode){	
			case USER_MODE:
				Log.d(TAG,"Write to user buffer "+ length + " total:"+ mUserUnitBuffer.uBufferLen + " " + mUserUnitBuffer.uBuffer.remaining());
				//if((length+mUserUnitBuffer.uBufferLen)> BUFFER_SIZE)//the unit buffer is full
				if(length > mUserUnitBuffer.uBuffer.remaining())
				{	
					Log.d(TAG,"User buffer bigger than size, attach it");
					LinkCurBuffer(mUserUnitBuffer);
					ByteBuffer newByteBuffer = ByteBuffer.allocate(BUFFER_SIZE);
					mUserUnitBuffer = new UnitBuffer(newByteBuffer, USER_MODE, 0);
				}
				mUserUnitBuffer.uBuffer.put(input, 0, length);
				mUserUnitBuffer.uBufferLen += length;
				break;
			case KERNEL_MODE:
				ByteBuffer tmpBuffer = ByteBuffer.wrap(input);
				UnitBuffer KernelUnitBuffer = new UnitBuffer(tmpBuffer, KERNEL_MODE, length);
				LinkCurBuffer(KernelUnitBuffer);
		}
	}
	
	private void LinkCurBuffer(UnitBuffer unitBuffer){
		try {
				mQueues[mQueueIndex].put(unitBuffer);
				mCurQueueLen += unitBuffer.uBufferLen;
				Log.d(TAG, "BufferQueue attach new unit buffer " + unitBuffer.uBufferLen + " "+ unitBuffer.uBufferMode+ " total: "+ mCurQueueLen);
				if(mCurQueueLen > mUploader.UPLOAD_THRESHOLD)
				{
					Log.d(TAG,"Current buffer ready to sent "+ mCurQueueLen);
					export(mQueueIndex);
					mQueueIndex = 1- mQueueIndex;
					mCurQueueLen = 0;
				}
		} catch (InterruptedException e) {
			Log.e(TAG,"Failed to attach new buffer");
			e.printStackTrace();
		}
	}

	public void export(int index){//Upload the current queue when Wifi available, otherwise write to file
		EventLogging eventlogging = EventLogging.getInstance();
		eventlogging.onPauseExport();
		LinkedBlockingQueue<UnitBuffer> target = mQueues[index];
		UnitBuffer tmp = target.poll();
		while(tmp!=null){
			Log.d(TAG,"About to upload "+ tmp.uBufferLen);
			mUploader.upload(tmp.uBuffer.array(), tmp.uBufferLen, tmp.uBufferMode);
			tmp = target.poll();
		}
	}
	
	private class UnitBuffer{
		int uBufferLen;
		int uBufferMode;
		ByteBuffer uBuffer;
		
		public UnitBuffer(ByteBuffer buffer, int mode, int len){
			uBuffer = buffer;
			uBufferMode = mode;
			uBufferLen = len;
		}
		
	}
}
