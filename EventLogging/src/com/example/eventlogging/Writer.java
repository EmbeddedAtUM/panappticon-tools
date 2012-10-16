package com.example.eventlogging;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

import android.content.Context;
import android.util.Log;


public class Writer {
	private static String TAG = "LogUploader";
	private static Writer mWriter = new Writer();
	
	private FileOutputStream fout;
	public static Writer getInstance(){
		return mWriter;
	}
	
	
	public void initialize(Context context){
		File UserDirectory = new File("/sdcard/user/");
		UserDirectory.mkdir();
		File KernelDirectory = new File("/sdcard/kernel/");
		KernelDirectory.mkdir();
	}
	
	public void writeToFile(long runId, byte [] buffer, int len, int mode)
	{
		String filename = "";
		if(mode == BufferQueue.KERNEL_MODE)
			filename = filename + "kernel/";
		else
			filename = filename+ "user/";
		filename = filename+ runId;
		Log.d(TAG,"Write to file "+ filename);
		try{
			fout = new FileOutputStream("/sdcard/"+filename);
			//fout = mContext.openFileOutput(filename, Context.MODE_WORLD_READABLE);
			fout.write(buffer,0,len);
			fout.flush();
			fout.close();
		}catch(IOException ioe){
			
		}
	}
}
