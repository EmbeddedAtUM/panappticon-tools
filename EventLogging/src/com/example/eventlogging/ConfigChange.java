package com.example.eventlogging;

import java.io.DataOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Random;
import java.util.ArrayDeque;
import java.lang.Process;
import java.util.EventLogging;

import android.util.Log;

public class ConfigChange extends Thread{
	private final String TAG = "ConfigChange";
	private final int CHECKING_INTERVAL = 10* 60 * 1000; // 10 minutes
	
	public static final int DVFS_ON_DUO = 0;
	public static final int DVFS_OFF_DUO = 1;
	public static final int DVFS_ON_SINGLE = 2;
	public static final int DVFS_OFF_SINGLE = 3;
	
	private static final int NUM_SAMPLE = 10;
	
	private final String FREQ_GOVERNOR = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor";
	private final String FREQ_SETSPEED = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed";
	private final String CPU_ONLINE = "/sys/devices/system/cpu/cpu1/online";
	
	
	private ArrayDeque<Integer> configQueue;
	private int [] count;
	
	private Random random;
	
	private boolean active;
	
	private long [] statsBuf;
	private long mTotal;
	private long mUser;
	private long mSystem;
	
	public ConfigChange() {
		int i =0;
		count = new int[4];
		for(i=0; i<4; i++){
			count[i]=0;
			}
		random = new Random();
		configQueue = new ArrayDeque();
		GainAccess();
		ChangeDVFS(0);
		active = true;
		
		statsBuf = new long[8];
		mTotal = 0;
		mUser = 0;
		mSystem = 0;
		}
	
	@Override
	public void run() {
		while((active) && (!interrupted()))
		{
			if(ShouldChangeConfig())
			{
				Log.i(TAG,"Should change configuration");
				ChangeConfig();
			}
			try {
				sleep(CHECKING_INTERVAL);
			} catch (InterruptedException e) {
				break;
			}		
		}
	}	
	
	public void terminate(){
		active = false;
		interrupt();
	}
	
	public void GainAccess(){
		try {
			Process process = Runtime.getRuntime().exec("su");
			DataOutputStream os = new DataOutputStream(process.getOutputStream());
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
	/* 
	 * Monitor the average utilization for NUM_SAMPLE seconds and then determine
	 */	
	public boolean ShouldChangeConfig(){
		fastReadStats();
		double avgUsage = 0;
		for(int i=0; i< NUM_SAMPLE; i++)
		{
			try {
				sleep(1000);
			 } catch (InterruptedException e) {
				// The thread got terminated
				return false;
			}
		}
		avgUsage = fastReadStats();
		if(avgUsage < 10.0)
			return true;
		else
			return false;
	}
	
	private void ExecuteCommand(String cmd)
	{
		try {
			Process process = Runtime.getRuntime().exec("su");
			DataOutputStream os = new DataOutputStream(process.getOutputStream());
			os.writeBytes(cmd + "\n");
			os.writeBytes("exit\n");
			os.flush();
			os.close();
			process.waitFor();
		} catch (IOException e) {
			Log.d(TAG,"Cannot execute command "+ cmd);			
			} catch (InterruptedException e) {
			Log.d(TAG,"Got interrupted while waiting for command");
		}
	}
	
	public void ChangeDVFS(int dvfs)
	{
		if(dvfs == 1){// Turn on DVFS
			ExecuteCommand("echo interactive > "+FREQ_GOVERNOR );
		}else{//Turn off DVFS
			ExecuteCommand("echo userspace > "+FREQ_GOVERNOR + "\n" + "echo 1200000 > "+FREQ_SETSPEED);
		}
	}
	
	public void ChangeCore(int core){
		if(core == 1){//duo core running
			ExecuteCommand("echo 1 > "+CPU_ONLINE);
		}else{//single core running
			ExecuteCommand("echo 0 > "+CPU_ONLINE);
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
		EventLogging eventlogging = EventLogging.getInstance();
		eventlogging.addEvent(EventLogging.EVENT_SWITCH_CONFIG, next_config);
		return next_config;
	}
	public double fastReadStats(){
		SystemInfo sysInfo = SystemInfo.getInstance();
		
		if(!sysInfo.getUsrSysTotalTime(statsBuf)){
			Log.d(TAG,"Failed to read cpu times");
			return 0.0;
		}
		long usrTime = statsBuf[SystemInfo.INDEX_USER_TIME];
		long sysTime = statsBuf[SystemInfo.INDEX_SYS_TIME];
		long totalTime = statsBuf[SystemInfo.INDEX_TOTAL_TIME];
		
		double usr_sys_perc = updateStats(usrTime, sysTime, totalTime);
		Log.d(TAG,"User stats: "+ usrTime + " "+ sysTime + " "+ totalTime+ " "+ usr_sys_perc);
		return usr_sys_perc;	
	}
	
	private double updateStats(long user, long system, long total)
	{
		double user_sys_perc = 0.0;
		double user_perc = 0.0;
		double sys_perc = 0.0;
		if (mTotal != 0 || total >= mTotal) {
			long duser = user - mUser;
			long dsystem = system - mSystem;
			long dtotal = total - mTotal;
			user_sys_perc = (double)(duser+dsystem)*100.0/dtotal;
			user_perc = (double)(duser)*100.0/dtotal;
			sys_perc = (double)(dsystem)*100.0/dtotal;
		} 
		mUser = user;
		mSystem = system;
		mTotal = total;	
		return user_sys_perc;
	}
}
