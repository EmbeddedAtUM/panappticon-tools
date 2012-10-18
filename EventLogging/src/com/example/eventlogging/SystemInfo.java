package com.example.eventlogging;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;


import android.util.Log;
import android.os.Process;

public class SystemInfo {
	  private final String TAG = "SystemInfo";
	  
	  private static SystemInfo instance = new SystemInfo();

	  public static SystemInfo getInstance() {
	  	return instance;
	  }
	
	  private Method methodReadProcFile;
	 /* These are stolen from Process.java which hides these constants. */
	  public static final int PROC_SPACE_TERM = (int)' ';
	  public static final int PROC_TAB_TERM = (int)'\t';
	  public static final int PROC_LINE_TERM = (int)'\n';
	  public static final int PROC_COMBINE = 0x100;
	  public static final int PROC_OUT_LONG = 0x2000;
	  public static final int PROC_OUT_STRING = 0x1000;
	  
	  public static final int INDEX_USER_TIME = 0;
	  public static final int INDEX_SYS_TIME = 1;
	  public static final int INDEX_TOTAL_TIME = 2;
	  public static final int INDEX_IO_TIME = 3;
	  
	  
	  
	  private static final int[] PROCESS_TOTAL_STATS_FORMAT = new int[] {
		    PROC_SPACE_TERM,
		    PROC_SPACE_TERM|PROC_OUT_LONG,
		    PROC_SPACE_TERM|PROC_OUT_LONG,
		    PROC_SPACE_TERM|PROC_OUT_LONG,
		    PROC_SPACE_TERM|PROC_OUT_LONG,
		    PROC_SPACE_TERM|PROC_OUT_LONG,
		    PROC_SPACE_TERM|PROC_OUT_LONG,
		    PROC_SPACE_TERM|PROC_OUT_LONG,
		  };
	  
	  public SystemInfo(){
		  try {
		      methodReadProcFile = Process.class.getMethod("readProcFile", String.class,
		          int[].class, String[].class, long[].class, float[].class);
		    } catch(NoSuchMethodException e) {
		      Log.w(TAG, "Could not access readProcFile method");
		    }
	  }
	  /* times should contain seven elements.  times[INDEX_USER_TIME] will be filled
	   * with the total user time, times[INDEX_SYS_TIME] will be filled
	   * with the total sys time, and times[INDEX_TOTAL_TIME] will have the total
	   * time (including idle cycles).  Returns true on success.
	   */
	  public boolean getUsrSysTotalTime(long[] times) {
	    if(methodReadProcFile == null) return false;
	    try {
	      if((Boolean)methodReadProcFile.invoke(
	          null, "/proc/stat",
	          PROCESS_TOTAL_STATS_FORMAT, null, times, null)) {
	        long usr = times[1] + times[2];
	        long sys = times[3] + times[6] + times[7];
	        long total = usr + sys + times[4] + times[5];
	        long io = times[5];
	        times[INDEX_USER_TIME] = usr;
	        times[INDEX_SYS_TIME] = sys;
	        times[INDEX_TOTAL_TIME] = total;
	        times[INDEX_IO_TIME] = io;
	        return true;
	      }
	    } catch(IllegalAccessException e) {
	      Log.w(TAG, "Failed to get total cpu usage");
	    } catch(InvocationTargetException e) {
	      Log.w(TAG, "Exception thrown while getting total cpu usage");
	    }
	    return false;
	  }
	
}
