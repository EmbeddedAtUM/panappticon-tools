package com.example.eventlogging;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

import android.content.Context;
import android.util.Log;

public class SendFiles implements Runnable{
	private final String kernel_path = "/sdcard/kernel/";
	private final String user_path = "/sdcard/user/";
	
	private LogUploader mUploader;
	public SendFiles(Context context){
		mUploader = new LogUploader(context);
	}
	@Override
	public void run() {
		if(mUploader.connectionAvailable() == mUploader.CONNECTION_WIFI){
			ReadAndSend(kernel_path, BufferQueue.KERNEL_MODE);
			ReadAndSend(user_path, BufferQueue.USER_MODE);
		}
	}
	
	private void ReadAndSend(String file_path, int mode){
		File[] files = new File(file_path).listFiles();
		for(File file: files){
			Log.d("ServerService","filename  is "+ file.getName()+file.length());
			byte [] file_buffer = new byte[(int)file.length()];
			try {
				BufferedInputStream in= new BufferedInputStream(new FileInputStream(file));
				int sz = in.read(file_buffer, 0, (int) file.length());
				if(sz == -1)
					continue;
				mUploader.upload(file_buffer, (int)file.length(), mode, Long.valueOf(file.getName()));
				in.close();
				file.delete();
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}		
		}
	}

}
