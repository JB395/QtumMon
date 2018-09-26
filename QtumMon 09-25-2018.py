version = "09/25/2018"
'''
QtumMon.py (QM)

Copyright (c) 2018 Jackson Belove
Beta software, use at your own risk
MIT License, free, open software for the Qtum Community

A program to monitor the Qtumd application, send emails and log activity.
QM uses qtum-cli to send RPC queries to the qtumd server application
to identify staking events, and log various activities of the application.
QM sends a query to check for a new block approximately every 4 seconds.
QM will require qtumd to be running and staking enabled (decrypted for
staking), or will stay in an error loop until these two conditions are met.

To run with Python 2.7 edit all the print statements marked by "#PY3" and "#PY2"
(about 30 lines). To run in Python 2.7 comment out all the print functions
marked "#PY3" and uncomment out all the adjacent print statements marked "#PY2".

A note on the terminology for "stake" and "staking". Strictly speaking, the
"stake" is the quantity of QTUM that your wallet selects to "send" to the 
blockchain when your wallet is randomly chosen to receive a block
reward. Your wallet will choose one or more UTXOs (previous discrete transactions
received by the wallet) to commit to the stake. This amount of QTUM is "staked"
for 501 blocks, and is subtracted from your wallet's ongoing
staking weight for the 501 block interval. At the end of 501 blocks, the stake
amount is reenabled, and the stake ends.

The wallet can be "staking" and decrypted for "staking", but there is only a
"stake" defined during the block reward period. Just because the wallet is
staking doesn't mean it currently has a stake. In the code and comments below,
"stake" refers to the quantity of QTUM "staked" during the block reward period,
and "staking" refers to the capability of the wallet to be chosen for 
a block reward.

Any examples that reference Skynet are idential for Mainnet Ignition.

To Add
Adjust to a whole second in delayBlockWaiting
Have send_email() return a string of the actual email sent (or not if during
    a do not disturb period) so that the display is correct
Better recovery for loss of network connection (alerts on low connections now)    

Revisions

09/25/2018 Removed new network weight
09/20/2018 Changed getinfo to -getinfo for v0.16.01
05/28/2018 Fixed dataLen bug
01/29/2018 Fixed sendmail, comment cleanup, condensed display
01/28/2018 Removed alert on missed block
12/25/2017 Added New Network Weight
12/23/2017 Removed unix time from display
10/27/2017 commented out immature
10/23/2017 adding secondsMovingAverage to catch 16 second cycle
10/13/2017 adding timing sequence string, for occasional missed block
10/12/2017 timer() based pacing for new block wating loop and Day/Hour waiting loop
10/09/2017 Bug fix, detect new stake
10/05/2017 Queued messages during doNotDisturb times
10/03/2017 Changed waiting loop to 3..6 seconds variable
09/30/2017 Added comments to run in Python 2 or 3
09/29/2017 Added doNotDisturb[], removed Windows functions
09/28/2017 Print formatting with commas
09/27/2017 Read config file on startup
09/27/2017 Adding check for staking turned on
09/26/2017 Using getblocknumber every 6 seconds for pacing
09/26/2017 Added functions for parsing numbers and letters
09/25/2017 Added multi (overlapping) reward alerts
09/24/2017 Adding logging .csv file to current directory
09/22/2017 All new (i.e., sections copied from my previous scripts)

Block reward sequence from Skynet (testnet) on September 22, 2017
Note the two alert points (when an email would be sent)

Overlapping reward periods would show up as a stake increase
while there was already a stake in place. In the example below,
if the stake went from 307.6 to 724.8 (not shown), this will generate
a "MULTI" alert.

Stake	Block	Relative	
   0    26476		
   0    26477		
 307.6  26478  	  1     Alert REWARD, 1st 0.4 placeholder payment received
 307.6  26479     2	
        <snip>
 307.6  26976  	499	
 307.6  26977   500	
   0    26978   501     Alert RETURNED, a stake has been returned
   0.4  26979   502     Additional payments received
   0.8  26980   503	
   1.2  26981   504	
   1.6  26982   505	
   2.0  26983   506	
   2.4  26984   507	
   2.8  26985   508	
   3.2  26986   509	
   3.6  26987   510     All payments collected, but need to mature
   3.6  26988   511
        <snip>
   3.6  27478  1001
   3.2  27479  1002
   2.8  27480  1003
   2.4  27481  1004
   2.0  27483  1005
   1.6  27484  1006
   1.2  27485  1007
   0.8  27486  1008
   0.4  27487  1009    
   0.0  27488  1010    All payments matured

Logging

A log is written as comma separated values (.csv) for easy importing into Excel.
The log filename is changed daily at 0000 UTC, and has the name QM_Log_DD_MMM_YYYY.csv.
The first column of the log file has these reference numbers:

000 Startup and system messages
100 New block received
200 End of the day
300 
400 Block reward, staking actions
500 
600
700
800 Missed block (commented out)
900 Errors

Example
000,Program,start,or,restart,version,10/09/2017
000,Logging,start,_0247,hours,GMT,11_Oct2017
000,unix time, date time, balance, stake, block, my weight, net weight, connections, staking, expectedHours, secondsLastBlock
100,1507690092,2017 10 11 10:48:12,000000.2,000000.0,24577, 00000.0,006918989,000000.2,8,  yes ,0.0,47
100,1507690214,2017 10 11 10:50:14,000000.2,000000.0,24578, 00000.0,006955841,000000.2,8,  yes ,0.0,121
100,1507690230,2017 10 11 19:50:30,000000.2,000000.0,24579, 00000.0,006992693,000000.2,8,  yes ,0.0,15

Path and folders
qtumd and QM do not require any path setup. These files should be located
in the same directory/folder, and both qtumd and QM run from that directory.
QM will write the log files to that same directory.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

Program Summary

function send_email()
    send if doNotDisturb = False, send queued messages
    else queue the message to send later

fuctions parse_number(), parse_alphanum() and parse_logical()

read configuration file
Initialize log file
make sure qtumd is running
    if not, send alert and wait for qtumd to start

main program loop
    qtum-cli -getinfo 
    qtum-cli getstakinginfo 
    detect new block reward - single or overlapping (multi)
    make sure qtumd is staking 
        if not, send alert and wait for staking to be enabled
    format all the data
    send out alert if found:
        new block reward - single
        new block reward - multiple
        stake returned
        blocks getting stale (no new block in 30 minutes)
    send an hourly status email
        send queued messages if noNotDisturb == False
    for a new block
        log it
        check for a skipped block (commented out)
    wait here, 4 seconds from last block        
    new block waiting loop
        qtum-cli -getinfo
        if new block, exit new block waiting loop
        Check for stale blocks
        Date and Hours waiting loop, after a new block wait 4, 8, 12... seconds
            wait 0.3 second
            check the time, if a new day (UTC)
                open new log file
            check the time, if xx:59:56 set to do hourly email and exit new block waiting loop

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
'''

