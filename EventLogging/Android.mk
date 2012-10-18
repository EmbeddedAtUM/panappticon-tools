LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE_TAGS := optional

LOCAL_STATIC_JAVA_LIBRARIES := \
        android-support-v13 \
        android-support-v4 \

LOCAL_SRC_FILES := \
        $(call all-java-files-under, src) 

LOCAL_PACKAGE_NAME := EventLogging

LOCAL_PROGUARD_FLAG_FILES := proguard.flags

#LOCAL_EMMA_COVERAGE_FILTER := *,-com.android.common.*


include $(BUILD_PACKAGE)

