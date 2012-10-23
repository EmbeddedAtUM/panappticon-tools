#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct event{
	long timestamp;
	int event_type;
	int pid;
	int qid;
	int mid; 
}event;
int main(int argc, char *argv[])
{
	event* buffer;

	if (argc != 2)
	{	
		printf("Usage: ./parse filename\n");
		return -1;
	}
	
	char filename[256];
	strcpy(filename, argv[1]);
	FILE *input_file = fopen(filename, "rb");
	
	fseek(input_file, 0, SEEK_END);
	unsigned long fileLen = ftell(input_file);
	fseek(input_file, 0, SEEK_SET);
	buffer = (event *)malloc(fileLen);
	fread(buffer, fileLen, 1, input_file);
	fclose(input_file); 
	int i = 0;
	int first_timestamp = 0;
	//printf("size of event is %d\n", sizeof(event));	
	for(i=0; i< (fileLen)/sizeof(event); i++)
	{
		printf("%ld\t%d\t%d\t%d\t%d\n", buffer[i].timestamp, buffer[i].pid, buffer[i].event_type, buffer[i].qid, buffer[i].mid);
	}
	return 0;
}