oldStake = 0            # the previous stake
oldBlock = 0            # the block last time it changed
stake = 0               # for startup
sendOneTimeQtumdOffline = False   # send an alert once if qtumd is offline
qtumdIsRunning = False  # set this on startup
labelsPrintedAtStartup = False  # print the label row once at startup
logNewBlock = False     # set to log new block
blocksToday = 0         # new blocks today, accurate if QM running 24 hours+
savedUnixBlockTime = 0  # for time since last block
sendOneTimeNotStaking = False  # will check below if staking

sendEmailForNewHour = False   # send a status email for new hour
secondsSinceLastBlock = 0   # for logging
didNewHour = False      # switch to allow a few seconds to detect the hour change
didNewLog = False       # did we just detect a UTC day change and opened a new log file
sendLowConnectionsAlert = False # send an alert for low connections
lowConnectionsAging = 0 # age the low connections alert to only send again after 7 blocks
staleBlockAging = 0     # age the stale block alert to only send again after 15 minutes
config_file_name = "qtumMonConfig.txt" # name of configuration file
firstTimeThrough = True # the first time through, do/don't do certain things
minimumStakeSize = 99   # value of minimum UTXO size, used to detect stakes
delayBlockWaiting = 3   # set on 10/14/2017, delay in seconds for the block waiting loop
                        # this parameter is critical for setting the delay until the next
                        # block check immediately after a new block is found
delayDateHours = 3.36   # set to 3.86 on 10/13/2017, 4 second delay,delay in seconds for the loop that detects date and hour change
                        # set to 3.36 on 10/15/2017 because still missing 4 second blocks
loopSeq = ""            # log timing of loops, if miss block
savedLoopSeq = ""       # for logging
oldestMAValue = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # holds old moving average seconds
secondsMovingAverage = 0.0  # just something for first printout
MAcount= 0              # counter for 0..9 to calculate seconds moving average
firstBlockFound = True  # we are going to find the first block
currentSecondsMod16 = 0.0 # for startup
printBlockMod10 = True  # toggle to print the labels every 10 blocks

trueNetworkWeight = 15000000            # estimate
dDiff = trueNetworkWeight / 5.86        # slope from chart of simulated results, uniform wallets

startingDifficulty = dDiff              # starting value for the four 121 block moving averages
                                        # 30 million network weight 5693691
                                        # 20 million network weight 3409395, 3900000 128 seconds
                                        # 15 million 2824920
                                        # 3.86 million 679000

# labels for the display and log
#           123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
labelRow = "  time   |  balance | stake |    block  | my weight| net weight | con | stking |exp hrs|secLast| offst| ave"
logLabels = '000,unix time, date time, balance, stake, block, weight, net weight, connections, staking, expected Hours, secondsLastBlock'

import subprocess
import time
from time import localtime, strftime, sleep
from datetime import datetime
import smtplib                          # email sending function
from email.mime.text import MIMEText    # for email formatting
import os, sys                          # for file operations
from timeit import default_timer as timer
from array import *                     # for arrays

# doNotDisturb[] gives the hours when emails will not be sent. 
# times given in GMT as follows, 0000 = 12 midnight, 2300 = 11:00 pm, etc.
# Enter the do not disturb hours here in GMT, and they will be
# converted to the local time zone by the configuration file parameter
# UTCtimezoneoffset. Enter a "1" in the array to suppress emails during
# that hour. For example, to suppress emails for 0800 hours, enter a "1"
# in the 9th element of the array, which is doNotDisturb[8]. UTCtimezoneoffset
# will convert this time to 0800 hours local time.
#
#  0000,  0100,  0200,  0300,  0400,  0500,  0600, 0700
#  0800,  0900,  1000,  1100,  1200,  1300,  1400, 1500
#  1600,  1700,  1800,  1900,  2000,  2100,  2200, 2300
#

doNotDisturb=array('b',\
    [1, 1, 1, 1, 1, 1, 1, 0,\
     0, 0, 0, 0, 0, 0, 0, 0,\
     0, 0, 0, 0, 0, 0, 0, 1])

# need to send email info in two pieces (subject and message), the subject will be truncated

def send_email(subjectText, messageText):

    "Send an email to an address which may be an email-to-text address for mobile operator"

    # if in a doNotDisturb hour, do not send this email
    # can get here up to 4 seconds early for the new hour, so make some adjustment here
    # to index into the current (or immediately upcoming) hour for doNotDisturb[]

    global doNotDisturbQueue

    unixTime = int(time.time())
    unixTimeEarly = unixTime + 4    # allow 4 seconds of being early

    UTCHour = int((unixTimeEarly % 86400) / 3600) # 0..23, no half hour time zones
    localHour = UTCHour + UTCTimeOffset
    
    if localHour > 23:
        localHour -= 24
    elif localHour < 0:
        localHour += 24

    # print("localHour =", localHour, "doNotDisturb =", doNotDisturb[localHour])

    if doNotDisturb[localHour] == 0:                # go ahead and send email

        if len(doNotDisturbQueue) > 0:             # had some messages queued, add them
            messageText += '\n'
            messageText += doNotDisturbQueue 
            doNotDisturbQueue = ''                  # clear out for next time
       
        msg = MIMEText(messageText)                     # use as message

        server = smtplib.SMTP('smtp.gmail.com:587')
        msg['Subject'] = subjectText                    # email subject
        msg['From'] = fromAddress                       # from: email address
        msg['To'] = toAddress                           # to: email address
        server.starttls()
        time.sleep(0.05)
        server.login(username, password)
        time.sleep(0.05)
        # server.set_debuglevel(1)
        server.sendmail(fromAddress, toAddress, msg.as_string())
        time.sleep(0.05)
        server.quit()
        time.sleep(0.05)

    else:                 # queue up the message for when doNotDisturb is over
        if sendEmailForNewHour != True:   # but don't queue up hourly status messages
            now = datetime.now()
            current_timeHMS = now.strftime("%H:%M:%S")
            doNotDisturbQueue += current_timeHMS + subjectText + messageText + '\n'
            # print("doNotDisturbQueue =", doNotDisturbQueue)

def parse_number(field, offset, lenData, periodAllowed):
    '''
    parse the global variable "data" which is the response from qtum-cli calls.
    Search for the text "field", then get the digit characters starting 
    "offset" characters from the start of the field, and search through at
    least "lenData" characters, and respond to a period "." if "periodAllowed"
    is True.
    
    For example, to find the balance from the qtum-cli command -getinfo:
                       periodAllowed = True
                       v
    ..."balance": 14698.3456000, \r\n...
                  ^    
                  offset = 10 characters from start of balance
    '''
    global data
    
    temp = ' '
	
    dataIndex = data.find(field, 0, lenData)

    i = dataIndex + offset  	# point at the first digit
	
    if dataIndex > 0:  # found field
        while i <= lenData - 1:
            
            if data[i] >= '0' and data[i] <= '9':
                temp += data[i]
            elif data[i] == "." and periodAllowed == True:  # if period allowed
                temp += data[i]
            elif data[i] == ",":
                break
            elif (i == dataIndex + offset) and (data[i] == "-"):  # allow negative sign
                temp += data[i]                                   # first character only
            else:  # how to find \r at end of response, like for estimated time?
                # print("QM error, bad character in ", field)
                break
                    
            i += 1	
            if i >= lenData:
                break
            
        return(temp)
            
    else:
        return(-1)      # an error

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# parse alphanumeric text like "True", "xyz@gmail.com" and "HP8200"

