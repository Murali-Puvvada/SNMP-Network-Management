#!/usr/bin/python3
#Shebang Notation

#Importing system,time and easysnmp module
import sys
import time
import easysnmp 
from easysnmp import Session,snmp_get, snmp_walk

#Getting agent details using argv
inputs=sys.argv[1].split(":")
agent_ip = inputs[0]
agent_port = inputs[1]
agent_community = inputs[2]

#Getting sample details using argv
samplefreq = float(sys.argv[2]) 
freqtime = 1/samplefreq
samplesize = int(sys.argv[3])

#Created empty list for OID
OID = []
#Added sysUpTime OID
OID.insert(0, '1.3.6.1.2.1.1.3.0')
prevTime=0
prevOID = []
endOID = []
uptimeOID=[]
specOID=[]
gauOID2=[]
#Added OIDs to list
OID=OID+sys.argv[4:]

timer=""

def snmpfunc(number):
	global prevOID, currTime, timer, gauOID2, prevTime, sleepTime
# Creating SNMP session to handle all requests from easysnmp
	session=Session(hostname=agent_ip,remote_port=agent_port,community='public',version=2,timeout=1,retries=1)
#Retrieving OIDs using easysnmp get request
	resOID = session.get(OID)
	endOID = []
	gauOID1=[]
	#print(resOID)
		
	for j in range(0,len(resOID)):
		if resOID[j].value!='NOSUCHOBJECT' and resOID[j].value!='NOSUCHINSTANCE' and resOID[j].snmp_type!=None:
			if resOID[j].snmp_type == "GAUGE":
				gauOID1.append(int(resOID[j].value))
			elif resOID[j].snmp_type == "OCTETSTR":
				specOID.append(str(resOID[j].value))
			elif resOID[j].snmp_type == "TICKS":
				uptimeOID.append((int(resOID[j].value))/100)
				prevTime=uptimeOID[-1]
				#print(uptimeOID)
			else:
				endOID.append(int(resOID[j].value))
			#print(number)
			#print(j)
			#print(endOID)
			#print(prevOID)

#If we get OID response as no object,instance we are not adding into the endOID       
			if resOID[j].snmp_type == 'COUNTER' or resOID[j].snmp_type=="COUNTER32" or resOID[j].snmp_type=="COUNTER64":

				if number!=0 and len(prevOID)>0:
					#print(j)
					subOID = endOID[-1] - prevOID[len(endOID)-1]
					#print(subOID)
					#subTime = float(prevTime - currTime)
					subTime = prevTime - currTime
					#print(subTime)
					#print(str(subTime) + "|"+str(subOID))
					OIDrate = subOID/subTime
					#print(OIDrate)
			
					if OIDrate < 0:
						if resOID[j].snmp_type == 'COUNTER32':
							try:
								if timer == str(prevTime):
									subOID = subOID+2**32 # Wrap Around
									print( str(round(subOID/subTime)),end="|")
								else:
									print(str(time.time()) + "|"+ str(round(subOID/subTime)),end="|")
									timer=str(prevTime)
							except:
								print(str(time.time()) + "|"+ str(round(subOID/subTime)),end="|")
								timer=str(prevTime)					
						elif resOID[j].snmp_type =='COUNTER64':
							try:
								if timer == str(prevTime):
									subOID = subOID+2**64
									print(str(round(subOID/subTime)),end="|")
								else:
									subOID = subOID + 2**64
									print(str(time.time()) +"|"+ str(round(subOID/subTime)),end="|")
									timer=str(prevTime)		
							except:
								print(str(time.time()) +"|"+ str(round(OIDrate)),end="|")
								timer=str(prevTime)
						else:
							break
						
					else:
						try:
							if timer == str(prevTime):
								print(str(round(OIDrate)),end="|")	
							else:
								print(str(time.time()) +"|"+ str(round(OIDrate)),end="|")
								timer=str(prevTime)		
						except:
							print(str(time.time()) +"|"+ str(round(OIDrate))+"|")
							timer=str(prevTime)

			
	prevOID = endOID
	gauOID2 = gauOID1
	currTime = prevTime

if samplesize == -1:
#Running Cont. until interrupted
	number = 0
	prevOID = []
	while True:
		startTime = (time.time())
#Getting time using inbuilt python time module. 
		snmpfunc()
		endTime=(time.time())
		number = number +1
		time.sleep(abs(freqtime - endTime + startTime))
else:
#Running for samples between 0 and samplesize
	prevOID = []
	for number in range(0, samplesize+1):
		startTime = (time.time())
		if len(uptimeOID)>1 and uptimeOID[-2]>uptimeOID[-1] and number!=0:
			print("SNMP agent restart") #Restart Problem
			break
		snmpfunc(number)
		if number!=0:
			print(end="\n")
		endTime = (time.time())
		#print(endTime-startTime)
		if endTime - startTime- freqtime > 0: #Sleep for Additional Time if sample gets skipped
			time.sleep(abs(freqtime - abs(endTime - startTime - freqtime)))
		else:
			time.sleep(abs(endTime - startTime -freqtime))                                    
					   
	

