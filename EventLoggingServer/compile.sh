#rm *.jar

#cd bin
#jar cvfm test.jar ../MANIFEST_test test/*.class
#mv test.jar ..
#cd ..

#Downlink
javac -d bin src/servers/*.java src/servers/reach/*.java src/common/*.java

cd bin


#for i in Downlink Uplink Collector Version Whoami Bt BtNondft Http UserState
for i in Collector
do
	jar cvfm $i.jar ../manifest/MANIFEST_$i servers/$i*.class  common/*.class
	#mv $i.jar /home/3gtest/3G_servers_2.0/server/$i/$i.jar
done

#Reach start
#for i in Auth_smtp Dns Ftp Https Imap_ssl Imap Netbios Pop_ssl Pop Rpc Secure_imap Sip Smb Smtp_ssl Smtp Snmp
#do
#	jar cvfm $i.jar ../manifest/reach/MANIFEST_$i servers/reach/$i*.class  common/*.class
	#mv $i.jar /home/3gtest/3G_servers_2.0/server/Reach/$i.jar
#done

cd ..