def parse_alphanum(field, offset, lenData):
    # parse against the global variable "data"
    
    global data
    
    temp = ''
    
    dataIndex = data.find(field, 0, lenData)
    
    i = dataIndex + offset  	# point at the first digit
	
    if dataIndex > 0:  # found field
        # allow characters 0..9, @..Z, a..z
        while i <= lenData - 1:

            # print("data[i] = ", data[i])
            
            if (data[i] >= 'a' and data[i] <= 'z') or +\
               (data[i] >= '@' and data[i] <= 'Z') or +\
               (data[i] >= '0' and data[i] <= '9') or +\
               (data[i] == '.') or +\
               (data[i] == '-'):
                temp += data[i]
            elif data[i] == "," or data[i] == "'\'":     # for -getinfo proof-of-stake
                break
            else:
                # print("QM error, bad character in ", field) #PY3
                # print "QM error, bad character in " + field #PY2
                break
                    
            i += 1
                    
            if i >= lenData:
                break
        return(temp)
            
    else:
        return(-1)   # an error
        
def parse_logical(field, offset, lenData):
    # parse against the global variable "data"

    global data
    
    temp = ''
    
    dataIndex = data.find(field, 0, lenData)
    
    i = dataIndex + offset  	# point at the first digit

    if dataIndex > 0:  # found field
        while i <= lenData - 1:
            if data[i] >= 'a' and data[i] <= 'z':
                temp += data[i]
            elif data[i] == ",":
                break
            else:
                print("QM error, bad character in ", field)   #PY3
                # print "QM error, bad character in " + field #PY2
                break
                    
            i += 1
                    
            if i >= lenData:
                break    

        # print("field =", field, "temp =", temp)
        
        if temp == "true":
            return(True)
        elif temp == "false":	
            return(False)
 
    else:
        return(-1)   # an error
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                            
print("QtumMon version", version)    #PY3
# print "QtumMon version " + version #PY2
    
testPass = 0                      # for testing
sendNewSingleBlockReward = False  # send an alert when have all the info, new single reward
sendNewMultiBlockReward = False   # send and alert for a new overlapping reward
sendStakeReturned = False         # send an alert that the stake is returned
sendBlockStaleAlert = False       # blocks are getting stale > 1/2 hours
doNotDisturbQueue = ''            # alert messages queued up during doNotDisturb times

QMStartTime = int(time.time())    # time program started, after 30 minutes look for stale blocks
                                  # and low connections

start = timer()                   # for timing block loop below, first time through
start2 = timer()                  # kludge, for loop timing
lastBlockCheckTime = timer()      # for startup

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Testing response times of qtum-cli and qtumd: 
# average of 100 loops in seconds, no display             getinfo   getstakingdata
# HP 8200 64 bit i5-2400 3.1 GHz, 32 bit qtumd              1.224       1.224
# HP 750-411 64 bit i5-6400 2.7 GHz, 64 bit qtumd           1.013       1.008 
# HP 750-411 64 bit i5-6400 2.7 GHz, 64 bit qtumd 140301    1.007       1.008

'''
start = timer()
i = 0
while i < 100:
    # output = subprocess.check_output('qtum-cli "-getinfo"', shell = True)
    # output = subprocess.check_output('qtum-cli "getstakinginfo"', shell = True)
    time.sleep(1.0)
    i += 1
end = timer()
print(end - start)
sys.exit()
'''

# read config file  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

'''
hostname: "LD18",
sendemail: "true",
sendhourlyemail: "true",
setdomestic: "true",
domesticaddress: "87654321@starhubenterprisemessaging.com",
internationaladdress: "9876543210@txt.att.net",
enablelogging: "true",
emailaddress: "mygmail@gmail.com",
emailusername: "mygmail",
emailpassword: "abcdefghijklmnop",
UTCtimezoneoffset: "8",
'''

try:
    configFile = open(config_file_name, 'r')  # check for success, or exit
except:
    print("ERROR opening configuration file")
    print('The configuration file "qtumMonConfig.txt" must be in the same directory with QM, qtumd and qtum-cli')
    sys.exit()
    
data = configFile.read()
lenData = len(data)
configFile.close()
# print(data)

# parse the configuration values

hostName = parse_alphanum("hostname", 11, lenData)

sendEmail = parse_logical("sendemail", 12, lenData) # set to control sending of alert emails

sendHourlyEmail = parse_logical("sendhourlyemail", 18, lenData)

setDomestic = parse_logical("setdomestic", 14, lenData)  # set for domestic vs. international

# email addresses can send a text to mobile phone, check your carrier
# domestic email address, could be a mobile number text address
# see http://www.makeuseof.com/tag/email-to-sms/
domesticAddress = parse_alphanum("domesticaddress", 18, lenData)

# international email address, could be a mobile number text address
internationalAddress = parse_alphanum("internationaladdress", 23, lenData)

if setDomestic == True:
    toAddress = domesticAddress
else:    
    toAddress = internationalAddress

# print("toAddress =", toAddress)    

enableLogging = parse_logical("enablelogging", 16, lenData)

# emails are sent from this email account, Gmail log in credentials
# See https://support.google.com/accounts/answer/185833?hl=en
# for Gmail, turn on 2FA and assign app password, make new device "Python"

fromAddress = parse_alphanum("emailaddress", 15, lenData)
# print("fromAddress =", fromAddress)

username = parse_alphanum("emailusername", 16, lenData)
# print("username =", username)

# Application Specific password from Python
password = parse_alphanum("emailpassword", 16, lenData)
# print("password =", password)

UTCTimeOffset = int(parse_number("UTCtimezoneoffset", 20, lenData, False))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

print("hostName =", hostName)    #PY3
# print "hostName =" + hostName  #PY2

if sendEmail == True:
    print("Email enabled, sending to", toAddress)
    
    if sendHourlyEmail == True:
        print("Sending hourly emails")
    else:
        print("But not sending hourly emails")
else:
    print("Not sending emails")
    
if enableLogging == True:
    print("Logging enabled")
else:
    print("Logging not enabled")

# initialize log file - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Can set the Z drive, as an Administrator, go to System - Disk Management - All Tasks - 
# Change Drive Letter and Paths

