package com.example.eventlogging;

import java.io.DataOutputStream;
import java.io.IOException;
import java.util.Random;
import java.util.ArrayDeque;
import android.util.Log;

public class ConfigChange {
	private final String TAG = "ConfigChange";
	public static final int DVFS_ON_DUO = 0;
	public static final int DVFS_OFF_DUO = 1;
	public static final int DVFS_ON_SINGLE = 2;
	public static final int DVFS_OFF_SINGLE = 3;
	
	private final String FREQ_GOVERNOR = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor";
	private final String FREQ_SETSPEED = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed";
	private final String CPU_ONLINE = "/sys/devices/system/cpu/cpu1/online";
	
	private ArrayDeque<Double> usageQueue;
	private double sumQueue;
	private double avgUsage;
	
	private ArrayDeque<Integer> configQueue;
	private int [] count;
	
	private Random random;
	
	public ConfigChange(){
		sumQueue = 0;
		avgUsage = 0;
		int i =0;
		count = new int[4];
		for(i=0; i<4; i++){
			count[i]=0;
			}
		random = new Random();
		usageQueue = new ArrayDeque<Double>();
		configQueue = new ArrayDeque<Integer>();
		GainAccess();
		ChangeDVFS(0);
		}
	
	public void GainAccess(){
		try {
			Process process = Runtime.getRuntime().exec("su");
			DataOutputStream os = new DataOutputStream(process.getOutputStream());
			/*os.writeBytes("chmod 777 "+ FREQ_GOVERNOR);
			os.writeBytes("chmod 777 " + FREQ_SETSPEED);
			os.writeBytes("chmod 777 "+ CPU_ONLINE);*/
			os.writeBytes("exit\n");
			os.flush();
			os.close();
			process.waitFor();
		} catch (IOException e) {
			Log.d(TAG,"Cannot gain root");			
			} catch (InterruptedException e) {
			Log.d(TAG,"Got interrupted while waiting for command");
		}
	}
	
	public boolean ShouldChangeConfig(){
		if(avgUsage < 10.0)
			return true;
		else
			return false;
	}
	
	public void updateQueue(double usage){
		if(usageQueue.size()<10){
			usageQueue.add(usage);
			sumQueue += usage;
			avgUsage = sumQueue/usageQueue.size();
		}else{
			double removed = (double) usageQueue.remove();
			sumQueue -= removed;
			usageQueue.add(usage);
			sumQueue += usage;
			avgUsage = sumQueue/usageQueue.size();
		}
	}
	
	public void ChangeDVFS(int dvfs)
	{
		if(dvfs == 1){
			try {
				Process process = Runtime.getRuntime().exec("su");
				DataOutputStream os = new DataOutputStream(process.getOutputStream());
				os.writeBytes("echo interactive > "+FREQ_GOVERNOR + "\n");
				os.writeBytes("exit\n");
				os.flush();
				os.close();
				process.waitFor();
			} catch (IOException e) {
				Log.d(TAG,"Cannot change frequency governor");			
				} catch (InterruptedException e) {
				Log.d(TAG,"Got interrupted while waiting for command");
			}
		}else{//Turn off DVFS
			try {
				Process process = Runtime.getRuntime().exec("su");
				DataOutputStream os = new DataOutputStream(process.getOutputStream());
				os.writeBytes("echo userspace > "+FREQ_GOVERNOR + "\n");
				os.flush();
				os.writeBytes("echo 1200000 > "+FREQ_SETSPEED +"\n");
				os.writeBytes("exit\n");
				os.flush();
				os.close();
				process.waitFor();
			} catch (IOException e) {
				Log.d(TAG,"Cannot change frequency governor");			
				} catch (InterruptedException e) {
				Log.d(TAG,"Got interrupted while waiting for command");
			}
		}
	}
	
	public void ChangeCore(int core){
		if(core == 1){//duo core running
			try {
				Process process = Runtime.getRuntime().exec("su");
				DataOutputStream os = new DataOutputStream(process.getOutputStream());
				os.writeBytes("echo 1 > "+CPU_ONLINE+ "\n");
				os.writeBytes("exit\n");
				os.flush();
				os.close();
				process.waitFor();
			} catch (IOException e) {
				Log.d(TAG,"Cannot make core 1 online");			
				} catch (InterruptedException e) {
				Log.d(TAG,"Got interrupted while waiting for command");
			}
		}else{//single core running
			try {
				Process process = Runtime.getRuntime().exec("su");
				DataOutputStream os = new DataOutputStream(process.getOutputStream());
				os.writeBytes("echo 0 > "+CPU_ONLINE+ "\n");
				os.writeBytes("exit\n");
				os.flush();
				os.close();
				process.waitFor();
			} catch (IOException e) {
				Log.d(TAG,"Cannot make core 1 online");			
				} catch (InterruptedException e) {
				Log.d(TAG,"Got interrupted while waiting for command");
			}
		}
	}
	
	public void SwitchToConfig(int config){
		Log.d(TAG,"Change configures "+ config);
		switch(config){
		case DVFS_ON_DUO:
			ChangeDVFS(1);
			ChangeCore(1);
			Log.d(TAG,"Change to DUO core with DVFS");
			break;
		case DVFS_OFF_DUO:
			ChangeDVFS(0);
			ChangeCore(1);
			Log.d(TAG,"Change to DUO core without DVFS");
			break;
		case DVFS_ON_SINGLE:
			ChangeDVFS(1);
			ChangeCore(0);
			Log.d(TAG,"Change to SINGLE core with DVFS");
			break;
		case DVFS_OFF_SINGLE:
			ChangeDVFS(0);
			ChangeCore(0);
			Log.d(TAG,"Change to SINGLE core without DVFS");
		}
	}
	public int ChangeConfig(){
		int next_config;
		if(configQueue.size() >= 10){
			int i = 0;
			int uniform = 1;
			for(i=0; i<4; i++){
				if(count[i] < 2){
					uniform  = 0;
					break;
				}		
			}
			if(uniform == 0)//Some configs have been skipped
				next_config = i;
			else{
				next_config = random.nextInt(4);
			}
			int removed_config = configQueue.remove();
			count[removed_config] --;
			count[next_config] ++;
			SwitchToConfig(next_config);
		}else{
			next_config = random.nextInt(4);
			count[next_config] ++;
			SwitchToConfig(next_config);
			
		}
		return next_config;
	}
}
