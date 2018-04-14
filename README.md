# QtumMon
A python script to monitor a wallet server app on the Qtum blockchain, log new blocks, and send emails/texts for PoS staking events.

Description:
A program to monitor the Qtum wallet server application qtumd application, send emails and logs activity. QtumMon uses qtum-cli to send RPC queries to the qtumd server application to identify staking events, and log various activities of the application. QtumMon sends a query to check for a new block approximately every 4 seconds. QtumMon will check that qtumd is running with staking enabled (ecrypted for staking).

Installation:
qtumd and QtumMon do not require any path setup. These files should be located in the same directory/folder, and both qtumd and QtumMon run from that directory. QtumMon will write the log files to that same directory. Python 2.7 or 3.6 should be installed.  For sending emails, an email account with login enabled for the Python script is required. See the document “Gmail Device Password Setup” for advice on how to enable this for Gmail.

Usage:
Use QtumMon for real-time monitoring of the qtumd server application. The program prints to the computer display to show various Qtum wallet parameters with each new block.

The program also writes a .csv file to local storage, for easy import and analysis in Excel.

JB395 is an independent researcher not affiliated with the Qtum Team.

For more information on Qtum see https://qtum.org

Credits:
Thanks to the Qtum Team for providing and open forum and great technical advice
to help the community grow and understand this powerful platform. From the QtumNexus Slack, thanks to @cryptominder and @Michael Anuzis for code comments.

--------------------------------------------

Python 3.6 and 2.7

To run with Python 2.7 edit all the print statements marked by "#PY3" and "#PY2"
(about 30 lines). To run in Python 2.7 comment out all the print functions
marked "#PY3" and uncomment out all the following print statements marked "#PY2".

Pre-GitHub Revisions

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

09/22/2017 All new


Key words
Qtum qtumd qtum-cli qtummon

