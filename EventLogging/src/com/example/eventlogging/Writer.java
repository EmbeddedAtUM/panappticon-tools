package com.example.eventlogging;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

import android.content.Context;
import android.util.Log;


public class Writer {
	private String filename = "user_trace";
	private static Writer mWriter = new Writer();
	
	private FileOutputStream fout;
	private OutputStreamWriter osw; 
	
	public static Writer getInstance(){
		return mWriter;
	}
	
	
	public void initialize(Context context){
		try{
			 fout = context.openFileOutput(filename, Context.MODE_WORLD_READABLE);
			 osw = new OutputStreamWriter (fout);
		}catch(IOException ioe){
			ioe.printStackTrace();
		}
	}
	
	public void writeBytes(byte [] buffer){
		try {
			fout.write(buffer);
			fout.flush();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void writeString(byte [] buffer, int len){
		Log.d("Server", "Write to file with string "+ len);
		try {
			ByteBuffer tmp = ByteBuffer.wrap(buffer);
			tmp.order(ByteOrder.LITTLE_ENDIAN);
			for(int i=0; i< len/24; i++)
				osw.write(tmp.getLong()+":"+tmp.getInt()+":"+tmp.getInt()+":"+tmp.getInt()+":"+tmp.getInt()+" ");
			osw.flush();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void close(){
		try{
			osw.flush();
			osw.close();
		}catch (IOException e) {
			e.printStackTrace();
		}
		
	}

}
