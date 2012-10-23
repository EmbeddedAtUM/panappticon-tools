#include <jni.h>
#include <sys/time.h>


jlong Java_com_example_eventlogging_ServerService_getCurrentMicroSeconds(JNIEnv* env,
                                                  jobject thiz )
{
	struct timeval time1;
	gettimeofday(&time1, NULL);
	long long time_micro_seconds = (long long)time1.tv_sec*1000000 + (long long)time1.tv_usec;
	return time_micro_seconds;
}