if enableLogging == True:    
    GMT = strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())  # GMT
    # open log file in the format "QM_Log_DD_MMM_YYYY.csv"
    out_file_name_QM = 'QM_Log_'+GMT[5]+GMT[6]+'_'+GMT[8]+GMT[9]+GMT[10]+\
                    '_'+GMT[12]+GMT[13]+GMT[14]+GMT[15]+'.csv'
    
    print("QM log file name =", out_file_name_QM)    #PY3
    # print "QM log file name =" + out_file_name_QM  #PY2
        
    try:
        outFileQM = open(out_file_name_QM, 'a')   # create or open log file for appending
        print("QM log file open for appending")
        # print("Opening file", out_file_name_QM, "on", GMT)
        tempStr = '000,Program,start,or,restart,version,' + version
        outFileQM.write(tempStr)
        outFileQM.write('\n')
        
        # log starting time:
        tempStr = '000,Logging,start,' + '_' + GMT[17]+GMT[18]+GMT[20]+GMT[21]+',hours,GMT,'+\
                  GMT[5]+GMT[6]+'_'+GMT[8]+GMT[9]+GMT[10]+GMT[12]+GMT[13]+GMT[14]+GMT[15]
        outFileQM.write(tempStr)
        outFileQM.write('\n')
        outFileQM.write(logLabels)  # write a row of column labels to the log
        outFileQM.write('\n')
        time.sleep(0.01)
        outFileQM.close()
        
    except IOError:   # NOT WORKING
        print("QM ERROR: File didn't exist, open for appending")

fileOpenQM = False

# check that qtumd is running - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# look for a response from qtum-cli getblockcount

while True:  # wait here if qtumd is not running

    block = -1    # error condition, unless set by qtumd

    try:
        block = int(subprocess.check_output('qtum-cli "getblockcount"', shell = True))
    except:
        print("ERROR, no response from qtumd")  

    # print("In qtumd check,block =", block)

    if block > 0:
        if qtumdIsRunning == False:   # on startup or restart
            qtumdIsRunning = True
            print("qtumd is running")
        sendOneTimeQtumdOffline = False # reset to find next qtumd offline
        
        # the first time through, set oldBlock so don't get double row print
        if firstTimeThrough == True:
            oldBlock = block
        
        break
    else:
        print("qtumd is NOT RUNNING. Standby")
        qtumdIsRunning = False

        if sendOneTimeQtumdOffline == False:  # send an alert and log once for this problem
            sendOneTimeQtumdOffline = True

            tempMessage = " on" + hostName
            tempSubject = " QTUMD NOT RUNNING"

            if sendEmail == True:
                send_email(tempSubject, tempMessage)  
                print("Sending email" + tempSubject + tempMessage)  #PY3
                # print "Sending email" + tempSubject + tempMessage #PY2

            if enableLogging == True:
                tempStr = "900, QTUMD OFFLINE"
                if fileOpenQM == False:
                    fileOpenQM = True
                    outFileQM = open(out_file_name_QM, 'a')   # open log file
                    # print("Opening file")  
                outFileQM.write(tempStr)
                outFileQM.write('\n')
                # print(tempStr)
                time.sleep(0.01)
                outFileQM.close()
                fileOpenQM = False

        time.sleep(15) # give some time to start/restart qtumd     

# MAIN PROGRAM LOOP = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

