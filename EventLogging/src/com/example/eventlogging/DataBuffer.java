package com.example.eventlogging;

import java.nio.ByteBuffer;

import android.content.Context;
import android.util.Log;


public class DataBuffer {
	private final String TAG = "DataBuffer";

	private final int BUFFER_SIZE = 100*1024;
	private final boolean DEBUG_SERVER = true;
	
	private ByteBuffer [] mByteBuffers;
	private int [] mLength;
	private int mBuffer = 0;
	
	private LogUploader mUploader;
	
	
	private static DataBuffer myBuffer = new DataBuffer();
	
	public static DataBuffer getInstance(){
		return myBuffer;
	}
	
	public DataBuffer(){
		mByteBuffers = new ByteBuffer [2];
		mByteBuffers[0] = ByteBuffer.allocate(BUFFER_SIZE);
		mByteBuffers[1] = ByteBuffer.allocate(BUFFER_SIZE);
		mLength = new int [2];
		mLength[0] = 0;
		mLength[1] = 0;
	}
	
	public void initialize(Context context){
		mUploader = new LogUploader(context);
	}
	
	public synchronized void WriteToBuffer(byte [] input, int length){
		Log.d(TAG,"Writer to buffer "+length+":"+mLength[mBuffer] + "order "+mByteBuffers[mBuffer].order());
		/* When one buffer gets full, export the buffer and switch to the other buffer*/
		if(length + mLength[mBuffer] > BUFFER_SIZE){
			SwitchBuffer();
		}
		try{
			mByteBuffers[mBuffer].put(input, 0, length);
		}catch(Exception e){
			e.printStackTrace();
		}
		mLength[mBuffer] += length;
		if(DEBUG_SERVER)
			SwitchBuffer();
		
	}
	
	private void SwitchBuffer(){
		export_buffer(mBuffer);
		mBuffer = 1 - mBuffer;
	
	}
	
	/* Export the buffer to file*/
	/*public void export_buffer(int cur_buffer){
		Writer writer = Writer.getInstance(); 	
		writer.writeBytes(mByteBuffers[cur_buffer].array());
		//writer.writeString(mByteBuffers[cur_buffer].array(), mLength[cur_buffer]);
	}*/
	
	
	/* Export the buffer to Internet*/
	public void export_buffer(int cur_buffer){
		mUploader.upload(mByteBuffers[cur_buffer].array(), mLength[cur_buffer]);
		mByteBuffers[cur_buffer].rewind();
		mLength[cur_buffer] = 0;
	}

	
}