while True:

    if labelsPrintedAtStartup == False:  # print the label row once during startup
        labelsPrintedAtStartup = True
        if block % 10 != 0:     # because if block % 10 == True at startup, it will print below
            print(labelRow)

    # print("Top of loop")        

    # check "getinfo" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    '''  Typical response from Skynet 9/27/2017
    b'{\r\n  "version": 140200,\r\n
    "protocolversion": 70015,\r\n
    "walletversion": 130000,\r\n
    "balance": 5651.98847287,\r\n
    "stake": 304.00000000,\r\n
    "blocks": 29798,\r\n
    "timeoffset": 0,\r\n
    "connections": 25,\r\n
    "proxy": "",\r\n
    "difficulty": {\r\n
      "proof-of-work": 1.52587890625e-005,\r\n
      "proof-of-stake": 16976158.39177359\r\n  },\r\n
    "testnet": false,\r\n
    "moneysupply": 100099192,\r\n
    "keypoololdest": 1505054992,\r\n
    "keypoolsize": 101,\r\n
    "unlocked_until": 1606442385,\r\n
    "paytxfee": 0.00000000,\r\n
    "relayfee": 0.00001000,\r\n
    "errors": ""\r\n}\r\n'
    '''
    if firstTimeThrough == True:     # for the display, otherwise -getinfo in the block waiting loop below
        try:    
            output = subprocess.check_output('qtum-cli "-getinfo"', shell = True)
            # print(output)
        except:
            print("NO RESPONSE from qtumd. EXITING")
            sys.exit()

        data = str(output)

    '''
    # for testing
    if testPass == 0:
        print("Test data 1")
        data = '{"balance": 0.00000000,"stake": 0.00000000, "blocks": 13765, "timeoffset": 0"}'
        testPass = 1
    elif testPass == 1:
        print("Test data 2")
        data = '{"balance": 0.00000000,"stake": 549.87654321, "blocks": 13766, "timeoffset": 0"}'
    '''    

    # parse data to get various values  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
    # temp = ''
    lenData = len(data)
    # print("lenData =", lenData)     # lenData = 568
    
    balance = float(parse_number("balance", 10, lenData, True))  # get balance
    # print("balance = ", balance)

    stake = float(parse_number("stake", 8, lenData, True))  # get stake
    # print("stake = ", stake)
      
    block = int(parse_number("blocks", 9, lenData, False)) # get the current block
    # print("block = ", block)

    proofOfWork = parse_alphanum("proof-of-work", 16, lenData)
    # print("proofOfWork = ", proofOfWork)

    dDiff = float(parse_alphanum("proof-of-stake", 17, lenData))
    # print("proofOfStake = ", dDiff)
             
  
    # detect new block reward and flag to send alert  - - - - - - - - - - - - - - - - - - - - -

    '''
    testPass += 1        # testing stake detection below

    if testPass == 2:
        stake = 10.8     # some pesky 3.6s
    elif testPass == 3:
        stake = 500.5    # new single reward
    elif testPass == 4:
        stake = 500.5
    elif testPass == 5:
        stake = 1000.8   # new multi reward
    elif testPass == 6:
        stake = 1000.8
    elif testPass == 7:  # returned
        stake = 500.5
    elif testPass == 8:  # returned
        stake = 0
    '''

    if stake != oldStake:		 # found a stake change

        # no stake alert the first time through, for a stake in progress

        if stake >= oldStake + minimumStakeSize and firstTimeThrough == False: # filters out 0.4s

            if oldStake < minimumStakeSize:
                print("Found a new single reward, block =", block, "stake =", stake)      #PY3
                # print "Found a new single reward, block =" + block + "stake =" + stake  #PY2
                sendNewSingleBlockReward = True
            elif oldStake >= minimumStakeSize:       # at least double reward period
                print("Found a new multi reward, block =", block, "stake =", stake)       #PY3
                # print "Found a new multi reward, block =" + block + "stake =" + stake   #PY2
                sendNewMultiBlockReward = True    

        # detect a stake return, and filter out the 0.4 stuff

        elif stake <= oldStake - minimumStakeSize: # block 26978, stake returned, works for overlapping reward periods
            print("Stake returned, block =", block, "stake =", stake)      #PY3
            # print "Stake returned, block =" + block + "stake =" + stake  #PY2
            sendStakeReturned = True

        oldStake = stake

    connections = int(parse_number("connections", 14, lenData, False))  # get connections

    unixTime = int(time.time())

    # low connections checked with every new block. If low connections is discovered
    # which may be triggered if the network connection to the wallet PC is lost, or partially
    # lost, wait 7 blocks (about 15 minutes) before resending, using lowConnectionsAging
            
    if (unixTime - QMStartTime) >= 1800:                # 30 minutes after QM start
        if connections <= 5 and lowConnectionsAging <= 0:   # is this a good error quantity?
            print("ALERT: low connections, only", connections)    #PY3
            # print "ALERT: low connections, only" + connections  #PY2 
            sendLowConnectionsAlert = True              # send alert below
            lowConnectionsAging = 6                     # set for aging process

        elif connections <= 5:      # still in low connections situation
            lowConnectionsAging -= 1

        elif connections >= 6:
            lowConnectionsAging = 0  # reset it, no more low connections

    # print("connections = ", connections)

    # check "getstakinginfo"  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ''' Typical response from Skynet 9/27/2017 (there were some brutal network weights on Skynet)
    b'{\r\n  "enabled": true,\r\n
    "staking": true,\r\n
    "errors": "",\r\n
    "currentblocksize": 0,\r\n
    "currentblocktx": 1000,\r\n
    "pooledtx": 0,\r\n
    "difficulty": 21729576.68254313,\r\n
    "search-interval": 19456,\r\n
    "weight": 565198847287,\r\n
    "netstakeweight": 7968576249052219,\r\n
    "expectedtime": 119083\r\n}\r\n'
    '''
    	
    try:    
        output = subprocess.check_output('qtum-cli "getstakinginfo"', shell = True)
        # print(output)
    except:
        print("NO RESPONSE from qtumd. EXITING")
        sys.exit()

    data = str(output)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # parse output to get enabled, staking, weight and netstakeweight, calculate immature

    '''
    # for testing
    if testPass == 0:
        print("Test data 1")
        data = '{"balance": 0.00000000,"stake": 0.00000000, "blocks": 13765, "timeoffset": 0"}'  
        testPass = 1
    elif testPass == 1:
        print("Test data 2")
        data = '{"balance": 0.00000000,"stake": 549.87654321, "blocks": 13766, "timeoffset": 0"}'
    '''

    temp = ''
    lenData = len(data)
    # print("lenData =", lenData)     # lenData = 297

    enabled = parse_logical("enabled", 10, lenData)  # get enabled     
    # print("enabled =", enabled)

    # confirm that staking is enabled, or send alert and wait here  - - - - - - - - - - - - - -

    while True:
        
        staking = parse_logical("staking", 10, lenData)       # get staking
        
        if hostName == "HP8200":
            staking = True   # force for testing, with no mature coins or 0.0 balance
        
        if staking == True:
            sendOneTimeNotStaking = False   # reset to detect problem below, next pass
            # print("staking is True")
            break
        
        else:                       # not staking  :-(
            if sendOneTimeNotStaking == False:
                if sendEmail == True:
                    tempMessage = ".on " + hostName      
                    tempSubject = ".NOT STAKING"                                                    
                    send_email(tempSubject, tempMessage)
                    print("Sending email", tempSubject, tempMessage)     #PY3
                    # print "Sending email" + tempSubject + tempMessage  #PY2
                sendOneTimeNotStaking = True

            if enableLogging == True:
                tempStr = "900, NOT STAKING"
                if fileOpenQM == False:
                    fileOpenQM = True
                    outFileQM = open(out_file_name_QM, 'a')   # open log file
                    # print("Opening file") 
                outFileQM.write(tempStr)
                outFileQM.write('\n')
                # print(tempStr)
                time.sleep(0.01)
                outFileQM.close()
                fileOpenQM = False

            print('ERROR: qtumd not set for staking. Run qtum-cli walletpassphrase "passphrase" 99999999 true')
            time.sleep(15)  # give some time to fix this

    # weight is "my weight", the mature coins staking in this wallet           
    weight = float(parse_number("weight", 9, lenData, True)) / 100000000  # get weight in QTUM
    # print("weight =", weight)

    # calculate immature since qtumd doesn't seem to provide it
    immature = balance - weight                     # coins that will mature after 500 blocks, but don't use it

    # get netstakeweight in millions, the calculated estimate of all QTUM currently being staked
    longNetStakeWeight = float(parse_number("netstakeweight", 17, lenData, False)) / 100000000
    netStakeWeight = int(longNetStakeWeight)
    # print("netstakeweight = ", netStakeWeight)

    # get expectedtime in hours, average time until the next block reward
    expectedTimeHours = float(parse_number("expectedtime", 15, lenData, False)) / 3600
    # print("expectedTimeHours = ", expectedTimeHours)

    '''
    Format the data for printing on a display. Add commas and calculate the pads to keep 
    the columns aligned. Numbers are right justified:

    Left side:
       time   |  balance | stake |   block
     22:21:41 |  1,000.0 | 120.0 |  17,430
     22:21:41 | 10,000.0 | 210.0 |  97,430
     22:21:41 | 23,000.0 | 999.9 | 999,999
               \pad1      \pad2   \pad3
    Right side:
    |my weight | net weight | con | stking |exp hrs| secLast
    |  1,000.0 |  3,653,699 |   4 |  yes   | 340.0 |    10
    | 10,000.0 | 23,653,699 |  10 |  yes   | 340.0 |   258
    | 23,000.0 | 93,653,699 |  25 |  yes   |   2.3 |   558
     \pad4      \pad5        \pad7 \pad8    \pad9
    '''

    if balance <= 99999:
        balanceWithCommas = ("{:,f}".format(round(balance, 1)))[:-5]
        pad1 = " " * (8 - len(balanceWithCommas))
        balancePadCommas = pad1 + balanceWithCommas
    else:
        balancePadCommas = "xxxxxxxx"

    if stake <= 999:
        stakeWithCommas = ("{:,f}".format(round(stake, 1)))[:-5]
        pad2 = " " * (5 - len(stakeWithCommas))
        stakePadCommas = pad2 + stakeWithCommas
    else:
        stakePadCommas = "xxxxx"

    if block <= 999999:
        blockWithCommas = "{:,d}".format(int(block))
        pad3 = " " * (9 - len(blockWithCommas))
        blockPadCommas = pad3 + blockWithCommas
    else:
        blockPadCommas = "xxxxxxxxx"

    if weight <= 99999:
        weightWithCommas = ("{:,f}".format(round(weight, 1)))[:-5]
        pad4 = " " * (8 - len(weightWithCommas))
        weightPadCommas = pad4 + weightWithCommas
    else:
        weightPadCommas = "xxxxxxxx"

    if netStakeWeight <= 99999999:
        netWeightWithCommas =  "{:,d}".format(int(netStakeWeight))
        pad5 = " " * (10 - len(netWeightWithCommas))
        netWeightPadCommas = pad5 + netWeightWithCommas
    else:
        netWeightPadCommas = "xxxxxxxxxx"
        netWeightWithCommas = "xxxxxxxxxx" # Skynet start > 100m, to hourly
    
    '''
    if immature <= 999999:
        immatureWithCommas = ("{:,f}".format(round(immature, 1)))[:-5]
        pad6 = " " * (9 - len(immatureWithCommas))
        immaturePadCommas = pad6 + immatureWithCommas
    else:
        immaturePadCommas = "xxxxxxxxx"
    '''    

    # connections is a low range integer, say 0 to 120, and doesn't need commas
    if connections <= 999:
        strConnections = str(connections)
        pad7 = " " * (3 - len(strConnections))
        connectionsPad = pad7 + strConnections
    else:
        connectionsPad = "xxx"

    if expectedTimeHours <= 999:
        exphrsWithCommas = ("{:,f}".format(round(expectedTimeHours, 1)))[:-5]
        pad8 = " " * (5 - len(exphrsWithCommas))
        exphrsPadCommas = pad8 + exphrsWithCommas
    else:
        exphrsPadCommas = "xxxxx"  

    if secondsSinceLastBlock <= 9999:
        secLastWithCommas = "{:,d}".format(int(secondsSinceLastBlock))
        pad9 = " " * (5 - len(secLastWithCommas))
        secLastPadCommas = pad9 + secLastWithCommas
    else:
        secLastPadCommas = "xxxx"

    if firstTimeThrough == True:
        secLastPadCommas = "   na"   # not applicable

    unixTime = int(time.time())
    now = datetime.now()
    # current_time2 = now.strftime("%Y %m %d %H:%M:%S")
    current_time2 = now.strftime("%H:%M:%S")

    # format the data for emails and logging
    unixTimeFormatted = str(unixTime)
    balanceFormatted = format(balance, "08.1f")
    balanceForEmail = format(balance, "0.1f")
    stakeFormatted = format(stake, "08.1f")
    stakeForEmail = format(stake, "0.1f")
    blockFormatted = str(block)
    weightFormatted = format(weight, " 08.1f")
    weightForEmail = format(weight, " 0.1f")
    netStakeWeightFormatted = format(netStakeWeight, "09d")
    netStakeWeightForEmail = format(netStakeWeight, "1d")
    # immatureFormatted = format((immature), "08.1f")
    connectionsFormatted = str(connections)
    expectedTimeHoursFormatted = format(expectedTimeHours, "0.1f")
    secondsSinceLastBlockFormatted = format(secondsSinceLastBlock, "1d")
    secondsMovingAverageFormatted = format(secondsMovingAverage, "0.2f")
    currentSecondsMod16Formatted = format(currentSecondsMod16, "0.2f")

    if staking == True:
        stakingForEmail = "  yes "  # yes
    else:
        stakingForEmail = "  NOT "  # no, but get blocked above, should never get here

    # send email if alerts have been set  - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if sendNewSingleBlockReward == True:  # found a new block reward above
        sendNewSingleBlockReward = False  # reset it

        stakeForEmail = format(stake, "0.1f") + " "
        tempMessage = "." + hostName + " blk " + str(block) + " stk " + stakeForEmail
        tempSubject = ".REWARD"
                    
        if sendEmail == True:
            send_email(tempSubject, tempMessage)
            print("Sending email", tempSubject, tempMessage)     #PY3
            # print "Sending email" + tempSubject + tempMessage  #PY2

        if enableLogging == True:
            tempStr = "400, REWARD"
            if fileOpenQM == False:
                fileOpenQM = True
                outFileQM = open(out_file_name_QM, 'a')   # open log file
                # print("Opening file")
            outFileQM.write(tempStr)
            outFileQM.write('\n')
            # print(tempStr)
            time.sleep(0.01)
            outFileQM.close()
            fileOpenQM = False

    if sendNewMultiBlockReward == True:  # found a new overlapping block reward above
        sendNewMultiBlockReward = False  # reset it

        tempMessage = "." + hostName + " blk " + str(block) + " stk " + stakeForEmail   
        tempSubject = ".MULTI"

        if sendEmail == True:
            send_email(tempSubject, tempMessage)
            print("Sending email", tempSubject, tempMessage)     #PY3
            # print "Sending email" + tempSubject + tempMessage  #PY2

        if enableLogging == True:
            tempStr = "400, MULTI"
            if fileOpenQM == False:
                fileOpenQM = True
                outFileQM = open(out_file_name_QM, 'a')   # open log file
                # print("Opening file")
            outFileQM.write(tempStr)
            outFileQM.write('\n')
            # print(tempStr)
            time.sleep(0.01)
            outFileQM.close()
            fileOpenQM = False

    if sendStakeReturned == True:  # the stake has been returned
        sendStakeReturned = False  # reset it

        tempMessage = "." + hostName + " blk " + str(block) + " stk " + stakeForEmail   
        tempSubject = ".RETURNED"

        if sendEmail == True:
            send_email(tempSubject, tempMessage)
            print("Sending email", tempSubject, tempMessage)     #PY3
            # print "Sending email" + tempSubject + tempMessage  #PY2

        if enableLogging == True:
            tempStr = "400, RETURNED"
            if fileOpenQM == False:
                fileOpenQM = True
                outFileQM = open(out_file_name_QM, 'a')   # open log file
                # print("Opening file")
            outFileQM.write(tempStr)
            outFileQM.write('\n')
            # print(tempStr)
            time.sleep(0.01)
            outFileQM.close()
            fileOpenQM = False

    if sendLowConnectionsAlert == True:
        sendLowConnectionsAlert = False

        tempMessage = "." + hostName + " only " + str(connections)
        tempSubject = ".LOW CONNECTIONS"

        if sendEmail == True:
            send_email(tempSubject, tempMessage)
            print("Sending email", tempSubject, tempMessage)     #PY3
            # print "Sending email" + tempSubject + tempMessage  #PY2   

        if enableLogging == True:
            tempStr = "900, LOW CONNECTIONS"
            if fileOpenQM == False:
                fileOpenQM = True
                outFileQM = open(out_file_name_QM, 'a')   # open log file
                # print("Opening file")
            outFileQM.write(tempStr)
            outFileQM.write('\n')
            # print(tempStr)
            time.sleep(0.01)
            outFileQM.close()
            fileOpenQM = False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    if block % 10 == 0:                # print the labels every 10 blocks (rows)
        if printBlockMod10 == True:
            printBlockMod10 = False    # protect against multiple prints when block % 10 is true
            print(labelRow)
    else:
        printBlockMod10 = True         # arm for next block % 10 is true
        
    if sendEmailForNewHour == False:  # avoids double print if coming through here for new hour 
        print(current_time2, "|", balancePadCommas, "|", stakePadCommas, "|", blockPadCommas, "|", weightPadCommas, "|", netWeightPadCommas, "|", connectionsPad, "|", stakingForEmail, "|", exphrsPadCommas, "|", secLastPadCommas, "|", currentSecondsMod16Formatted, "|", secondsMovingAverageFormatted) # PY3    

    if logNewBlock == True:  # found a new block below, log it
        logNewBlock = False

        if enableLogging == True:  # for log (and Excel) no commas, Excel ingnores leading zeros 
            tempStr = "100," + unixTimeFormatted +"," + current_time2 + "," + balanceFormatted + "," + stakeFormatted + "," + blockFormatted + "," + weightFormatted + "," + netStakeWeightFormatted + "," + connectionsFormatted + "," + stakingForEmail + "," + expectedTimeHoursFormatted + "," + secondsSinceLastBlockFormatted + "," + currentSecondsMod16Formatted + "," + secondsMovingAverageFormatted + "," + savedLoopSeq
            if fileOpenQM == False:
                fileOpenQM = True
                outFileQM = open(out_file_name_QM, 'a')   # open log file
                # print("Opening file")
            outFileQM.write(tempStr)
            outFileQM.write('\n')
            # print(tempStr)
            time.sleep(0.01)
            outFileQM.close()
            fileOpenQM = False       

    # send hourly status email  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if sendEmailForNewHour == True:
        
        if sendHourlyEmail == True:          # okay to send hourly status email
            tempMessage =  " bal " + balanceWithCommas + " blk " + blockWithCommas + " mwt " + weightWithCommas + " nnwt " +  stakingForEmail
            tempSubject = "." + hostName + " stk " + stakeWithCommas
                          
            if sendEmail == True:
                send_email(tempSubject, tempMessage)
                # print("Sending hourly status email", tempSubject, tempMessage)     #PY3
                # print "Sending email" + tempSubject + tempMessage  #PY2

    sendEmailForNewHour = False

    # print("new block loop slack", lastBlockCheckTime + delayBlockWaiting - timer())
    # typical: new block loop slack 1.470697567243377

    # this is the delay that runs a single time after each new block is detected
    # set to 4.0 on 10/13/2017, but finding a 4 second block
    # set to 3.0 on 10/14/2017

    # FUT line up to a whole second here

    while True:         # wait here until we get to 4 seconds from the last block check
        if timer() > lastBlockCheckTime + delayBlockWaiting:
            break
        else:
            time.sleep(0.1)

    # new block waiting loop  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    breakOut = False  # kludge to allow break from 2 levels

    while breakOut == False:
        # end = timer()
        # print("Loop =", format(end - start, "0.2f"))

        lenLoopSeq = len(loopSeq)
        
        if lenLoopSeq < 1425:      # about 5 minutes
            now = datetime.now()
            temp = now.strftime("%M:%S.%f")
            timeMSS = "b" + temp[1:8] + "_"   # for before the getinfo call
            loopSeq += timeMSS

        lastBlockCheckTime = timer()

        try:    
            output = subprocess.check_output('qtum-cli "-getinfo"', shell = True)
            # print(output)
        except:
            print("NO RESPONSE from qtumd. EXITING")
            sys.exit()

        data = str(output)
        dataLen = len(data)
        
        block = int(parse_number("blocks", 9, dataLen, False)) # get the current block
        # print("block = ", block)

        blockMod10 = block % 100    # get the two log digits for loopSeq

        '''
        Create a timing diagnostic string with the time right before and after reading
        the block. This is to investibate the skipped blocks (the 4 second ones) and
        this code can be commented out eventually. 

        A a sample string is b0:39.80_26_0:41.00_b0:43.81_27_0:45.00_

        "b" means before the getinfo to read the new block
        0:39.80 is clock minute, seconds and hundreds
        26 is the last two digits of the block number read
        0:41.00 is minute, seconds and hundreds, so this read took 1.20 seconds
        after the delay, the next getinfo starts at 0:43.81, a delay of
        43.81 - 39.80 = 4.01 seconds between reads.
        the new block arrives with last two digits "27" on that next read,
        so there are something less than 43.81 - 39.80 = 4.01 seconds between
        these two blocks
        '''

        if lenLoopSeq < 1425:
            loopSeq += str(blockMod10)
            loopSeq += "_"
            now = datetime.now()
            temp = now.strftime("%M:%S.%f")
            timeMSS = temp[1:8]
            loopSeq += timeMSS
            loopSeq += "_"

        # print(loopSeq)    

        if block != oldBlock:  # found a new block
            # print("found a new block =", block)
            end2 = timer()
            newDuration = int(end2 - start2) # saves the time since the last block
            start2 = timer()

            # get the moving average seconds to try and find the 16 second cycle timing

            currentSecondsMod16 = time.time() % 16

            if firstBlockFound == True:  # set the seconds moving average, an array, for the first block found
                firstBlockFound = False
                secondsMovingAverage = currentSecondsMod16  # stuff the whole thing in, not just 1 tenth.
                i = 0
                while i <= 9:
                    oldestMAValue[i] = currentSecondsMod16 / 10
                    i += 1

            secondsMovingAverage += currentSecondsMod16 /10
            secondsMovingAverage -= oldestMAValue[MAcount]      # subtract the value from 10 blocks ago
            oldestMAValue[MAcount] = currentSecondsMod16 / 10   # save the current value
            
            # print("MAcount ", MAcount, "secondsMovingAverage ", format(secondsMovingAverage, "0.2f"))
            MAcount += 1
            if MAcount >= 10:
                MAcount = 0       # wrap end
                  
            if int((block) != int(oldBlock) + 1) and firstTimeThrough == False:
                print("MISSED BLOCK")
                print(loopSeq)

                                     # do not send email on missed block 
                if sendEmail == True:
                    tempMessage = ".on " + hostName + " at block " + str(block)
                    tempSubject = ".MISSED BLOCK"            
                    # send_email(tempSubject, tempMessage)
                    # print("Sending email", tempSubject, tempMessage)    #PY3
                    # print "Sending email" + tempSubject + tempMessage #PY2   

                if enableLogging == True:
                    now = datetime.now()
                    current_timeHMS = now.strftime("%H:%M:%S")
                    tempStr = "800, MISSED BLOCK, at," + current_timeHMS + ", before blk" + str(block) + "," + loopSeq    # removed seq
                    if fileOpenQM == False:
                        fileOpenQM = True
                        outFileQM = open(out_file_name_QM, 'a')
                    outFileQM.write(tempStr)
                    outFileQM.write('\n')
                    time.sleep(0.01)
                    outFileQM.close()
                    fileOpenQM = False      

            savedLoopSeq = loopSeq           # for logging above
            loopSeq = ""                     # reset the sequence string
            oldBlock = block                 # save for check next block
            firstTimeDontMissBlock = False   # allow check for missing block next time
            now = datetime.now()
            blockTime = now.strftime("%H:%M:%S") # save for use in stale block alert

            unixFoundBlockTime = int(time.time())
            
            # on average, subtract half of delayDateHours, but this understates the
            # superfast blocks, e.g., a 4 second block was logged as 3 seconds
            # so don't correct if the newDuration is under one minute

            if newDuration > 60:
                secondsSinceLastBlock = newDuration - int(delayDateHours/2)
            else:
                secondsSinceLastBlock = newDuration
                
            # print("Seconds since last block - found =", secondsSinceLastBlock)
            
            savedUnixBlockTime = int(time.time()) 	 # save for determining stale blocks
            blocksToday += 1        # count the blocks today, accurate if QM runs 24x7
            logNewBlock = True      # set to log the new block above

            staleBlockAging = 0     # reset to catch stale block below
            break

        else:
            unixBlockTime = int(time.time())

            if firstTimeThrough == True:
                savedUnixBlockTime = QMStartTime - 60  # kludge to set at startup, half the target block time                

            # print("Seconds since last block - not found =", secondsSinceLastBlock)

            if (unixBlockTime - QMStartTime) >= 1800:          # 30 minutes after QM start

                if unixBlockTime >= savedUnixBlockTime + 1800 and staleBlockAging == 0: # a half hour

                    staleBlockAging = 1             # start aging for next alert

                    print("ALERT: 30 minutes since last block ", block, "unixBlockTime =", unixBlockTime, "savedUnixBlockTime =", savedUnixBlockTime)        #PY3
                    # print "ALERT: 30 minutes since last block " + block + "unixBlockTime =" + unixBlockTime + "savedUnixBlockTime =" + savedUnixBlockTime  #PY2

                    # send an alert email

                    tempMessage = " " + hostName + " no blk since " + str(block) +" at " + blockTime   
                    tempSubject = ".BLOCK STALE"
            
                    if sendEmail == True:
                        send_email(tempSubject, tempMessage)
                        print("Sending email", tempSubject, tempMessage)     #PY3
                        # print "Sending email" + tempSubject + tempMessage  #PY2

                    if enableLogging == True:
                        tempStr = "900, BLOCK STALE, none since," + blockTime
                        if fileOpenQM == False:
                            fileOpenQM = True
                            outFileQM = open(out_file_name_QM, 'a')
                        outFileQM.write(tempStr)
                        outFileQM.write('\n')
                        time.sleep(0.01)
                        outFileQM.close()
                        fileOpenQM = False
                else:
                    if staleBlockAging >= 1:
                        staleBlockAging += 1
                        # print("staleBlockAging =", staleBlockAging)
                        if staleBlockAging >= 150:  # about 15 minutes
                            staleBlockAging = 0     # reset to send another email

        firstTimeThrough = False  # reset (and keep resetting) after first time through

        # date and hours waiting loop  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # print("date and hours loop, slack ", lastBlockCheckTime + delayDateHours - timer())
        # typical: date and hours loop, slack  2.6042726875139124
        
        while timer() <= lastBlockCheckTime + delayDateHours:

            time.sleep(0.3)

            unixTime = int(time.time())

            # End of day - make a new log file  - - - - - - - - - - - - - - - - - - - - - - - - - - -

            # do not break out of the date hours waiting loop for a new day

            # testUnixTime = unixTime - 4380

            # print("testUnixTime = ", testUnixTime, "testUnixTime % 86400 =", testUnixTime % 86400)

            if (unixTime % 86400) < 4 and didNewLog == False:  # catch the first four seconds of a new GMT day

                didNewLog = True            # toggle to only do one time for each new day
          
                if enableLogging == True:

                    blocksTodayFormatted = str(blocksToday)         # the number of blocks today, if QM running all day
                    
                    tempStr = "200, blocks," + blocksTodayFormatted
                    if fileOpenQM == False:
                        fileOpenQM = True
                        outFileQM = open(out_file_name_QM, 'a')   # open log file
                        # print("Opening file")

                    blocksToday = 0     # reset for new day

                    outFileQM.write(tempStr)
                    outFileQM.write('\n')
                    time.sleep(0.01)
                    outFileQM.close()
                    fileOpenQM = False

                print("Making new log file, new day")

                # initialize log file for new day
                if enableLogging == True:
                    GMT = strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())  # GMT
                    # open log file in the format "QM_Log_DD_MMM_YYYY.csv"
                    out_file_name_QM = 'QM_Log_'+GMT[5]+GMT[6]+'_'+GMT[8]+GMT[9]+GMT[10]+\
                                    '_'+GMT[12]+GMT[13]+GMT[14]+GMT[15]+'.csv'

                    print("QM log file name new day =", out_file_name_QM)    #PY3
                    # print "QM log file name new day =" + out_file_name_QM  #PY2

                    try: # create or open log file for appending
                        outFileQM = open(out_file_name_QM, 'a')
                        print("QM file open for appending")
                        # print("Opening file", out_file_name_QM, "on", GMT)
                        tempStr = '000,Program,start,or,restart,version,' + version
                        outFileQM.write(tempStr)
                        outFileQM.write('\n')
                        tempStr = '000,Logging,start,' + '_' + GMT[17]+GMT[18]+GMT[20]+GMT[21]+\
                                  ',hours,GMT,'+GMT[5]+GMT[6]+'_'+\
                                  GMT[8]+GMT[9]+GMT[10]+'_'+GMT[12]+GMT[13]+GMT[14]+GMT[15]
                        outFileQM.write(tempStr)
                        outFileQM.write('\n')
                        time.sleep(0.01)
                        outFileQM.write(logLabels) # write a row of column labels
                        outFileQM.write('\n')
                        time.sleep(0.01)
                        outFileQM.close()
                        fileOpenQM = False
                    except IOError:   # NOT WORKING
                        print("QM ERROR: File didn't exist, open for appending")
            elif didNewLog == True and (unixTime % 86400) >= 15:
                didNewLog = False   # kludge?

            # detect a new hour - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

            # start 4 seconds early because it takes some time to read process and process qtum-cli calls above

            unixTimeEarly = unixTime + 4    # go 4 seconds early, but compare to delayDateHour also
                                            # that is, if delayDateHour is reduced, consider
                                            # reducing this go early value too
                                            
            # print("unixTimeEarly =", unixTimeEarly)

            # catch the first four seconds of a new hour
            if (unixTimeEarly % 3600) <= 4 and didNewHour == False:
                didNewHour = True                              # block for the next few seconds
                sendEmailForNewHour = True
                breakOut = True         # break out of new block waiting loop, back to the top
                # print("breakOut, hour change, unixTime =", unixTime)
                break

            elif didNewHour == True and (unixTimeEarly % 3600) >= 10:
                didNewHour = False    # reset it for the next hour transtion
                # print("didNewHour set to False")

        # end of date hours waiting loop

    # end of while True, MAIN PROGRAM LOOP
