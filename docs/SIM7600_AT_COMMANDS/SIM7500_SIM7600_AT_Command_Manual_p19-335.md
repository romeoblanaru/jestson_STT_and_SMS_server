# SIM7500/SIM7600 Series AT Command Manual — Text Extract

- Source: `SIM7500_SIM7600_Series_AT_Command_Manual_V1.12.pdf`
- Pages: 19–335 (inclusive)
- Extracted with: PyPDF2
- Note: This is raw text; formatting, tables, and images are not preserved.


---

## Page 19

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 18 17.7 AT+CGPSAUTO  Start GPS automatic  ........................................................................................... 296 
17.8 AT+CGPSNMEA  Configure NMEA sentence type  ........................................................................ 297 
17.9 AT+CGPSNEMARATE   Set NMEA output rate  ........................................................................... 298 
17.10  AT+CGPSMD  Configure AGPS MO method  ................................................................................. 299 
17.11  AT+CGPSFTM  Start GPS test mode  .............................................................................................. 300 
17.12  AT+CGPSDEL  Delete the GPS information  ................................................................................... 301 
17.13  AT+CGPSXE  Enable/Disable GPS XTRA function  ....................................................................... 302 
17.14  AT+CGPSXD  Download XTRA assistant file  ................................................................................ 303 
17.15  AT+CGPSXDAUTO  Download XTRA assistant file automatically ............................................... 304 
17.16  AT+CGPSINFOCFG  Report GPS NMEA- 0183 sentence  .............................................................. 304 
17.17  AT+CGPSPMD  Configure positioning mode  ................................................................................. 306 
17.18  A T+CGPSMSB  Configure based mode switch to standalone  ......................................................... 307 
17.19  AT+CGPSHOR  Configure positioning desired accuracy  ................................................................ 308 
17.20  A T+CGPSNOTIFY  LCS respond positioning request  .................................................................... 309 
17.21  AT+CGNSSINFO  Get GNSS fixed position information  ............................................................... 310 
17.22  A T+CGNSSMODE  Configure GNSS support mode  ...................................................................... 312 
17.23  Unsolicited XTRA download Codes  .................................................................................................. 313 
17.24  AT+CLBS  Base station location  ...................................................................................................... 313 
17.25  AT+CLBSCFG  Base station location configure .............................................................................. 316 
17.26  AT+CASSISTLOC  Base station location of LTE/CDMA1x mode  ................................................. 317 
17.27  AT +CGP S IPV6   Set AGPS IPV6 ADDR & PORT  .......................................................................... 318 
17.28  AT+CGPSXTRADATA  Query  The Validity Of The Current  gpsOne Xtra Data  ............................ 319 
18 Audio Application Commands  ................................................................................................. 321  
18.1 A T+CREC   Record wav audio file  ................................................................................................. 321 
18.2 AT+CCMXPLAYWA V   Play wav audio file  .................................................................................. 322 
18.3 AT+CCMXSTOPWA V   Stop playing wav audio file  ..................................................................... 323 
18.4 AT+CCMXPLAY  Play audio file  .................................................................................................... 323 
18.5 AT+CCMXSTOP  Stop playing audio file  ....................................................................................... 325 
18.6 AT+CRECAMR   Record amr audio file  ........................................................................................ 325 
19 Appendixes .............................................................................................................................. 327  
19.1 Verbose code and numeric code  ......................................................................................................... 327 
19.2 Response string o f AT+CEER  ............................................................................................................ 327 
19.3 Summary of CME ERROR codes  ...................................................................................................... 331 
19.4 Summary of CMS ERROR codes ...................................................................................................... 334 
SIMCom Confidential File
---

## Page 20

1  Introduction 
1.1  Scope  
 
The present document describes the AT Command Set for the SIMCom Module: 
SIM7 500 series, SIM7600 series. 
 More information about the SIMCom Module which includes the Software Version information can be retrieved by the command ATI . In this document, a short description, the syntax, the possible setting values 
and responses, and some examples of AT commands are presented.  Prior to using the Module, please read this document and the Version History  to know the difference from 
the previous document.  In order to implement communication successfully between Customer Application and the Module, it is recommended to use the AT commands in this document, but not to use some commands which are not included in this document. 
1.2  References  
The present document is based on the following standards: 
[1] ETSI GSM 01.04: Abbreviations and acronyms. 
[2] 3GPP TS 27.005: Use of Data Terminal Equipment – Data Circuit terminating Equipment (DTE – 
DCE) interface for Short Message Service (SMS) and Cell Broadcast Service (CBS).  
[3] 3GPP TS 27.007: AT command set for User Equipment (UE). 
[4] WAP -224- WTP -20010710-a 
[5] WAP -230- WSP -20010705-a 
[6] WAP -209-MMSEncapsulation-20010601-a 
1.3  Terms and abbreviations  
For the purposes of the present document, the following abbreviations apply:  AT   ATtention; the two -character abbreviation is used to start a command line to be sent 
from TE/DTE to TA/DCE  
 DCE  Data Communication Equipment; Data Circuit terminating Equipment 
 DCS   Digital Cellular Network  
 DTE  Data Terminal Equipment 
SIMCom Confidential File
---

## Page 21

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 20  DTMF   Dual Tone Multi –Frequency 
 EDGE   Enhanced Data GSM Environment  
 EGPRS   Enhanced General Packet Radio Service 
 GPIO   General –Purpose Input/Output 
 GPRS   General Packet Radio Service 
 GSM   Global System for Mobile communications 
 HSDPA   High  Speed Downlink Packet Access  
 HSUPA   High Speed Uplink Packet Access  
 I2C  Inter–Integrated Circuit  
 IMEI   International Mobile station Equipment Identity 
 IMSI   International Mobile Subscriber Identity 
 ME  Mobile Equipment 
 MO  Mobile –Originated  
 MS   Mobile Station  
 MT  Mobile –Terminated; Mobile Termination  
 PCS  Personal Communication System 
 PDU  Protocol Data Unit 
 PIN  Personal Identification Number 
 PUK   Personal Unlock Key  
 SIM  Subscriber Identity Module 
 SMS   Short Message Service  
 SMS –SC Short Message Service  – Service Center  
 TA   Terminal Adaptor; e.g. a data card (equal to DCE) 
 TE   Terminal Equipment; e.g. a computer (equal to DTE) 
 UE   User Equipment 
 UMTS   Universal Mobile Telecommunications System 
 USIM   Universal Subscriber Identity Module 
 WCDMA  Wideband Code Division Multiple Access  
 FTP         File Transfer Protocol  
 HTTP       Hyper Text Transfer Protocol  
 RTC        Real Time Clock  
 URC        Unsolicited Result Code  
1.4  Definitions and conventions  
1. For the purposes of the present document, the following synt actical definitions apply:  
<CR>   Carriage return character. 
<LF>   Linefeed character.  
<…>  Name enclosed in angle brackets is a syntactical element. Brackets themselves do not 
appear in the command line. 
[…] Optional subparameter of AT command or an optional part of TA information response 
is enclosed in square brackets. Brackets themselves do not appear in the command line. 
SIMCom Confidential File
---

## Page 22

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 21 If subparameter is not given, its value equals to its previous value or the recommended 
default value.  
underline  Underlined defined subparameter value is the recommended default setting or factory 
setting.  
2. Document conventions: 
♦ Display the examples of AT commands with Italic  format.  
♦ Not display blank- line between command line and responses or inside the responses. 
♦ Generally, the character s <CR> and <LF>  are intentionally omitted throughout this document. 
♦ If command response is ERROR, not list the ERROR response inside command syntax. 
NOTE:  AT commands and responses in figures may be not following above conventions. 
3. Special marks for comman ds or parameters:  
SIM PIN   –  Is the command PIN protected? 
    Y ES  –  AT command can be used only when SIM PIN is READY. 
NO  –  AT command can be used when SIM card is absent or SIM PIN validation is 
pending. 
 References   –  Where is the derivation of co mmand?  
     3GPP TS 27.007  –  3GPP Technical Specification 127 007. 
     V.25ter     –  ITU –T Recommendation V.25ter.  
     Vendor     –  This command is supported by SIMCom. 
SIMCom Confidential File
---

## Page 23

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 22  
2  AT Interface Synopsis  
2.1  Interface settings  
Between Customer Application and the Module, standardized RS –232 interface is used for the 
communication, and default values for the interface settings as following: 
115200bps, 8 bit data, no parity, 1 bit stop , no data stream control. 
2.2  AT command syntax  
The prefix “ AT” or “ at” (no case sens itive) must be included at the beginning of each command line 
(except A/ and +++), and the character <CR>  is used to finish a command line so as to issue the command 
line to the Module. It is recommended that a command line only includes a command. 
When Customer Application issues a series of AT commands on separate command lines, leave a pause 
between the preceding and the following command until information responses or result codes are retri eved 
by Customer Application, for example, “OK” is appeared. This advice avoids too many AT commands are issued at a time without waiting for a response for each command. 
In the present document, AT commands are divided into three categories: Basic Command , S Parameter 
Command , and Extended Command. 
1. Basic Command 
The format of Basic Command is “AT<x><n>” or “AT&<x><n>”, “<x>” is the command name, and “ <n>” 
is/are the parameter(s) for the basic command, and optional. An example of Basic Command is “ATE <n>”, 
which informs the TA/DCE whether received characters should be echoed back to the TE/DTE according to 
the value of “<n> ”; “<n>” is optional and a default value will be used if omitted. 
2. S Parameter Command  
The format of S Parameter Command is “ATS <n>=<m>”, “<n>” is the index of the S –register to set, and 
“<m> ” is the value to assign to it. “ <m> ” is optional; in this case, the format is “ ATS<n>”, and then a 
default value is assigned.  
3. Extended Command  
The Extended Command has several formats, as following tabl e list:  
 
 
SIMCom Confidential File
---

## Page 24

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 23 Table 2 -1: Types of Extended Command 
Command Type  Syntax Comments  
Test Command  AT+<NAME>=?  Test the existence of the command; give some 
information about the command subparameters. 
Read Command  AT+<NAME>?  Check the current values of subparameters.  
Write Command  AT+<NAME>=<…> Set user -definable subparameter values.  
Execution Command AT+<NAME>  Read non -variable subparameters determined by 
internal processes.  
NOTE:  The character “+” between the prefix “AT” and command name may be replaced by oth er 
character. For example, using “#” or “$”instead of “+”.  
2.3  Information responses  
If the commands included in the command line are supported by the Module and the subparameters are 
correct if presented, some information responses will be retrieved by from the Module. Otherwise, the 
Module will report “ERROR” or “+CME ERROR” or “+CMS ERROR” to Customer Application. 
Information responses start and end with <CR><LF>, i.e. the format of information responses is 
“<CR><LF><response> <CR><LF>”. Inside information responses, there may be one or more <CR><LF>. 
Throughout this document, only the responses are presented, and <CR><LF>  are intentionally omitted.  
SIMCom Confidential File
---

## Page 25

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 24  
3  AT Commands According V.25TER 
3.1  A/  Repeat last command  
Description  
This command is used for implement previous AT command repeatedly (except A/), and the return 
value depends on the last AT command. If A/  is issued to the Module firstly after power on, the 
response “OK” is only returned. 
 
SIM PIN  References  
NO V.25ter  
Syntax 
Execu tion Command Responses 
A/ The response the last AT command return  
Examples 
AT+GCAP  
+GCAP:+CGSM,+FCLASS,+DS  
OK 
A/ 
+GCAP:+CGSM,+FCLASS,+DS  
OK 
3.2  ATD  Dial command  
Description  
This command is used to list characters that may be used in a dialling string f or making a call or 
controlling supplementary services. 
NOTE:  
1. Support several “P” or “p” in the DTMF string but the valid auto- sending DTMF after characters 
“P” or “p” should not be more than 29. 
2. Auto -sending DTMF after character “P” or “p” should be ASCI I character in the set 0 -9, *, #.  
SIM PIN  References  
NO V25.ter 
SIMCom Confidential File
---

## Page 26

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 25 Syntax 
Execution Commands  Responses 
ATD <n>[<mgsm> ][;] Originate a voice call successfully:  
OK 
VOICE CALL: BEGIN  
Originate a data call successfully:  
CONNECT [ <text> ] 
Originate a call u nsuccessfully during command execution:  
ERROR 
Originate a call unsuccessfully for failed connection recovery:  
NO CARRIER  
Originate a call unsuccessfully for error related to the MT:  
+CME ERROR: <err>  
Defined values  
<n> 
String of dialing digits and op tionally V.25ter modifiers dialing digits:  
0  1  2  3  4  5  6  7  8  9  *  #  +  A  B  C  
Following V.25ter modifiers are ignored:  
,  T  P  !  W  @  
<mgsm>  
String of GSM modifiers:  
I    Activates CLIR (disables presentation of own phone number to called party)  
i    Deactivates CLIR (enables presentation of own phone number to called party) 
G   Activate Closed User Group explicit invocation for this call only  
    g    Deactivate Closed User Group explicit invocation for this call only  
<;> 
The terminatio n character ";" is mandatory to set up voice calls. It must not be used for data and fax 
calls.  
<text>  
CONNECT result code string; the string formats please refer ATX/AT \V/AT&E command.  
<err>  
Service failure result code string; the string formats please refer +CME ERROR result code and 
AT+CMEE command. 
Examples 
ATD10086; 
OK 
VOICE CALL:BEGIN  
SIMCom Confidential File
---

## Page 27

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 26 3.3  ATD><mem><n>  Originate call from specified memory  
Description  
This command is used to originate a call using specified memory and index number. 
SIM PIN  References  
NO V.25ter 
Syntax 
Execution Commands  Responses  
ATD> <mem><n>[ ;] Originate a voice call successfully:  
OK 
VOICE CALL: BEGIN  
Originate a data call successfully:  
CONNECT [ <text> ] 
Originate a call unsuccessfully during command execution:  
ERROR 
Originate a call unsuccessfully for failed connection recovery:  
NO CARRIER  
Originate a call unsuccessfully for error related to the MT:  
+CME ERROR: <err>  
Defined values  
<mem>  
Phonebook storage: (For detailed description of storages see AT+CPBS ) 
"DC"   ME di aled calls list  
"MC"     ME missed (unanswered received) calls list  
"RC"    ME received calls list  
"SM"    SIM phonebook 
"ME"    UE phonebook 
"FD"    SIM fixed dialing phonebook 
"ON"      MSISDN l ist  
"LD"      Last number dialed phonebook  
"EN"      Emergency n umbers  
<n> 
Integer type memory location in the range of locations available in the selected memory, i.e. the 
index returned by AT+CPBR. 
<;> 
The termination character ";" is mandatory to set up voice calls. It must not be used for data and fax 
calls.  
SIMCom Confidential File
---

## Page 28

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 27 <text>  
CONNECT result code string; the string formats please refer ATX/AT \V/AT&E command.  
<err>  
Service failure result code string; the string formats please refer +CME ERROR result code and 
AT+CMEE command. 
Examples 
ATD>SM3; 
OK 
VOICE CALL: BEGIN  
3.4  ATD ><n>  Originate call from active memory (1)  
Description  
This command is used to originate a call to specified number. 
SIM PIN  References  
NO V.25ter  
Syntax 
Execution Commands  Responses 
ATD> <n>[;] Originate a voice call successfully:  
OK 
VOICE CALL: BEGIN  
Originate a data call successfully:  
CONNECT [ <text> ] 
Originate a call unsuccessfully during command execution:  
ERROR 
Originate a call unsuccessfully for failed connection recovery:  
NO CARRIER  
Originate a call unsuccessfully for error related to the MT:  
+CME ERROR: <err>  
Defined values  
<n> 
Integer type memory location in the range of locations available in the selected memory, i.e. the          
index number returned by  AT+CPBR . 
<;> 
The termination character ";" is mandatory to set up voice calls . It must not be used for data and fax 
SIMCom Confidential File
---

## Page 29

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 28 calls.  
<text>  
CONNECT result code string; the string formats please refer ATX/AT \V/AT&E command.  
<err>  
Service failure result code string; the string formats please refer +CME ERROR result code and 
AT+CMEE command . 
Examples 
ATD>2;  
OK 
VOICE CALL: BEGIN  
3.5  ATD><str>  Originate call from active memory (2)  
Description  
This command is used to originate a call to specified number.  
SIM PIN  References  
NO V.25ter 
Syntax 
Execution Commands  Responses 
ATD> <str> [;] Origina te a voice call successfully:  
OK 
VOICE CALL: BEGIN  
Originate a data call successfully:  
CONNECT [ <text> ] 
Originate a call unsuccessfully during command execution:  
ERROR  
Originate a call unsuccessfully for failed connection recovery:  
NO CARRIER  
Origi nate a call unsuccessfully for error related to the MT:  
+CME ERROR: <err>  
Defined values  
<str>  
String type value, which should equal to an alphanumeric field in at least one phone book entry in 
the searched memories. <str> formatted as current TE charact er set specified by AT+CSCS .<str>  
must be double quoted. 
SIMCom Confidential File
---

## Page 30

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 29 <;> 
The termination character ";" is mandatory to set up voice calls. It must not be used for data and fax 
calls.  
<text>  
CONNECT result code string; the string formats please refer ATX/AT \V/AT&E command. 
<err>  
Service failure result code string; the string formats please refer +CME ERROR result code and 
AT+CMEE command. 
Examples 
ATD>”Kobe”;  
OK 
VOICE CALL: BEGIN  
3.6  ATA  Call answer  
Description  
This command is used to make remote station to go of f-hook, e.g. answer an incoming call. If there 
is no an incoming call and entering this command to TA, it will be return “ NO CARRIER ” to TA.  
SIM PIN  References  
YES V.25ter 
Syntax 
Execution Commands  Responses  
ATA  For voice call:  
OK 
VOICE CALL: BEGIN   
For data call, and TA switches to data mode:  
CONNECT  
No connection or no incoming call:  
NO CARRIER  
Examples 
ATA 
VOICE CALL: BEGIN  
OK 
SIMCom Confidential File
---

## Page 31

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 30 3.7  ATH  Disconnect existing call  
Description  
This command is used to disconnect existing call. Before using ATH  command to hang up a voice 
call, it must set AT+CVHU=0 . Otherwise, ATH command will be ignored and “ OK” response is 
given only.  
This command is also used to disconnect PS data call, and in this case it doesn’t depend on the value of AT+CVHU . 
SIM PIN  References  
NO V.25ter 
Syntax 
Execution Command Responses 
ATH  If AT+CVHU =0: 
VOICE CALL: END: <time>  
OK 
OK 
Defined values  
<time>  
Voice call connection time:  
Format  –  HHMMSS (HH: hou r, MM: minute, SS: second) 
Examples 
AT+CVHU=0  
OK 
ATH 
VOICE CALL:END:000017  
OK 
3.8  ATS0  Automatic answer incoming call  
Description  
The S -parameter command controls the automatic answering feature of the Module. If set to 000, 
automatic answering is disab led, otherwise it causes the Module to answer when the incoming call 
indication (RING) has occurred the number of times indicated by the specified value; and the 
setting will not be stored upon power- off, i.e. the default value will be restored after restart.  
SIM PIN  References  
SIMCom Confidential File
---

## Page 32

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 31 YES  V.25ter  
Syntax 
Read Command  Responses 
ATS0?  <n> 
OK 
ERROR  
Write Command  Responses  
ATS0= <n> OK 
ERROR  
Defined values  
<n> 
    000    Automatic answering mode is disable. (default value when power-on) 
001–255  Enable automa tic answering on the ring number specified.  
NOTE: 1.The S- parameter command is effective on voice call and data call.  
2.If <n> is set too high, the remote party may hang up before the call can be answered 
automatically.  
Examples 
ATS0? 
000 
OK 
ATS0=003 
OK 
3.9  +++  Switch from data mode to command mode  
Description  
This command is only available during a connecting PS data call. The +++ character sequence 
causes the TA to cancel the data flow over the AT interface and switch to Command Mode. This 
allows to enter AT commands while maintaining the data connection to the remote device. 
NOTE:  To prevent the +++ escape sequence from being misinterpreted as data, it must be preceded 
and followed by a pause of at least 1000 milliseconds, and the interval between two ‘+’ character 
can’t exceed 900 milliseconds.  
SIM PIN  References  
YES  V.25ter  
SIMCom Confidential File
---

## Page 33

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 32 Syntax 
Execution Command  Responses 
+++ OK 
Examples 
+++ 
OK 
3.10  ATO  Switch from command mode to data mode  
Description  
ATO  is the corresponding command to the +++  escape sequence. When there is a PS data call 
connected and the TA is in Command Mode, ATO  causes the TA to resume the data and takes back 
to Data Mode.  
SIM PIN  References  
YES V.25ter 
Syntax 
Execution Command Responses 
ATO  TA/DCE switches to Data Mode from Command Mode:  
CONNECT [ <baud rate>]  
If connection is not successfully resumed: 
NO CARRIER  
ERROR  
Examples 
ATO 
CONNECT 115200  
3.11  ATI  Display product identification information  
Description  
This command is used to request the product information, which consists of manufacturer 
identification, model identification, revision identification, International Mobile station Equipment 
Identity (IMEI) and overall capabilities of the product. 
SIM PIN  References  
SIMCom Confidential File
---

## Page 34

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 33 NO V.25ter  
Syntax 
Execution Command Responses 
ATI Manufacturer: <manufacturer>  
Model: <model>  
Revision: <revision>  
IMEI: [ <sn> ] 
+GCAP: list of <name> s 
 
OK 
Defined values 
<manufacturer>  
The identification of manufacturer. 
<model>  
The identification of model. 
<revision>  
The revision identification of firmware.  
<sn>  
Serial number identification, which consists of a single line containing IMEI (International Mobile 
station Equipment Identity) number. 
<name>  
List of additional capabilities:  
 +CGSM     GSM function is supported 
 +FCLASS   FAX function is supported 
 +DS      Data compression is supported 
+ES         Synchronous data mode is supported.  
 +CIS707- A  CDMA data service command set  
 +CIS -856    EVDO data service command set  
 +MS        Mobile Specific command set  
Examples 
ATI 
Manufacturer: SIMCOM INCORPORATED  
Model: SIMCOM_SIM7600C  
Revision: SIM 7600C  _V1.0  
IMEI: 351602000330570 
+GCAP: +CGSM,+FCLASS,+DS 
 
SIMCom Confidential File
---

## Page 35

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 34 OK 
3.12  AT+IPR  Set local baud rate temporarily  
Description  
This command sets the baud rate of module’s serial interface temporarily, after reboot the baud rate 
is set to value of  IPREX.  
SIM PIN  References  
NO V.25ter 
Syntax 
Test Command  Responses 
AT+IP R=? +IPR: (list of supported <speed> s) 
OK 
Read Command  Responses 
AT+IPR?  +IPR: <speed>  
OK 
Write Command  Responses  
AT+IPR= <speed>  OK 
ERROR 
Execution Command Responses  
AT+IPR  Set the  value to boot value: 
OK 
Defined values  
<speed>  
Baud rate per secon d: 
0, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800,921600,  
3000000,3200000,3686400 
 
Note: LE20 doesn’t support 0.  
Examples 
AT+IPR?  
+IPR: 115200 
OK 
AT+IPR=?  
+IPR:(0,300,600,1200,2400,4800,9600,19200,38400,57600,115200,230400,460800,921600, 
3000000,3200000,3686400) 
SIMCom Confidential File
---

## Page 36

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 35 OK 
AT+IPR=115200  
OK 
AT+IPR=0  
OK 
3.13  AT+ICF  Set control character framing  
Description  
This command sets character framing which contains data bit, stop bit and parity bit. 
SIM PIN  References  
NO Vendor  
Synt ax 
Test Command  Responses 
AT+ICF=?  +ICF: (list of supported <format> s), (list of supported <parity> s) 
OK 
Read Command  Responses 
AT+ICF?  +ICF: <format> ,<parity>  
OK 
Write Command  Responses 
AT+ICF=  
<format> [,<parity> ] OK 
ERROR 
Execution Command  Responses  
AT+ICF  Set default value:  
OK 
Defined values  
<format>  
1  –  data bit 8, stop bit 2 
2  –  data bit 8, parity bit 1,stop bit 1  
3  –  data bit 8, stop bit 1 
4  –  data bit 7, stop bit 2 
5  –  data bit 7, parity bit 1,stop bit 1  
6  –  data bit 7, stop bit 1 
<parity>  
0  –  Odd 
1  –  Even 
2  –  Space 
SIMCom Confidential File
---

## Page 37

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 36 3  –  none 
Examples 
AT+ICF?  
+ICF: 3,3  
OK 
AT+ICF=?  
+ICF: (1 -6),(0 -3) 
OK 
AT+ICF=3,3  
OK 
3.14  AT+IFC  Set local data flow control  
Description  
The command sets the flow control mode of the module.  
SIM PIN  References  
NO V.25ter  
Syntax   
Test Command  Responses 
AT+IFC=?  +IFC: (list of supported <DCE> s), (list of supported <DTE> s) 
OK 
ERROR  
Read Command  Responses 
AT+IFC?  +IFC: <DCE> ,<DTE>  
OK 
ERROR 
Write Command  Responses  
AT+IFC=<DCE> [,<DTE> ] OK 
ERROR 
Execu tion Command  Responses  
AT+IFC  Set default value:  
OK 
ERROR  
Defined values  
<DCE>  
SIMCom Confidential File
---

## Page 38

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 37 0  –  none (default) 
2  –  RTS hardware flow control 
 
<DTE>  
0  –  none (default) 
2  –  CTS hardware flow control 
Examples 
AT+IFC?  
+IFC: 0,0  
OK 
AT+IFC=?  
+IFC: (0,2),(0 ,2) 
OK 
AT+IFC=2,2  
OK 
3.15  AT&C  Set DCD function mode  
Description  
This command determines how the state of DCD PIN relates to the detection of received line signal 
from the distant end. 
SIM PIN  References  
NO V.25ter 
Syntax 
Execution Command  Responses  
AT&C[<value> ] OK 
ERROR 
Defined values  
<value>  
  0  DCD line shall always be on.  
  1  DCD line shall be on only when data carrier signal is present.  
  2  Setting winks(briefly transitions off,then back on)the DCD line when data calls end.  
Examples 
AT&C1  
OK 
SIMCom Confidential File
---

## Page 39

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 38 3.16  ATE  Enable command echo  
Description  
This command sets whether or not the TA echoes characters.  
SIM PIN  References  
NO V.25ter 
Syntax 
Execution Command  Responses  
ATE[ <value> ] OK 
ERROR 
Defined values  
<value>  
0  –  Echo mode off 
1  –  Echo mode  on 
Examples 
ATE1  
OK 
3.17  AT&V  Display current configuration 
Description  
This command returns some of the base configuration parameters settings. 
SIM PIN  References  
YES V.25ter 
Syntax 
Execution Command Responses 
AT&V  <TEXT>  
OK 
ERROR 
Defined values  
<TEXT>  
SIMCom Confidential File
---

## Page 40

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 39 All relative configuration information.  
Examples 
AT&V  
&C: 0; &D: 2; &F: 0; E: 1; L: 0; M: 0; Q: 0; V: 1; X: 0; Z: 0; S0: 0;  
S3: 13; S4: 10; S5: 8; S6: 2; S7: 50; S8: 2; S9: 6; S10: 14; S11: 95; 
+FCLASS: 0; +ICF: 3,3; +IFC: 2,2; +IPR: 115200; +DR: 0; +DS: 0,0,2048,6; 
+WS46: 12; +CBST: 0,0,1; 
…… 
OK 
3.18  AT&D  Set DTR function mode  
Description  
This command determines how the TA responds when DTR PIN is changed from the ON t
o the OFF condition during data mode.  
SIM PIN  References  
NO V.25ter 
Syntax 
Execution Command Responses 
AT&D[ <value> ] OK 
ERROR  
Defined values  
<value>  
  0  TA ignores status on DTR.  
  1  ON ->OFF on DTR: Change to Command mode with remaining the connected call  
  2  ON->OFF on DTR: Disconnect call, change to Command mode.During stat e DTR = 
OFF is auto -answer off.  
Examples 
AT&D1  
OK 
3.19  AT&S  Set DSR function mode  
Description  
SIMCom Confidential File
---

## Page 41

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 40 The command determines how the state of DSR pin works. 
SIM PIN  References  
YES V.25ter 
Syntax 
Execution Command Responses 
AT&S <value>  OK 
ERROR  
Defined values  
<value>  
  0  DSR line shall always be on.  
  1  DSR line shall be on only when DTE and DCE are connected.  
Examples 
AT&S0  
OK 
3.20  ATV  Set result code format mode 
Description  
This parameter setting determines the contents of the header and trailer transmi tted with result 
codes and information responses. 
NOTE:  In case of using This command without parameter <value > will be set to 0.  
SIM PIN  References  
No V.25ter  
Syntax 
Write Command  Responses 
ATV[ <value> ] If <value> =0  
0  
If <value> =1  
OK 
Defined value s 
<value>  
0  Information response: <text><CR><LF>   
SIMCom Confidential File
---

## Page 42

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 41 Short result code format: <numeric code><CR>   
1  Information response: <CR><LF><text><CR><LF>  
Long result code format: <CR><LF><verbose code><CR><LF>  
Examples 
ATV1  
OK 
 
3.21  AT&F  Set all current parameter s to manufacturer defaults  
Description   
This command is used to set all current parameters to the manufacturer defined profile. 
NOTE :List of parameters reset to manufacturer default can be found in defined values, factory 
default settings restorable with A T&F[ <value> ]. 
Every ongoing or incoming call will be terminated. 
SIM PIN  References  
NO V.250 
Syntax 
Execution Command Responses 
AT&F[ <value> ] OK 
Defined values  
<value>  
0 —  Set some temporary TA parameters to manufacturer defaults. The setting after power on or reset is 
same as value 0.  
default values 
TA parameters  V ALUE  
AT+CATR  0 
AT+CNMP  2 
AT+CNAOP ① 7,9,4,2,5,3,11 
AT+CTZU  0 
① The default value of no CDMA/EVDO version is 7,9,5,3,11,2,4 
Examples 
AT&F  
OK 
SIMCom Confidential File
---

## Page 43

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 42 3.22  ATQ  Set Result Code Presentation Mode  
Description   
Specify whether the TA transmits any result code to the TE or not. Text information transmitted in 
response is not affected by this setting  
SIM PIN  References  
YES  3GPP TS 27.005  
Syntax 
Write Command  Responses 
ATQ<n>  If <n>=0:  
OK 
If <n>=1:  
No Responses  
Execution Command Responses 
ATQ  Set default value:0  
OK 
No Responses  
Defined values  
<n> 
0  –  DCE transmits result code  
1  –  DCE not transmits result code  
Examples 
ATQ0 
OK 
3.23  ATX  Set CONNECT Result Cod e Format  
Description   
This parameter setting determines whether the TA transmits unsolicited result codes or not. The 
unsolicited result codes are 
<CONNECT><SPEED><COMMUNICATION PROTOCOL>[<TEXT>]  
SIM PIN  References  
YES 3GPP TS 27.005 
SIMCom Confidential File
---

## Page 44

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 43 Syntax 
Write Comman d Responses 
ATX<VALUE>  OK 
ERROR 
Execution Command  Responses  
ATX  Set default value:1  
OK 
ERROR  
Defined values  
<value>  
0  –  CONNECT result code returned  
1,2,3,4  –  May be transmits extern result codes according to AT&E and AT \V settings. Refer to 
AT&E.  
Examples 
ATX1  
OK 
3.24  AT\V  Set CONNECT Result Code Format About Protocol  
Description   
This parameter setting determines whether report the communication protocol. If PS call, it also 
determines wether report APN, uplink rate, downlink rate. 
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Write Command  Responses  
AT\V<value>  OK 
ERROR 
Execution Command Responses 
AT\V Set default value: 0  
OK 
ERROR 
Defined values  
SIMCom Confidential File
---

## Page 45

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 44 <value>  
0  –  Don’t report 
1  –  Report communication protocol. And report APN, uplink rate, downlink rate if PS call. 
Refer to AT&E. The maybe communication protocol report include 
“NONE”,”PPPoverUD”,”A V32K”,”AV64K”,”PACKET”. And APN in string format while 
uplink rate and downlink rate in integer format with kb unit. 
Examples 
AT\V0 
OK 
3.25  AT&E  Set CONNECT Result Code Format About Speed  
Description   
This parameter setting determines to report Serial connection rate or Wireless connection speed. It 
is valid only ATX above 0. 
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Write Command  Respo nses 
AT&E<value>  OK 
ERROR  
Execution Command  Responses  
AT&E  Set default value: 1  
OK 
Defined values  
<value>  
0  –  Wireless connection speed in integer format.  
1  –  Serial connection rate in integer format. Such as: “115200” 
Examples 
AT&E0  
OK 
SIMCom Confidential File
---

## Page 46

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 45 3.26  AT&W   Save the user setting to ME  
Description   
This command will save the user settings to ME which set by ATE, ATQ, ATV, ATX, AT&C AT&D, 
AT&S, AT \V, AT+IFC and ATS0.  
SIM PIN  References  
YES  3GPP TS 27.005  
Syntax 
Write Command  Responses 
AT&W<value>  OK 
ERR OR 
Execution Command Responses 
AT&W  Set default value: 0  
OK 
ERROR 
Defined values  
<value>  
0  –  Save  
Examples 
AT&W0  
OK 
3.27  ATZ  Restore the user setting from ME  
Description   
This command will restore the user setting from ME which set by ATE, ATQ, ATV , ATX, AT&C 
AT&D, AT&S, AT \Q , AT \V, and ATS0.  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Write Command  Responses  
ATZ<value>  OK 
SIMCom Confidential File
---

## Page 47

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 46 ERROR  
Execution Command Responses 
ATZ  Set default value: 0  
OK 
ERROR  
Defined values  
<value>  
0  –  Restore  
Examples 
ATZ0  
OK 
3.28  AT+CGMI  Request manufacturer identification  
Description  
This command is used to request the manufacturer identification text, which is intended to permit 
the user of the Module to identify the manufacturer. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGMI=?  OK 
Execution Command Responses 
AT+CGMI  <manufacturer>  
OK 
Defined values  
<manufacturer>  
The identification of manufacturer.  
Examples 
AT+CGMI  
SIMCOM INCORPORATED  
OK 
SIMCom Confidential File
---

## Page 48

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 47 3.29  AT+CGMM  Request model identification  
Description  
This command is used to requests model identification text, which is intended to permit the user of 
the Module to identify the specific model.  
SIM PIN  References  
NO 3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CGMM=?  OK 
Execution Command Responses 
AT+CGMM  <model> 
OK 
Defined values  
<model>  
The identification of model. 
Examples 
AT+CGMM  
SIMCOM_SIM7600C  
OK 
3.30  AT+CGMR  Request revision identification  
Description  
This command is used to request product firmware revision identification text, which is intended to 
permit the user of the Module to identify the version.  
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGMR=?  OK 
Execution Command  Responses  
SIMCom Confidential File
---

## Page 49

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 48 AT+CGMR  +CGMR : <revision>  
OK 
Defined values  
<revision>  
The revis ion identification of firmware.  
Examples 
AT+CGMR  
+CGMR:  LE1 1B01SIM7600C 
OK 
3.31  AT+CGSN  Request product serial number identification  
Description  
This command requests product serial number identification text, which is intended to permit the 
user of the Mo dule to identify the individual ME to which it is connected to. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGSN=?  OK 
Execution Command Responses 
AT+CGSN  <sn>  
OK 
+CME ERROR: memory failure  
Defined values  
<sn>  
Serial number identification, which consists of a single line containing the IMEI (International 
Mobile station Equipment Identity) number of the MT. 
If in CDMA/EVDO mode ,it will show ESN(Electronic Serial Number)  
Examples 
AT+CGSN  
351602000330570 
SIMCom Confidential File
---

## Page 50

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 49 OK 
AT+CGSN (CDMA /EVDO mode)  
0x8059D1F6  
OK 
 
3.32  AT+CSCS  Select TE character set  
Description  
Write command informs TA which character set <chest>  is used by the TE. TA is then able to 
convert character strings correctly between TE and MT character sets.  
Read command shows c urrent setting and test command displays conversion schemes implemented 
in the TA.  
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CSCS=?  +CSCS: (list of supported <chset> s) 
OK 
Read Command  Responses 
AT+CSCS?  +CSCS: <chset>  
OK 
Write Command  Responses 
AT+CSCS= <chset>  OK 
ERROR  
Execution Command Responses 
AT+CSCS  Set subparameters as default value:  
OK 
Defined values  
<chest>  
Character set, the definition as following:  
“IRA”   International reference alphabet.  
“GSM”  GSM defaul t alphabet; this setting causes easily software flow control (XON 
/XOFF) problems. 
“UCS2”  16- bit universal multiple -octet coded character set; UCS2 character strings are 
converted to hexadecimal numbers from 0000 to FFFF. 
SIMCom Confidential File
---

## Page 51

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 50 Examples 
AT+CSCS=”IRA”  
OK 
AT+CS CS? 
+CSCS:”IRA”  
OK 
3.33  AT+CIMI  Request international mobile subscriber identity  
Description  
Execution command causes the TA to return <IMSI> , which is intended to permit the TE to identify 
the individual SIM card which is attached to MT. 
NOTE: If USIM card  contains two apps, like China Telecom 4G card, one RUIM/CSIM app, and 
another USIM app; so there are two IMSI in it; AT+CIMI will return the RUIM/CSIM IMSI; 
AT+CIMIM will return the USIM IMSI;  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CIMI=?  OK 
ERROR 
Execution Command  Responses  
AT+CIMI  <IMSI>  
OK 
ERROR 
Defined values  
<IMSI>  
International Mobile Subscriber Identity (string, without double quotes). 
Examples 
AT+CIMI  
460010222028133  
OK 
SIMCom Confidential File
---

## Page 52

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 51 3.34  AT+CIMIM  Request another international mobile subscriber identity  
Description  
Execution command causes the TA to return <IMSI> , which is intended to permit the TE to identify 
the individual SIM card which is attached to MT. 
NOTE: If USIM card contains two apps, like China Telecom 4G card, one RUIM/CSIM app, and another USIM app; so there are two IMSI in it; AT+CIMIM will return the USIM IMSI; AT+CIMI will return the RUIM/CSIM IMSI;  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CIMIM=?  OK 
ERROR  
Execution C ommand  Responses  
AT+CIMIM  <IMSI>  
OK 
ERROR 
Defined values  
<IMSI>  
International Mobile Subscriber Identity (string, without double quotes).  
Examples 
AT+CIMIM  
460110222028133 
OK 
3.35  AT+GCAP  Request overall capabilities  
Description  
Execution command caus es the TA reports a list of additional capabilities.  
SIM PIN  References  
YES  V.25ter  
Syntax 
SIMCom Confidential File
---

## Page 53

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 52 Test Command  Responses  
AT+GCAP=?  OK 
ERROR  
Execution Command  Responses  
AT+GCAP  +GCAP: (list of <name> s) 
OK 
ERROR 
Defined values  
<name>  
List of additional capabilities.  
 +CGSM     GSM function is supported 
 +FCLASS  FAX function is supported 
 +DS      Data compression is supported 
+ES         Synchronous data mode is supported.  
 +CIS707- A   CDMA data service command set  
 +CIS -856    EVDO data service command set  
+MS        Mobile Specific command set  
Examples 
AT+GCAP  
+GCAP:+CGSM,+FCLASS,+DS  
OK 
 
 
SIMCom Confidential File
---

## Page 54

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 53  
4  AT Commands for Status Control  
4.1  AT+CFUN  Set phone functionality 
Description  
This command is used to select the level of functionality <fun>  in the ME. Level "fu ll 
functionality" is where the highest level of power is drawn. "Minimum functionality" is where 
minimum power is drawn. Level of functionality between these may also be specified by 
manufacturers. When supported by manufacturers, ME resetting with <rst>  parameter may be 
utilized.  
NOTE: AT+CFU N =6 must be used after setting AT+CFUN =7. If module in offline mode, must 
execute AT+CFU N =6 or restart module to online mode. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CFUN=?  +CFUN: (lis t of supported <fun> s), (list of supported <rst> s) 
OK 
ERROR 
+CME ERROR: <err>  
Read Command  Responses 
AT+CFUN?  +CFUN: <fun>  
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses  
AT+CFUN= <fun> [,<rst> ] OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<fun> 
0  –  minimum functionality  
1  –  full functionality, online mode 
SIMCom Confidential File
---

## Page 55

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 54 4  –  disable phone both transmit and receive RF circuits  
5  –  Factory Test Mode 
6  –  Reset  
7  –  Offline Mode 
<rst>  
0  –  do not reset the ME before setting it to <fun>  power level 
1  –  reset the ME before setting it to <fun>  power level.  This value only takes effect when 
<fun> equals 1. 
Examples 
AT+CFUN?  
+CFUN: 1  
OK 
AT+CFUN=0  
OK 
4.2  AT+CPIN  Enter PIN 
Description  
This command is used to send the ME a password which is necessary  before it can be operated 
(SIM PIN, SIM PUK, PH -SIM PIN, etc.). If the PIN is to be entered twice, the TA shall 
automatically repeat the PIN. If no PIN request is pending, no action is taken towards MT and an 
error message, +CME ERROR, is returned to TE.  
If the PIN required is SIM PUK or SIM PUK2, the second pin is required. This second pin, 
<newpin> , is used to replace the old pin in the SIM. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CPIN=?  OK 
Read Command  Responses 
AT+CP IN? +CPIN: <code>  
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+CPIN= <pin> [,<newpin>
] OK 
ERROR  
SIMCom Confidential File
---

## Page 56

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 55 +CME ERROR: <err>  
Defined values  
<pin> 
String type values. 
<newpin>  
String type values. 
<code> 
Values reserved by the present document:  
READY   –  ME is not pending for any password 
SIM PIN    –  ME is waiting SIM PIN to be given  
SIM PUK   –  ME is waiting SIM PUK to be given  
PH-SIM PIN   –  ME is waiting phone- to-SIM card password to be given 
SIM PIN2   –  ME is waiting SIM PIN2 to be given  
SIM PUK2   –  ME is waiting SIM PUK2 to be given  
PH-NET PIN   –  ME is waiting network personalization password to be given  
Examples 
AT+CPIN?  
+CPIN: SIM PUK2  
OK 
4.3  AT+CICCID  Read ICCID from SIM card  
Description  
This command is used to Read the ICCID from SI M card  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CICCID=?  OK 
Execution Command  Responses  
AT+CICCID  +ICCID: <ICCID>  
OK 
ERROR 
+CME ERROR: <err>  
SIMCom Confidential File
---

## Page 57

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 56 Defined values  
<ICCID>  
Integrate circuit card identity, a standard ICCID is a 20 -digit serial number of the SIM card,          
it presents the publish state, network code, publish area, publish date, publish manufacture and 
press serial number of the SIM card.  
Examples 
AT+CICCID  
+ICCID: 898600700907A6019125  
OK 
4.4  AT+CSIM  Generic SIM a ccess  
Description  
This command is used to control the SIM card directly. 
Compared to restricted SIM access command AT+CRSM , AT+CSIM  allows the ME to take more 
control over the SIM interface. For SIM –ME interface  please refer 3GPP TS 11.11. 
NOTE：The SIM Application Toolkit functionality is not supported by AT+CSIM . Therefore the 
following SIM commands can not be used: TERMINAL PROFILE , ENVELOPE , 
FETCH  and TEMINAL RESPONSE . 
SIM PIN  References  
NO 3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CSIM=?  OK 
Write Command  Responses 
AT+CSIM= <length> ,<com
mand>  +CSIM: <length> , <response>  
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<length>  
Interger type; length of characters that are sent to TE in <command> or <response> 
<command> 
Command passed from MT to SIM card.  
SIMCom Confidential File
---

## Page 58

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 57 <response>  
Response to the command passed from SIM card to MT.  
Examples 
AT+CSIM=?  
OK 
4.5  AT+CRSM  Restricted SIM access  
Description  
By using AT+CRSM  instead of Generic SIM Access AT+CSIM , TE application has easier but 
more lim ited access to the SIM database.  
Write command transmits to the MT the SIM <command> and its required parameters. MT handles 
internally all SIM -MT interface locking and file selection routines. As response to the command, 
MT sends the actual SIM information parameters and response data. MT error result code  +CME 
ERROR may be returned when the command cannot be passed to the SIM, but failure in the 
execution of the command in the SIM is reported in <sw1>  and <sw2>  parameters.  
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CRSM=?  OK 
Write Command  Responses 
AT+CRSM= <command> [,<f
ileID> [,<p1> ,<p2> , <p3>  
[,<data> ]]] +CRSM: <sw1> ,<sw2> [,<response> ] 
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<command> 
Command passed on by the MT to the SIM:  
176  –   READ BINARY  
178  –   READ RECORD  
192  –   GET RESPONSE  
214  –   UPDATE BINARY 
220  –   UPDATE RECORD  
242  –   STATU S  
203  –   RETRIEVE DATA  
SIMCom Confidential File
---

## Page 59

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 58 219  –   SET D ATA  
<fileID>  
Identifier for an elementary data file on SIM, if used by <command>.  
The following list the fileID hex value, user needs to convet them to decimal. 
EFs under MF 
  0x2FE2       ICCID  
  0x2F05       Extended Language Preferences  
  0x2F00       EF DIR  
  0x2F06       Access Rule Reference  
EFs under USIM ADF  
0x6F05        Language Indic ation  
  0x6F07        IMSI  
  0x6F08        Ciphering and Integrity keys  
  0x6F09        C and I keys for pkt switched domain 
  0x6F60        User controlled PLMN selector w/Acc Tech  
  0x6F30        User controlled PLMN selector  
  0x6F31        HPLMN search period 
  0x6F37        ACM maximum value  
  0x6F38        USIM Service table  
  0x6F39        Accumulated Call meter  
  0x6F3E        Group Identifier Level  
  0x6F3F        Group Identifier Level 2  
  0x6F46        Service Provider Name  
  0x6F41        Price Per Unit and Currency table  
  0x6F45        Cell Bcast Msg identifier selection  
  0x6F78        Access control class  
  0x6F7B        Forbidden PLMNs  
  0x6F7E        Location information  
  0x6FAD        Administrative data  
  0x6F48        Cell Bcast msg id for data download 
  0x6FB7        Emergency call codes  
  0x6F50        Cell bcast msg id range selection 
  0x6F73        Packet switched location information  
  0x6F3B        Fixed dialling numbers  
  0x6F3C        Short messages  
  0x6F40        MSISDN  
  0x6F42        SMS parameters  
  0x6F43        SMS Status  
  0x6F49        Service dialling numbers  
  0x6F4B        Extension 2  
  0x6F4C        Extension 3  
  0x6F47        SMS reports  
  0x6F80        Incoming call information  
SIMCom Confidential File
---

## Page 60

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 59   0x6F81        Outgoing call inform ation  
  0x6F82        Incoming call timer  
  0x6F83        Outgoing call timer  
  0x6F4E        Extension 5  
  0x6F4F        Capability Config Parameters 2 
  0x6FB5        Enh Multi Level Precedence and Pri  
  0x6FB6        Automatic answer for eMLPP service  
  0x6FC2        Group identity  
  0x6FC3        Key for hidden phonebook entries  
  0x6F4D        Barred dialling numbers  
  0x6F55        Extension 4  
  0x6F58        Comparison Method information  
  0x6F56        Enabled services table  
  0x6F57        Access P oint Name Control List  
  0x6F2C        De -personalization Control Keys 
  0x6F32        Co- operative network list  
  0x6F5B        Hyperframe number  
  0x6F5C        Maximum value of Hyperframe number  
  0x6F61        OPLMN selector with access tech  
  0x6F5D        OPLMN selector  
  0x6F62        HPLMN selector with access technology  
  0x6F06        Access Rule reference  
  0x6F65        RPLMN last used access tech  
  0x6FC4        Network Parameters  
  0x6F11        CPHS: Voice Mail Waiting Indicator  
  0x6F12,        CPHS: Service String Table  
  0x6F13        CPHS: Call Forwarding Flag 
  0x6F14        CPHS: Operator Name String 
  0x6F15        CPHS: Customer Service Profile  
  0x6F16        CPHS: CPHS Information  
  0x6F17        CPHS: Mailbox Number  
  0x6FC5        PLMN Network Name  
  0x6FC6        Operator PLMN List  
  0x6F9F        Dynamic Flags Status  
  0x6F92        Dynamic2 Flag Setting  
  0x6F98        Customer Service Profile Line2 
  0x6F9B        EF PARAMS - Welcome Message  
  0x4F30        Phone book reference  file 
  0x4F22        Phone book synchronization center  
  0x4F23        Change counter  
  0x4F24        Previous Unique Identifier  
  0x4F20        GSM ciphering key Kc  
  0x4F52        GPRS ciphering key  
SIMCom Confidential File
---

## Page 61

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 60   0x4F63        CPBCCH information 
  0x4F64        Inv estigation scan  
  0x4F40        MExE Service table  
  0x4F41        Operator Root Public Key  
  0x4F42        Administrator Root Public Key  
  0x4F43        Third party Root public key  
  0x6FC7        Mail Box Dialing Number  
  0x6FC8        Extension 6  
  0x6F C9        Mailbox Identifier  
  0x6FCA        Message Waiting Indication Status  
  0x6FCD        Service Provider Display Information 
  0x6FD2        UIM_USIM_SPT_TABLE  
  0x6FD9        Equivalent HPLMN  
  0x6FCB        Call Forwarding Indicator Status  
  0x6FD 6        GBA Bootstrapping parameters  
  0x6FDA        GBA NAF List  
  0x6FD7        MBMS Service Key 
  0x6FD8        MBMS User Key  
  0x6FCE        MMS Notification  
  0x6FD0        MMS Issuer connectivity parameters  
  0x6FD1        MMS User Preferences  
  0x6FD2        MMS User connectivity parameters  
  0x6FCF         Extension 8  
  0x5031        Object Directory File  
  0x5032        Token Information File  
  0x5033         Unused space Information File  
EFs under Telecom DF  
  0x6F3A        Abbreviated Dialing Numbers  
  0x6F3B        Fixed dialling numbers  
  0x6F3C        Short messages  
  0x6F3D        Capability Configuration Parameters  
  0x6F4F        Extended CCP  
  0x6F40        MSISDN  
  0x6F42        SMS parameters  
  0x6F43        SMS Status  
  0x6F44        La st number dialled  
  0x6F49        Service Dialling numbers  
  0x6F4A        Extension 1  
  0x6F4B        Extension 2  
  0x6F4C        Extension 3  
  0x6F4D        Barred Dialing Numbers  
  0x6F4E        Extension 4  
  0x6F47        SMS reports  
SIMCom Confidential File
---

## Page 62

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 61   0x6F58        Comparison Method Information 
  0x6F54        Setup Menu elements  
  0x6F06        Access Rule reference  
  0x4F20        Image  
  0x4F30        Phone book reference file  
  0x4F22        Phone book synchronization center  
  0x4F23        Change counter  
  0x4F24        Previous Unique Identifier  
<p1>  <p2>  <p3>  
Integer type; parameters to be passed on by the Module to the SIM. 
<data>  
Information which shall be written to the SIM (hexadecimal character format, refer AT+CSCS ). 
<sw1>  <sw2>  
Status information  from the SIM about the execution of the actual command. It is returned in both 
cases, on successful or failed execution of the command. 
<response>  
Response data in case of a successful completion of the previously issued command. 
“STATUS” and “GET RESPO NSE” commands return data, which gives information about the 
currently selected elementary data field. This information includes the type of file and its size.  
After “READ BINARY” or “READ RECORD” commands the requested data will be returned.  
<response>  is empty after “UPDATE BINARY” or “UPDATE RECORD” commands.  
Examples 
AT+CRSM=?  
OK 
4.6  AT+SPIC  Times remain to input SIM PIN/PUK  
Description  
This command is used to inquire times remain to input SIM PIN/PUK. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Comman d Responses  
AT+SPIC=?  OK 
Execution Command Responses 
AT+SPIC  +SPIC: <pin1> ,<puk1> ,<pin2> ,<puk2>  
OK 
SIMCom Confidential File
---

## Page 63

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 62 Defined values  
<pin1> 
Times remain to input PIN1 code. 
<puk1>  
Times remain to input PUK1 code. 
<pin2> 
Times remain to input PIN2 code. 
<puk2> 
Time s remain to input PUK2 code.  
Examples 
AT+SPIC=?  
OK 
AT+SPIC  
+SPIC: 3,10,0,10 
OK 
 
4.7  AT+CSPN  Get service provider name from SIM  
Description  
  This command is used to get service provider name from SIM card. 
SIM PIN  References  
YES Vendor 
Syntax 
Test Co mmand  Responses  
AT+CSPN=?  OK 
ERROR 
Read Command  Responses  
AT+CSPN?  +CSPN: <spn> ,<display mode>  
OK 
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<spn>  
SIMCom Confidential File
---

## Page 64

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 63   String type; service provider name on SIM 
<display mode>  
0  –  doesn’t display PLMN. Already registered on PLMN.  
1  –  display PLMN  
Examples 
AT+CSPN=?  
OK 
AT+CSPN?  
+CSPN: “CMCC”,0  
OK 
4.8  AT+CSQ  Query signal quality  
Description  
This command is used to return received signal strength indication <rssi>  and channel bit error rate 
<ber>  from the ME. Test command returns values supported by the TA as compound values. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CSQ=?  +CSQ: (list of supported <rssi> s),(list of supported <ber> s) 
OK 
Execution Command  Responses  
AT+CSQ  +CSQ:  <rssi> ,<ber>  
OK 
ERROR  
Defined values  
<rssi>  
0       –     -113 dBm or less  
1     –     - 111 dBm  
2...30      –     -109... -53 dBm 
31     –     -51 dBm or greater 
99     –     not known or not detectable 
100     –     - 116 dBm or less 
101     –     - 115 dBm 
102…191 –     -114... -26dBm  
SIMCom Confidential File
---

## Page 65

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 64 191     –     -25 dBm or greater  
199     –      not known or not detectable 
100…199 –      expand to TDSCDMA, indicate RSCP received 
<ber>  
(in percent)  
0   –  <0.01% 
1   –  0.01% --- 0.1% 
2   –  0.1% ---  0.5% 
3   –  0.5% - -- 1.0% 
4   –  1.0% ---  2.0% 
5   –  2.0% ---  4.0% 
6   –  4.0% ---  8.0% 
7   –  >=8.0% 
99  –  not known or not detectable 
Examples 
AT+CSQ  
+CSQ: 22,0 
OK 
4.9  AT+AUTOCSQ  Set CSQ report  
Description  
This command is used to enable or disable automatic report CSQ information, when automatic 
report enabled, the module reports CSQ information every five seconds or only after <rssi> or 
<ber>  is changed , the format of automatic report is “+CSQ: <rssi> ,<ber> ”. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Response s 
AT+AUTOCSQ=?  +AUTOCSQ: (list of supported<auto> s),(list of supported <mod
e>s) 
OK 
Read Command  Responses  
AT+AUTOCSQ?  +AUTOCSQ: <auto> ,<mode>  
OK 
Write Command  Responses 
AT+AUTOCSQ= <auto> [,< OK 
SIMCom Confidential File
---

## Page 66

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 65 mode> ] ERROR  
Defined values  
<auto>  
0  –  disable automat ic report  
1  –  enable automatic report  
<mode>  
0  –  CSQ automatic report every five seconds  
1  –  CSQ automatic report only a fter <rssi> or  <ber> is changed  
NOTE:  If the parameter of <mode>  is omitted when executing write command, <mode>  will be set 
to default value.  
Examples 
AT+AUTOCSQ=?  
+AUTOCSQ: (0 -1),(0 -1) 
OK 
AT+AUTOCSQ?  
+AUTOCSQ: 1,1 
OK 
AT+AUTOCSQ=1,1 
OK 
+CSQ: 23,0 ( when <rssi> or <ber> changing)  
4.10  AT+CSQDELTA  Set RSSI delta change threshold  
Description  
This command is used to set RSSI delta threshold for signal strength reporting. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CSQDELTA=?  +CSQDELT A: (list of supported <delta> s) 
OK 
Read Command  Responses 
AT+CSQDELTA?  +CSQDELTA: <delta>  
OK 
ERROR 
SIMCom Confidential File
---

## Page 67

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 66 Write Command  Responses  
AT+CSQDELTA= <delta>  OK 
ERROR 
Execution Command  Responses  
AT+CSQDELTA  Set default value （<delta>=5 ）: 
OK 
Defined values  
<delta>  
Range: from 0 to 5.  
Examples 
AT+CSQDELTA?  
+CSQDELTA: 5  
OK 
4.11  AT+CATR  Configure URC destination interface 
Description  
This command is used to configure the serial port which will be used to output URCs. We 
recommend configure a destination port for receiving URC in the system initialization phase, in 
particular, in the case that transmitting large amounts of data, e.g. use TCP/UDP and MT SMS 
related AT command.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CATR=?  +CATR: ( list of supported <port> s) 
OK 
Read Command  Responses 
AT+CATR? +CATR: <port>  
OK 
Write Command  Responses 
AT+CATR= <port>  OK 
ERROR 
Defined values  
SIMCom Confidential File
---

## Page 68

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 67 <port> 
0  –  all ports  
1  –  use UART port to output URCs 
2  –  use MODEM port to output URCs 
3  –  use ATCOM port to output URCs 
4  –  use cmux vritual port1 to output URCs 
5  –  use cmux virtual port2 to output URCs 
6  –  use cmux vritual port3 to output URCs 
7  –  use cmux vritual port4 to output URCs 
 
Examples 
AT+CATR=1  
OK 
AT+CATR?  
+CATR: 1  
OK 
 
4.12  AT+CPOF  Power down the module  
Description  
This command is used to power off the module. Once the AT+CPOF command is executed, The 
module will store user data and deactivate from network, and then shutdown. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CPOF=?  OK 
Execution Command Responses 
AT+CPOF  OK 
Examples 
AT+CPOF 
OK 
SIMCom Confidential File
---

## Page 69

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 68 4.13  AT+CRESET  Reset the module  
Description  
This command is used to reset the module. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CRESET=?  OK 
Execution Command  Responses  
AT+CRESET OK 
Examples 
AT+CRESET=?  
OK 
AT+CRESET  
OK 
4.14  AT+CACM  Accumulated call meter  
Description  
This command is used to reset the Advice of Charge related accumulated call meter value in SIM 
file EF ACM. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CACM=?  OK 
ERROR 
Read Command  Responses 
AT+CACM?  +CACM: <acm>  
OK 
ERROR  
SIMCom Confidential File
---

## Page 70

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 69 +CME ERROR: <err>  
Write Command  Responses  
AT+CACM= <passwd>  OK 
ERROR 
+CME ERROR: < err> 
Execution Command Responses 
AT+CACM  OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<passwd>  
String type, SIM PIN2. 
<acm>  
String type, accumulated call meter value similarly coded as <ccm> under +CAOC.  
Examples 
AT+CACM?  
+CACM: "000000" 
OK 
4.15  AT+C AMM  Accumulated call meter maximum  
Description  
This command is used to set the Advice of Charge related accumulated call meter maximum value 
in SIM file EF ACMmax.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CAMM=?  OK 
ERROR 
Read Command  Responses  
AT+CAMM?  +CAMM: <acmmax>  
OK 
ERROR 
SIMCom Confidential File
---

## Page 71

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 70 +CME ERROR:  <err>  
Write Command  Responses  
AT+CAMM=  
<acmmax> [,<passwd> ] OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses  
AT+CAMM  OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<acmmax>  
String type, accumulated call meter maximum value similarly coded as <ccm>  under AT+CAOC , 
value zero disables ACMmax feature.  
<passwd>  
String type, SIM PIN2.  
Examples 
AT+CAMM?  
+CAMM: "000000"  
OK 
4.16  AT+CPUC  Price per unit and currency table  
Description  
This command is used to set the parameters of Advice of Charge related price per unit and currency 
table in SIM file EF PUCT.. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CPUC=?  OK 
ERROR 
Read Command  Responses 
AT+CP UC? +CPUC: [ <currency> ,<ppu> ] 
OK 
SIMCom Confidential File
---

## Page 72

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 71 ERROR  
+CME ERROR: <err>  
Write Command  Responses  
AT+CPUC= <currency> ,<pp
u>[,<passwd> ] OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<currency>  
String type, three- character currency code (e.g. "GBP", "DEM"), character set as specified by 
command Select TE Character Set AT+CSCS.  
<ppu>  
String type, price per unit, dot is used as a decimal separator. (e.g. "2.66").  
<passwd>  
String type, SIM PIN2.  
Examples 
AT+CPUC?  
+CPUC: “GBP”  , “2.66”  
OK 
4.17  AT+CCLK  Real time clock m anagement  
Description  
This command is used to manage Real Time Clock of the module. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CCLK=?  OK 
Read Command  Responses 
AT+CCLK?  +CCLK: <time>  
OK 
Write Command  Responses 
AT+CCLK= <time> OK 
ERROR 
SIMCom Confidential File
---

## Page 73

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 72 Defined values  
<time>  
String type value; format is “yy/MM/dd,hh:mm:ss±zz”, where characters indicate year (two last 
digits), month, day, hour, minutes, seconds and time zone (indicates the difference, expressed in 
quarters of an hour, betw een the local time and GMT; three last digits are mandatory, range 
-47…+48). E.g. 6th of May 2008, 14:28:10 GMT+8 equals to “08/05/06,14:28:10+32”. 
NOTE:  1. Time zone is nonvolatile, and the factory value is invalid time zone. 
       2. Command +CCLK ? will return time zone when time zone is valid, and if time zone is 
00, command +CCLK ? will return “+00”, but not “ -00”. 
Examples 
AT+CCLK=“08/11/28,12:30:33+32” 
OK 
AT+CCLK?  
+CCLK: “08/11/28,12:30:35+32” 
OK 
AT+CCLK=“08/11/26,10:15:00”  
OK 
AT+CCLK?  
+CCLK: “08/11/26,10:15:02+32” 
OK 
 
4.18  AT+CMEE  Report mobile equipment error  
Description  
This command is used to disable or enable the use of result code “+CME ERROR: <err> ” or 
“+CMS ERROR: <err> ” as an indication of an error relating to the functionality of ME ; when 
enabled, the format of <err>  can be set to numeric or verbose string. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CMEE=?  +CMEE: (list of supported <n>s) 
OK 
Read Command  Responses 
AT+CMEE?  +CMEE: <n>  
OK 
Write Command  Resp onses  
SIMCom Confidential File
---

## Page 74

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 73 AT+CMEE= <n> OK 
ERROR 
Execution Command Responses 
AT+CMEE  Set default value:  
OK 
Defined values  
<n> 
0  –  Disable result code,i.e. only “ERROR” will be displayed. 
1  –  Enable error result code with numeric values.  
2  –  Enable error result code  with string values.  
Examples 
AT+CMEE?  
+CMEE: 2  
OK 
AT+CPIN="1234","1234"  
+CME ERROR: incorrect password  
AT+CMEE=0  
OK 
AT+CPIN="1234","1234"  
ERROR  
AT+CMEE=1  
OK 
AT+CPIN="1234","1234"  
+CME ERROR: 16  
4.19  AT+CPAS  Phone activity status  
Description  
This command is used to return the activity status  <pas>  of the ME. It can be used to interrogate the 
ME before requesting action from the phone. 
NOTE:  This command is same as AT+CLCC, but AT+CLCC is more commonly used. So 
AT+CLCC is recommended to use. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses  
SIMCom Confidential File
---

## Page 75

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 74 AT+CPAS=?  +CPAS: (list of supported <pas> s) 
OK 
Execution Command  Responses  
AT+CPAS  +CPAS: <pas>  
OK 
Defined values  
<pas>  
0  –  ready (ME allows commands from TA/TE)  
3  –  ringing (ME is re ady for commands from TA/TE, but the ringer is active) 
4  –  call in progress (ME is ready for commands from TA/TE, but a call is in progress)  
Examples 
RING (with incoming call)  
AT+CPAS  
+CPAS: 3  
OK 
AT+CPAS=?  
+CPAS: (0,3,4) 
OK 
4.20  AT+SIMEI  Set IMEI for the module  
Description  
This command is used to set the module’s IMEI value.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+SIMEI=?  OK 
Read Command  Responses 
AT+SIMEI?  +SIMEI: <imei>  
OK 
ERROR  
Write Command  Responses  
AT+SIMEI= <imei>  OK 
SIMCom Confidential File
---

## Page 76

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 75 ERROR 
Defined values  
<imei>  
The 15 -digit IMEI value . 
Examples 
AT+SIMEI=357396012183170  
OK 
AT+SIMEI?  
+SIMEI:  357396012183170  
OK 
AT+SIMEI=?  
OK 
4.21  AT+SMEID  Request Mobile Equipment Identifier  
Description  
Only task effect in 7600CE 
SIM PIN  Refere nces 
NO 3GPP TS 27.007 
Syntax 
Read Command  Responses 
AT+SMEID?  +SMEID: <MEID>  
OK 
ERROR  
Defined values  
<MEID>  
Mobile Equipment Identifier (string, without double quotes).  
Examples 
AT+SMEID?  
+SMEID: A1000021A5906F  
 
SIMCom Confidential File
---

## Page 77

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 76 OK 
4.22  AT+CSVM  Voice Mail Subscribe r number  
Description  
Execution command returns the voice mail number related to the subscriber.  
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CSVM=?  +CSVM: (0 -1), “(0 -9,+)”, (128-255) 
OK 
ERROR 
Read Command  Responses  
AT+CSV M? +CSVM:  <valid> , “<number> ”,<type>  
OK 
ERROR 
Write Command  Responses 
AT+CSVM= <valid> , 
“<number> ”,<type>  OK 
ERROR 
Defined values  
<valid>  
Whether voice mail number is valid:  
0  –  V oice mail number is invalid . 
1  –  V oice mail number is valid . 
<num ber> 
String type phone number of format specified by <type> . 
<type>  
Type of address octet in integer format. see also  AT+CPBR <type>  
Examples 
AT+CSVM?  
+CSVM: 1 ,"13697252277",129  
OK 
SIMCom Confidential File
---

## Page 78

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 77 4.23  AT+CUSBPIDSWITCH  Change module’s PID  
Description  
Execution command change the module’s PID. This command will reset the module  if change to 
other PID (not current used PID) . 
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CUSBPIDSWITCH=?  +CUSBPIDSWITCH: 
(9000,9001,9002,9003,9004,9005,9006,9007,9011,9016,9018,9019
,901A,901B,9020,9021,9022,9023,9024,9025,9026,9027,9028,902
9,902A,902B ),(0-1),(0 -1) 
OK 
ERROR 
Read Command  Responses 
AT+CUSBPIDSWITCH?  +CUSBPIDSWITCH:  <pid>  
OK 
ERROR 
Write Command  Responses 
AT+CUSBPIDSWITCH= <p
id>, < reserve1> ,< reserve2>  OK 
ERROR 
Defined values  
<pid> 
This command support pids, 9001 is the default value. 
9000,9001,9002,9003,9004,9005,9006,9007,9011,9016,9018,9019,901A,901B,9020,9021,9022,90
23,9024,9025,9026,9027,9028,9029,902A,902B 
< reserve1>  
0 or 1, this value is for the reserve  
< reserve2>  
0 or 1, this value is for the reserve  
Examples 
AT+CUSBPIDSWITCH?  
+CUSBPIDSWITCH: 9001  
OK 
SIMCom Confidential File
---

## Page 79

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 78 AT+CUSBPIDSWITCH=9001,1,1 
OK 
 
PID configuration: 9000:Diag, NMEA, At, Modem, Audio, Rmnet 9001:Diag, NMEA, At, Modem, Audio, Rmnet 9002:Diag, NMEA, At, Modem, Audio, Rmnet 
9003:Diag, NMEA, At, Modem, Audio, MBIM 9004:Diag, NMEA, At, Modem, Audio, GNSS, Rmnet  
9005:Diag, NMEA, At, Modem, Audio, GNSS, MBIM 9006:Diag, NMEA, At,Modem  
9007:Diag, NMEA, At, Modem, Audio, Rmnet,mass_storage 9011:RNDIS,Diag, NMEA, At, Modem, Audio 9016:Diag, Rmnet 9018:Diag, NMEA, At, Modem, Audio, Ecm 9019:RNDIS 901A: Diag, NMEA, At, Rmnet 901B:NMEA, At, Rmnet  
9020: Diag, At, Modem  
9021: Diag, Modem  
9022: Diag, Modem, Rmnet 9023: Modem 9024: At, Modem  
9025: Modem,rm net 
9026: Modem,Audio 9027: Modem,Audio, Rmnet  
9028:Diag, Modem,Audio, Rmnet  
9029:Diag, Modem,Audio 902A: At  
902B : Diag, NMEA,  At, Modem, R mnet, Usb-audio 
 
4.24  Indication of EONS  
This module supports EONS function; the following table shows the URC related EON S. 
OPL INIT  Description  
OPL DONE  This indication means EF -OPL has been read successfully. Only 
after this URC is reported, the AT+COPS? can query the network 
name that supports EONS function. 
PNN INIT  Description  
PNN DONE  This indication means EF- PNN ha s been read successfully  
OPL UPDATING Description  
SIMCom Confidential File
---

## Page 80

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 79 OPL UPDATING This indication means the EF- OPL is updating using OTA message. 
After updating, the “OPL DONE” should report.  
PNN UPDATING  Description  
PNN UPDATING This indication means the EF -PNN is updat ing using OTA 
message. After updating, the “PNN DONE” should report. 
PNN UPDATING  This indication means the EF -PNN is updating using OTA 
message. After updating, the “PNN DONE” should report. 
4.25  Indication of Voice Mail  
This module supports voice mail function; the subscriber number is configured by AT+CSVM 
command, the following table shows the URC related Voice Mail.  
Box Empty  Description  
+VOICEMAIL: EMPTY  This indication means the voice mail box is empty 
New Message  Description  
+VOICEMAIL: NEW MSG  This indication means there is a new voice mail message 
notification received. This is for CPHS.  
Voice Mail Status Updated  Description  
+VOICEMAIL: WAITING, 
<count>  This indication means that there are <count>  number of  voice 
mail messages that needs to be got.  
Defined values  
< count > 
Count of voice mail message that waits to be got. 
Examples 
+VOICEMAIL: WAITING, <count>  
+VOICEMAIL: WAITING, 5  
SIMCom Confidential File
---

## Page 81

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 80 5  AT Commands for Network  
5.1  AT+CREG  Network registration  
Description  
This command is used to control the prese ntation of an unsolicited result code +CREG: <stat>  
when <n> =1 and there is a change in the ME network registration status, or code +CREG: 
<stat> [,<lac> ,<ci>] when <n>=2 and there is a change of the network cell. 
Read command returns the status of result code presentation and an integer <stat>  which shows 
whether the network has currently indicated the registration of the ME. Location information 
elements <lac>  and <ci> are returned only when <n> =2 and ME is registered in the network. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CREG=?  +CREG: (list of supported <n>s) 
OK 
Read Command  Responses 
AT+CREG?  +CREG: <n>,<stat> [,<lac> ,<ci>] 
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+CREG= <n> OK 
ERROR 
+CME ERROR: <er r> 
Execution Command  Responses  
AT+CREG  Set default value （<n>=0）: 
OK 
Defined values  
<n> 
0  –  disable network registration unsolicited result code  
1  –  enable network registration unsolicited result code +CREG: <stat>  
2  –  enable network registration and location information unsolicited res ult code +CREG: 
SIMCom Confidential File
---

## Page 82

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 81 <stat> [,<lac> ,<ci>] 
<stat>  
0  –  not registered, ME is not currently searching a new operator to register to  
1  –  registered, home network 
2  –  not registered, but ME is currently searching a new operator to register to 
3  –  registration denied 
4  –  unknown 
5  –  registered, roaming 
<lac>  
Two byte location area code in hexadecimal format(e.g.”00C3” equals 193 in decimal). 
 
NOTE:  The <lac> not supported in CDMA/HDR mode  
<ci> 
Cell Identify in hexadecimal format.  
GSM :  Maximum is two byte  
WCDMA :  Maximum is four byte 
TDS -CDMA :  Maximum is four byte 
 
NOTE:  The <ci> not supported in CDMA/HDR mode 
Examples 
AT+CREG?  
+CREG: 0,1  
OK 
5.2  AT+COPS  Operator selection  
Description  
SIMCom Confidential File
---

## Page 83

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 82 Write command forces an attempt to select and register the GSM/UMTS  network operator. <mode>  
is used to select whether the selection is done automatically by the ME or is forced by this 
command to operator  <oper>  (it shall be given in format <format> ). If the selected operator is not 
available, no other operator shall be selected (except <mode> =4). The selected operator name 
format shall apply to further read commands ( AT+COPS ?) also. <mode> =2 forces an attempt to 
deregister from the network. The selected mode affects to all further network registration (e.g. after 
<mode> =2, ME shall be unregistered until <mode> =0 or 1 is selected).  
Read command returns the current mode and the currently selected operator. If no operator is 
selected, <format>  and <oper>  are omitted.  
Test command returns a list of quadruplets, each represent ing an operator present in the network. 
Quadruplet consists of an integer indicating the availability of the operator <stat> , long and short 
alphanumeric format of the name of the operator, and numeric format representation of the operator. 
Any of the form ats may be unavailable and should then be an empty field. The list of operators shall 
be in order: home network, networks referenced in SIM, and other networks. 
It is recommended (although optional) that after the operator list TA returns lists of supporte d 
<mode> s and <format> s. These lists shall be delimited from the operator list by two commas. 
When executing AT+COPS=? , any input from serial port will stop this command.  
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+COPS=?  [+COPS:  [list of supported ( <stat> ,long alphanumeric <oper>  
,short alphanumeric <oper> ,numeric <oper> [,< AcT> ])s] 
[,,(list of supported <mode> s),(list of supported <format> s)]] 
OK 
ERROR 
+CME ERROR: <err>  
Read Command  Responses 
AT+COPS?  +COPS: <mode> [,<format> ,<oper> [,< AcT> ]] 
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+COPS= <mode> [,<form
at>[,<oper> [,< AcT> ]]] OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses 
AT+COPS  OK 
SIMCom Confidential File
---

## Page 84

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 83 Defined values  
<mode>  
0  –  automatic 
1  –  manual 
2  –  force deregister  
3  –  set only <format>  
4  –  manual/automatic 
5  –  manual,but do not modify the network selection mode(e.g GSM,WCDMA) after 
module resets.  
 
NOTE: if <mode> is set to 1, 4, 5 in write command, the <oper> is needed. 
<format>  
0  –  long format alphanumeric <oper>  
1  –  short format alphanumeric <oper>  
2  –  numeric <oper>  
<oper>  
 string type, <format>  indicates if the format is alphanumeric or numeric.  
<stat>  
0  –  unknown  
1  –  available  
2  –  current  
3  –  forbidden  
<AcT>  
Access t echnology selected  
0  –  GSM  
1  –  GSM Compact  
2  –  UTRAN  
7  –  EUTRAN  
8  –  CDMA/HDR  
 
NOTE: the value 8 do not follow the 3gpp spec, we add this value to distinguish cdma/hdr. 
Examples 
AT+COPS?  
+COPS: 0,0,"China Mobile Com",0 
OK 
AT+COPS=?  
+COPS: (2," China Unicom","Unicom","46001",0),(3,"China Mobile Com","DGTMPT",  
"46000",0),,(0,1,2,3,4,5),(0,1,2) 
OK 
SIMCom Confidential File
---

## Page 85

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 84 5.3  AT+CLCK  Facility lock  
Description  
This command is used to lock, unlock or interrogate a ME or a network facility <fac> . Password is 
normally needed to do such actions. When querying the status of a network service ( <mode> =2) the 
response line for 'not active' case ( <status> =0) should be returned only if service is not active for 
any <class> . 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CLCK=?  +CLCK: (list of supported <fac> s) 
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+CLCK=<fac> ,<mode>  
[,<passwd> [,<class> ]] OK 
When <mode>=2 and command successful: 
+CLCK: <status> [,<class1> [<CR><LF> 
+CLCK: <status> ,<class2>  
[...]] 
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<fac>  
"PF"      lock Phone to the very First inserted SIM card or USIM card  
"SC" lock SIM card or USIM card  
"AO"    Barr All Outgoing Calls  
"OI"     Barr Outgoing International Calls 
"OX"  Barr Outgoing International Calls except to Home Country 
"AI"    Barr All Incoming Calls  
"IR"    Barr Incoming Calls when roaming outside the home country 
"AB"    All Barring services (only for <mode> =0) 
"AG"  All outGoing barring services (only for <mode> =0) 
"AC"   All inComing barring services (only for <mode> =0) 
SIMCom Confidential File
---

## Page 86

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 85 "FD"  SIM fixed dialing memory feature 
"PN"  Network Personalization  
"PU"    network subset Personalization 
"PP"    service Provider Personalization  
"PC"    Corporate Personalization  
<mode> 
0  –  unlock 
1  –  l ock 
2  –  query status 
<status>  
0  –  not active  
1  –  active  
<passwd>  
Password.  
string type; shall be the same as password specified for the facility from the ME user interface or 
with command Change Password +CPWD 
<classX>  
It is a sum of integers e ach representing a class of information (default 7):  
1    –   voice (telephony) 
2    –   data (refers to all bearer services)  
4    –   fax (facsimile services) 
8    –   short message service  
16   –   data circuit sync  
32  –  data circuit async 
64   –   dedicated  packet access  
128  –   dedicated PAD access  
255  –  The value 255 covers all classes  
Examples 
AT+CLCK="SC",2  
+CLCK: 0  
OK 
5.4  AT+CPWD  Change password  
Description  
Write command sets a new password for the facility lock function defined by command Facility 
Lock AT+CLCK . 
Test command returns a list of pairs which present the available facilities and the maximum length 
of their password.  
SIM PIN  References  
SIMCom Confidential File
---

## Page 87

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 86 YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CPWD=?  +CPWD:  (list of supported ( <fac> ,<pwdlength> )s) 
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+CPWD=  
<fac> ,<oldpwd> ,<newpwd>  OK 
ERROR  
+CME ERROR: <err>  
Defined values  
<fac>  
Refer Facility Lock +CLCK for other values:  
"SC"   SIM or USIM PIN1  
"P2"   SIM or USIM PIN2  
"AB"  All B arr ing services  
"AC"  All inComing barring services (only for <mode> =0) 
"AG"  All outGoing barring services (only for <mode> =0) 
"AI"   Barr All Incoming Calls  
"AO"  Barr All Outgoing Calls  
"IR"   Barr Incoming Calls when roaming outside the home country 
"OI"   Barr Outgoing International Calls 
"OX"  Barr Outgoing International Calls except to Home Country 
<oldpwd>  
String type, it shall be the same as password specified for the facility from the ME user interface or 
with command Change Password AT+CPWD . 
<new pwd>  
String type, it is the new password; maximum length of password can be determined with 
<pwdlength> . 
<pwdlength> 
Integer type, max length of password. 
Examples 
AT+CPWD=?  
+CPWD: ("AB",4),("AC",4),("AG",4),("AI",4),("AO",4),("IR",4),("OI",4),("OX",4),(  
"SC",8),("P2",8)  
SIMCom Confidential File
---

## Page 88

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 87  
OK 
5.5  AT+CCUG  Closed user group  
Description  
This command allows control of the Closed User Group supplementary service. Set command 
enables the served subscriber to select a CUG index, to suppress the Outgoing Access (OA), and to 
suppress the preferential CUG.  
NOTE:  This command not supported in CDMA/HDR mode. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CCUG=?  OK 
ERROR 
Read Command  Responses 
AT+CCUG?  +CCUG: <n> ,<index> ,<info>  
OK 
ERROR 
+CME ERROR:  <err>  
Write Command  Responses 
AT+CCUG= 
<n>[,<index> [,<info> ]] OK 
ERROR  
+CME ERROR: <err>  
Execution Command  Responses  
AT+CCUG  Set default value: 
OK 
Defined values  
<n> 
0  –  disable CUG temporary mode  
1  –  enable CUG temporary mode 
<index>  
0...9  –  CUG index  
10  –  no index (preferred CUG taken from subscriber data) 
<info>  
SIMCom Confidential File
---

## Page 89

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 88 0  –  no information 
1  –  suppress OA  
2  –  suppress preferential CUG  
3  –  suppress OA and preferential CUG  
Examples 
AT+CCUG?  
+CCUG: 0,0,0  
OK 
5.6  AT+CUSD  Unstructured s upplementary service data  
Description  
This command allows control of the Unstructured Supplementary Service Data (USSD). Both 
network and mobile initiated operations are supported. Parameter <n> is used to disable/enable the 
presentation of an unsolicited result code (USSD response from the network, or network initiated 
operation) +CUSD: <m> [,<str> ,<dcs> ] to the TE. In addition, value <n> =2 is used to cancel an 
ongoing USSD session.  
NOTE:  This command not supported in CDMA/HDR mode. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CUSD=?  +CUSD: (list of supported <n>s) 
OK 
Read Command  Responses 
AT+CUSD?  +CUSD: <n> 
OK 
Write Command  Responses  
AT+CUSD=  
<n>[,<str> [,<dcs> ]] OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses 
AT+CUSD  Set default value ( <n>=0): 
OK 
Defined values  
SIMCom Confidential File
---

## Page 90

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 89 <n> 
0  –  disable the result code presentation in the TA 
1  –  enable the result code presentation in the TA 
2  –  cancel session (not applicable to read command response) 
<str>  
String type USSD- string. 
<dcs>  
Cell Broadcast Data Coding Scheme in integer format (default 0).  
<m>  
0  –  no further user action required (network initiated USSD -Notify, or no further 
information needed after mobile initiated operation) 
1  –  further user action required (network initiated USSD -Request, or further information 
needed after mobile initiated operation) 
2  –  USSD terminated by network  
4  –  operation not supported 
5  –  network time out 
Examples 
AT+CUSD?  
+CUSD: 1  
OK 
AT+CUSD=0  
OK 
5.7  AT+CAOC  Advice of charge 
Description  
This command refers to Advice of Charge supplementary service that enables subscriber to get 
information about the cost of calls. With <mode> =0, the execute command returns the current call 
meter value from the ME.  
This command also includes the possibility to enable an unsolicited event reporting of the CCM 
information. The unsolicited result code +CCCM: <ccm>  is sent when the CCM value changes, but 
not more that every 10 seconds. Deactivation of the unsolicited event reporting is made with t he 
same command.  
NOTE:  This command not supported in CDMA/HDR mode. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
SIMCom Confidential File
---

## Page 91

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 90 AT+CAOC=?  +CAOC: (list of supported <mode> s) 
OK 
ERROR 
Read Command  Responses  
AT+CAOC?  +CAOC: <mode>  
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses  
AT+CAOC= <mode>  +CAOC:  <ccm>  
OK 
OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses 
AT+ CAOC  Set default value ( <mode> =1): 
OK 
ERROR  
Defined values  
<mode>  
0  –  query CCM value 
1  –  deactivate the u nsolicited reporting of CCM value 
2  –  activate the unsolicited reporting of CCM value 
<ccm>  
String type, three bytes of the current call meter value in hexadecimal format (e.g. "00001E" 
indicates decimal value 30), value is in home units and bytes are similarly coded as ACMmax value 
in the SIM.  
Examples 
AT+CAOC=0  
+CAOC: "000000" 
OK 
5.8  AT+CSSN  Supplementary service notifications 
Description  
SIMCom Confidential File
---

## Page 92

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 91 This command refers to supplementary service related network initiated notifications. The set 
command enables/disables the presentation of notification result codes from TA to TE. 
When <n>=1 and a supplementary service notification is received after a mobile originated call 
setup, intermediate result code +CSSI: <code1> [,<index> ] is sent to TE before any other MO cal l 
setup result codes presented in the present document. When several different <code1>s are received 
from the network, each of them shall have its own +CSSI result code. 
When  <m> =1 and a supplementary service notification is received during a mobile terminated call 
setup or during a call, or when a forward check supplementary service notification is received, 
unsolicited result code +CSSU: <code2> [,<index> [,<number> ,<type> [,<subaddr> ,<satype> ]]] is 
sent to TE. In case of MT call setup, result code is sent a fter every +CLIP result code (refer 
command "Calling line identification presentation +CLIP") and when several different <code2> s 
are received from the network, each of them shall have its own +CSSU result code.  
NOTE:  This command not supported in CDMA/HDR mode. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CSSN=?  +CSSN: (list of supported <n> s),(list of supported <m> s) 
OK 
ERROR 
Read Command  Responses 
AT+CSSN?  +CSSN:  <n> ,<m>  
OK 
ERROR 
Write Command  Responses 
AT+CSSN= <n>[,<m> ] OK 
ERROR  
+CME ERROR: <err>  
Defined values  
<n> 
Parameter sets/shows the +CSSI result code presentation status in the TA:  
0  –  disable  
1  –  enable  
<m>  
Parameter sets/shows the +CSSU result code presentation status in the TA:  
0  –  disable  
1  –  enable  
SIMCom Confidential File
---

## Page 93

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 92 <code1> 
0  –  unconditional call forwarding is active  
1  –  some of the conditional call forwarding are active 
2  –  call has been forwarded  
3  –  call is waiting  
5  –  outgoing calls are barred 
<index> 
Refer "Closed user group +CCUG".  
<code2> 
0  –  this is a forwarded call (MT call setup)  
2  –  call has been put on hold (during a voice call) 
3  –  call has been retrieved (during a voice call)  
5  –  call on hold has been released (this is not a SS notification) (during a voice call) 
<number> 
String type phone number of format specified by <type> . 
<type>  
Type of address octet in integer format; default 145 when dialing string includes international 
access code character "+", otherwise 129.  
<subaddr> 
String type sub address of format specified by <satype> . 
<satype>  
Type of sub address octet in integer format, default 128. 
Examples 
AT+CSSN=1,1  
OK 
AT+CSSN?  
+CSSN: 1,1 
OK 
5.9  AT+CPOL  Preferred operator list  
Description  
This command is used to edit the SIM preferred list of networks. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CPOL=?  +CPOL: (list of supported <index> s), (list of supported  <format> s) 
SIMCom Confidential File
---

## Page 94

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 93 OK 
ERROR 
Read Command  Responses 
AT+CPOL?  [+CPOL: <index1> ,<format> ,<oper1> [<GSM_AcT1> ,<GSM_Com
pact_AcT1> ,<UTR AN_AcT1>,<LTE_AcT1> ][<CR><LF>  
+CPOL: 
<index2> ,<format> ,<oper2> [,<GSM_AcT1> ,<GSM_Compact_Ac
T1>,<UTRAN_AcT1>,<LTE_AcT1>] 
[...]]]  
OK 
ERROR 
Write Command  Responses 
AT+CPOL=<index> 
[,<format >[,<oper> ][,<GSM
_AcT1> ,<GSM_Compact_A
cT1> ,<UTRAN_AcT1>,<LT
E_AcT1>  ]] 
NOTE:  If using USIM card, 
the last four parameters must 
set. OK 
ERROR  
+CME ERROR: <err>  
Defined values  
<index> 
Integer type, the order number of operator in the SIM preferred operator list. 
If only input <index> , command will delete the value indic ate by <index> . 
<format>  
0  –  long format alphanumeric <oper>  
1  –  short format alphanumeric <oper>  
2  –  numeric  <oper>  
<operX> 
String type. 
<GSM_AcT n> 
GSM access technology:  
0  –  access technology not selected  
1  –  access technology selected  
<GSM_Compact_AcT n> 
GSM compact access technology:  
0  –  access technology not selected  
1  –  access technology selected  
<UTRA_AcT n> 
UTRA access technology:  
SIMCom Confidential File
---

## Page 95

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 94 0  –  access technology not selected  
1  –  access technology selected  
<LTE_AcT n> 
LTE access tech nology: 
0  –  access technology not selected  
1  –  access technology selected  
Examples 
AT+CPOL?  
+CPOL: 1,2,"46001",0,0,1,0  
OK 
AT+CPOL=?  
+CPOL: (1 -8),(0-2) 
OK 
5.10  AT+COPN  Read operator names 
Description  
This command is used to return the list of operator  names from the ME. Each operator code 
<numericX>  that has an alphanumeric equivalent <alphaX>  in the ME memory shall be returned. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+COPN=?  OK 
ERROR  
Write Command  Responses  
AT+COP N +COPN: <numeric1> ,<alpha1> [<CR><LF>  
+COPN: <numeric2> ,<alpha2>  
[...]] 
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<numericX>  
String type, operator in numeric format (see AT+COPS ). 
SIMCom Confidential File
---

## Page 96

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 95 <alphaX> 
String type, operator in long alphanumeric format (see AT+CO PS). 
Examples 
AT+COPN  
+COPN: "46000","China Mobile Com" 
+COPN: "46001"," China Unicom" 
…… 
OK 
5.11  AT+CNMP  Preferred mode selection  
Description  
This command is used to select or set the state of the mode preference.  
NOTE:  The set value in Write Command will take efficient immediately; The set value will retain 
after module reset;   
NOTE:  The respon se will be returned immediately for Test Command and Read Command; The 
maximum respon se time  for Write  Command is 10 seconds.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CNMP=?  +CNMP:  (list of supported <mode> s) 
OK 
Read Command  Responses 
AT+CNMP?  +CNMP: <mode>  
OK 
Write Command  Responses 
AT+CNMP= <mode>  OK 
If <mode> not supported by module, this command will return 
ERROR.  
ERROR 
Defined values  
<mode>  
2   –  Automatic  
13  –  GSM Only  
14  –  WCDMA Only  
SIMCom Confidential File
---

## Page 97

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 96 38  –  LTE Only  
59  –  TDS -CDMA Only  
9   –  CDMA Only  
10  –  EVDO Only  
19  –  GSM+WCDMA Only  
22  –  CDMA+EVDO Only  
48  –  Any but LTE 
60  –  GSM+TDSCDMA Only  
63  –  GSM+WCDMA+TDSCDMA Only  
67  –  CDMA+EVDO+GSM+WCDMA+TDSCDMA Only  
39  –  GSM+W CDMA+LTE Only  
51  –  GSM+LTE Only  
54  –  WCDMA+LTE Only  
Examples 
AT+CNMP=13  
OK 
AT+CNMP?  
+CNMP: 2  
OK 
5.12  AT+CNBP  Preferred band selection  
Description  
This command is used to select or set the state of the band preference.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CNBP?  +CNBP: <mode> [,<lte_mode> ][,<tds_mode> ] 
OK 
Write Command  Responses 
AT+CNBP= <mode> [,<lte_
mode> ][,<tds_mode> ] OK 
ERROR 
Defined values  
<mode> 
64 bit number, the value is “1” << “ <pos> ”, then or by bit. 
SIMCom Confidential File
---

## Page 98

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 97 Some special mode value declared below:  
0x40000000                  BAND_PREF_NO_CHANGE  
<pos>  
Value:  
0xFFFFFFFF7FFFFFFF      Any (any value)  
7      GSM_DCS_1800 
8        GSM_EGSM_900 
9        GSM_PGSM_900  
16      GSM_450 
17       GSM_480 
18      GSM_750 
19       GSM_850 
20       GSM_RGSM_900 
21      GSM_PCS_1900 
22      WCDMA_IMT_2000 
23       WCDMA_PCS_1900 
24      WCDMA_III_1700 
25       WCDMA_IV_1700 
26      WCDMA_850 
27      WCDMA_800 
48      WCDMA_VII_2600 
49      WCDMA_VIII_900 
50      WCDMA_IX_1700 
<lte_mode> 
64/256 bit number, the value is “1” << “ <lte_pos> ”, then or by bit. 
NOTE: FDD(band1 ~ band32, band66 , band252, and band255), TDD(band33 ~ band42)  
<lte_pos>  
Value:  
0x480000000000000000000000000000000000000000000002000007FF3FDF3FFF      
Any (any value)  
0      EUTRAN_BAND1(UL:1920 -1980; DL:2110-2170) 
1      EUTRAN_BAND2(UL:1850 -1910; DL:1930-1990) 
2      EUTRAN_BAND3(UL:1710 -1785; DL:1805-1880) 
3      EUTRAN_BAND4(UL:1710 -1755; DL:2110-2155) 
4      EUTRAN_BAND5(UL: 824-849; DL: 869-894) 
5      EUTRAN_BAND6(UL: 830 -840; DL: 875-885) 
6      EUTRAN_BAND7(UL:2500 -2570; DL:2620-2690) 
7      EUTRAN_BAND8(UL: 880 -915; DL: 925-960) 
8          EUTRAN_BAND9(UL:1749.9- 1784.9; DL:1844.9-1879.9) 
9      EUTRAN_BAND10(UL:1710 -1770; DL:2110-2170) 
10      EUTRAN_BAND11(UL:1427.9- 1452.9; DL:1475.9-1500.9) 
11      EUTRAN_BAND12(UL:698 -716; DL:728-746) 
12      EUTRAN_BAND13(UL: 777 -787; DL: 746-756) 
SIMCom Confidential File
---

## Page 99

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 98 13      EUTRAN_BAND14(UL: 788 -798; DL: 758-768) 
16      EUTRAN_BAND17(UL: 704 -716; DL: 734-746) 
17      EUTRAN_BAND18(UL: 815 -830; DL: 860-875) 
18      EUTRAN_BAND19(UL: 830 -845; DL: 875-890) 
19      EUTRAN_BAND20(UL: 832 -862; DL: 791-821) 
20      EUTRAN_BAND21(UL: 1447.9- 1462.9; DL: 1495.9-1510.9) 
22      EUTRAN_BAND23(UL: 2000 -2020; DL: 2180-2200) 
23      EUTRAN_BAND24(UL: 1626.5- 1660.5; DL: 1525 -1559) 
24      EUTRAN_BAND25(UL: 1850 -1915; DL: 1930 -1995) 
25      EUTRAN_BAND26(UL: 814 -849; DL: 859 -894) 
26      EUTRAN_BAND27(UL: 807.5-824; DL: 852 -869) 
27      EUTRAN_BAND28(703 -748; DL: 758-803) 
28      EUTRAN_BAND29(UL:1850 -1910 or 1710-1755; 
DL:716-728) 
29      EUTRAN_BAND30(UL: 2305 -2315 ; DL: 2350 - 2360) 
32      EUTRAN_BAND33(UL: 1900 -1920; DL: 1900-1920) 
33      EUTRAN_BAND34(UL: 2010 -2025; DL: 2010-2025) 
34      EUTRAN_BAND35(UL:  1850-1910; DL: 1850-1910) 
35      EUTRAN_BAND36(UL: 1930 -1990; DL: 1930-1990) 
36      EUTRAN_BAND37(UL: 1910 -1930; DL: 1910-1930) 
37      EUTRAN_BAND38(UL: 2570 -2620; DL: 2570-2620) 
38      EUTRAN_BAND39(UL: 1880 -1920; DL: 1880-1920) 
39      EUTRAN_BAND40 (UL: 2300-2400; DL: 2300-2400) 
40      EUTRAN_BAND41(UL: 2496 -2690; DL: 2496-2690) 
41      EUTRAN_BAND42(UL: 3400 -3600; DL: 3400-3600) 
42      EUTRAN_BAND43(UL: 3600 -3800; DL: 3600-3800) 
65      EUTRAN_BAND66(UL: 1710-1780; DL: 2110-2200) 
70                      EUTRAN_BAND 71(UL: 663-698; DL: 617-652) 
251      EUTRAN_BAND252(D L: 5150-5250) 
254      EUTRAN_BAND255(DL: 5725-5850) 
<tds_mode> 
64bit number, the value is “1” << “ <tds_pos> ”, then or by bit.  
<tds_pos>  
Value:  
0x000000000000003F     Any (any valu e) 
0      TDS Band A (1900-1920 MHz, 2010-2020 MHz) 
1      TDS Band B (1850-1910 MHz, 1930-1990 MHz) 
2      TDS Band C (1910-1930 MHz) 
3      TDS Band D (2570-2620 MHz) 
4      TDS Band E (2300-2400 MHz) 
5      TDS Band F (1880-1920 MHz) 
<term_mode>  
0  –  term permanent  
SIMCom Confidential File
---

## Page 100

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 99 1  –  term until a power cycle  
Examples 
AT+CNBP=,0x0000000000000095  
OK 
AT+CNBP?  
+CNBP: 
0x0002000004FF0387,0x00000000000000000000000000000000000000000000000000000000000
00095,0x000000000000003F  
AT+CNBP=,0x48000000000000000000000000000000 00000000000000 020000000000000095  
OK 
AT+CNBP?  
+CNBP: 
0x0002000004FF0387,0x48000000000000000000000000000000000000000000000200000000000
00095,0x000000000000003F 
5.13  AT+CNAOP  Acquisitions order preference  
Description  
This command is used to reset the state of acquisitions order preference.  
SIM PIN  References  
NO Vendor 
Syntax 
Read  Command  Responses  
AT+CNAOP ? +CNAOP:  <mode> [,<sys_mode 1>,[<sys_mode 2>[,<sys_mode 3>[,
<sys_mode 4>[,<sys_mode 5>[,<sys_mode 6>]]]]]]  
OK 
Write Command  Responses  
AT+CNAOP= <mode> [,<sys
_mode 1>[,<sys_mode 2>[,<sy
s_mode 3>[,<sys_mode 4>[,<s
ys_mode 5>[,<sys_mode 6>]]]
]]] OK 
ERROR 
Defined values  
<mode>  
7  –  Acquistion by priority order list <sys_mode n>s. 
<sys_mode n> 
SIMCom Confidential File
---

## Page 101

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 100 sys_mode values:  
2  –  CDMA  
3  –  GSM  
4  –  HDR  
5  –  WCDMA  
9  –  LTE  
11  –  TDSCDMA  
 
Examples 
AT+CNAOP=7,9,5,3,11,2,4 
OK 
AT+CNAOP?  
+CNAOP: 7,9,5,3,11,2,4 
OK 
5.14  AT+CPSI  Inquiring UE system information  
Description  
This command is used to return the UE system information. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Resp onses  
AT+CPSI=?  +CPSI:   (scope of <time> ) 
OK 
Read Command  Responses 
 If camping on a cdma/evdo cell:  
+CPSI: CDMA ,<Operation Mode>[ ,<MCC>- <MNC>,<CDMA ch 
num>,<CDMA pilot PN>,<CDMA RX Chain 0 AGC>,<CDMA 
RX Chain 1 AGC>,<CDMA Chain 0 LNA>,<CDMA Chain 1 
LNA >,<CDMA TX AGC>,<SID>,<NID>,<CDMA 
EC/IO>,<BID>]  
+CPSI: EVDO, <Operation Mode>[,<MCC> -<MNC>,<EVDO ch 
num>,<EVDO RX Chain 0 AGC>,<EVDO RX Chain 1 AGC>,< 
EVDO TX AGC>,<EVDO Serving PN>,<EVDO Rel0 
SCI>,<EVDO RelA SCI>,<EVDO EC/IO>]  
OK 
SIMCom Confidential File
---

## Page 102

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 101 AT+CPSI?  If camping on a gsm cell:  
+CPSI: <System Mode> ,<Operation Mode> ,<MCC> -<MNC>,<L
AC> ,<Cell ID> ,<Absolute RF Ch Num> ,<RxLev> , 
<Track LO Adjust> ,<C1-C2> 
OK 
If camping on a wcdma cell:  
+CPSI: <System Mode>,<Operation Mode>,<MCC> -<MNC>,<
LAC>,<Cell ID>,<Frequency Band>,<PSC>,<Fr eq>,<SSC>,<EC
/IO>,<RSCP>,<Qual>,<RxLev>,<TXPWR>  
OK 
If camping on a tds -cdma cell:  
+CPSI: <System Mode>,<Operation Mode>,<MCC> -<MNC>,<
LAC>,<Cell ID>,<Frequency Band>,<Uarfcn>,<Cpid>  
OK 
If camping on a lte cell:  
+CPSI: <System Mode>,<Operation Mode>[,<MC C>-<MNC>,<
TAC>,<SCellID>,<PCellID>,<Frequency Band>,<earfcn>,<dlb
w>,<ulbw>,<RSRQ>,<RSRP>,<RSSI>,<RSSNR>]  
OK 
If camping on a cdma/evdo cell:  
+CPSI: CDMA ,<Operation Mode>[ ,<MCC>- <MNC>,<CDMA ch 
num>,<CDMA pilot PN>,<CDMA RX Chain 0 AGC>,<CDMA 
RX Chain 1 AGC >,<CDMA Chain 0 LNA>,<CDMA Chain 1 
LNA>,<CDMA TX AGC>,<SID>,<NID>,<CDMA 
EC/IO>,<BID>]  
+CPSI: EVDO, <Operation Mode>[,<MCC> -<MNC>,<EVDO ch 
num>,<EVDO RX Chain 0 AGC>,<EVDO RX Chain 1 AGC>,< 
EVDO TX AGC>,<EVDO Serving PN>,<EVDO Rel0 
SCI>,<EVDO RelA SCI>,<EVDO  EC/IO>]  
OK 
If camping on a cdma/ehrpd cell:  
+CPSI: CDMA ,<Operation Mode>[ ,<MCC>- <MNC>,<CDMA ch 
num>,<CDMA pilot PN>,<CDMA RX Chain 0 AGC>,<CDMA 
RX Chain 1 AGC>,<CDMA Chain 0 LNA>,<CDMA Chain 1 
LNA>,<CDMA TX AGC>,<SID>,<NID>,<CDMA 
EC/IO>,<BID>]  
+CPSI: eHRPD, <Operation Mode>[,<MCC> -<MNC>,<EVDO ch 
num>,<EVDO RX Chain 0 AGC>,<EVDO RX Chain 1 AGC>,< 
EVDO TX AGC>,<EVDO Serving PN>,<EVDO Rel0 
SCI>,<EVDO RelA SCI>,<EVDO EC/IO>]  
OK 
SIMCom Confidential File
---

## Page 103

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 102 If camping on 1xlte cell:  
+CPSI: CDMA ,<Operation Mode>[ ,<MCC>- <MNC>,<CDMA ch 
num>,<CDMA pilot PN>,<CDMA RX Chain 0 AGC>,<CDMA 
RX Chain 1 AGC>,<CDMA Chain 0 LNA>,<CDMA Chain 1 
LNA>,<CDMA TX AGC>,<SID>,<NID>,<CDMA 
EC/IO>,<BID>]  
+CPSI: LTE, <Operation Mode>[,<MCC> -<MNC>,<TAC>,<SCe
llID>,<PCellID>,<Frequency Band>,<earfcn>,<dlbw>,<ulbw>,<R
SRQ>,<RSRP>,<RSSI>,<RSSNR>]  
OK 
If no service:  
+CPSI: NO SERVICE, Online  
OK 
ERROR 
Write Command  Responses 
AT+CPSI= <time>  OK 
ERROR 
Defined values  
<time>  
The range is 0 -255, unit is second, after set <time>  will report the system information every th e 
seconds. 
<System Mode>  
System mode, values: “NO SERVICE”, “GSM”, “WCDMA”, “LTE”, “TDS”…  
If module in LIMITED SERVICE state and +CNLSA command is set to 1, the system mode will 
display as “GSM -LIMITED”, “WCDMA -LIMITED”…  
<Operation Mode> 
UE operation mode, values: “Unknown”, “Online”,  “Offline”,  “Factory Test Mode”,  “Reset”, “Low 
Power Mode”. 
<MCC>  
Mobile Country Code (first part of the PLMN code)  
<MNC>  
Mobile Network Code (second part of the PLMN code) 
<LAC>  
Location Area Code (hexadecimal digits ) 
<Cell ID>  
Service -cell Identify.  
<Absolute RF Ch Num>  
AFRCN for service -cell. 
<Track LO Adjust>  
Track LO Adjust  
SIMCom Confidential File
---

## Page 104

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 103 <C1>  
Coefficient for base station selection  
<C2>  
Coefficient for Cell re -selection  
<Frequency Band> 
Frequency Band of active set  
<PSC>  
Primary synchronization code  of active set . 
<Freq>  
Downlink frequency of active set. 
<SSC>  
Secondary synchronization code of active set  
<EC/IO>  
Ec/Io value  
<RSCP>  
Received Signal Code Power  
<Qual>  
Quality value for base station selection  
<RxLev>  
RX level value for base station selection  
<TXPWR>  
UE TX power in dBm. If no TX, the value is 500. 
<Cpid>  
Cell Parameter ID  
<TAC>  
Tracing Area Code  
<PCellID>  
Physical Cell ID  
<earfcn>  
E-UTRA absolute radio frequency channel number for se arching LTE cells  
<dlbw> 
Transmission bandwidth configuration of the serving cell on the downlink  
<ulbw>  
Transmission bandwidth configuration of the serving cell on the uplink 
<RSRP>  
Current reference signal received power in -1/10 dBm. Available for LTE  
<RSRQ>  
Current reference signal receive quality as measured by L1.  
<RSSNR>  
Average reference signal signal -to-noise ratio of the serving cell 
<BID>  
Base ID  
SIMCom Confidential File
---

## Page 105

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 104 Examples 
AT+CPSI?  
+CPSI: GSM,Online,460- 00,0x182d,12401,27 EGSM 900,-64,2110,42-42 
OK 
AT+CPSI?  
+CPSI: WCDMA,Online,460-01,0xA809,11122855,WCDMA IMT 2000,279,10663,0,1.5,62,33, 
52,500 
OK 
AT+CPSI=?  
+CPSI: (0 -255) 
OK 
5.15  AT+CNSMOD  Show network system mode  
Description  
This command is used to return the current network system mode.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CNSMOD=?  +CNSMOD: (list of supported  <n> s) 
OK 
Read Command  Responses  
AT+CNSMOD?  +CNSMOD: <n>,<stat>  
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses  
AT+CNSMOD=<n>  OK 
ERROR 
+CME ERROR: <er r> 
Defined values  
<n> 
0  –  disable auto report the network system mode information 
1  –  auto report the network system mode information, command: +CNSMOD:<stat> 
<stat>  
SIMCom Confidential File
---

## Page 106

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 105 0  –  no service  
1  –  GSM  
2  –  GPRS  
3  –  EGPRS (EDGE)  
4  –  WCDMA  
5  –  HSDPA o nly(WCDMA)  
6  –  HSUPA only(WCDMA)  
7  –  HSPA (HSDPA and HSUPA, WCDMA)  
8  –  LTE  
9  –  TDS -CDMA 
10  –  TDS -HSDPA only  
11  –   TDS - HSUPA only 
12  –  TDS - HSPA (HSDPA and HSUPA)  
13  –  CDMA  
14  –  EVDO 
15  –  HYBRID (CDMA and EVDO)  
16  –  1XLTE(CDMA and LTE)  
23  –  eHRPD  
24  –  HYBRID(CDMA and eHRPD)  
Examples 
AT+CNSMOD?  
+CNSMOD: 0,2 
OK 
5.16  AT+CEREG  EPS network registration status  
Description  
The set command controls the presentation of an unsolicited result code +CEREG:  <stat>  when 
<n>=1 and there is a cha nge in the MT's EPS network registration status in E -UTRAN, or 
unsolicited result code +CEREG: <stat> [,<tac> ,<ci>[,<AcT> ]] when <n> =2 and there is a change 
of the network cell in E -UTRAN; in this latest case <AcT> , <tac>  and <ci> are sent only if 
available . 
NOTE  1: If the EPS MT in GERAN/UTRAN/E -UTRAN also supports circuit mode services and/or 
GPRS services, the +CREG  command and +CREG : result codes and/or the +CGREG command 
and +CGREG: result codes apply to the registration status and location information for those 
services.  
The read command returns the status of result code presentation and an integer <stat> which shows 
whether the network has currently indicated the registration of the MT. Location information 
elements <tac> , <ci> and <AcT> , if available,  are returned only when <n>=2  and MT is registered 
in the network. 
SIMCom Confidential File
---

## Page 107

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 106 SIM PIN  References  
NO 3GPP  TS 24.008 [8]  
Syntax 
Test Command  Responses 
AT+CEREG=?  +CEREG : (list of supported <n>s) 
OK 
ERROR 
Read Command  Responses 
AT+CEREG?  +CEREG:  <n>,<stat> [,<tac>,<ci>[,<AcT> ]] 
OK 
ERROR 
Write Command  Responses  
AT+ CERE G=[<n>] OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses 
AT+CEREG  Set default value （<n>=0）: 
OK 
ERROR  
Defined values  
<n> 
0  –  disable network registration unsolicited result code 
1  –  enable network registration unsolicited result code +CEREG: <stat>  
2 – enable network registration and location information unsolicited result code 
+CEREG:  <stat> [,<tac> ,<ci> [,<AcT> ]] 
<stat>  
0 –  not registered, MT is not currently searching an ope rator to register to  
1 – registered, home network 
2 – not registered, but MT is currently trying to attach or searching an operator to register to 
3 – registration denied  
4 – unknown (e.g. out of E- UTRAN coverage)  
5 – registered, roaming 
6 – registered for  "SMS only", home network (not applicable) 
7 – registered for "SMS only", roaming (not applicable) 
8 – attached for emergency bearer services only (See NOTE  2) 
<tac>  
string type; two byte tracking area code in hexadecimal format (e.g. "00C3" equals 195 i n decimal)  
SIMCom Confidential File
---

## Page 108

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 107 <ci> 
string type; four byte E -UTRAN cell identify  in hexadecimal format  
<AcT>  
A numberic parameter that indicates the access technology of serving cell  
0 GSM (not applicable) 
1 GSM Compact (not applicable)  
2 UTRAN (not applicable)  
3 GSM w/EG PRS (see NOTE  3) (not applicable) 
4 UTRAN w/HSDPA (see NOTE  4) (not applicable) 
5 UTRAN w/HSUPA (see NOTE  4) (not applicable) 
6 UTRAN w/HSDPA and HSUPA (see NOTE  4) (not applicable) 
7 E- UTRAN  
Examples 
AT+CEREG?  
+CEREG: 0,4  
OK 
5.17  AT+CTZU  Automatic time an d time zone update  
Description  
This command is used to enable and disable automatic time and time zone update via NITZ 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CTZU=?  +CTZU: (list of supported <on/off>s) 
OK 
Read Command  Responses 
AT+CTZU?  +CTZU: < on/off >  
OK 
Write Command  Responses 
AT+CTZU= < on/off >  OK 
ERROR 
Defined values  
SIMCom Confidential File
---

## Page 109

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 108 <on/off> 
Integer type value indicating:  
    0  –  Disable automatic time zone update via NITZ (default).  
1  –  Enable automatic time zone update via NITZ.  
NOTE:  1. The value of < on/off >  is nonvolatile, and factory value is 0. 
2. For automatic time and time zone update is enabled ( +CTZU =1): 
If time zone is only received from network and it isn’t equal to local time zone 
(AT+CCLK ), time zone is  updated automatically, and real time clock is updated based 
on local time and the difference between time zone from network and local time zone 
(Local time zone must be valid).  
If Universal Time and time zone are received from network, both time zone and real 
time clock is updated automatically, and real time clock is based on Universal Time and 
time zone from network. 
Examples 
AT+CTZU?  
+CTZU: 0  
OK 
AT+CTZU=1  
OK 
5.18  AT+CTZR  Time and time zone reporting  
Description  
This command is used to enable and disa ble the time zone change event reporting. If the reporting 
is enabled the MT returns the unsolicited result code +CTZV: <tz>[,<time> ][,<dst> ]whenever the 
time zone is changed.  
NOTE:  The time zone reporting is not affected by the Automatic Time and Time Zone command  
AT+CTZU . 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CTZR=?  +CTZR: (list of supported < on/off > s) 
OK 
Read Command  Responses 
AT+CTZR?  +CTZR: < on/off >  
OK 
Write Command  Responses 
SIMCom Confidential File
---

## Page 110

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 109 AT+CTZR= < on/off >  OK 
ERROR 
Execution Command Responses 
AT+CTZR  Set default value: 
OK 
Defined values  
<on/off> 
Integer type value indicating:  
    0  –  Disable time zone change event reporting (default).  
1  –  Enable time zone change event reporting.  
+CTZV: <tz>[,<time> ][,<dst> ] 
Unsolicited result code when time zone received from network isn’t equal to local time zone, and if 
the informations from network don’t include date and time, time zone will be only reported, and if 
network daylight saving time is present, it is also reported. For example: 
+CTZV: 32  (Only report time zone)   
+CTZV: 32,1  (Report time zone and network daylight saving time)  
+CTZV: 32,08/12/09,17:00:00  (Report time and time zone)  
+CTZV: 32,08/12/09,17:00:00,1  (Report time, time zone and daylight saving time)  
For more detailed informations about time and time zone, please refer 3GPP TS 24.008. 
<tz>    Local time zone received from network.  
<time>  Universal time received from network, and the format is “ yy/MM/dd,hh:mm:ss ”, 
where characters indicate year (two la st digits), month, day, hour, minutes and 
seconds. 
<dst>   Network daylight saving time, and if it is received from network, it indicates the 
value that has been used to adjust the local time zone. The values as following: 
            0  –  No adjustment for Daylight Saving Time. 
            1  –  +1 hour adjustment for Daylight Saving Time. 
            2  –  +2 hours adjustment for Daylight Saving Time. 
NOTE:  Herein,  <time>  is Universal Time or NITZ time, but not local time.  
Examples 
AT+CTZR?  
+CTZR: 0 
OK 
AT+CTZR=1  
OK 
SIMCom Confidential File
---

## Page 111

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 110 6 AT Commands for Call Control 
6.1  AT+CVHU  Voice hang up control  
Description  
Write command selects whether ATH  or “drop DTR ” shall cause a voice connection to be 
disconnected or not. By voice connection is also meant al ternating mode calls that are currently in 
voice mode.  
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CVHU=?  +CVHU: ( list of supported <mode> s) 
OK 
Read Command  Responses 
AT+CVHU?  +CVHU: <mode>  
OK 
Write Command  Responses 
AT+CV HU= <mode>  OK 
ERROR 
Execution Command Responses 
AT+CVHU Set default value: 
OK 
Defined values  
<mode>  
0  –  “Drop DTR ” ignored but OK response given. ATH  disconnects.  
1  –  “Drop DTR ” and ATH ignored but OK response given. 
Examples 
AT+CVHU=0  
OK 
AT+CV HU?  
+CVHU: 0 
OK 
SIMCom Confidential File
---

## Page 112

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 111 6.2  AT+CHUP  Hang up call  
Description  
This command is used to cancel voice calls. If there is no call, it will do nothing but OK response is 
given. After running AT+CHUP, multiple “VOICE CALL END: ” may be reported which relies on 
how many calls exist before calling this command.  
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CHUP=?  OK 
Execution Command Responses 
AT+CHUP  VOICE CALL: END: <time>  
[… 
VOICE CALL: END: <time> ] 
OK 
No call:  
OK 
Defined values  
<time>  
Voice call connection time.  
Format  –  HHMMSS (HH: hour, MM: minute, SS: second)  
Examples 
AT+CHUP  
VOICE CALL:END: 000017  
OK 
6.3  AT+CBST  Select bearer service type  
Description  
Write command selects the bearer service <name>  with data rate <speed> , and the connection 
element <ce>  to be used when data calls are originated. Values may also be used during mobile 
terminated data call setup, especially in case of single numbering scheme calls.  
SIM PIN  References  
SIMCom Confidential File
---

## Page 113

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 112 YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CBST=?  +CBST: (list of supported <speed> s), (list of supported <name> s), 
(list of supported <ce> s) 
OK 
Read Command  Responses 
AT+CBST?  +CBST: <speed> ,<name> ,<ce>  
OK 
Write Command  Responses 
AT+CBST=  
<speed> [,<name> [,<ce> ]] OK 
ERROR 
Execution Comma nd Responses  
AT+CBST Set default value: 
OK 
Defined values  
<speed>  
0    –    autobauding(automatic selection of the speed; this setting is possible in case of 3.1 
kHz modem and non- transparent service)  
7  –  9600 bps (V.32)  
12  –  9600 bps (V.34)  
14  –  14400 bps(V.34) 
16  –  28800 bps(V.34) 
17  –  33600 bps(V.34) 
39  –  9600 bps(V.120)  
43  –  14400 bps(V.120) 
48  –  28800 bps(V.120) 
51  –  56000 bps(V.120) 
71  –  9600 bps(V.110)  
75  –  14400 bps(V.110) 
80  –  28800 bps(V.110 or X.31 flag stuffing) 
81  –  38400 bps(V.110 or X.31 flag stuffing) 
83  –  56000 bps(V.110 or X.31 flag stuffing) 
84  –  64000 bps(X.31 flag stuffing) 
116  –  64000 bps(bit transparent) 
134  –  64000 bps(multimedia) 
<name>  
0  –  Asynchronous modem 
1  –  Synchronous modem 
SIMCom Confidential File
---

## Page 114

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 113 4  –  data circuit asynchronous (RDI) 
<ce>  
0  –  transparent  
 1  –  non-transparent  
NOTE: If <speed>  is set to 116 or 134, it is necessary that <name>  is equal to 1 and  <ce>  is equal 
to 0. 
Examples 
AT+CBST=0,0,1  
OK 
AT+CBST?  
+CBST:0,0,1  
OK  
6.4  AT+CRLP  Radio lin k protocol  
Description  
Radio Link Protocol(RLP) parameters used when non- transparent data calls are originated may be 
altered with write command.  
Read command returns current settings for each supported RLP version <verX> . Only RLP 
parameters applicable t o the corresponding <verX>  are returned.  
Test command returns values supported by the TA as a compound value. If ME/TA supports several 
RLP versions <verX> , the RLP parameter value ranges for each <verX>  are returned in a separate 
line. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CRLP=?  +CRLP: ( list of supported <iws> s), (list of supported <mws> s), 
(list of supported <T1> s), (list of supported <N2> s) [,<ver1>  
[,(list of supported  <T4> s)]][<CR><LF>  
+CRLP: ( list of supported <iws>s), (list of supported <mws> s), 
(list of supported <T1> s), (list of supported <N2> s) [,<ver2>  
[,(list of supported  <T4> s)]] 
[...]] 
OK 
Read Command  Responses 
AT+CRLP?  +CRLP: <iws> , <mws> , <T1> , <N2>  [,<ver1>  [, <T4> ]][<CR>
<LF>  
SIMCom Confidential File
---

## Page 115

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 114 +CRLP: <iws> ,<mws> ,<T1> ,<N2> [,<ver2> [,<T4> ]] 
[...]] 
OK 
Write Command  Responses 
AT+CRLP=<iws>  
[,<mws> [,<T1> [,<N2>  
[,<ver> [,<T4> ]]]]] OK 
ERROR 
Execution Command Responses 
AT+CRLP  OK 
Defined values  
<ver>, <verX>  
RLP version number in integer format, and it can be 0, 1 or 2; w hen version indication is not 
present it shall equal 1.  
<iws>  
IWF to MS window size.  
<mws>  
MS to IWF window size.  
<T1>  
Acknowledgement timer.  
<N2>  
Retransmission attempts.  
<T4>  
Re-sequencing period in integer format. 
NOTE:  <T1>  and <T4>  are in u nits of 10 ms. 
Examples 
AT+CRLP?  
+CRLP:61,61,48,6,0 
+CRLP:61,61,48,6,1 
+CRLP:240,240,52,6,2 
OK 
6.5  AT+CR  Service reporting control  
Description  
SIMCom Confidential File
---

## Page 116

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 115 Write command controls whether or not intermediate result code “+CR:  <serv>” is returned from 
the TA to the TE. If enabled, the intermediate result code is transmitted at the point during connect 
negotiation at which the TA has determined which speed and quality of service will be used, before 
any error control or data compression reports are transmitted, and before  the intermediate result 
code CONNECT is transmitted.  
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CR=?  +CR: (list of supported <mode> s) 
OK 
Read Command  Responses 
AT+CR?  +CR: <mode>  
OK 
Write Command  Responses  
AT+CR= <mode>  OK 
Execution Command Responses 
AT+CR  Set default value: 
OK 
Defined values  
<mode>  
0  –  disables reporting 
1  –  enables reporting  
<serv>  
ASYNC    asynchronous transparent 
SYNC    synchronous transparent 
 REL ASYNC   asynchronous non- transparent  
 REL syn c   synchronous non- transparent  
 GPRS [ <L2P> ] GPRS  
The optional <L2P>  proposes a layer 2 protocol to use between the MT and the TE. 
Examples 
AT+CR?  
+CR:0  
OK 
AT+CR=1  
OK 
SIMCom Confidential File
---

## Page 117

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 116 6.6  AT+CRC  Cellular result codes  
Description  
Write command controls whether or not th e extended format of incoming call indication or GPRS 
network request for PDP context activation is used. When enabled, an incoming call is indicated to 
the TE with unsolicited result code “+CRING:  <type> ” instead of the normal RING. 
Test command returns values supported by the TA as a compound value. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CRC=?  +CRC: ( list of supported <mode> s) 
OK 
Read Command  Responses 
AT+CRC?  +CRC: <mode>  
OK 
Write Command  Responses 
AT+CRC= <mode>  OK 
Execution Command  Responses  
AT+CRC  Set default value: 
OK 
Defined values  
<mode> 
0 – disable extended format  
 1 – enable extended format 
<type>  
ASYNC        asynchronous transparent 
 SYNC        synchronous transparent 
 REL ASYNC       asynchronous non-t ransparent  
 REL SYNC       synchronous non- transparent  
 FAX         facsimile  
 VOICE        normal voice  
VOICE/ XXX voice followed by data( XXX is ASYNC, SYNC, REL ASYNC or REL 
SYNC)  
 ALT VOICE/ XXX  alternating voice/data, voice first  
 ALT XXX/VOICE  alternatin g voice/data, data first  
 ALT FAX/VOICE  alternating voice/fax, fax first 
SIMCom Confidential File
---

## Page 118

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 117  GPRS     GPRS network request for PDP context activation 
Examples 
AT+CRC=1  
OK 
AT+CRC?  
+CRC: 1  
OK 
 
6.7  AT+CLCC  List current calls  
Description  
This command isused to return list of current calls of ME. If command succeeds but no calls are 
available, no information response is sent to TE. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CLCC=?  +CLCC: (list of supported <n>s) 
OK 
Read Command  Responses 
AT+CLCC ? +CLCC: <n> 
OK 
Write Command  Responses  
AT+CLCC =<n> OK 
Execution Command Responses 
AT+CLCC  +CLCC: <id1> ,<dir> ,<stat> ,<mode> ,<mpty> [,<number> ,<type> [,<
alpha> ]][<CR><LF>  
+CLCC: <id2> ,<dir> ,<stat> ,<mode> ,<mpty> [,<number> ,<type> [,<
alpha> ]] 
[...]] 
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
SIMCom Confidential File
---

## Page 119

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 118 <n> 
0  –  Don’t report a list of current calls of ME automatically when the current call status 
changes.  
1  –  Report a list of current calls of ME automatically when the current call status changes.  
<idX>  
Integer typ e, call identification number, this number can be used in +CHLD command operations. 
<dir>  
0  –  mobile originated (MO) call  
1  –  mobile terminated (MT) call 
<stat>  
State of the call: 
0  –  active  
1  –  held 
2  –  dialing (MO call)  
3  –  alerting (MO call)  
4  –  incoming (MT call)  
5  –  waiting (MT call) 
6  –  disconnect 
<mode> 
bearer/teleservice:  
0  –  voice  
1  –  data 
2  –  fax  
9  –  unknown 
<mpty>  
0  –  call is not one of multiparty (conference) call parties 
1  –  call is one of multiparty (confe rence) call parties  
<number> 
String type phone number in format specified by  <type> . 
<type>  
Type of address octet in integer format; 
128  –   Restricted number type includes unknown type and format 
145  –   International number type 
161  –   national number.The network support for this type is optional 
177  –   network specific number,ISDN format 
    129  –   Otherwise  
<alpha> 
String type alphanumeric representation of <number>  corresponding to the entry found in 
phonebook; used character set should be the  one selected with command Select TE Character Set 
AT+CSCS . 
Examples  
SIMCom Confidential File
---

## Page 120

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 119 ATD10011; 
OK 
AT+CLCC  
+CLCC: 1,0,0,0,0,"10011",129,"sm" 
OK 
RING (with incoming call)  
AT+CLCC  
+CLCC: 1,1,4,0,0,"02152063113",128,"gongsi"  
OK 
 
6.8  AT+CEER  Extended error report  
Descrip tion 
Execution command causes the TA to return the information text <report> , which should offer the 
user of the TA an extended report of the reason for: 
1 The failure in the last unsuccessful call setup(originating or answering) or in- call 
modification. 
2 The last call release.  
3 The last unsuccessful GPRS attach or unsuccessful PDP context activation. 
4 The last GPRS detach or PDP context deactivation.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CEER=?  OK 
Execution Command Responses 
AT+CEER  +CEER: <report>  
OK 
Defined values  
<report>  
Wrong information which is possibly occurred. 
Examples 
AT+CEER  
+CEER: Invalid/incomplete number  
SIMCom Confidential File
---

## Page 121

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 120 OK 
6.9  AT+CCWA  Call waiting  
Description  
This command allows control of the Call Waiting supplementary s ervice. Activation, deactivation 
and status query are supported. When querying the status of a network service ( <mode> =2) the 
response line for 'not active' case ( <status> =0) should be returned only if service is not active for 
any <class> . Parameter <n> is used to disable/enable the presentation of an unsolicited result code 
+CCW A: <number> ,<type> ,<class>  to the TE when call waiting service is enabled. Command 
should be abortable when network is interrogated. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CCWA=?  +CCWA: (list of supported  <n>s) 
OK 
Read Command  Responses 
AT+CCW A?  +CCWA: <n> 
OK 
Write Command  Responses 
AT+CCWA=  
<n>[,<mode> [,<class> ]] When <mode>=2 and command successful: 
+CCWA: <status> ,<class> [<CR><LF>  
+CCWA: <status> , <class> [...]] 
OK 
ERROR  
+CME ERROR: <err>  
Execution Command  Responses  
AT+CCWA  Set default value ( <n>=0):  
OK 
Defined values  
<n> 
Sets/shows the result code presentation status in the TA 
0  –  disable  
1  –  enable  
<mode>  
SIMCom Confidential File
---

## Page 122

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 121 When <mode> parameter is not given, network is not interrogated: 
0  –  disable  
1  –  enable  
2  –  query status 
<class>  
It is a sum of integers each representing a class of information (default 7) 
1    –   voice (telephony) 
2    –   data (refers to all bearer services)  
4    –   fax (facsimile services) 
7    –   voice,data and fax(1+2+4) 
8    –   short message service  
16   –   data circuit sync  
32   –   data circuit async 
64   –   dedicated packet access  
128  –   dedicated PAD access  
255  –   The value 255 covers all classes  
<status>  
0  –  not active  
1  –  active  
<number> 
String type phone number of calling address in format specified by <type> . 
<type>  
Type of address octet in integer format;  
128  –   Restricted number type includes unknown type and format 
145  –   International number type  
    129  –   Otherwise  
Examples 
AT+CCWA=?  
+CCWA:(0 -1) 
OK 
AT+CCWA?  
+CCWA: 0  
OK 
6.10  AT+CHLD  Call related supplementary services  
Description  
SIMCom Confidential File
---

## Page 123

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 122 This command allows the control the following call related services:  
1. A call can be temporarily disconnecte d from the ME but the connection is retained by the 
network. 
2. Multiparty conversation (conference calls). 
3. The served subscriber who has two calls (one held and the other either active or alerting) 
can connect the other parties and release the served subscriber's own connection. 
Calls can be put on hold, recovered, released, added to conversation, and transferred. This is 
based on the GSM/UMTS supplementary services.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CHLD=?  +CHLD : (list of supported <n> s) 
OK 
Write Command  Responses 
AT+CHLD= <n> OK 
ERROR  
+CME ERROR: <err>  
Execution Command  Responses  
AT+CHLD  
Default to <n>=2. OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<n> 
0   –  Terminate all held calls; or set User Dete rmined User Busy for a waiting call  
1   –  Terminate all active calls and accept the other call (waiting call or held call)  
1X  –  Terminate a specific call X  
2   –  Place all active calls on hold and accept the other call (waiting call or held call) as 
the active call  
2X  –  Place all active calls except call X on hold  
3   –  Add the held call to the active calls  
4   –  Connect two calls and cut off the connection between users and them simultaneously 
Examples 
AT+CHLD=?  
+CHLD: (0,1,1x,2,2x,3,4) 
OK 
SIMCom Confidential File
---

## Page 124

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 123 6.11  AT+C CFC  Call forwarding number and conditions  
Description  
This command allows control of the call forwarding supplementary service. Registration, erasure, 
activation, deactivation, and status query are supported. 
SIM PIN  References  
YES 3GPP TS 27.007 
Synta x 
Test Command  Responses 
AT+CCFC=?  +CCFC: (list of supported <reason> s) 
OK 
Write Command  Responses 
AT+CCFC= <reason> ,<mode
>[,<number> [,<type> [,<clas
s>[,<subaddr> [,<satype> [,<ti
me> ]]]]]]  When <mode>=2 and command successful: 
+CCFC: <status> ,<class1> [,<number> ,<type>  
[,<subaddr> ,<satype> [,<time> ]]][<CR><LF>  
+CCFC: <status> ,<class2> [,<number> ,<type>  
[,<subaddr> ,<satype> [,<time> ]]][...]]  
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<reason>  
0  –  unconditional 
1  –  mobile busy 
2  –  no reply 
3  –  not rea chable  
4  –  all call forwarding  
5  –  all conditional call forwarding  
<mode> 
0  –  disable  
1  –  enable  
2  –  query status 
3  –  registration  
4  –  erasure  
<number> 
String type phone number of forwarding address in format specified by <type> . 
SIMCom Confidential File
---

## Page 125

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 124 <type>  
Type of address octet in integer format: 
145  –   dialing string <number> includes international access code character ‘+’  
129  –   otherwise  
<subaddr> 
String type sub address of format specified by <satype> . 
<satype>  
Type of sub address octet in intege r format, default 128.  
<classX>  
It is a sum of integers each representing a class of information (default 7): 
1    –   voice (telephony) 
2    –   data (refers to all bearer services)  
4    –   fax (facsimile services) 
16   –   data circuit sync  
32  –  data ci rcuit async  
64   –   dedicated packet access  
128  –   dedicated PAD access  
255  –   The value 255 covers all classes  
<time>  
1...30  –  when "no reply" is enabled or queried, this gives the time in seconds to wait before call 
is forwarded, default value 20. 
<status>  
0  –  not active  
1  –  active  
Examples 
AT+CCFC=?  
+CCFC: (0,1,2,3,4,5) 
OK 
AT+CCFC=0,2  
+CCFC: 0,255  
OK 
6.12  AT+CLIP  Calling line identification presentation  
Description  
SIMCom Confidential File
---

## Page 126

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 125 This command refers to the GSM/UMTS supplementary service CLIP (Calling Line  Identification 
Presentation) that enables a called subscriber to get the calling line identity (CLI) of the calling 
party when receiving a mobile terminated call.  
Write command enables or disables the presentation of the CLI at the TE. It has no effect on  the 
execution of the supplementary service CLIP in the network. 
When the presentation of the CLI at the TE is enabled (and calling subscriber allows), +CLIP: 
<number> ,<type> ,,[,[<alpha> ][,<CLI validity> ]] response is returned after every RING (or 
+CRING: <type> ; refer sub clause "Cellular result codes +CRC") result code sent from TA to TE. It 
is manufacturer specific if this response is used when normal voice call is answered.  
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CLIP= ? +CLIP: (list of supported <n> s) 
OK 
Read Command  Responses 
AT+CLIP?  +CLIP: <n> ,<m>  
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+CLIP= <n> OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses 
AT+CLIP  Set default value( <n>=0): 
OK 
Defined values  
<n> 
Parameter sets/shows the result code presentation status in the TA:  
0  –  disable  
1  –  enable  
<m>  
0  –  CLIP not provisioned 
1  –  CLIP provisioned 
2  –  unknown (e.g. no network, etc.) 
<number> 
SIMCom Confidential File
---

## Page 127

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 126 String type phone number of calling address in format specified by <type> . 
<type>  
Type of address octet in integer format;  
128  –   Restricted number type includes unknown type and format 
145  –   International number type 
161  –   national number.The network support for this type is optional 
177  –   network specific number,ISDN format 
    129  –   Otherwise  
<alpha> 
String type alphanumeric representation of <number> corresponding to the entry found in phone 
book. 
<CLI validity>  
0  –  CLI valid  
1  –  CLI has been withheld by the originator 
2  –   CLI is not available due to interworking problems or limitations of originating           
network 
Examples 
AT+CLIP=1  
OK 
RING (with incoming call) 
+CLIP: "02152063113",128,,,"gongsi",0  
6.13  AT+CLIR  Calling line identification restriction  
Description  
This command refers to CLIR -service that allows a calling subscriber to enable or disable the 
presentation of the CLI to the called party when originating a call. 
Write command overrides the CLIR subscription (default is restricted or allowed) when temporary  
mode is provisioned as a default adjustment for all following outgoing calls. This adjustment can be 
revoked by using the opposite command.. If this command is used by a subscriber without 
provision of CLIR in permanent mode the network will act. 
Read com mand gives the default adjustment for all outgoing calls (given in <n>), and also triggers 
an interrogation of the provision status of the CLIR service (given in <m> ). 
Test command returns values supported as a compound value. 
SIM PIN  References  
YES 3GPP  TS 27.007 
Syntax 
Test Command  Responses 
SIMCom Confidential File
---

## Page 128

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 127 AT+CLIR=?  +CLIR: (list of supported  <n> s) 
OK 
Read Command  Responses 
AT+CLIR?  +CLIR: <n> ,<m>  
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+CLIR= <n> OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<n> 
0  –  presentation indicator is used according to the subscription of the CLIR service 
1  –  CLIR invocation  
2  –  CLIR suppression  
<m>  
0  –  CLIR not provisioned  
1  –  CLIR provisioned in permanent mode 
2  –  unknown (e.g. no network, etc.) 
3  –  CLIR  temporary mode presentation restricted  
4  –  CLIR temporary mode presentation allowed 
Examples 
AT+CLIR=?  
+CLIR:(0 -2) 
OK 
6.14  AT+COLP  Connected line identification presentation  
Description  
This command refers to the GSM/UMTS supplementary service COLP(Conn ected Line 
Identification Presentation) that enables a calling subscriber to get the connected line identity 
(COL) of the called party after setting up a mobile originated call. The command enables or 
disables the presentation of the COL at the TE. It has no effect on the execution of the 
supplementary service COLR in the network. 
When enabled (and called subscriber allows), +COLP: <number> , <type>  [,<subaddr> , <satype> 
[,<alpha> ]] intermediate result code is returned from TA to TE before any +CR responses. It is 
SIMCom Confidential File
---

## Page 129

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 128 manufacturer specific if this response is used when normal voice call is established.  
When the AT+COLP=1 is set, any data input immediately after the launching of “ATDXXX;” will 
stop the execution of the ATD command, which may cancel the establishing of the call.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+COLP=?  +COLP: (list of supported <n>s) 
OK 
Read Command  Responses 
AT+COLP?  +COLP: <n> ,<m>  
OK 
ERROR 
+CME ERROR: <err>  
Write Command  Responses 
AT+COLP = <n> OK 
ERROR  
+CME ERROR: <err>  
Execution Command  Responses  
AT+COLP  Set default value( <n>=0,  <m> =0): 
OK 
Defined values  
<n> 
Parameter sets/shows the result code presentation status in the TA:  
0  –  disable  
1  –  enable  
<m>  
0  –  COLP not provisioned 
1  –  COLP provisioned 
2  –  unknown (e.g. no network, etc.) 
Examples 
AT+COLP?  
+COLP: 1,0 
OK 
ATD10086;  
VOICE CALL: BEGIN  
SIMCom Confidential File
---

## Page 130

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 129  
+COLP: "10086",129,,,  
 
OK 
6.15  AT+VTS  DTMF and tone generation  
Description  
This command allows the transmission of DTMF tones and arbitrary tones which cause the Mobile 
Switching Center (MSC) to transmit tones to a remote subscriber. The command can only be used 
in voice mode of operation (active voice call).  
NOTE : The END event of voice call will terminate the transmission of tones, and as an  operator 
option, the tone may be ceased after a pre- determined time whether or not tone duration has been 
reached.  
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+VTS=?  +VTS: (list of supported <dtmf> s) 
OK 
Write Command  Responses  
AT+VTS= <dtmf>  
[,<duration> ] 
 
AT+VTS= <dtmf -string>  OK 
ERROR 
Defined values  
<dtmf>  
A single ASCII character in the set 0 -9, *, #, A, B, C, D.  
<duration>  
Tone duration in 1/10 seconds, from 0 to 255. This is interpreted as a DTMF tone of different 
duration from that mandated by the AT+VTD  command, otherwise, the duration which be set the 
AT+VTD command will be used for the tone ( <duration>  is omitted).  
<dtmf -string>  
A sequence of ASCII character in the set 0 -9, *, #, A, B, C, D, and maximal length of  the string is 
29. The string must be enclosed in double quotes (“”), and separated by commas between the ASCII 
characters (e.g. “1,3,5,7,9,*”). Each of the tones with a duration which is set by the AT+VTD  
command. 
SIMCom Confidential File
---

## Page 131

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 130 Examples 
AT+VTS=1  
OK 
AT+VTS=1,20  
OK 
AT+VTS=”1,3,5” 
OK 
AT+VTS=?  
+VTS: (0 -9,*,#,A,B,C,D)  
OK 
6.16  AT+VTD  Tone duration  
Description  
This refers to an integer <n>  that defines the length of tones emitted as a result of the AT+VTS  
command. A value different than zero causes a tone of duration <n> /10 seconds. 
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+VTD=?  +VTD: ( list of supported <n> s) 
OK 
Read Command  Responses  
AT+VTD?  +VTD: <n>  
OK 
Write Command  Responses  
AT+VTD= <n> OK 
Defined values  
<n> 
Tone duration in integer format, from 0 to 255, and 0 is factory value. 
0       Tone duration of every single tone is dependent on the network. 
1…255   Tone duration of every single tone in 1/10 seconds. 
Examples 
AT+VTD=?  
+VTD: (0 -255) 
SIMCom Confidential File
---

## Page 132

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 131 OK 
AT+VTD?  
+VTD: 0  
OK 
AT+VTD=5  
OK 
6.17  AT+CSTA  Select type of address  
Description  
Write command is used to select the type of number for further dialing commands ( ATD ) according 
to GSM/UMTS specifications.  
Read command returns the current type of number. 
Test command returns values supported by the Module as a compound value. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CSTA=?  +CSTA:(list of supported <type> s) 
OK 
Read Command  Responses  
AT+CSTA?  +CSTA: <type>  
OK 
Write Command  Responses 
AT+ CSTA= <type>  OK  
ERROR 
Execution Command Responses 
AT+CSTA  OK 
Defined values  
<type>  
Type of address octet in integer format: 
145  –   when dialling string includes international access code character “+”  
161  –   national number.The network support for this type is optional 
177  –   network specific number,ISDN format 
129  –   otherwise  
NOTE : Because the type of address is automatically detected on the dial string of dialing 
command, command AT+CSTA  has really no effect.  
SIMCom Confidential File
---

## Page 133

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 132 Examp les 
AT+CSTA?  
+CSTA: 129 
OK 
AT+CSTA=145  
OK 
6.18  AT+CMOD  Call mode  
Description  
Write command selects the call mode of further dialing commands ( ATD ) or for next answering 
command ( ATA). Mode can be either sing le or alternating.  
Test command returns values supported by the TA as a compound value. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CMOD=?  +CMOD: ( list of supported  <mode> s) 
OK 
Read Command  Responses 
AT+CMOD?  +CMOD: <mode>  
OK 
Write Command  Responses  
AT+CMOD= <mode>  OK 
ERROR 
Execution Command Responses 
AT+CMOD  Set default value:  
OK 
Defined values  
<mode> 
0  –  single mode(only supported) 
NOTE:  The value of <mode>  shall be set to zero after a successfully completed alter nating mode 
call. It shall be set to zero also after a failed answering. The power -on, factory and user resets shall 
also set the value to zero. This reduces the possibility that alternating mode calls are originated or 
answered accidentally.  
SIMCom Confidential File
---

## Page 134

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 133 Examples 
AT+CMOD?  
+CMOD: 0  
OK 
AT+CMOD=0  
OK 
6.19  AT+VMUTE  Speaker mute control  
Description  
This command is used to control the loudspeaker to mute and unmute during a voice call or a video 
call which is connected. If there is not a connected call, write command can’t be used. 
When all calls are disconnected, the Module sets the subparameter as 0 automatically.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+VMUTE=?  +VMUTE: ( list of supported <mode> s) 
OK 
Read Command  Responses 
AT+VMUTE?  +VMUTE: <mode>  
OK 
Write Command  Responses  
AT+VMUTE= <mode>  OK 
ERROR 
Defined values  
<mode>  
0  –  mute off 
1  –  mute on  
Examples 
AT+VMUTE=1  
OK 
AT+VMUTE?  
+VMUTE:1  
OK 
SIMCom Confidential File
---

## Page 135

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 134 6.20  AT+CMUT  Microphone mute control  
Description  
This command is used to enable and disable the up link voice muting during a voice call or a video 
call which is connected. If there is not a connected call, write command can’t be used.  
When all calls are disconnected, the Module sets the subparameter as 0 automatically.  
SIM PIN  References  
NO 3GPP TS 2 7.007 
Syntax 
Test Command  Responses 
AT+CMUT=?  +CMUT: ( list of supported <mode> s) 
OK 
Read Command  Responses  
AT+CMUT?  +CMUT: <mode>  
OK 
Write Command  Responses 
AT+CMUT= <mode>  OK 
ERROR  
Defined values  
<mode> 
0  –  mute off 
1  –  mute on  
Examples 
AT+C MUT=1  
OK 
AT+CMUT?  
+CMUT: 1  
OK 
6.21  AT+MORING  Enable or disable report MO ring URC  
Description  
This command is used to enable or disable report MO ring URC 
SIM PIN  References  
SIMCom Confidential File
---

## Page 136

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 135 NO Vendor  
Syntax 
Test Command  Responses 
AT+MORING=?  +MORING: (0 -1) 
OK 
Read Command  Responses 
AT+MORING?  +MORING : <mode>  
OK 
Write Command  Responses  
AT+MORING= <mode>  OK 
ERROR 
Defined values  
<mode> 
Enable or disable report MO ring URC: 
    0  –  disable  
1  –  enable.  
Examples 
AT+MORING=1  
OK 
AT+MORING?  
+MORING:1  
OK 
AT+MO RING=?  
+MORING: (0 -1) 
OK 
 
6.22  AT+CSDVC   Switch voice channel device  
Description  
This command is used to switch voice channel device. After changing current voice channel device 
and if there is a connecting voice call, it will use the settings of previous d evice (loudspeaker 
volume level, mute state of loudspeaker and microphone, refer to AT+CLVL , AT+VMUTE , and 
AT+CMUT ). 
SIM PIN  References  
SIMCom Confidential File
---

## Page 137

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 136 NO Vendor  
Syntax 
Test Command  Responses 
AT+CSDVC=?  +CSDVC: ( list of supported <dev> s) 
OK 
Read Command  Responses 
AT+CSDVC?  +CSDVC: <dev>  
OK 
Write Command  Responses 
AT+CSDVC= <dev>  OK 
Defined values  
<dev>  
0  –  close voice channel device. only used after AT+CODECCTL=1  
1  –  handset 
 3  –  speaker phone  
Examples 
AT+CSDVC=1  
OK 
AT+CSDVC? 
+CSDVC:1  
OK 
 
6.23  AT+CLVL   Loud speaker volume level  
Description  
Write command is used to select the volume of the internal loudspeaker audio output of the device. 
Test command returns supported values as compound value. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Respon ses 
AT+CLVL=?  +CLVL: (list of supported <level> s) 
OK 
SIMCom Confidential File
---

## Page 138

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 137 Read Command  Responses  
AT+CLVL?  +CLVL: <level>  
OK 
Write Command  Responses  
AT+CLVL= <level>  OK 
ERROR  
Defined values  
<level>  
Integer type value which represents loudspeaker volume level. The range is from 0 to 5, and 0 
represents the lo west loudspeaker volume level, 4 is default factory value. 
NOTE:  <level>  is nonvolatile, and it is stored when restart.  
Examples 
AT+CLVL?  
+CLVL: 4 
OK 
AT+CLVL=3  
OK 
 
6.24  AT+SIDET  Set sidetone  
Description  
This command is used to enable or disable sidetone. Please refer to related hardware design 
document for more information. This command is only used after call start.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+SIDET=?  +SIDET: (list of supported < en>s) 
OK 
Read Command  Responses 
AT+SIDET?  +SIDET: <en>  
OK 
Write Command  Responses 
AT+SIDET= <en> OK 
SIMCom Confidential File
---

## Page 139

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 138 ERROR  
Defined values  
<en>  
0: disable sidetone 
1: enable sidetone 
Examples 
AT+SIDET?  
+SIDET: 0  
OK 
AT+SIDET=?  
+SIDET: (0 -1) 
OK 
AT+SIDET=1  
OK 
 
6.25  AT+CACDBFN  Change default ACDB filename  
Description  
This command is used to change default acdb filename. But there are six  adcd files used by system, 
we can’t change default acdb filename to them. These filenames including Bluetooth_cal.acdb, 
General_cal.acdb,  Global_cal.acdb, Hdmi_cal.acdb, Headset_cal.acdb,  Speaker_cal.acdb  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CACDBFN=?  +CACDBFN: (acdb file(s) listed in /data <acdb file> s,except s
ix acdb file used by  system ) 
OK 
Read Command  Responses 
AT+CACDBFN?  +CACDBFN: <acdb file>  
OK 
Write Command  Responses  
AT+CACDBFN= <acdb file>  OK 
ERROR  
SIMCom Confidential File
---

## Page 140

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 139 Defined values  
<acdb file > 
<acdb file > file(s) in the directory /data with suffix: acdb , except six acdb file used by system  
Examples 
AT+CACDBFN =Handset_cal.acdb 
OK 
AT+CACDBFN ? 
+CACDBFN : Handset_cal.acdb  
OK 
AT+CACDBFN =? 
+CACDBFN : (Handset_cal.acdb,Handset_tianmai.acdb) 
OK 
 
6.26  AT+CPCMREG   USB audio control  
Description  
This command is used to start/stop usb audio function. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CPCMREG=?  +CPCMREG: (list of supported < mode > s) 
OK 
Read Command  Responses 
AT+CPCMREG ? +CPCMREG: <mode>  
OK 
Write Command  Responses 
AT+CPCMREG= <mode>[,<
stop>]  OK 
ERROR 
Defined values  
<mode> 
0  –  stop usb audio function,need used after call stop. 
1  –  start usb audio function,need used after call start(ATDxxx;) 
<stop> 
SIMCom Confidential File
---

## Page 141

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 140 1  –  stop usb audio function, need used after call stop. only used when mode=0; 
Examples 
AT+CPCMREG=1               //start usb audio fu nction  
OK 
AT+CPCMREG=0,1             //stop usb audio function 
OK 
AT+CPCMREG?  
+CPCMREG:1  
OK 
 
6.27  AT+CMICGAIN  Adjust mic gain  
Description  
This command is used to adjust mic gain. If this command was used during call, it will take 
immediate effect. Otherwise, it will take effect in next call.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CMICGAIN=?  +CMICGAIN: (list of supported <value> s) 
OK 
Read Command  Responses  
AT+CMICGAIN ? +CMICGAIN: <value>  
OK 
Write Command  Responses 
AT+CMICGAI N=<value>  OK 
ERROR  
Defined values  
<value>  
Gain value from 0 -8, 8 is the max. 3 is the default value. This value will be reset to default value 
after Module reset.  
Examples 
AT+CMICGAIN=1  
SIMCom Confidential File
---

## Page 142

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 141 OK 
AT+CMICGAIN?  
+CMICGAIN:1  
OK 
 
6.28  AT+COUTGAIN   Adjust out gain  
Description  
This command is used to adjust out(speaker/handset) gain. If this command was used during call, it 
will take immediate effect . Otherwise, it will take effect in next call.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+COUT GAIN=?  +COUTGAIN: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+COUTGAIN? +COUTGAIN: <value>  
OK 
Write Command  Responses  
AT+COUTGAIN= <value>  OK 
ERROR 
Defined values  
<mode>  
Gain value from 0 -8, 8 is the max. 8 is the default value. This value will be reset to default value 
after Module reset.  
Examples 
AT+COUTGAIN=1  
OK 
AT+COUTGAIN?  
+COUTGAIN:1  
OK 
 
SIMCom Confidential File
---

## Page 143

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 142 6.29  AT+CTXVOL   Adjust TX voice mic volume  
Description  
This command is used to adjust mic gain. It modify the TX_VOICE_VOL in DSP . This command 
only be used during call  and do n’t save the parameter after call.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+C TXVOL =? +CTXVOL : (list of supported <value> s) 
OK 
Read Command  Responses 
AT+CTXVOL ? +CTXVOL : <value>  
OK 
Write Command  Responses 
AT+ CTXVOL =<value>  OK 
ERROR 
Defined values  
<value>  
Gain value from 0x0000-0xffff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CTXVOL =0x1234 
OK 
AT+CTXVOL ? 
+CTXVOL : 0x2d33  
OK 
 
6.30  AT+C TXMICGAIN  Adjust TX v oice mic  gain 
Description  
This command is used to adjust mic gain. It m odify the TX_VOICE_MIC_GAIN in DSP . This 
command only be used during call and don’t save the parameter after call.  
SIM PIN  References  
SIMCom Confidential File
---

## Page 144

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 143 NO Vendor 
Syntax 
Test Command  Responses 
AT+CTXM ICGAIN =? +CTXMICGAIN : (list of supported <mode>,<value> s) 
OK 
Read Command  Responses  
AT+CTXMICGAIN ? +CTXMICGAIN : <mode>, <value>  
OK 
Write Command  Responses  
AT+ CTXMICGAIN =<mode
>,<value>  OK 
ERROR  
Defined values  
<mode> 
mode value from 0 -1, default value  is not a fixed value. It varies with different versions. 
<value>  
gain value from 0x0000-0xffff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+C TXMICGAIN =1,0x1234  
OK 
AT+CTXMICGAIN ? 
+CTXMICGAIN : 1,0x2000 
OK 
 
6.31  AT+C RXVOL  Adjust RX voice output speaker volume  
Description  
This command is used to adjust digital Volume of output signal after speech decoder, before 
summation of sidetone and DAC. It modify the RX_VOICE_SPK_GAIN in DSP. This command 
only be used during cal l and don’t save the parameter after call.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
SIMCom Confidential File
---

## Page 145

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 144 AT+CRXVOL=?  +CRXVOL: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+C RXVOL ? +CRXVOL: <value>  
OK 
Write Command  Responses 
AT+CRXVOL= <valu e> OK 
ERROR  
Defined values  
<value>  
Gain value from 0x0000-0xffff, default value is not a fixed value. It varies with different versions. 
 
Examples 
AT+CRXVOL=0x1234 
OK 
AT+CRXVOL?  
+CRXVOL: 0x3fd9 
OK 
 
6.32  AT+CECH  Inhibit far -end echo  
Description  
This c ommand is used to adjust additional muting gain applied in DES during far -end only. It 
modify the DENS_gamma_e_high of TX_VOICE_SMECNS in DSP. The bigger the value, the 
stronger the inhibition .This command only be used during call and don’t save the param eter after 
call. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CECH=?  +CECH: (list of supported <value> s) 
OK 
Read Command  Responses 
SIMCom Confidential File
---

## Page 146

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 145 AT+C ECH ? +CECH: <value>  
OK 
Write Command  Responses 
AT+CECH= <value>  OK 
ERROR 
Defined values  
<value > 
Gain value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CECH=0x1234 
OK 
AT+CECH?  
+CECH: 0x0200  
OK 
 
6.33  AT+CECDT  Inhibit echo during doubletalk  
Description  
This command is used to adjust additio nal muting gain applied in DES during doubletalk. It modify 
the DENS_gamma_e_dt of TX_VOICE_SMECNS in DSP. The bigger the value, the stronger the 
inhibition .This command only be used during call and don’t save the parameter after call. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CECDT=?  +CECDT: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+C ECDT? +CECDT: <value>  
OK 
Write Command  Responses  
AT+CECDT= <value>  OK 
ERROR 
SIMCom Confidential File
---

## Page 147

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 146 Defined values  
<value>  
Gain value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CECDT=0x1234 
OK 
AT+CECDT?  
+CECDT: 0x0100  
OK 
 
6.34  AT+CECWB  Inhibit echo in the high band  
Description  
This command is used to adjust the aggressiveness of EC in the high band (4 ~ 8 kHz). A higher 
value is more aggressive and suppresses more high- band echo. Q -format - Q4.11WB_gamma_E = 
2048 * gammaWhere gamma is in the range [0,15]. It modify the WB_gamma_e of 
TX_VOICE_SMECNS in DSP. The bigger the value, the stronger the  inhibition .This command 
only be used during call and don’t save the parameter after call.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CECWB=?  +CECWB: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+C ECWB ? +CECWB: <value>  
OK 
Write Command  Responses  
AT+CECWB= <value>  OK 
ERROR 
Defined values  
<value>  
Gain value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions. 
SIMCom Confidential File
---

## Page 148

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 147 Examples 
AT+CECWB=0x1234  
OK 
AT+CECWB?  
+CECWB: 0x0300 
OK 
 
6.35  AT+CNSN  MIC NOISE suppression  
Description  
This command is used to adjust oversubtraction factor and bias compensation for noise estimation. 
It modify the DENS_gamma_n of TX_VOICE_SMECNS in DSP. The bigger the value, the 
stronger the noise suppression .This comma nd only be used during call and don’t save the 
parameter after call.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CNSN=?  +CNSN: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+C NSN ? +CNSN: <value>  
OK 
Write Command  Responses 
AT+CNSN= <value>  OK 
ERROR 
Defined values  
<value>  
Gain value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CNSN=0x1234  
OK 
AT+CNSN?  
+CNSN: 0x0258 
SIMCom Confidential File
---

## Page 149

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 148 OK 
 
6.36  AT+CNSLIM  MIC NOISE suppression  
Description  
This command is used to controls the maximum amount of noise suppression. It modify the 
DENS_limit_NS of TX_VOICE_SMECNS in DSP. The bigger the value, the stronger the noise 
suppression .This command only be used during call and don’t save the param eter after call.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CNSLIM=?  +CNSLIM: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+C NSLIM ? +CNSLIM: <value>  
OK 
Write Command  Responses 
AT+CNSLIM= <value>  OK 
ERROR 
Defined values  
<value>  
Gain value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CNSLIM=0x1234 
OK 
AT+CNSLIM?  
+CNSLIM: 0x16c4  
OK 
6.37  AT+CFNSMOD  Adjust parameter fnsMode of RX_VOICE_FNS  
Description  
This comman d is used to modify the fnsMode of RX_VOICE_FNS in DSP. This command only be 
SIMCom Confidential File
---

## Page 150

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 149 used during call and don’t save the parameter after call.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CFNSMOD=?  +CFNSMOD: (list of supported <value> s) 
OK 
Read Command Responses 
AT+C FNSMOD ? +CFNSMOD: <value>  
OK 
Write Command  Responses  
AT+CFNSMOD= <value>  OK 
ERROR 
Defined values  
<value>  
Gain value is bellow, default value is not a fixed value. It varies with different versions. 
0x00FF – Maximum NS  
0x0073 – Basic stationary NS  
0x00F3 – Enhanced stationary NS 
0x01FF – Aggressive NS  
Examples 
AT+CFNSMOD=0x0073 
OK 
AT+CFNSMOD?  
+CFNSMOD: 0x0073  
OK 
6.38  AT+CFNSIN  Adjust parameter fnsInputGain of RX_VOICE_FNS  
Description  
This command is used to modify the fnsInp utGain of RX_VOICE_FNS in DSP. This command 
only be used during call and don’t save the parameter after call. 
SIM PIN  References  
NO Vendor 
SIMCom Confidential File
---

## Page 151

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 150 Syntax 
Test Command  Responses 
AT+CFNSIN=?  +CFNSIN: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+C FNSIN ? +CFNSIN: <value>  
OK 
Write Command  Responses 
AT+CFNSIN= <value>  OK 
ERROR 
Defined values  
<value>  
Gain value from 0x2000-0x7fff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CFNSIN=0x2234 
OK 
AT+CFNSIN?  
+CFN SIN: 0x2000 
OK 
6.39  AT+CFNSLVL  Adjust parameter fnsTargetNS of RX_VOICE_FNS  
Description  
This command is used to modify the fnsTargetNS of RX_VOICE_FNS in DSP. This command only 
be used during call and don’t save the parameter after call.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CFNSLVL=?  +CFNSLVL: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+C FNSLVL ? +CFNSLVL: <value>  
OK 
Write Command  Responses  
SIMCom Confidential File
---

## Page 152

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 151 AT+CFNSLVL=<value>  OK 
ERROR 
Defined values  
<value>  
Gain value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CFNSLVL=0x2234  
OK 
AT+CFNSLVL?  
+CFNSLVL: 0x1000  
OK 
6.40  AT+CECRX  Enable or disable VOICE_MOD_ENABLE  
Description  
This command is used to enable or disable VOICE _MOD_ENABLE. It modify the 
VOICE_MOD_ENABLE in DSP. This command only be used during call and don’t save the 
parameter after call.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CECRX=?  +CECRX: (list of supported <value> s) 
OK 
Read Comma nd Responses 
AT+CECRX ? +CECRX: <value>  
OK 
Write Command  Responses  
AT+CECRX= <value>  OK 
ERROR 
Defined values  
<value>  
This default value is not a fixed value. It varies with different versions. 
1: Enable  
SIMCom Confidential File
---

## Page 153

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 152 0: Disable  
Examples 
AT+CECRX =1 
OK 
AT+CECRX?  
+CECRX: 1  
OK 
 
6.41  AT+CNLPPG  Modify the NLPP_gain in DSP 
Description  
This command is used to modify the NLPP_gain of VOICE_ECRX_PARAM in DSP. This 
command only be used during call and don’t save the parameter after call.  
SIM PIN  References  
NO Vendor 
Synt ax 
Test Command  Responses 
AT+CNLPPG=?  +CNLPPG: (list of supported <value> s) 
OK 
Read Command  Responses  
AT+CNLPPG ? +CNLPPG: <value>  
OK 
Write Command  Responses 
AT+CNLPPG = <value>  OK 
ERROR  
Defined values  
<value>  
Gain value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions.  
Examples 
AT+CNLPPG=0x1234 
OK 
AT+CNLPPG?  
+CNLPPG: 0x1000  
SIMCom Confidential File
---

## Page 154

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 153 OK 
 
6.42  AT+CNLPPL  Modify the NLPP_limit in DSP  
Description  
This command is used to modify the NLPP_limit of VOICE_ECRX_PARAM in DSP. This 
command only be used during call and don’t save the parameter after call.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CNLPPL=?  +CNLPPL: (list of supported <value> s) 
OK 
Read Command  Responses  
AT+CNLPPL ? +CNLPPL: <value>  
OK 
Write Command  Responses 
AT+CNLPPL = <value>  OK 
ERROR  
Defined values  
<value>  
Value from 0x0000-0x7fff, default value is not a fixed value. It varies with different versions. 
Examples 
AT+CNLPPL=0x1234 
OK 
AT+CNLPPL?  
+CNLPPL: 0x7fff  
OK 
6.43  AT+CECM  Adjust echo canceller  
Description  
This AT command is used to select the echo cancellation mode. Write command only be used 
during call. 
SIMCom Confidential File
---

## Page 155

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 154 SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CECM=?  +CECM: (list of supported <value> s) 
OK 
Read Command  Responses 
AT+CECM ? +CECM: <value>  
OK 
Write Command  Responses  
AT+CECM= <value>  OK 
ERROR 
Defined values  
<value>  
This default value is not a fixed value. It varies with different versions. 
0: disable EC mode 
1: EC mode recommended for Speaker phone aggressive  
2: EC mode recommended for Speaker phone medium 
3: EC mode recommended for Speaker least aggressive 
4: EC mode recommended for Bluetooth 
5: EC mode recommended for Bluetooth (less aggressive) 
6: EC mode recommended for Bluetooth (least aggressive) 
7: EC mode recommended for HANDSFREE 
8: EC mode recommended for Headset  
9: EC mode recommended for Handset  
Examples 
AT+CECM =1 
OK 
AT+CECM?  
+CECM: 1  
OK 
6.44  AT+CPCMFRM  Set usb audio sample rate to 16k bit  
Description  
SIMCom Confidential File
---

## Page 156

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 155 This command is used to set usb audio sample rate to 16K bit.  
NOTE: This command only support for usb audio 8k to 16k switching, but not support for 16k to 
8k switching. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CPCMFRM=?  +CPCMFRM: (list of supported <value> s) 
OK 
Read Comm and Responses 
AT+CPCMFRM ? +CPCMFRM: <value>  
OK 
Write Command  Responses 
AT+CPCMFRM= <value>  OK 
ERROR 
Defined values  
<value>  
Gain value from 0 -1, default value is 0.  
0 : usb audio use 8k bit 
1 : usb audio use 16k bit 
Examples 
AT+CPCMFRM=1  
OK 
AT+CPC MFRM?  
+CPCMFRM: 1  
OK 
6.45  AT+CPTONE  Play tone  
Description  
This AT command is used to local play a tone.  
SIM PIN  References  
NO Vendor  
Syntax 
SIMCom Confidential File
---

## Page 157

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 156 Read Command  Responses  
AT+CPTONE=?  +CPTONE: (list of supported <tone> s) 
OK 
Write Command  Responses 
AT+CPTONE=<t one> OK 
AT+CPTONE=<tone>,<time>,<gain
> OK 
Defined values  
<tone>  
Support 0- 16. 
< time > 
Duration, the default value is 50ms.  Support 1- 1000.  
<gain>  
The default value is  4000.  Support 1 -9999.  
Examples 
AT+CPTONE=1  
OK 
AT+CPTONE=1,200,1000 
OK 
 
6.46  AT+CO DECCTL  Control codec by Host device or Module  
Description  
This command is used to select Host device or Module to control codec. This command doesn’t 
save the parameter after reboot.  
IM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CODECCT L=? +CCODECCTL: (list of supported <mode> s) 
OK 
Read Command  Responses 
AT+CODECCTL ? +CCODECCTL: <mode>  
OK 
SIMCom Confidential File
---

## Page 158

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 157 Write Command  Responses  
AT+CODECCTL =<mode>  OK 
ERROR 
Defined values  
<mode> 
mode value from 0 -1, default value is 0.  
0 : Module control codec when play sound. 
1 : Host device control codec. Host device can open codec by AT+CSDVC=1 or AT+CSDVC=3, 
close codec by AT+CSDVC=0.  
Examples 
AT+CODECCTL=1  
OK 
AT+CODECCTL?  
+CCODECCTL: 0  
OK 
6.47  AT+CPCMBANDWIDTH   Modify the sampling rate of the PCM  
Description  
This command is used to modify the sampling rate of the PCM to 8k or 16k. This command don’t 
save the parameter after reboot.  
IM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CPCMBANDWIDTH=?  +CPCMBANDWIDTH: (list of supported <volte_sample >s), (list 
of supported <novolte_sample> s) 
OK 
Read Command  Responses 
AT+CPCMBANDWIDTH ? +CPCMBANDWIDTH: <volte_sample>,<novolte_sample>  
OK 
Write Command  Responses 
AT+CPCMBANDWIDTH=
<volte_sample>,<novolte_sa
mple>  OK 
ERROR 
SIMCom Confidential File
---

## Page 159

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 158 Defined values  
<volte_sample>  
Value from 0 -1, default value is 0.  
0 : Sampling rate is 16K.  
1 : Sampling rate is 8K.  
< novolte_sample > 
Value from 0 -1, default value is 1.  
0 : Sampling rate is 16K. 
1 : Sampling rate is 8K.  
Examples 
AT+CPCMBANDWIDTH=1,0  
OK 
AT+CPCMBANDWIDTH?  
+CPCMBANDWIDTH: 1,0 
OK 
 
SIMCom Confidential File
---

## Page 160

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 159  
7 AT Commands for SMS  
7.1  AT+CSMS  Select message service  
Description  
This command is used to select messaging service <service> . 
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CSMS=?  +CSMS: (list of supported <service> s) 
OK 
Read Command  Responses 
AT+CSMS?  +CSMS: <service> ,<mt> ,<mo> ,<bm>  
OK 
Write Command  Responses 
AT+CSMS= <service>  +CSMS: <mt> ,<mo> ,<bm>  
OK 
ERROR 
+CMS ERROR: <err>  
Defined values  
<service > 
0  –  SMS at command is compatible with GSM phase 2.  
1  –  SMS at command is compatible with GSM phase 2+. 
<mt>  
Mobile terminated messages:  
0  –  type not supported. 
1  –  type supported. 
<mo>  
Mobile originated messages: 
0  –  type not supported. 
1  –  type supported. 
SIMCom Confidential File
---

## Page 161

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 160 <bm>  
Broadcast type messages:  
0  –  type not supported. 
1  –  type supported. 
Examples 
AT+CSMS=0  
+CSMS:1,1,1 
OK 
AT+CSMS?  
+CSMS:0,1,1,1 
OK 
AT+CSMS=?  
+CSMS:(0 -1) 
OK 
7.2  AT+CPMS  Preferred message storage  
Description  
This command is  used to select memory storages <mem1> , <mem2>  and <mem3>  to be used for 
reading, writing, etc. 
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CPMS=?  +CPMS: (list of supported <mem1> s), (list of supported 
<mem2> s), (list of supp orted <mem3> s) 
OK 
Read Command  Responses  
AT+CPMS?  +CPMS: <mem1> ,<used1> ,<total1 >,<mem2> ,<used2> ,<total2> , 
<mem3> ,<used3> ,<total3>  
OK 
ERROR 
+CMS ERROR: <err>  
Write Command  Responses  
AT+CPMS= <mem1>  
[,<mem2> [,<mem3> ]] +CPMS: <used1> ,<total1> ,<used2> ,<total2> ,<used3> ,<total3>  
OK 
SIMCom Confidential File
---

## Page 162

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 161 ERROR  
+CMS ERROR:  <err>  
Execution Command Responses 
AT+CPMS  Set default value ( <mem1> =”SM”, <mem2> =”SM”, 
<mem3> =”SM”):  
+CPMS: <used1> ,<total1> ,<used2> ,<total2> ,<used3> ,<total3>  
OK 
ERROR  
Defined values  
<mem1>  
String type , memory from which messages are read and deleted (commands List Messages 
AT+CMGL , Read Message AT+CMGR  and Delete Message AT+CMGD ). 
“ME” and “MT”   FLASH message storage  
“SM”            SIM message storage  
“SR”          Status report storage ( not used in CD MA/EVDO mode ) 
<mem2>  
String type, memory to which writing and sending operations are made (commands Send Message 
from Storage AT+CMSS  and Write Message to Memory  AT+CMGW ). 
“ME” and “MT”   FLASH message storage  
“SM”           SIM message storage  
<mem3>  
String type, memory to which received SMS is preferred to be stored (unless forwarded directly to 
TE; refer command New Message Indications AT+CNMI ). 
“ME”           FLASH message storage  
“SM”           SIM message storage  
<usedX>  
Integer type, number of mess ages currently in <memX> . 
<totalX>  
Integer type, total number of message locations in <memX> . 
Examples 
AT+CPMS=?  
+CPMS: ("ME", "MT","SM","SR"),("ME","MT","SM" ),("ME","SM")  
OK 
AT+CPMS?  
+CPMS:"ME", 0, 23,"ME", 0, 23,"ME", 0, 23 
OK 
AT+CPMS="SM","SM","SM " 
+CPMS:3,50,3,50,3,50 
OK 
SIMCom Confidential File
---

## Page 163

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 162 7.3  AT+CMGF  Select SMS message format  
Description  
This command is used to specify the input and output format of the short messages. 
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CMGF=?  +CMGF: (list of  supported <mode> s) 
OK 
ERROR 
Read Command  Responses 
AT+CMGF?  +CMGF: <mode>  
OK 
ERROR 
Write Command  Responses 
AT+CMGF=<mode>  OK 
ERROR  
Execution Command Responses 
AT+CMGF  Set default value ( <mode> =0): 
OK 
ERROR 
Defined values  
<mode> 
0  –  PDU m ode 
1  –  Text mode 
Examples 
AT+CMGF?  
+CMGF: 0  
OK 
AT+CMGF=?  
+CMGF: (0 -1) 
OK 
AT+CMGF=1  
SIMCom Confidential File
---

## Page 164

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 163 OK 
7.4  AT+CSCA  SMS service centre address  
Description  
This command is used to update the SMSC address, through which mobile originated SMS are 
transmitted.  
Note: Thi s command not support in CDMA/EVDO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CSCA=?  OK 
Read Command  Responses 
AT+CSCA?  +CSCA:  <sca> ,<tosca>  
OK 
Write Command  Responses  
AT+CSCA= <sca> [,<tosca> ] OK 
Defined values  
<sca> 
Service Cent re Address , value field in string format, BCD numbers (or GSM 7 bit default alphabet 
characters) are converted to characters of the currently selected TE character set  (refer to command 
AT+CSCS ), type of address given by <tosca> . 
<tosca>  
SC address Type -of-Address octet in integer format, when first character of <sca>  is + (IRA 43) 
default is 145, otherwise default is 129. 
Examples 
AT+CSCA="+8613012345678"  
OK 
AT+CSCA?  
+CSCA: "+8613010314500", 145  
OK 
SIMCom Confidential File
---

## Page 165

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 164 7.5  AT+CSCB  Select cell broadcast mess age indication  
Description  
The test command returns the supported <mode> s as a compound value. 
The read command displays the accepted message types.  
Depending on the <mode>  parameter, the write command adds or deletes the message types 
accepted.  
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CSCB=?  +CSCB: (list of supported <mode> s) 
OK 
ERROR  
Read Command  Responses  
AT+CSCB?  +CSCB:  <mode> ,<mids> ,<dcss>  
OK 
ERROR 
Write Command  Responses 
AT+CSCB= <mode> [,<mids
>[,<dcss>]] OK 
ERROR 
+CMS ERROR: <err>  
Defined values  
<mode> 
0  –  message types specified in <mids>  and <dcss>  are accepted.  
1  –  message types specified in <mids>  and <dcss>  are not accepted.  
<mids>  
String type; all different possible combinations of CBM message identifiers. 
<dcss>  
String type; all different possible combinations of CBM data coding schemes(default is empty 
string)  
Examples 
AT+CSCB=?  
+CSCB: (0 -1) 
SIMCom Confidential File
---

## Page 166

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 165 OK 
AT+CSCB=0,”15 -17,50,86”,””  
OK 
7.6  AT+CSMP  Set text mode parameters 
Description  
This command is used to select values for additional parameters needed when SM is sent to the 
network or placed in storage when text format message mode is selected. 
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses  
AT+CSMP=?  OK 
Read Command  Responses 
AT+CSMP?  +CSMP: <fo> ,<vp> ,<pid> ,<dcs> 
OK 
Write Command  Responses  
AT+CSMP= [<fo> [,<vp> [,<p
id>[,<dcs> ]]]] OK 
ERROR 
Defined values  
<fo>  
Depending on the  Command or result code: first octet of GSM 03.40 SMS- DELIVER, 
SMS -SUBMIT (default 17), SMS -STATUS -REPORT, or SMS -COMMAND (default 2) in integer 
format. SMS status report is supported under text mode if <fo>  is set to 49.  
<vp>  
Depending on SMS -SUBMIT <fo> setting: GSM 03.40,TP -Validity -Period either in integer format 
(default 167), in time -string format, or if is supported, in enhanced format (hexadecimal coded 
string with quotes),  (<vp>  is in range 0... 255).  
<pid> 
GSM 03.40 TP -Protocol- Identifier in integer format (default 0). 
<dcs>  
GSM 03.38 SMS Data Coding Scheme (default 0), or Cell Broadcast Data Coding Scheme in 
integer format depending on the command or result code.  
Examples 
SIMCom Confidential File
---

## Page 167

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 166 AT+CSMP=17,23,64,244 
OK 
7.7  AT+CSDH  Show text mode parameters 
Descrip tion 
This command is used to control whether detailed header information is shown in text mode result 
codes.  
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CSDH=?  +CSDH: (list of supported <show> s) 
OK 
ERROR 
Read Command  Responses 
AT+CSDH?  +CSDH:  <show>  
OK 
Write Command  Responses  
AT+CSDH= <show>  OK 
ERROR 
Execution Command Responses 
AT+CSDH  Set default value ( <show> =0): 
OK 
ERROR 
Defined values  
<show> 
0  –  do not show he ader values defined in commands AT+CSCA  and AT+CSMP  (<sca> , 
<tosca> , <fo> , <vp> , <pid>  and <dcs> ) nor  <length> , <toda>  or <tooa>  in +CMT , 
AT+CMGL , AT+CMGR  result codes for SMS -DELIVERs and SMS -SUBMITs in text 
mode; for SMS -COMMANDs in AT+CMGR  result code, do not show <pid> , <mn> , 
<da> , <toda> , <length>  or <data>  
1  –  show the values in result codes 
Examples 
SIMCom Confidential File
---

## Page 168

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 167 AT+CSDH?  
+CSDH: 0  
OK 
AT+CSDH=1  
OK 
7.8  AT+CNMA  New message acknowledgement to ME/TA  
Description  
This command is used to confirm successful receipt of  a new message (SMS -DELIVER or 
SMS -STATUSREPORT) routed directly to the TE. If ME does not receive acknowledgement within 
required time (network timeout), it will send RP -ERROR to the network. 
NOTE:  The execute / write command shall only be used when AT+CS MS parameter  <service>  
equals 1 (= phase 2+) and appropriate URC has been issued by the module, i.e.: 
  <+CMT> for <mt> =2 incoming message classes 0, 1, 3 and none; 
  <+CMT> for <mt> =3 incoming message classes 0 and 3; 
  <+CDS> for <ds> =1. 
Note: This comma nd not support in CDMA/EVDO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CNMA=?  if text mode( AT+CMGF =1): 
OK 
if PDU mode ( AT+CMGF =0): 
+CNMA: (list of supported <n>s) 
OK 
Write Command  Responses 
AT+CNMA=<n>  OK 
ERROR 
+CMS ERROR: <err>  
Execution Command Responses 
AT+CNMA  OK 
ERROR  
+CMS ERROR: <err>  
Defined values  
<n> 
SIMCom Confidential File
---

## Page 169

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 168 Parameter required only for PDU mode. 
   0  –   Command operates similarly as execution command in text mode. 
   1  –   Send positive (RP -ACK) acknowl edgement to the network. Accepted only in PDU 
mode. 
 2  –   Send negative (RP- ERROR) acknowledgement to the network. Accepted only in PDU 
mode. 
Examples 
AT+CNMI=1,2,0,0,0  
OK 
+CMT:”1380022xxxx”,””,”02/04/03,11 :06 :38+32”<CR><LF> 
Testing  
(receive new sh ort message) 
AT+CNMA (send ACK to the network)  
OK 
AT+CNMA  
+CMS ERROR ：340 
(the second time return error, it needs ACK only once)  
7.9  AT+CNMI  New message indications to TE  
Description  
This command is used to select the procedure how receiving of new messages from the network is 
indicated to the TE when TE is active, e.g. DTR signal is ON. If TE is inactive (e.g. DTR signal is 
OFF). If set <mt> ＝3 or <ds> ＝1, make sure <mode> ＝1, If set <mt> =2,make sure <mode> =1 or 
2, otherwise it will return error.  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CNMI=?  +CNMI: (list of supported <mode> s),(list of supported <mt> s),(list 
of supported <bm> s),(list of supported <ds> s),(list of supported 
<bfr> s) 
OK 
Read Command  Responses 
AT+CNMI?  +CNMI: <mode> ,<mt> ,<bm> ,<ds> ,<bfr>  
OK 
Write Command  Responses 
SIMCom Confidential File
---

## Page 170

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 169 AT+CNMI= <mode> [,<mt> [,
<bm> [,<ds>  [,<bfr> ]]]] OK 
ERROR 
+CMS ERROR: <err>  
Execution Command Responses 
AT+ CNMI  Set default value: 
OK 
Defined values  
<mode>  
0   –   Buffer unsolicited result codes in the TA. If TA result code buffer is full, indications 
can be buffered in some other place or the oldest indications may be discarded and 
replaced with the new received indications.  
1   –   Discard indication and reject new received message unsolicited result codes when 
TA-TE link is reserved (e.g. in on- line data mode). Otherwise forward them directly 
to the TE.  
2   –   Buffer unsolicited result codes in the TA when TA-TE link is reserved (e.g. in on- line 
data mode) and flush them to the TE after reserva tion. Otherwise forward them 
directly to the TE.  
<mt>  
The rules for storing received SMS depend on its data coding scheme, preferred memory storage 
(AT+CPMS ) setting and this value:  
0   –   No SMS -DELIVER indications are routed to the TE.  
1   –   If SMS -DELIVER is stored into ME/TA, indication of the memory location is routed 
to the TE using unsolicited result code: +CMTI: <mem3> ,<index> . 
2   –   SMS -DELIVERs (except class 2 messages and messages in the message waiting 
indication group (store message)) ar e routed directly to the TE using unsolicited 
result code:  
+CMT:[ <alpha> ],<length> <CR><LF> <pdu>  (PDU mode enabled); or 
+CMT: <oa> ,[<alpha> ],<scts> [,<tooa> ,<fo> ,<pid> ,<dcs> ,<sca> ,<tosca> ,<length> ] 
<CR> <LF><data>  
(text mode enabled, about parameters in itali cs, refer command Show Text Mode 
Parameters AT+CSDH ). 
3   –   Class 3 SMS -DELIVERs are routed directly to TE using unsolicited result codes 
defined in <mt> =2. Messages of other data coding schemes result in indication as 
defined in <mt> =1. 
<bm> （not used in CDMA/EVDO mode ） 
The rules for storing received CBMs depend on its data coding scheme, the setting of Select CBM 
Types ( AT+CSCB) and this value: 
0  –  No CBM indications are routed to the TE. 
2  –  New CBMs are routed directly to the TE using unsolicited result code: 
+CBM:  <length> <CR><LF> <pdu> (PDU mode enabled); or 
SIMCom Confidential File
---

## Page 171

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 170 +CBM:  <sn> ,<mid> ,<dcs>, <page> ,<pages> <CR><LF> <data>  (text mode enabled) 
<ds> （not used in CDMA/EVDO mode ） 
0  –  No SMS -STATUS -REPORTs are routed to the TE.  
1  –  SMS -STATUS -REPOR Ts are routed to the TE using unsolicited result code: 
+CDS:  <length> <CR><LF> <pdu>  (PDU mode enabled); or 
+CDS: <fo> ,<mr> ,[<ra> ],[<tora> ],<scts> ,<dt> ,<st> (text mode enabled) 
2  –  If SMS -STATUS -REPORT is stored into ME/TA, indication of the memory locatio n is 
routed to the TE using unsolicited result code: +CDSI: <mem3> ,<index> . 
<bfr>  
0  –  TA buffer of unsolicited result codes defined within this command is flushed to the TE 
when <mode>  1 to 2 is entered (OK response shall be given before flushing the codes).  
1  –  TA buffer of unsolicited result codes defined within this command is cleared when 
<mode>  1 to 2 is entered.  
Examples 
AT+CNMI?  
+CNMI: 0,0,0,0,0  
OK 
AT+CNMI=?  
+CNMI: (0,1,2),(0,1,2,3),(0,2),(0,1,2),(0,1) 
OK 
AT+CNMI=2,1 (unsolicited result co des after received messages.)  
OK 
7.10  AT+CGSMS  Select service for MO SMS messages  
Description  
The write command is used to specify the service or service preference that the MT will use to send 
MO SMS messages.  
The test command is used for requesting inform ation on which services and service preferences can 
be set by using the AT+CGSMS  write command  
The read command returns the currently selected service or service preference.  
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CGSMS=?  +CGSMS: (list of supported <service> s) 
OK 
SIMCom Confidential File
---

## Page 172

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 171 Read Command  Responses  
AT+CGSMS?  +CGSMS: <service>  
OK 
Write Command  Responses 
AT+CGSMS= <service>  OK 
ERROR  
+CME ERROR: <err>  
Defined values  
<service>  
A num eric parameter which indicates the service or service preference to be used  
0  –  GPRS(value is not really supported and is internally mapped to 2) 
1  –  circuit switched(value is not really supported and is internally mapped to 3) 
2  –  GPRS preferred (use circuit switched if GPRS not available)  
3  –  circuit switched preferred (use GPRS if circuit switched not available)  
Examples 
AT+CGSMS? 
+CGSMS: 3  
OK 
AT+CGSMS=? 
+CGSMS: (0 -3) 
OK 
7.11  AT+CMGL  List SMS messages from preferred store  
Description  
This comma nd is used to return messages with status value <stat>  from message storage <mem1>  
to the TE.  
If the status of the message is 'received unread', the status in the storage changes to 'received read'.  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Comm and Responses  
AT+CMGL=?  +CMGL: (list of supported <stat> s) 
OK 
Write Command  Responses 
SIMCom Confidential File
---

## Page 173

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 172 AT+CMGL= <stat>  If text mode ( AT+CMGF =1), command successful and SMS -S
UBMITs and/or SMS -DELIVERs:  
+CMGL: <index> ,<stat> ,<oa> /<da> ,[<alpha> ],[<scts> ][,<tooa> /<t
oda> ,<fo> ,<pid> ,<dcs> ,<sca> ,<tosca> ,<length> ]<CR><LF> <data
>[<CR><LF>  
+CMGL: <index> ,<stat> ,<oa> /<da> ,[<alpha> ],[<scts> ][,<tooa> /<t
oda> ,<fo> ,<pid> ,<dcs> ,<sca> ,<tosca> ,<length> ]<CR><LF> <data
>[...]] 
OK 
If text mode ( AT+CMGF =1), command successful and SMS-  
STATUS -REPORTs:  
+CMGL: <index> ,<stat> ,<fo> ,<mr> ,[<ra> ],[<tora> ],<scts> ,<dt> ,<s
t>[<CR><LF> 
+CMGL: <index> ,<stat> ,<fo> ,<mr> ,[<ra> ],[<tora> ],<scts> ,<dt> ,<s
t>[...]] 
OK 
If text mode ( AT+CMGF =1), command successful and SMS - 
COMMANDs: 
+CMGL: <index> ,<stat> ,<fo> ,<ct>[<CR><LF> 
+CMGL: <index> ,<stat> ,<fo> ,<ct>[...]] 
OK 
If text mode ( AT+CMGF =1), command successful and CBM 
storage: 
+CMGL: <index> ,<stat> ,<sn> ,<mid> ,<page> ,<pages>  
<CR><LF><data> [<CR><LF>  
+CMGL: <index> ,<stat> ,<sn> ,<mid> ,<page> ,<pages>  
<CR><LF><data> [...]] 
OK 
If PDU mode ( AT+CMGF =0) and Command successful: 
+CMGL: <index> ,<stat> ,[<alpha> ],<length> <CR><LF> <pdu> [<C
R><LF>  
+CMGL: <index> ,<stat> ,[<alpha> ],<length> <CR><LF> <pdu>  
[…]] 
OK 
+CMS ERROR: <err>  
Defined values  
<stat>  
1. Text Mode:  
"REC UNREAD"  received unread message (i.e. new message) 
SIMCom Confidential File
---

## Page 174

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 173 "REC READ"  received read message 
"STO UNSENT"  stored unsent message  
"STO SENT"   stored sent message  
"ALL"    all mes sages  
2. PDU Mode:  
0  –  received unread message (i.e. new message)  
1  –  received read message 
2  –  stored unsent message 
3  –  stored sent message  
4  –  all messages 
<index> 
Integer type; value in the range of location numbers supported by the associa ted memory and start 
with zero.  
<oa>  
Originating -Address, Address- Value field in string format; BCD numbers (or GSM 7 bit default 
alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by <tooa> . 
<da>  
Destination -Address, Address- Value field in string format; BCD numbers (or GSM 7 bit default 
alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by <toda> . 
<alpha> 
String type alphan umeric representation of <da>  or <oa>  corresponding to the entry found in MT 
phonebook; implementation of this feature is manufacturer specific; used character set should be 
the one selected with command Select TE Character Set AT+CSCS . 
<scts>  
TP-Service -Centre -Time -Stamp in time -string format (refer <dt> ). 
<tooa> 
TP-Originating -Address, Type -of-Address octet in integer format. (default refer <toda> ). 
<toda> 
TP-Destination -Address, Type-of- Address octet in integer format. (when first character of <da>  is + 
(IRA 43) default is 145, otherwise default is 129). The range of value is from 128 to 255.  
<length>  
Integer type value indicating in the text mode ( AT+CMG F =1) the length of the message body 
<data>  in characters; or in PDU mode ( AT+CMGF =0), the leng th of the actual TP data unit in 
octets. (i.e. the RP layer SMSC address octets are not counted in the length)  
<data>  
In the case of SMS: TP -User-Data in text mode responses; format:  
1. If <dcs>  indicates that GSM 7 bit default alphabet is used and <fo>  indicates that 
TP-User-Data -Header -Indication is not set: 
a. If TE character set other than "HEX": ME/TA converts GSM alphabet into current TE 
character set.  
b. If TE character set is "HEX": ME/TA converts each 7 -bit character of GSM 7 bit 
SIMCom Confidential File
---

## Page 175

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 174 default alphabet  into two IRA character long hexadecimal numbers. (e.g. character Π 
(GSM 7 bit default alphabet 23) is presented as 17 (IRA 49 and 55)) 
2. If <dcs>  indicates that 8 -bit or UCS2 data coding scheme is used, or <fo>  indicates that 
TP-User-Data -Header -Indication is set: ME/TA converts each 8- bit octet into two IRA 
character long hexadecimal numbers. (e.g. octet with integer value 42 is presented to TE as 
two characters 2A (IRA 50 and 65)) 
3. If <dcs>  indicates that GSM 7 bit default alphabet is used: 
a. If TE c haracter set other than "HEX": ME/TA converts GSM alphabet into current TE 
character set.  
b. If TE character set is "HEX": ME/TA converts each 7- bit character of the GSM 7 bit 
default alphabet into two IRA character long hexadecimal numbers. 
4. If <dcs>  indicates that 8 -bit or UCS2 data coding scheme is used: ME/TA converts each 
8-bit octet into two IRA character long hexadecimal numbers. 
<fo>  
Depending on the command or result code: first octet of GSM 03.40 SMS -DELIVER, 
SMS -SUBMIT (default 17), SMS -STATU S-REPORT, or SMS -COMMAND (default 2) in integer 
format. SMS status report is supported under text mode if <fo>  is set to 49.  
<mr>  
Message Reference  
GSM 03.40 TP -Message -Reference in integer format.  
<ra>  
Recipient Address  
GSM 03.40 TP -Recipient- Address Address- Value field in string format;BCD numbers (or GSM 
default alphabet characters) are converted to characters of the currently selected TE character 
set(refer to command AT+CSCS );type of address given by <tora>  
<tora>  
Type of Recipient Address  
GSM 04 .11 TP -Recipient -Address Type -of-Address octet in integer format (default refer <toda> ) 
<dt>  
Discharge Time 
GSM 03.40 TP -Discharge- Time in time -string format:”yy/MM/dd,hh:mm:ss+zz”,where characters 
indicate year (two last digits),month,day,hour,minutes,s econds and time zone.  
<st> 
Status  
GSM 03.40 TP -Status in integer format  
0…255 
<ct> 
Command Type  
GSM 03.40 TP -Command -Type in integer format 
0…255 
<sn>  
Serial Number  
GSM 03.41 CBM Serial Number in integer format 
SIMCom Confidential File
---

## Page 176

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 175 <mid>  
Message Identifier  
GSM 03.41 CB M Message Identifier in integer format  
<page> 
Page Parameter  
GSM 03.41 CBM Page Parameter bits 4-7 in integer format 
<pages>  
Page Parameter  
GSM 03.41 CBM Page Parameter bits 0-3 in integer format 
<pdu> 
In the case of SMS: SC address followed by TPDU in hexadecimal format: ME/TA converts each 
octet of TP data unit into two IRA character long hexadecimal numbers. (e.g. octet with integer 
value 42 is presented to TE as two characters 2A (IRA 50 and 65)). 
Examples 
AT+CMGL=?  
+CMGL: ("REC UNREAD","REC REA D","STO UNSENT","STO SENT","ALL")  
OK 
AT+CMGL="ALL"  
+CMGL: 1,"STO UNSENT","+10011",,,145,4 
Hello World  
OK 
7.12  AT+CMGR  Read message  
Description  
This command is used to return message with location value <index> from message storage 
<mem1> to the TE. 
SIM PIN References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CMGR=?  OK 
Write Command  Responses  
AT+CMGR= <index>  If  text mode ( AT+CMGF =1), command successful and SMS-  
DELIVER:  
+CMGR: <stat> ,<oa> ,[<alpha> ],<scts> [,<tooa> ,<fo> ,<pid> ,<dcs> , 
<sca> , <tosca>, <length> ]<CR><LF> <data>  
OK 
SIMCom Confidential File
---

## Page 177

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 176 If  text  mode ( AT+CMGF =1), command successful and SMS - 
SUBMIT:  
+CMGR: <stat> ,<da> ,[<alpha> ][,<toda> ,<fo> ,<pid> ,<dcs> ,[<vp> ], 
<sca> , <tosca> ,<length> ]<CR><LF><data>  
OK 
If  text mode ( AT+CMGF =1), command successful and SM S- 
STATUS -REPORT:  
+CMGR: <stat> ,<fo> ,<mr> ,[<ra> ],[<tora> ],<scts> ,<dt> ,<st> 
OK 
If  text mode ( AT+CMGF =1), command successful and SMS-  
COMMAND: 
+CMGR: <stat> ,<fo> ,<ct>[,<pid> ,[<mn> ],[<da> ],[<toda> ],<length
>]<CR><LF> <data>  
OK 
If  text mode ( AT+CMGF =1), com mand successful and CBM 
storage: 
+CMGR: <stat> ,<sn> ,<mid> ,<dcs> ,<page> ,<pages> <CR><LF><d
ata> 
OK 
If PDU mode ( AT+CMGF =0) and Command successful: 
+CMGR: <stat> ,[<alpha> ],<length> <CR><LF><pdu>  
OK 
+CMS ERROR: <err>  
Defined values  
<index> 
Integer type; valu e in the range of location numbers supported by the associated memory and start 
with zero.  
<stat>  
1.Text Mode ： 
"REC UNREAD"  received unread message (i.e. new message) 
"REC READ"  received read message 
"STO UNSENT"  stored unsent message  
"STO SENT"   stored sent message  
2. PDU Mode ： 
0  –  received unread message (i.e. new message)  
1  –  received read message.  
2  –  stored unsent message. 
3  –  stored sent message  
<oa>  
Originating -Address, Address- Value field in string format; BCD numbers (or GSM 7 bit default 
SIMCom Confidential File
---

## Page 178

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 177 alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by <tooa> . 
<alpha>  
String type alphanumeric representation of <da>  or <oa> corresponding to the entry found in MT 
phonebook; implem entation of this feature is manufacturer specific; used character set should be 
the one selected with command Select TE Character Set AT+CSCS . 
<scts>  
TP-Service -Centre -Time -Stamp in time -string format (refer <dt> ). 
<tooa> 
TP-Originating -Address, Type -of-Address octet in integer format. (default refer <toda> ). 
<fo>  
Depending on the command or result code: first octet of GSM 03.40 SMS -DELIVER, 
SMS -SUBMIT (default 17), SMS -STATUS -REPORT, or SMS -COMMAND (default 2) in integer 
format. SMS status report is supported under text mode if <fo>  is set to 49.  
<pid> 
Protocol Identifier  
GSM 03.40 TP -Protocol- Identifier in integer format  
0…255 
<dcs>  
Depending on the command or result code: SMS Data Coding Scheme (default 0), or Cell 
Broadcast Data Coding Scheme i n integer format. 
<sca>  
RP SC address Address -Value field in string format; BCD numbers (or GSM 7 bit default alphabet 
characters) are converted to characters of the currently selected TE character set, type of address 
given by  <tosca> . 
<tosca>  
RP SC a ddress Type -of-Address octet in integer format (default refer <toda> ). 
<length>  
Integer type value indicating in the text mode ( AT+CMG F =1) the length of the message body 
<data>  > (or <cdata> ) in characters; or in PDU mode ( AT+CMGF =0), the length of the actual TP 
data unit in octets. (i.e. the RP layer SMSC address octets are not counted in the length). 
<data>  
In the case of SMS: TP -User-Data in text mode responses; format:  
1  –  I f <dcs>  indicates that GSM 7 bit default alphabet is used and <fo>  indicat es that 
TP-User-Data -Header -Indication is not set: 
a. If TE character set other than "HEX": ME/TA converts GSM alphabet into current 
TE character set.  
b. If TE character set is "HEX": ME/TA converts each 7- bit character of GSM 7 bit 
default alphabet into t wo IRA character long hexadecimal numbers. (e.g. character 
Π (GSM 7 bit default alphabet 23) is presented as 17 (IRA 49 and 55)). 
2  –  I f <dcs>  indicates that 8 -bit or UCS2 data coding scheme is used, or <fo> indicates that 
TP-User-Data -Header -Indication is set: ME/TA converts each 8 -bit octet into two IRA 
character long hexadecimal numbers. (eg. octet with integer value 42 is presented to TE 
SIMCom Confidential File
---

## Page 179

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 178 as two characters 2A (IRA 50 and 65)).  
3  –  I f <dcs>  indicates that GSM 7 bit default alphabet is used: 
a. If TE c haracter set other than "HEX": ME/TA converts GSM alphabet into current 
TE character set.  
b. If TE character set is "HEX": ME/TA converts each 7 -bit character of the GSM 7 
bit default alphabet into two IRA character long hexadecimal numbers. 
4  –  I f <dcs>  indicates that 8 -bit or UCS2 data coding scheme is used: ME/TA converts 
each 8 -bit octet into two IRA character long hexadecimal numbers. 
<da>  
Destination -Address, Address- Value field in string format; BCD numbers (or GSM 7 bit default 
alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by <toda> . 
<toda> 
TP-Destination -Address, Type-of- Address octet in integer format. (when first character of <da>  is + 
(IRA 43) default is 145, otherwise default is 129). The range of value is from 128 to 255. 
<vp>  
Depending on SMS -SUBMIT <fo>  setting: TP -Validity -Period either in integer format (default 
167) or in time- string format (refer <dt> ). 
<mr>  
Message Reference  
GSM 03.40 TP -Message -Reference in in teger format.  
<ra>  
Recipient Address  
GSM 03.40 TP -Recipient -Address Address- Value field in string format;BCD numbers(or GSM 
default alphabet characters) are converted to characters of the currently selected TE character 
set(refer to command AT+CSCS );type  of address given by <tora>  
<tora>  
Type of Recipient Address  
GSM 04.11 TP -Recipient -Address Type -of-Address octet in integer format (default refer <toda> ) 
<dt>  
Discharge Time 
GSM 03.40 TP -Discharge- Time in time -string format:”yy/MM/dd,hh:mm:ss+zz”,wher e characters 
indicate year (two last digits),month,day,hour,minutes,seconds and time zone. 
<st> 
Status  
GSM 03.40 TP -Status in integer format  
0…255 
<ct> 
Command Type  
GSM 03.40 TP -Command -Type in integer format 
0…255 
<mn>  
Message Number 
SIMCom Confidential File
---

## Page 180

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 179 GSM 03.40 TP -Message -Number in integer format 
<sn>  
Serial Number  
GSM 03.41 CBM Serial Number in integer format 
<mid>  
Message Identifier  
GSM 03.41 CBM Message Identifier in integer format 
<page>  
Page Parameter  
GSM 03.41 CBM Page Parameter bits 4-7 in integer format 
<pages>  
Page parameter  
GSM 03.41 CBM Page Parameter bits 0-3 in integer format 
<pdu> 
In the case of SMS: SC address followed by TPDU in hexadecimal format: ME/TA converts each 
octet of TP data unit into two IRA character long hexadecimal numbers. (eg. octet with integer 
value 42 is presented to TE as two characters 2A (IRA 50 and 65)).  
Examples 
AT+CMGR=1  
+CMGR: "STO UNSENT","+10011",,145,17,0,0,167,"+8613800100500",145, 11 
Hello World  
OK 
7.13  AT+CMGS  Send message  
Description  
This command is used to send message from a TE to the network (SMS -SUBMIT).  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CMGS=?  OK 
Write Command  Responses 
If text mode ( AT+CMGF =1): 
AT+CMGS= <da> [,<toda> ]<
CR> Text is entered.  
<CTRL -Z/ESC>  If sending successfully: 
+CMGS: <mr>  
OK 
If cancel sending: 
SIMCom Confidential File
---

## Page 181

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 180 If PDU mode( AT+CM GF=
0): 
AT+CMGS= <length> <CR>  
PDU is entered  
<CTRL -Z/ESC>  OK 
If sending fails:  
ERROR 
If sending fails:  
+CMS ERROR: <err>  
Defined values  
<da>  
Destination -Address, Address- Value field in string  format; BCD numbers (or GSM 7 bit default 
alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by <toda> . 
<toda> 
TP-Destination -Address, Type -of-Address octet in integer format. (when first c haracter of <da> is + 
(IRA 43) default is 145, otherwise default is 129). The range of value is from 128 to 255. 
<length>  
integer type value indicating in the text mode ( AT+CMGF =1) the length of the message body 
<data>  > (or <cdata>) in characters; or in  PDU mode ( AT+CMGF =0), the length of the actual TP 
data unit in octets. (i.e. the RP layer SMSC address octets are not counted in the length) 
<mr>  
Message Reference  
GSM 03.40 TP -Message -Reference in integer format.  
NOTE:  In text mode, the maximum length of an SMS depends on the used coding scheme: It is 
160 characters if the 7 bit GSM coding scheme is used.  
Examples 
AT+CMGS="13012832788"<CR>(TEXT MODE)  
> ABCD<ctrl -Z/ESC>  
+CMGS: 46  
OK 
7.14  AT+CMSS  Send message from storage 
Description  
This command is used to send message with location value <index> from preferred message 
storage <mem2>  to the network (SMS- SUBMIT or SMS -COMMAND).  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
SIMCom Confidential File
---

## Page 182

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 181 Test Command  Responses  
AT+CMSS=?  OK 
Write Command  Responses  
AT+CMSS=  
<index>  [,<da> [,<toda> ]] +CMSS: <mr>  
OK 
ERROR 
If sending fails:  
+CMS ERROR: <err>  
Defined values  
<index>  
Integer type; value in the range of location numbers supported by the associated memory and start 
with zero.  
<da>  
Destination -Address, Address- Value fi eld in string format; BCD numbers (or GSM 7 bit default 
alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by <toda> . 
<mr>  
Message Reference  
GSM 03.40 TP -Message -Reference in integer format.  
<toda>  
TP-Destination -Address, Type-of- Address octet in integer format. (when first character of <da>  is + 
(IRA 43) default is 145, otherwise default is 129). The range of value is from 128 to 255. 
NOTE:  In text mode, the maximum length of an SMS depen ds on the used coding scheme: It is 
160 characters if the 7 bit GSM coding scheme is used.  
Examples 
AT+CMSS=3  
+CMSS: 0  
OK 
AT+CMSS=3,"13012345678"  
+CMSS: 55  
OK 
7.15  AT+CMGW  Write message to memory  
Description  
This command is used to store message (either  SMS -DELIVER or SMS -SUBMIT) to memory 
storage <mem2> . 
SIMCom Confidential File
---

## Page 183

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 182 SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses  
AT+CMGW=?  OK 
Write Command  Responses 
If text mode( AT+CMGF =1): 
AT+CMGW=<oa> /<da> [,<t
ooa> /<toda> [,<stat> ]]<CR>
Text is entered.  
<CTRL-Z/ESC>  
If PDU mode( AT+CMGF =
0): 
AT+CMGW=<length> [,<sta
t>]<CR> PDU is entered.  
<CTRL -Z/ESC>  If write successfully:  
+CMGW: <index>  
OK 
If cancel write:  
OK 
If write fails:  
ERROR 
If write fails:  
+CMS ERROR: <err>  
Defined values  
<index> 
Integer type; va lue in the range of location numbers supported by the associated memory and start 
with zero.  
<oa>  
Originating -Address, Address- Value field in string format; BCD numbers (or GSM 7 bit default 
alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by <tooa> . 
<tooa>  
TP-Originating -Address, Type -of-Address octet in integer format. (default refer <toda> ). 
<da>  
Destination -Address, Address- Value field in string format; BCD numbers (or GSM 7 bit def ault 
alphabet characters) are converted to characters of the currently selected TE character set, type of 
address given by  <toda> . 
<toda> 
TP-Destination -Address, Type-of- Address octet in integer format. (when first character of <da>  is + 
(IRA 43) default is 145, otherwise default is 129). The range of value is from 128 to 255. 
<length>  
Integer type value indicating in the text mode ( AT+CMG F =1) the length of the message body 
<data>  > (or <cdata>) in characters; or in PDU mode ( AT+CMGF =0), the length of t he actual TP 
data unit in octets. (i.e. the RP layer SMSC address octets are not counted in the length).  
<stat>  
SIMCom Confidential File
---

## Page 184

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 183 1. Text Mode:  
"STO UNSENT"  stored unsent message  
"STO SENT"   stored sent message  
2. PDU Mode:  
2  –  stored unsent message 
3  –  stored sent  message  
NOTE:  In text mode, the maximum length of an SMS depends on the used coding scheme: It is 
160 characters if the 7 bit GSM coding scheme is used.  
Examples 
AT+CMGW="13012832788" <CR> (TEXT MODE) 
ABCD<ctrl -Z/ESC>  
+CMGW:1  
OK 
7.16  AT+CMGD  Delete mes sage 
Description  
This command is used to delete message from preferred message storage <mem1>  location 
<index> . If <delflag>  is present and not set to 0 then the ME shall ignore <index>  and follow the 
rules for <delflag>  shown below. 
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses 
AT+CMGD=?  +CMGD: (list of supported <index> s)[,(list of supported 
<delflag> s)] 
OK 
Write Command  Responses  
AT+CMGD=  
<index> [,<delflag> ] OK 
ERROR  
+CMS ERROR: <err>  
Defined values  
<index> 
Integer type;  value in the range of location numbers supported by the associated memory and start 
with zero.  
<delflag>  
SIMCom Confidential File
---

## Page 185

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 184 0  –  (or omitted) Delete the message specified in <index> . 
1  –  Delete all read messages from preferred message storage, leaving unread messages and 
stored mobile originated messages (whether sent or not) untouched. 
2  –  Delete all read messages from preferred message storage and sent mobile originated 
messages, leaving unread messages and unsent mobile originated messages untouched. 
3  –  Delete all read messages from preferred message storage, sent and unsent mobile 
originated messages leaving unread messages untouched. 
4  –  Delete all messages from preferred message storage including unread messages.  
NOTE:  If set <delflag> =1, 2, 3 or 4, <index>  is omitted, such as  AT+CMGD =,1. 
Examples 
AT+CMGD=1  
OK 
7.17  AT+CMGMT  Change message status 
Description  
This command is used to change the message status. If the status is unread, it will be changed read. 
Other statuses don’t change. 
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CMGMT=?  OK 
Write Command  Responses 
AT+CMGMT= <index>  OK 
ERROR  
+CMS ERROR: <err>  
Defined values  
<index> 
Integer type; value in the range of location numbers supported by the associated memory and start 
with zero.  
Examples 
AT+CMGMT=1  
SIMCom Confidential File
---

## Page 186

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 185 OK 
7.18  AT+CMVP  Set message valid period  
Description  
This command is used to set valid period for sending short message. 
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CMVP=?  +CMVP: ( list of supported <vp> s) 
OK 
Read Command  Responses 
AT+CMVP?  +CMVP: <vp>  
OK 
Write Command  Responses  
AT+CMVP= <vp>  OK 
ERROR 
+CMS ERROR: <err>  
Defined values  
<vp>  
Validity period value:  
0 to 143      ( <vp> +1) x 5 minutes (up to 12 hours) 
144 to 167    12 hours + ( <vp> -143) x 30 minutes 
168 to 196    ( <vp> -166) x 1 day 
197 to 255    ( <vp> -192) x 1 week 
 
Examples 
AT+CMVP=167  
OK 
AT+CMVP?  
+CMVP: 167  
OK 
SIMCom Confidential File
---

## Page 187

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 186 7.19  AT+CMGRD  Read and delete m essage  
Description  
This command is used to read message, and delete the message at the same time. It integrate 
AT+CMGR  and AT+CMGD , but it doesn’t change the message status. 
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CMGRD=?  OK 
Write Command  Responses 
AT+CMGRD=<index>  If text mode( AT+CMGF =1),command successful and SMS- DE-
LIVER:  
+CMGRD: <stat> ,<oa> ,[<alpha> ],<scts> [,<tooa> ,<fo> ,<pid> ,<dcs
>, <sca> ,<tosca> ,<length> ]<CR><LF> <data>  
OK 
If text mode( AT+CMGF =1),command successful and SMS -SU- 
BMIT:  
+CMGRD: <stat> ,<da> ,[<alpha> ][,<toda> ,<fo> ,<pid> ,<dcs> ,[<vp
>], <sca> ,<tosca> ,<length> ]<CR><LF><data>  
OK 
If text mode( AT+CMGF =1),command successful and SMS -STA- 
TUS- REPORT:  
+CMGRD: <stat> ,<fo> ,<mr>,[<ra> ],[<tora> ],<scts> ,<dt> ,<st>  
OK 
If text mode( AT+CMGF =1),command successful and SMS- CO-
MMAND:  
+CMGRD: <stat> ,<fo> ,<ct> [,<pid> ,[<mn> ],[<da> ],[<toda> ],<lengt
h><CR><LF><data> ] 
OK 
If text mode( AT+CMGF =1),command successful and CBM sto - 
rage: 
+CMGRD: <stat>,<sn> ,<mid> ,<dcs>,<page> ,<pages> <CR><LF> <
data>  
OK 
If PDU mode( AT+CMGF =0) and command successful: 
+CMGRD: <stat> ,[<alpha> ],<length> <CR><LF> <pdu>  
SIMCom Confidential File
---

## Page 188

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 187 OK 
ERROR 
+CMS ERROR: <err>  
Defined values  
Refer to command AT+CMGR.  
Examples 
AT+CMGRD=6  
+CMGRD:"REC READ","+8613917787249",,"06/07/10,12:09:38+32",145,4,0,0, "+86138002105 
00",145,4 
How do you do 
OK 
 
7.20  AT+CMGSEX  Send message  
Description  
This command is used to send message from a TE to the network (SMS -SUBMIT).  
Note: This command not support in CDMA/EV DO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses  
AT+CMGSEX=?  OK 
Write Command  Responses  
If text mode ( AT+CMGF =1): 
AT+CMGSEX= <da> [,<toda
>][,<mr> ,<msg_seg> ,<msg_
total>] <CR>Text is entered.  
<CTRL -Z/ESC>  If sending successfully: 
+CMGSEX: <mr>  
OK 
If cancel sending: 
OK 
If sending fails:  
ERROR 
If sending fails:  
+CMS ERROR: <err>  
Defined values  
SIMCom Confidential File
---

## Page 189

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 188 <da>  
Destination -Address, Address- Value field in string format; BCD numbers (or GSM 7 bit default 
alphabet characters) are converted  to characters of the currently selected TE character set, type of 
address given by <toda> . 
<toda> 
TP-Destination -Address, Type -of-Address octet in integer format. (When first character of <da> is 
+ (IRA 43) default is 145, otherwise default is 129). The range of value is from 128 to 255. 
<mr>  
Message Reference  
GSM 03.40 TP -Message -Reference in integer format. The maximum length is 255. 
<msg_seg> 
The segment number for long sms  
<msg_total>  
The total number of the segments for long sms. Its range is from 2 to 255. 
NOTE:  In text mode, the maximum length of an SMS depends on the used coding scheme: For 
single SMS, it is 160 characters if the 7 bit GSM coding scheme is used; For multiple long sms, it is 
153 characters if the 7 bit GSM coding scheme is u sed. 
Examples 
AT+CMGSEX="13012832788", 190, 1, 2<CR>(TEXT MODE)  
> ABCD<ctrl- Z/ESC>  
+CMGSEX: 190  
OK 
AT+CMGSEX="13012832788", 190, 2, 2<CR>(TEXT MODE)  
> EFGH<ctrl- Z/ESC>  
+CMGSEX: 190  
OK 
7.21  AT+CMSSEX  Send multi messages from storage  
Description  
This command is used to send messages with location value <index1>,<index2>,<index3>… from 
preferred message storage <mem2>  to the network (SMS -SUBMIT or SMS -COMMAND).The 
max count of index is 13 one time. 
Note: This command not support in CDMA/EVDO mode  
SIM PIN  References  
YES 3GPP TS 27.005 
Syntax 
Test Command  Responses  
SIMCom Confidential File
---

## Page 190

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 189 AT+CMSSEX=?  OK 
Write Command  Responses 
AT+CMSSEX=  
<index>  [,<index > [,… ]]  +CMSSEX: <mr> [,<mr> [,…]]  
OK 
ERROR 
If sending fails:  
[+CMSSEX: <mr> [,<mr> [,…]]] 
+CMS ERROR: <err>  
Defined values  
<index> 
Integer type; value in the range of location numbers supported by the associated memory and start 
with zero.  
<mr>  
Message Reference  
GSM 03.40 TP -Message -Reference in integer format.  
NOTE:  In text mode, the maximum length of an SMS depends on t he used coding scheme: It is 
160 characters if the 7 bit GSM coding scheme is used.  
Examples 
AT+CMSSEX=0,1 
+CMSSEX: 239,240  
 
OK 
AT+CMSSEX=0,1  
+CMSSEX: 238  
+CMS ERROR: Invalid memory index 
 
7.22  AT+CMGP  Set cdma/evdo text mode parameters  
Description  
The command is used to select values for additional parameters needed when SM is sent to the 
network or placed in storage when text format message mode is selected. 
NOTE: take effect in CDMA/EVDO mode  
SIM PIN  References  
NO 3GPP TS 27.005 
Syntax 
SIMCom Confidential File
---

## Page 191

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 190 Test Command  Responses  
AT+CMGP=?  OK 
Read Command  Responses  
AT+CMGP?  +CMGP: <tid> ,<vpf> ,<vp> ,<ddtf>,<ddt>  
OK 
Write Command  Responses  
AT+CMGP= [Tid] [,<vpf> ,<v
p>[,<ddtf>,<ddt> ]] OK 
Defined values  
<tid>  
Teleservice ID, value maybe 4095,4096,4097,4098,4099,4100,4101,4102 
Default 4098 
<vpf>  
Valid Period Format  
0, Absolute 
1, Relative  
<vp>  
Valid Period  
“YY/MM/DD,HH/MM/SS” if vpf=0,  
Integer not exceed 248 if vpf=1 
<ddtf> 
Deferred Delivery Time Format  
0, Absolute 
1, Relative  
<ddt> 
Deferred Delivery Time  
“YY/MM/D D,HH/MM/SS” if ddtf=0,  
Integer not exceed 248 if ddtf=1  
Examples 
AT+CMGP=4098,0,”11/04/22,16:21:00”,1,12 
OK 
SIMCom Confidential File
---

## Page 192

8  AT Commands for Phonebook 
8.1  AT+CPBS  Select phonebook memory storage  
Description  
This command selects the active phonebook storage,i.e.the phon ebook storage that all subsequent 
phonebook commands will be operating on. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CPBS=?  +CPBS: (list of supported <storage> s) 
OK 
Read Command  Responses 
AT+CPBS?  +CPBS: <storage> [,<used> ,<total> ] 
OK 
+CME ERROR: <err>  
Write Command  Responses 
AT+CPBS= <storage>  OK 
ERROR 
+CME ERROR: <err>  
Execution Command  Responses  
AT+CPBS  Set default value “SM”: 
OK 
Defined values  
<storage>  
Values reserved by the present document:  
"DC"   ME diale d calls list  
          Capacity: max. 100 entries 
          AT+CPBW command is not applicable to this storage. 
"MC"     ME missed (unanswered received) calls list  
          Capacity: max. 100 entries 
          AT+CPBW command is not applicable to this stor age. 
SIMCom Confidential File
---

## Page 193

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 192 "RC"    ME received calls list  
          Capacity: max. 100 entries 
          AT+CPBW command is not applicable to this storage. 
"SM"    SIM phonebook 
          Capacity: depending on SIM card 
"ME"    Mobile Equipment phonebook 
          Capacity: max. 5 00 entries 
"FD"      SIM fixdialling -phonebook 
          Capacity:depending on SIM card 
"ON"      MSISDN l ist  
          Capacity:depending on SIM card 
"LD"      Last number dialed phonebook  
          Capacity: depending on SIM card 
          AT+CPBW comman d is not applicable to this storage   
"EN"      Emergency numbers  
          Capacity: depending on SIM card 
          AT+CPBW command is not applicable to this storage.   
<used>  
Integer type value indicating the number of used locations in selected memor y. 
<total>  
Integer type value indicating the total number of locations in selected memory. 
Examples 
AT+CPBS=?  
+CPBS:  ("SM","DC","FD","LD","MC","ME","RC","EN","ON")  
OK 
AT+CPBS=”SM”  
OK 
AT+CPBS?  
+CPBS: "SM",1,200  
OK 
8.2  AT+CPBR  Read phonebook entries  
Description  
This command gets the record information from the selected memory storage in phonebook. If the 
storage is selected as “SM”  then the command will return the record in SIM phonebook, the same to 
others.  
SIM PIN  References  
YES 3GPP TS 27.007 
SIMCom Confidential File
---

## Page 194

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 193 Syntax 
Test Command  Responses 
AT+CPBR=?  +CPBR: ( <minIndex> -<maxIndex> ), [<nlength> ], [<tlength> ] 
OK 
+CME ERROR:  <err>  
Write Command  Responses 
AT+CPBR=  
<index1> [,<index2> ] [+CPBR: <index1> ,<number> ,<type> ,<text> [<CR><LF> 
+CPBR: <index2> ,<number> ,<type> ,<text>[…]]]  
OK 
ERROR  
+CME ERROR: <err>  
Defined values  
<index1> 
Integer type value in the range of location numbers of phonebook memory.                     
<index2> 
Integer type value in the range of location numbers of phonebook memory.   
<index>  
Integer type.the current position number of the Phonebook index. 
<minIndex> 
Integer type the minimum <index>  number. 
<maxIndex> 
Integer type the maximum <index>  number  
<number> 
String type, phone number of format  <type> , the maximum length is <nlength> . 
<type>  
Type of phone number octet in integer format, default 145 when dialing string includes international 
access code character "+", otherwise 129.  
<text>  
String type field of maximum length <tlength> ; often this value is set as name.  
<nlength> 
Integer type value indicating the maximum length of field <number> . 
<tlength>  
Integer type value indicating the maximum length of field <text> . 
Examples 
AT+CPBS?  
+CPBS: "SM",2,200  
OK 
SIMCom Confidential File
---

## Page 195

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 194 AT+CPBR=1,10  
+CPBR: 1,"1234567890",129,"James"                             
+CPBR: 2,"0987654321",129,"Kevin" 
OK  
8.3  AT+CPBF  Find phonebook entries  
Description  
This command finds the record in phonebook (from the current phonebook memory storage 
selected with  AT+CPBS ) which alphanumeric field has substring <findtext> .If <findtext> is null, it 
will lists all the entries.  
SIM PIN  References  
YES  3GPP TS 27.007  
Syntax 
Test Command  Responses 
AT+CPBF=?  +CPBF: [ <nlength> ],[<tlength> ] 
OK 
+CME ERROR: <err>  
Write Command  Responses 
AT+CPBF=[ <findt ext>] [+CPBF:  <index1> ,<number> ,<type> ,<text> [<CR><LF>  
+CPBF: <indexN> ,<number> ,<type> ,<text> […]]]  
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<findtext>  
String type, this value is used to find the record. Character set should be the one selected with 
command AT+CSCS.  
<index> 
Integer type values in the range of location numbers of phonebook memory. 
<number>  
String type, phone number of format <type> , the maximum length is  <nlength> . 
<type>  
Type of phone number octet in integer format, default 145 when dialing string includes international 
access code character "+", otherwise 129.  
<text>  
SIMCom Confidential File
---

## Page 196

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 195 String type field of maximum length <tlength> ; Often this value is set as name.  
<nlength>  
Integer type value indicating the maximum length of field <number> . 
<tlength>  
Integer type value indicating the maximum length of field <text> . 
Examples 
AT+CPBF=" James "   
+CPBF: 1,"1234567890",129," James "  
OK 
8.4  AT+CPBW  Write phonebook entry  
Description  
This command writes phonebook entry in location number <index>  in the current phonebook 
memory storage selected with AT+CPBS . 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CPBW=?  +CPBW:(list of supported  <index> s),[<nlength> ], 
(list of supported  <type> s),[<tlength> ] 
OK 
+CME ERROR: <err>  
Write Command  Responses 
AT+CPBW=[ <index> ][,<nu
mber> [,<type> [,<text> ]]] OK 
ERROR  
+CME ERROR: <err>  
Defined values  
<index>  
Integer type values in the range of location numbers of phonebook memory.If <index> is not given, 
the first free entry will be used. If <index>  is given as the only parameter, the phonebook entry 
specified by <index> is deleted.If record number <index> already exists, it will be overwritten. 
<number> 
String type, phone number of format  <type> , the maximu m length is <nlength> .It must be an 
non-empty string. 
SIMCom Confidential File
---

## Page 197

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 196 <type>  
Type of address octet in integer format, The range of value is from 129 to 255. If <number> 
contains a leading “+” <type> = 145 (international) is used.Supported value are: 
145  –   when diallin g string includes international access code character “+”  
161  –   national number.The network support for this type is optional 
177  –   network specific number,ISDN format 
129  –   otherwise  
 
NOTE:  Other value refer TS 24.008 [8] subclause 10.5.4.7. 
<text>  
String type field of maximum length <tlength> ; character set as specified by command Select TE 
Character Set AT+CSCS . 
<nlength> 
Integer type value indicating the maximum length of field <number> . 
<tlength>  
Integer type val ue indicating the maximum length of field <text> . 
NOTE:  If the parameters of <type>  and <text>  are omitted and the first character of <number>  is 
‘+’，it will specify <type>  as 145(129 if the first character isn’t ‘+’) and  <text>  as NULL.  
Examples 
AT+CPBW =3,"88888888",129,"John" 
OK 
AT+CPBW=,”6666666”,129,”mary” 
OK 
AT+CPBW=1  
OK 
8.5  AT+CNUM  Subscriber number  
Description  
Execution command returns the MSISDNs related to the subscriber (this information can be stored 
in the SIM or in the ME). If subscriber has different MSISDN for different services, each MSISDN 
is returned in a separate line.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CNUM=?  OK 
Execution Command Responses 
SIMCom Confidential File
---

## Page 198

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 197 AT+CNUM  [+CNUM:  <alpha> ,<number> ,<type> [<CR><LF>  
+CN UM:  <alpha> , <number> ,<type>  [...]]]  
OK 
+CME ERROR: <err>  
Defined values  
<alpha> 
Optional alphanumeric string associated with <number> , used character set should be the one 
selected with command Select TE Character Set  AT+CSCS . 
<number>  
String type phone number of format specified by <type> . 
<type>  
Type of address octet in integer format.see also  AT+CPBR <type>  
Examples 
AT+CNUM  
+CNUM: "","13697252277",129  
OK 
SIMCom Confidential File
---

## Page 199

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 198 9  AT Commands for GPRS  
9.1  AT+CGREG  GPRS network registration status  
Description  
This comm and controls the presentation of an unsolicited result code “+CGREG:  <stat> ” when 
<n>=1 and there is a change in the MT's GPRS network registration status. 
The read command returns the status of result code presentation and an integer  <stat> which shows 
Whether the network has currently indicated the registration of the MT. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGREG=?  +CGREG: (list of supported <n>s) 
OK 
Read Command  Responses  
AT+CGREG?  +CGREG: <n>,<stat> [,<lac> ,<ci> ] 
OK 
Write Command  Responses 
AT+CGREG= <n> OK 
Execution Command Responses  
AT+CGREG  Set default value:  
OK 
Defined values  
<n> 
0  –  disable network registration unsolicited result code 
1  –  enable network registration unsolicited result code +CGREG:  <stat> 
2  –  there is a change in the ME network registration status or a change of the network cell: 
      +CGREG: <stat> [,<lac> ,<ci>] 
<stat>  
0  –  not registered, ME is not currently searching an operator to register to 
1  –  registered, home network 
2  –  not registered, but ME is currently trying to attach or searching an operator to register 
to 
3  –  registration denied  
SIMCom Confidential File
---

## Page 200

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 199  
Examples 
AT+CGREG=?  
+CGREG: (0 -1) 
OK 
AT+CGREG?  
+CGREG: 0,0  
OK 
9.2  AT+CGATT  Packet domain attach or detach  
Description  
The write command is used to attach the MT to, or detach the MT from, the Packet Domain service.  
The read command returns the current Packet Domain service state.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGATT=?  +CGATT: (list of supported <state> s) 
OK 
ERROR 
Read Command  Responses 
AT+CGATT?  +CGATT: <state>  
OK 4  –  unknown 
5  –  registered, roaming  
<lac>  
Two bytes location area code in hexadecimal format (e.g.”00C3” equals 193 in decimal). 
 
NOTE:  The <lac> not supported in CDMA/HDR mode 
<ci> 
Cell ID in hexadecimal format.  
GSM :  Maximum is two byte  
WCDMA :  Maximum is four byte 
TDS -CDMA :  Maximum is four byte 
 
NOTE:  The <ci> not supported in CDMA/HDR mode 
SIMCom Confidential File
---

## Page 201

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 200 ERROR  
Write Command  Responses  
AT+CGATT= <state>  OK 
ERROR 
+CME ERROR: <err > 
Defined values  
<state>  
Indicates the state of Packet Domain attachment:  
0  –  detached  
1  –  attached  
Examples 
AT+CGATT?  
+CGATT: 0  
OK 
AT+CGATT=1  
OK 
9.3  AT+CGACT  PDP context activate or deactivate  
Description  
The write command is used to activate or deactivate the specified PDP context (s).  This command  is  
not used in CDMA/EVDO mode. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGACT=?  +CGACT: (list of supported <state> s) 
OK 
Read Command  Responses  
AT+CGACT?  +CGACT: [ <cid>, <state>  [<CR><LF> 
+CGACT: <cid> , <state>  
[...]]]  
OK 
Write Command  Responses 
AT+CGACT= <state> OK 
SIMCom Confidential File
---

## Page 202

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 201 [,<cid> ] ERROR  
+CME ERROR: <err>  
Defined values  
<state>  
Indicates the state of PDP context activation:  
0  –  deactivated  
1  –  activated  
<cid>  
A numeric parameter which specifies a particular PDP context definition (see AT+CGDCONT  
command). 
1…24,100…179 
Examples 
AT+CGACT?  
+CGACT: 1,1 
OK 
AT+CGACT=?  
+CGACT: (0,1)  
OK 
AT+CGACT=0,1  
OK 
9.4  AT+CGDCONT  Define PDP context  
Description  
The set command s pecifies PDP context parameter values for a PDP context identified by the 
(local) context identification parameter <cid> . The number of PDP contexts that may be in a 
defined state at the same time is given by the range returned by the test command. A speci al form of 
the write command ( AT+CGDCONT =<cid>) causes the values for context <cid>  to become 
undefined.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGDCONT=?  +CGDCONT: (range of supported <cid> s),<PDP_type> ,,,(list of 
suppor ted <d_comp> s),(list of supported <h_comp> s)(list of 
<ipv4_ctrl >s),(list of < emergency _flag >s) 
SIMCom Confidential File
---

## Page 203

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 202 OK 
ERROR 
Read Command  Responses 
AT+CGDCONT?  +CGDCONT: [ <cid> , <PDP_type> , <APN> ,<PDP_addr> , 
<d_comp> , <h_comp>,<ipv4_ctrl>,<emergency _flag >[<CR><LF>  
+CGDCONT : <cid> , <PDP_type> , <APN>, <PDP_addr> , 
<d_comp> , <h_comp>,< ipv4_ctrl>,<emergency _flag>[...]]]  
OK 
ERROR 
Write Command  Responses  
AT+CGDCONT= <cid> [,<P
DP_type> [,<APN> [,<PDP_a
ddr> [,<d_comp> [,<h_comp>
][,<ipv4_ctrl> [,<emergency _
flag>]]]]]]  OK 
ERROR 
Execu tion Command Responses  
AT+CGDCONT  OK 
ERROR 
Defined values  
<cid>  
(PDP Context Identifier) a numeric parameter which specifies a particular PDP context definition. 
The parameter is local to the TE -MT interface and is used in other PDP context -related co mmands. 
The range of permitted values (minimum value = 1) is returned by the test form of the command. 
1…24,100…179 
<PDP_type> 
(Packet Data Protocol type) a string parameter which specifies the type of packet data protocol.  
IP   Internet Protocol 
PPP   Point to Point Protocol  
IPV6  Internet Protocol Version 6 
IPV4V6  Dual PDN Stack  
<APN>  
(Access Point Name) a string parameter which is a logical name that is used to select the GGSN or 
the external packet data network.  
<PDP_addr> 
A string parameter that  identifies the MT in the address space applicable to the PDP.  
Read command will continue to return the null string even if an address has been allocated during 
the PDP startup procedure. The allocated address may be read using command AT+CGPADDR . 
<d_comp > 
SIMCom Confidential File
---

## Page 204

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 203 A numeric parameter that controls PDP data compression, this value may depend on platform: 
0  –  off (default if value is omitted)  
1  –  on 
2  –  V .42bis 
<h_comp> 
A numeric parameter that controls PDP header compression, this value may depend on platform:  
0  –  off (default if value is omitted)  
1  –  on 
2  –  RFC1144 
3  –  RFC2507 
4  –  RFC3095 
<ipv4_ ctrl> 
Parameter that controls how the MT/TA requests to get the IPv4 address information: 
0  –  Address Allocation through NAS Signaling  
1  –  on 
<emergency_flag> 
emergency_flag : 
0  –  off (default if value is omitted)  
1  –  on 
Examples 
AT+CGDCONT?  
+CGDCONT: 1,"IPV4V6","","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0,0,0  
+CGDCONT: 2,"IPV6","ims","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0,0,0  
+CGDCONT: 3,"IPV4V6", "","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0,0,1  
 
OK 
AT+CGDCONT=?  
+CGDCONT: (1 -24,100-179),"IP",,,(0-2),(0- 4),(0 -1),(0 -1) 
+CGDCONT: (1 -24,100-179),"PPP",,,(0- 2),(0 -4),(0 -1),(0 -1) 
+CGDCONT: (1 -24,100-179),"IPV6",,,(0- 2),(0 -4),(0-1),(0-1) 
+CGDCONT: (1 -24,100-179),"IPV4V6",,,(0- 2),(0 -4),(0 -1),(0 -1) 
 
OK 
9.5  AT+CGDSCONT  Define Secondary PDP Context  
Description  
The set command specifies PDP context parameter values for a Secondary PDP context identified 
by the (local) context identification parameter, <cid>. The n umber of PDP contexts that may be in a 
defined state at the same time is given by the range returned by the test command. A special form of 
the set command, AT+CGDSCONT=<cid> causes the values for context number <cid> to become 
SIMCom Confidential File
---

## Page 205

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 204 undefined. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGDSCONT=?  +CGDSCONT:  (range of supported <cid> s),(list of <p_cid> s for 
active primary contexts),  <PDP_type> , (list of supported 
<d_comp> s),(list of supported <h_comp> s) 
 
OK 
ERROR 
Read Command  Responses 
AT+CGDSCONT?  +CGDSCONT:  [<cid> ,<p_cid> ,<d_comp> ,<h_comp>  
[<CR><LF>+CGDSCONT:  <cid> ,<p_cid> ,<d_comp> ,<h_comp>  
[...]]]  
 
OK 
ERROR 
Write Command  Responses  
AT+CGDSCONT= <cid> [,<
p_cid> [,<d_comp> [,<h_com
p>]]] OK 
ERROR 
Defined values  
<cid>  
a numeric parameter which specifies a particular PDP context definition. The parameter is local to 
the TE -MT interface and is used in other PDP context -related commands. The range of permitted 
values (minimum value = 1) is returned by the test form of the command. 
 
NOTE:  The <cid>s for network- initiated PDP contexts will have values outside the ranges 
indicated for the <cid> in the test form of the commands +CGDCONT and +CGDSCONT. 
<p_cid> 
a numeric parameter which specifies a particular PDP context definition whi ch has been specified 
by use of the +CGDCONT command. The parameter is local to the TE -MT interface. The list of 
SIMCom Confidential File
---

## Page 206

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 205 permitted values is returned by the test form of the command. 
<PDP_type>  
(Packet Data Protocol type) a string parameter which specifies the t ype of packet data protocol.  
IP   Internet Protocol 
PPP   Point to Point Protocol  
IPV6  Internet Protocol Version 6 
IPV4V6  Dual PDN Stack  
<d_comp>  
a numeric parameter that controls PDP data compression (applicable for SNDCPonly) (refer 
3GPP  TS 44.065 [61])  
0   off  
1   on (manufacturer preferred compression)  
2     V .42bis  
Other values are reserved.  
<h_comp> 
a numeric parameter that controls PDP header compression (refer 3GPP  TS 44.065 [61] and 
3GPP  TS 25.323 [62])  
0   off  
1   on (manufacturer preferred compression) 
2     RFC1144 (applicable for SNDCP only)  
3     RFC2507  
4     RFC3095 (applicable for PDCP only)  
Other values are reserved.  
Examples 
AT+CGDSCONT?  
+CGDSCONT: 2,1,0,0  
 
OK 
AT+CGDSCONT=2,1  
OK 
AT+CGDSCONT=?  
+CGDSCONT: (1 -24,100-179),(4,5,6),"IP",(0 -2),(0 -4) 
+CGDSCONT: (1 -24,100-179),(4,5,6),"PPP",(0- 2),(0 -4) 
+CGDSCONT: (1 -24,100-179),(4,5,6),"IPV6",(0- 2),(0 -4) 
+CGDSCONT: (1 -24,100-179),(4,5,6),"IPV4V6",(0- 2),(0 -4) 
 
OK 
SIMCom Confidential File
---

## Page 207

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 206 9.6  AT+CGTFT  Traffic Flow Template  
Description  
This command allows the TE to  specify a Packet Filter - PF for a Traffic Flow Template - TFT that 
is used in the GGSN in UMTS/GPRS and Packet GW in EPS for routing of packets onto different 
QoS flows towards the TE. The concept is further described in the 3GPP  TS 23.060 [47]. A TFT 
consists of from one and up to 16 Packet Filters, each identified by a unique <packet filter 
identifier>. A Packet Filter also has an <evaluation precedence index> that is unique within all TFTs 
associated with all PDP contexts that are associated with the s ame PDP address.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CGTFT=?  +CGTFT:  <PDP_type> ,(list of supported <packet filter 
identifier> s),(list of supported <evaluation precedence 
index> s),(list of supported <source address and  subnet 
mask> s),(list of supported <protocol number (ipv4) / next header 
(ipv6)> s),(list of supported <destination port range> s),(list of 
supported <source port range> s),(list of supported <ipsec security 
parameter index (spi)> s),(list of supported <type o f service (tos) 
(ipv4) and mask / traffic class (ipv6) and mask> s),(list of supported 
<flow label (ipv6)> s) 
[<CR><LF>+CGTFT:  <PDP_type> ,(list of supported <packet filter 
identifier> s),(list of supported <evaluation precedence 
index> s),(list of supported <s ource address and subnet 
mask> s),(list of supported <protocol number (ipv4) / next header 
(ipv6)> s),(list of supported <destination port range> s),(list of 
supported <source port range> s),(list of supported <ipsec security 
parameter index (spi)> s),(list of supported <type of service (tos) 
(ipv4) and mask / traffic class (ipv6) and mask> s),(list of supported 
<flow label (ipv6)> s) 
[...]] 
 
OK 
ERROR 
Read Command  Responses 
AT+CGTFT?  +CGTFT:  [<cid> ,<packet filter identifier> ,<evaluation precedence 
index> ,<sour ce address and subnet mask> ,<protocol number (ipv4) 
/ next header (ipv6)> ,<destination port range> ,<source port 
SIMCom Confidential File
---

## Page 208

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 207 range> ,<ipsec security parameter index (spi)> ,<type of service (tos) 
(ipv4) and mask / traffic class (ipv6) and mask> ,<flow label 
(ipv6)>  
[<CR><LF>+CGTFT:  <cid> ,<packet filter identifier> ,<evaluation 
precedence index> ,<source address and subnet mask> ,<protocol 
number (ipv4) / next header (ipv6)> ,<destination port 
range> ,<source port range> ,<ipsec security parameter index 
(spi)> ,<type of service (t os) (ipv4) and mask / traffic class (ipv6) 
and mask> ,<flow label (ipv6)>  
[...]]]  
 
OK 
ERROR 
Write Command  Responses 
AT+CGTFT= <cid> [,[<packe
t filter 
identifier> ,<evaluation 
precedence index> [,<source 
address and subnet 
mask> [,<protocol number 
(ipv4) / ne xt header 
(ipv6)> [,<destination port 
range> [,<source port 
range> [,<ipsec security 
parameter index 
(spi)> [,<type of service (tos) 
(ipv4) and mask / traffic 
class (ipv6) and 
mask> [,<flow label 
(ipv6)> ]]]]]]]]]  OK 
ERROR 
Execute Command  Responses  
AT+CGTFT  OK 
ERROR 
Defined values  
<cid>  
a numeric parameter which specifies a particular PDP context definition (see theAT+CGDCONT  
and AT+CGDSCONT  commands). 
<PDP_type> 
(Packet Data Protocol type) a string parameter which specifies the type of packet data prot ocol. 
IP   Internet Protocol 
SIMCom Confidential File
---

## Page 209

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 208 PPP   Point to Point Protocol  
IPV6  Internet Protocol Version 6 
IPV4V6  Dual PDN Stack  
<packet filter identifier>  
a numeric parameter, value range from 1 to 16. 
<evaluation precedence index> 
a numeric parameter. The value r ange is from 0 to 255. 
<source address and subnet mask>  
string type  The string is given as dot- separated numeric (0 -255) parameters on the form: 
"a1.a2.a3.a4.m1.m2.m3.m4" for IPv4 or 
"a1.a2.a3.a4.a5.a6.a7.a8.a9.a10.a11.a12.a13.a14.a15.a16.m1.m2.m3.m4.m5.m6.m7.m8.m9.m10.m1
1.m12.m13.m14.m15.m16", for IPv6.  
<protocol number (ipv4) / next header (ipv6)> 
a numeric parameter, value range from 0 to 255. 
<destination port range> 
string type. The string is given as dot- separated numeric (0 -65535) parameters on the form "f.t". 
<source port range>  
string type. The string is given as dot -separated numeric (0 -65535) parameters on the form "f.t".  
<ipsec security parameter index (spi)>  
numeric value in hexadecimal format. The value range is from 00000000 to FFFF FFFF.  
<type of service (tos) (ipv4) and mask / traffic class (ipv6) and mask>  
string type. The string is given as dot- separated numeric (0 -255) parameters on the form "t.m". 
<flow label (ipv6)>  
numeric value in hexadecimal format. The value range is fr om 00000 to FFFFF. Valid for IPv6 only. 
Examples 
AT+CGTFT?  
+CGTFT: 2,1,0,"74.125.71.99.255.255.255.255",0,0.0,0.0,0,0.0,0  
 
OK 
AT+CGTFT=2,1,0,"74.125.71.99.255.255.255.255" 
OK 
AT+CGTFT=?  
+CGTFT: "IP",(1 -2),(0 -255),,(0-255),(0-65535.0-65535),(0-65535.0-65535),(0- FFFFF 
FFF),(0 -255.0-255),(0- FFFFF)  
+CGTFT: "PPP",(1 -2),(0 -255),,(0-255),(0-65535.0-65535),(0-65535.0-65535),(0- FFFF 
FFFF),(0 -255.0-255),(0- FFFFF)  
+CGTFT: "IPV6",(1 -2),(0-255),,(0-255),(0-65535.0-65535),(0-65535.0-65535),(0- FFF 
FFFFF),(0 -255.0-255),(0 -FFFFF)  
+CGTFT:"IPV4V6",(1-16),(0-255),,(0-255),(0-65535.0-65535),(0-65535.0-65535),(0- FFFFFFFF)
,(0-255.0-255),(0- FFFFF)  
 
SIMCom Confidential File
---

## Page 210

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 209 OK 
9.7  AT+CGQREQ  Quality of service profile (requested)  
Description  
This command allows the TE to specify a Quality of Service Profile that is used when the MT sends 
an Activate PDP Context Request message to the network.. A special form of the set command 
(AT+CGQREQ =<cid>)  causes the requested profile for context number <cid>  to become 
undefined. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGQREQ=?  +CGQREQ: <PDP_type> , (list of supported <precedence> s), (list 
of supported <delay> s), (list of supported <reliability> s) , (list of 
supported <peak> s), (list of supported <mean> s) [<CR><LF> 
+CGQREQ: <PDP_type> , (list of supported <precedence> s), (list 
of supported <delay> s), (list of supported <reliability> s) , (list of 
supported <peak> s), (list of supported <mean> s) 
[…]] 
OK 
ERROR  
Read Command  Responses 
AT+CGQREQ?  +CGQREQ: [ <cid> , <precedence > , <delay> , <reliability> , 
<peak> , <mean> [<CR><LF>  
+CGQREQ: <cid> , <precedence > , <delay> , <reliability.> , <peak> , 
<mean> […]]]  
OK 
ERROR 
Write Command  Responses 
AT+CGQREQ=<cid> [,<prec
edence> [,<delay> [,<reliabilit
y>[,<peak> [,<mean> ]]]]] OK 
ERROR  
Execution Command Responses  
AT+CGQREQ  OK 
ERROR 
Defined values  
SIMCom Confidential File
---

## Page 211

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 210 <cid>  
A numeric parameter which specifies a particular PDP context definition (see AT+CGDCONT  
command). The range is from 1 to 24,100 to 179 
<PDP_type> 
(Packet Data Protocol type) a string parameter which  specifies the type of packet data protocol. 
IP   Internet Protocol 
PPP   Point to Point Protocol  
IPV6  Internet Protocol Version 6 
IPV4V6  Dual PDN Stack  
<precedence>  
A numeric parameter which specifies the precedence class:  
0  –  network subscribed value 
1  –  high priority 
2  –  normal priority 
3  –  low priority  
<delay>  
A numeric parameter which specifies the delay class:  
0  –  network subscribed value 
1  –  delay class 1  
2  –  delay class 2  
3  –  delay class 3  
4  –  delay class 4  
<reliability>  
A numeric parameter which specifies the reliability class:  
0  –  network subscribed value 
1  –  Non real -time traffic,error -sensitive application that cannot cope with data loss 
2  –  Non real -time traffic,error -sensitive application that can cope with infrequent data loss 
3  –  Non real -time traffic,error -sensitive application that can cope with data loss, GMM/- 
SM,and SMS  
4  –  Real-time traffic,error -sensitive application that can cope with data loss  
5  –  Real-time traffic error non -sensitive application that can cope with data loss 
<peak>  
A numeric parameter which specifies the peak throughput class:  
0  –  network subscribed value 
1  –  Up to 1000 (8 kbit/s) 
2  –  Up to 2000 (16 kbit/s) 
3  –  Up to 4000 (32 kbit/s) 
4  –  Up to 8000 (64 kbit/s) 
5  –  Up to 16000 (128 kbit/s) 
6  –  Up to 32000 (256 kbit/s) 
7  –  Up to 64000 (512 kbit/s) 
8  –  Up to 128000 (1024 kbit/s) 
9  –  Up to 256000 (2048 kbit/s) 
SIMCom Confidential File
---

## Page 212

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 211 <mean>  
A numeric parameter which specifies the mean throughput class:  
0   –  network subscribed value  
1   –  100 (~0.22 bit/s) 
2   –  200 (~0.44 bit/s) 
3   –  500 (~1.11 bit/s)  
4   –  1000 (~2.2 bit/s) 
5   –  2000 (~4.4 bit/s) 
6   –  5000 (~11.1 bit/s) 
7   –  10000 (~22 bit/s) 
8   –  20000 (~44 bit/s) 
9   –  50000 (~111 bit/s) 
10  –  100000 (~0.22 kbit/s) 
11  –  200000 (~0.44 kbit/s) 
12  –  500000 (~1.11 kbit/s) 
13  –  1000000 (~2.2 kbit/s) 
14  –  2000000 (~4.4 kbit/s) 
15  –  5000000 (~11.1 kbit/s)  
16  –  10000000 (~22 kbit/s) 
17  –  20000000 (~44 kbit/s) 
18  –  50000000 (~111 kbit/s) 
31  –  optimization  
Examples  
AT+CGQREQ?  
+CGQREQ:  
OK 
AT+CGQREQ=?  
+CGQREQ: "IP",(0 -3),(0 -4),(0 -5),(0 -9),(0 -18,31) 
+CGQREQ: "PPP",(0 -3),(0 -4),(0 -5),(0 -9),(0 -18,31) 
+CGQREQ: "IPV6",(0 -3),(0 -4),(0 -5),(0 -9),(0 -18,31) 
+CGQREQ: "IPV4V6",(0 -3),(0- 4),(0 -5),(0 -9),(0 -18,31) 
 
OK 
9.8  AT+CGEQREQ  3G quality of service profile (requested)  
Description  
The test command returns values supported as a compound value. 
The read command returns the current settings for each defined context for which a QOS was 
explicitly specified.  
The write command all ows the TE to specify a Quality of Service Profile for the context identified 
SIMCom Confidential File
---

## Page 213

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 212 by the context identification parameter <cid> which is used when the MT sends an Activate PDP 
Context Request message to the network. 
A special form of the write command, AT+CGEQ REQ =<cid>  causes the requested profile for 
context number <cid>  to become undefined. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGEQREQ=?  +CGEQREQ: <PDP_type> ,(list of supported <Traffic class> s),(list 
of supported <Maximum bitrate UL> s),(list of supported 
<Maximum bitrate DL> s),(list of supported <Guaranteed bitrate 
UL> s,(list of supported  <Guaranteed bitrate DL> s),(list of 
supported <Deliv  ery order> s),(list of supported <Maximum SDU 
size> s),(list of supported <SDU error ra tio>s),(list of supported 
<Residual bit error  Ratio> s),(list of supported <Delivery of 
erroneous SDUs> s),(list of Supported <Transfer delay> s),(list of 
supported <Traffic handling  priority> s),(list of supported <Source 
statistics descriptor> s),(list of sup ported <Signaling indication 
flag> s) 
OK 
ERROR 
Read Command  Responses 
AT+CGEQREQ?  +CGEQREQ: [ <cid> ,<Traffic class> ,<Maximum bitrate UL> , 
<Maximum bitrate DL> ,<Guaranteed bitrate UL> ,<Guaranteed 
bitrate  DL> ,<Delivery order> ,<Maximum SDU size> ,<SDU error 
ratio> ,<Residual bit error ratio> ,<Delivery of erroneous SDUs> , 
<Transfer Delay> ,<Traffic handling priority> ,<Source statistics 
descriptor> ,< Signaling indication flag> ][<CR><LF>+CGEQREQ: 
<cid> ,<Traffic class> ,<Maximum bitrate UL> ,<Ma ximum bitrate 
DL> ,<Gua ranteed bitrate UL> ,<Guaranteed bitrate  DL> ,<Delivery 
order> ,<Maximum SDU size> ,<SDU error ratio> ,<Residual bit 
error ratio> ,<Delivery of erroneous SDUs> ,<Transfer Delay> , 
<Traffic handling priority> ,<Source statistics descriptor> , 
<Signaling indication fl ag> […]]  
OK 
ERROR 
Write Command  Responses 
SIMCom Confidential File
---

## Page 214

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 213 AT+CGEQREQ= <cid> [,<Tr
affic class> [,<Maximum bit
rate UL >[,<Maximum bitrat
e DL >[,<Guaranteed bitrate
 UL>[,<Guaranteed bitrate 
DL>[,<Delivery order> [,<M
aximum SDU size> [,<SDU
 error ratio> [,<Residual bit
 error rati o>[,<Delivery of 
erroneous SDUs> [,<Transfe
r delay> [,<Traffic handling
 priority> [,<Source statistic
s descriptor> [,<Signaling in
dication flag> ]]]]]]]]]]]]]]  OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses  
AT+CGEQREQ  OK 
ERROR 
Defined values  
<cid> 
Parameter specifies a particular PDP context definition.The parameter is also used in other PDP 
context- related commands. The range is from 1 to 24,100 to 179 
<Traffic class>  
0  –  conversational  
1  –  streaming  
2  –  interactive  
3  –  background 
4  –  subscribed value 
<Maximum bitrate UL>  
This parameter indicates the maximum number of kbits/s delivered to UMTS(up- link traffic)at a 
SAP. As an example a bitrate of 32kbit/s would be specified as 32(e.g. AT+CGEQREQ =…,32,…).  
The range is from 0 to 115 20. The default value is 0. If the parameter is set to '0' the subscribed 
value will be requested.  
<Maximum bitrate DL>  
This parameter indicates the maximum number of kbits/s delivered to UMTS(down- link traffic)at a 
SAP.As an example a bitrate of 32kbit/s would be specified as 32(e.g. AT+CGEQREQ =…,32,…).  
The range is from 0 to 42200 . The default value is 0. If the parameter is set to '0' the subscribed 
value will be requested.  
<Guaranteed bitrate UL>  
This parameter indicates the guaranteed number of kb it/s delivered to UMTS(up -link traffic)at a 
SAP(provided that there is data to deliver).As an example a bitrate of 32kbit/s would be specified as 
SIMCom Confidential File
---

## Page 215

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 214 32(e.g. AT+CGEQREQ =…,32,…). 
The range is from 0 to 11520. The default value is 0. If the parameter is set to '0 ' the subscribed 
value will be requested.  
<Guaranteed bitrate DL>  
This parameter indicates the guaranteed number of kbit/s delivered to UMTS(down- link traffic)at a 
SAP(provided that there is data to deliver).As an example a bitrate of 32kbit/s would be s pecified as  
32(e.g. AT+CGEQREQ =…,32,…). 
The range is from 0 to 42200 . The default value is 0. If the parameter is set to '0' the subscribed 
value will be requested.  
<Delivery order>  
This parameter indicates whether the UMTS bearer shall provide in -sequence SDU delivery or not.  
0   –  no 
1   –  yes 
2   –  subscribed value 
<Maximum SDU size>  
This parameter indicates the maximum allowed SDU size in octets.  
The range is from 0 to 1520. The default value is 0. If the parameter is set to '0' the subscribed val ue 
will be requested.  
<SDU error ratio>  
This parameter indicates the target value for the fraction of SDUs lost or detected as erroneous.SDU 
error ratio is defined only for conforming traffic.As an example a target SDU error ratio of 5*10-3 
would be specified as “5E3”(e.g.AT+CGEQREQ=..,”5E3”,…).  
“0E0”   –  subscribed value 
“1E2” 
“7E3” 
“1E3” 
“1E4” 
“1E5” 
“1E6” 
“1E1” 
<Residual bit error ratio>  
This parameter indicates the target value for the undetected bit error ratio in the delivered SDUs. If 
no error det ection is requested,Residual bit error ratio indicates the bit error ratio in the delivered 
SDUs.As an example a target residual bit error ratio of 5*10-3 would be specified as “5E3”(e.g. 
AT+CGEQREQ=…,”5E3”,..). 
    “0E0”   –  subscribed value  
“5E2”   
“1E2” 
“5E3” 
“4E3” 
“1E3” 
“1E4” 
“1E5” 
SIMCom Confidential File
---

## Page 216

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 215 “1E6” 
“6E8”  
<Delivery of erroneous SDUs>  
This parameter indicates whether SDUs detected as erroneous shall be delivered or not.  
0  –  no 
1  –  yes  
2  –  no detect  
3  –  subscribed value 
<Transfer delay>  
This parameter ind icates the targeted time between request to transfer an SDU at one SAP to its 
delivery at the other SAP,in milliseconds.  
The range is 0 and from 100 to 4000. The default value is 0. If the parameter is set to '0' the 
subscribed value will be requested. 
<Traffic handling priority>  
This parameter specifies the relative importance for handling of all SDUs belonging to the UMTS  
Bearer compared to the SDUs of the other bearers.  
The range is from 0 to 3. The default value is 0. If the parameter is set to '0' the subscribed value 
will be requested.  
<Source statistics descriptor > 
This parameter indicates profile parameter that Source statistics descriptor for requested UMTS 
QoS  
The range is from 0 to 1. The default value is 0. If the parameter is set to '0' the subscribed value 
will be requested.  
<Signaling indication flag > 
This parameter indicates Signaling flag. 
The range is from 0 to 1 The default value is 0. If the parameter is set to '0' the subscribed value will 
be requested.  
<PDP_type> 
(Packet Data P rotocol type) a string parameter which specifies the type of packet data protocol. 
IP   Internet Protocol 
PPP   Point to Point Protocol  
IPV6  Internet Protocol Version 6 
IPV4V6  Dual PDN Stack  
Examples 
AT+CGEQREQ?  
+CGEQREQ:  
OK 
AT+CGEQREQ=?  
+CGEQREQ: "I P",(0 -4),(0 -11520 ),(0-42200 ),(0-1152 0),(0-42200 ),(0-2),(0 -1520),("0E0","1E  
1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E 
4","1E5","1E6","6E8"),(0-3),(0,100-4000),(0- 3) ,(0 -1),(0-1) 
SIMCom Confidential File
---

## Page 217

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 216 +CGEQREQ: "PPP",(0 -4),(0- 1152 0),(0 -42200),(0 -11520 ),(0-42200),(0 -2),(0 -1520),("0E0","1 
E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1 
E4","1E5","1E6","6E8"),(0-3),(0,100-4000),(0- 3) ,(0 -1),(0 -1) 
+CGEQREQ: "IPV6",(0 -4),(0- 1152 0),(0 -42200),(0 -11520 ),(0-42200),(0 -2),(0 -1520),("0E0"," 
1E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3"," 
1E4","1E5","1E6","6E8"),(0- 3),(0 ,100-4000),(0- 3) ,(0 -1),(0 -1) 
+CGEQREQ:"IPV4V6",(0 -4),(0 -11520),(0 -42200),(0 -1152 0),(0 -42200),(0 -2),(0 -1520),("0E0","1E1
","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E4","1E5","1
E6","6E8"),(0-3),(0,100-4000),(0- 3),(0 -1),(0 -1) 
 
OK 
9.9  AT+CGQMIN  Quality of service profile (minimum acceptable)  
Description  
This command allows the TE to specify a mini mum acceptable profile which is checked by the MT 
against the negotiated profile returned in the Activate PDP Context Accept message.A special form 
of the set command,AT+CGQMIN =<cid>  causes the minimum acceptable profile for context 
number <cid>  to become undefined. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGQMIN=?  +CGQMIN: <PDP_type> , (list of supported <precedence> s), (list 
of supported <delay> s), (list of supported  <reliability> s) , (list of 
supported <peak> s), (list of supported <mean> s) [<CR><LF> 
+CGQMIN: <PDP_type> , (list of supported <precedence> s), (list 
of supported <delay> s), (list of supported <reliability> s) , (list of 
supported <peak> s), (list of supported <mean> s)[…]]  
OK 
ERROR 
Read Command  Responses 
AT+CGQM IN? +CGQMIN: [ <cid> , <precedence > , <delay> , <reliability> , 
<peak> , <mean> [<CR><LF>  
+CGQMIN: <cid> , <precedence > , <delay> , <reliability.> , <peak> , 
<mean>  
[…]]]  
OK 
ERROR  
SIMCom Confidential File
---

## Page 218

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 217 Write Command  Responses  
AT+CGQMIN= <cid> [,<prec
edence> [,<delay> [,<reliabilit
y>[,<peak> [,<mean> ]]]]] OK 
ERROR 
Execution Command Responses  
AT+CGQMIN  OK 
ERROR  
Defined values  
<cid>  
A numeric parameter which specifies a particular PDP context definition (see AT+CGDCONT  
command). The range is from 1 to 24,100 to 179.  
<PDP_type> 
(Packet Data Protocol type) a string parameter which specifies the type of packet data protocol.  
IP   Internet Protocol 
PPP   Point to Point Protocol  
IPV6  Internet Protocol Version 6 
IPV4V6  Dual PDN Stack  
<precedence>  
A numeric parameter which specifies the precedence class:  
0  –  network subscribed value 
1  –  high priority 
2  –  normal priority 
3  –  low priority  
<delay>  
A numeric parameter which specifies the delay class:  
0  –  network subscribed value 
1  –  delay class 1  
2  –  delay class 2  
3  –  delay class 3  
4  –  delay class 4  
<reliability>  
A numeric parameter which specifies the reliability class:  
0  –  network subscribed value 
1  –  Non real -time traffic,error -sensitive application that cannot cope with data loss  
2  –  Non real -time traffic,err or-sensitive application that can cope with infrequent data loss 
3  –  Non real -time traffic,error -sensitive application that can cope with data loss, GMM/- 
SM,and SMS  
4  –  Real-time traffic,error -sensitive application that can cope with data loss  
5  –  Real-time traffic error non -sensitive application that can cope with data loss  
<peak>  
SIMCom Confidential File
---

## Page 219

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 218 A numeric parameter which specifies the peak throughput class:  
0  –  network subscribed value 
1  –  Up to 1000 (8 kbit/s) 
2  –  Up to 2000 (16 kbit/s) 
3  –  Up to 4000 ( 32 kbit/s)  
4  –  Up to 8000 (64 kbit/s) 
5  –  Up to 16000 (128 kbit/s) 
6  –  Up to 32000 (256 kbit/s) 
7  –  Up to 64000 (512 kbit/s) 
8  –  Up to 128000 (1024 kbit/s) 
9  –  Up to 256000 (2048 kbit/s) 
<mean>  
A numeric parameter which specifies the mean thr oughput class: 
0   –  network subscribed value  
1   –  100 (~0.22 bit/s) 
2   –  200 (~0.44 bit/s) 
3   –  500 (~1.11 bit/s)  
4   –  1000 (~2.2 bit/s) 
5   –  2000 (~4.4 bit/s) 
6   –  5000 (~11.1 bit/s) 
7   –  10000 (~22 bit/s) 
8   –  20000 (~44 bit/s) 
9   –  50000 (~111 bit/s) 
10  –  100000 (~0.22 kbit/s) 
11  –   200000 (~0.44 kbit/s) 
12  –  500000 (~1.11 kbit/s) 
13  –  1000000 (~2.2 kbit/s) 
14  –  2000000 (~4.4 kbit/s) 
15  –  5000000 (~11.1 kbit/s)  
16  –  10000000 (~22 kbit/s) 
17  –  20000000 (~44 kbit/s) 
18  –  50000000 (~111 kbit/s) 
31  –  optimization  
Examples 
AT+CGQMIN?  
+CGQMIN:  
OK 
AT+CGQMIN=?  
+CGQMIN: "IP",(0 -3),(0 -4),(0 -5),(0 -9),(0 -18,31)  
+CGQMIN: "PPP",(0 -3),(0 -4),(0 -5),(0 -9),(0 -18,31) 
+CGQMIN: "IPV6",(0 -3),(0 -4),(0 -5),(0 -9),(0 -18,31) 
SIMCom Confidential File
---

## Page 220

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 219 +CGQMIN: "IPV4V6 ",(0-3),(0 -4),(0 -5),(0 -9),(0 -18,31) 
 
OK 
9.10  AT+CGEQMIN  3G quality of service profile (minimum acceptable)  
Description  
The test command returns values supported as a compound value. 
The read command returns the current settings for each defined context for w hich a QOS was 
explicitly specified.  
The write command allow the TE to specify a Quallity of Service Profile for the context identified by the context identification parameter  <cid>  
which is checked by the MT against the negotiated 
profile returned in the Activate/Modify PDP Context Accept message.  
A special form of the write command, AT+CGEQMIN =<cid>  causes the requested for context 
number <cid>  to become undefined.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CGEQMIN=?  +CGEQM IN: <PDP_type> ,(list of supported <Traffic class> s),(list 
of supported <Maximum bitrate UL> s),(list of supported 
<Maximum bitrate DL> s),(list of supported <Guaranteed bitrate 
UL> s,(list of supported  <Guaranteed bitrate DL> s),(list of 
supported <Deliv  ery o rder> s),(list of supported <Maximum SDU 
size> s),(list of supported <SDU error ratio> s),(list of supported 
<Residual bit error  Ratio> s),(list of supported <Delivery of 
erroneous SDUs> s),(list of Supported <Transfer delay> s),(list of 
supported <Traffic handl ing priority> s),(list of supported <Source 
statistics descriptor> s),(list of supported <Signaling indication 
flag> s) 
OK 
ERROR 
Read Command  Responses 
AT+CGEQMIN?  +CGEQMIN: [ <cid> ,<Traffic class> ,<Maximum bitrate UL> , 
<Maximum bitrate DL> ,<Guaranteed bitrate UL> ,<Guaranteed 
bitrate  DL> ,<Delivery order> ,<Maximum SDU size> ,<SDU error 
ratio> ,<Residual bit error ratio> ,<Delivery of erroneous SDUs> , 
<Transfer Delay> ,<Traffic handling priority> ,<Source statistics 
descriptor> ,< Signaling indication flag> ][<CR><L F>+CGEQMIN: 
SIMCom Confidential File
---

## Page 221

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 220 <cid> ,<Traffic class> ,<Maximum bitrate UL> ,<Maximum bitrate 
DL> ,<Guaranteed bitrate UL> ,<Guaranteed bitrate  DL> ,<Delivery 
order> ,<Maximum SDU size> ,<SDU error ratio> ,<Residual bit 
error ratio> ,<Delivery of erroneous SDUs> ,<Transfer Delay> , 
<Tra ffic handling priority> ,<Source statistics descriptor> , 
<Signaling indication flag> […]]  
OK 
ERROR 
Write Command  Responses 
AT+CGEQMIN= <cid> [,<Tr
affic class> [,<Maximum bit
rate UL >[,<Maximum bitrat
e DL >[,<Guaranteed bitrate
 UL>[,<Guaranteed bitrate 
DL>[,<Delivery order> [,<M
aximum SDU size> [,<SDU
 error ratio> [,<Residual bit
 error ratio> [,<Delivery of 
erroneous SDUs> [,<Transfe
r delay> [,<Traffic handling
 priority> [,<Source statistic
s descriptor> [,<Signaling in
dication flag> ]]]]]]]]]]]]]]  OK 
ERROR  
+CME ERRO R: <err>  
Execution Command Responses  
AT+CGEQMIN  OK 
ERROR 
Defined values  
<cid>  
Parameter specifies a particular PDP context definition.The parameter is also used in other PDP 
context- related commands. The range is from 1 to 24,100 to 179. 
<Traffic cl ass> 
0  –  conversational  
1  –  streaming  
2  –  interactive  
3  –  background 
4  –  subscribed value 
<Maximum bitrate UL>  
This parameter indicates the maximum number of kbits/s delivered to UMTS(up- link traffic)at a 
SAP.As an example a bitrate of 32kbit/s would be specified as 32(e.g. A T+CGEQMIN =…,32,…).  
The range is from 0 to 1152 0. The default value is 0. If the parameter is set to '0' the subscribed 
SIMCom Confidential File
---

## Page 222

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 221 value will be requested.  
<Maximum bitrate DL>  
This parameter indicates the maximum number of kbits/s delivered to UMTS(down -link traffic)at a 
SAP.As an example a bitrate of 32kbit/s would be specified as 32(e.g. A T+CGEQMIN =…,32,…).  
The range is from 0 to 42200 . The default value is 0. If the parameter is set to '0' the subscribed 
value will be requested.  
<Guaranteed bitrate UL>  
This parameter indicates the guaranteed number of kbit/s delivered to UMTS(up -link traffic)at a 
SAP(provided that there is data to deliver).As an example a bitrate of 32kbit/s would be specified as 
32(e.g. AT+CGEQMIN =…,32,…). 
The range is from 0 to 1152 0. The default value is 0. If the parameter is set to '0' the subscribed 
value will be requested.  
<Guaranteed bitrate DL>  
This parameter indicates the guaranteed number of kbit/s delivered to UMTS(down- link traffic)at a 
SAP(provided that there is data to deliver).As an example a bitrate of 32kbit/s would be specified as 
32(e.g. AT+CGEQMIN =…,32,…). 
The range is from 0 to 42200 . The default value is 0. If the parameter is set to '0' the subscribed 
value will be requested.  
<Delivery or der> 
This parameter indicates whether the UMTS bearer shall provide in -sequence SDU delivery or not. 
0  –  no 
1  –  yes  
2  –  subscribed value 
<Maximum SDU size>  
This parameter indicates the maximum allowed SDU size inoctets.  
The range is from 0 to 1520. The default value is 0. If the parameter is set to '0' the subscribed value 
will be requested.  
<SDU error ratio>  
This parameter indicates the target value for the fraction of SDUs lost or detected as erroneous.SDU 
error ratio is defined only for conforming traffic.As an example a target SDU error ratio of 5*10-3 
would be specified as “5E3”(e.g.A T+CGEQMIN =..,”5E3”,…). 
“0E0”   –  subscribed value 
“1E2” 
“7E3” 
“1E3” 
“1E4” 
“1E5” 
“1E6” 
“1E1” 
<Residual bit error ratio>  
This parameter indicates the target valu e for the undetected bit error ratio in the delivered SDUs. If 
no error detection is requested,Residual bit error ratio indicates the bit error ratio in the delivered 
SDUs.As an example a target residual bit error ratio of 5*10-3 would be specified as “5E3”(e.g.  
SIMCom Confidential File
---

## Page 223

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 222 AT+CGEQMIN =…,”5E3”,..). 
    “0E0”   –  subscribed value  
   “5E2”   
“1E2” 
“5E3” 
“4E3” 
“1E3” 
“1E4” 
“1E5” 
“1E6” 
“6E8” 
<Delivery of erroneous SDUs>  
This parameter indicates whether SDUs detected as erroneous shall be delivered or not.  
0  –  no 
1  –  ye s 
2  –  no detect  
3  –  subscribed value  
<Transfer delay>  
This parameter indicates the targeted time between request to transfer an SDU at one SAP to its 
delivery at the other SAP,in milliseconds.  
The range is 0 and from 100 to 4000. The default value is  0. If the parameter is set to '0' the 
subscribed value will be requested. 
<Traffic handling priority>  
This parameter specifies the relative importance for handling of all SDUs belonging to the UMTS  
Bearer compared to the SDUs of the other bearers.  
The range is from 0 to 3. The default value is 0. If the parameter is set to '0' the subscribed value 
will be requested.  
<Source statistics descriptor > 
This parameter indicates profile parameter that Source statistics descriptor for requested UMTS 
QoS  
The r ange is from 0 to 1. The default value is 0. If the parameter is set to '0' the subscribed value 
will be requested.  
<Signaling indication flag > 
This parameter indicates Signaling flag. 
The range is from 0 to 1 The default value is 0. If the parameter is set to '0' the subscribed value will 
be requested.  
<PDP_type> 
(Packet Data Protocol type) a string parameter which specifies the type of packet data protocol.  
IP   Internet Protocol 
PPP   Point to Point Protocol  
IPV6  Internet Protocol Version 6 
IPV4V6  Dual PDN Stack  
SIMCom Confidential File
---

## Page 224

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 223 Examples 
AT+CGEQMIN?  
+CGEQMIN:  
OK 
AT+CGEQMIN=?  
+CGEQMIN: "IP",(0 -4),(0 -11520),(0 -42200),(0 -115200),(0 -42200),(0 -2),(0 -1520),("0E0","1E 
1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E 
4","1E5","1E6","6E8") ,(0-3),(0,100-4000),(0- 3) ,(0 -1),(0-1) 
+CGEQMIN: "PPP",(0 -4),(0- 1152 0),(0 -42200),(0 -115200 ),(0-42200),(0 -2),(0 -1520),("0E0","1 
E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1 
E4","1E5","1E6","6E8"),(0- 3),(0 ,100-4000),(0- 3) ,(0 -1),(0 -1) 
+CGEQMIN: "IPV6",(0 -4),(0- 1152 0),(0 -42200),(0 -115200 ),(0-42200),(0 -2),(0 -1520),("0E0"," 
1E1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3"," 
1E4","1E5","1E6","6E8"),(0- 3),(0 ,100-4000),(0- 3) ,(0 -1),(0 -1) 
+CGEQMIN:"IP V4V6",(0- 4),(0 -11520),(0 -42200),(0 -115200),(0 -42200),(0 -2),(0 -1520),("0E0","1E
1","1E2","7E3","1E3","1E4","1E5","1E6"),("0E0","5E2","1E2","5E3","4E3","1E3","1E4","1E5","
1E6","6E8"),(0-3),(0,100-4000),(0- 3),(0 -1),(0 -1) 
 
OK 
9.11  AT+CGDATA  Enter data state  
Description  
The command causes the MT to perform whatever actions are necessary to establish 
communication between the TE and the network using one or more Packet Domain PDP types. This 
may include performing a PS attach and one or more PDP context activations. The command  is not 
used in CDMA/EVDO mode. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CGDATA=?  +CGDATA: (list of supported <L2P> s) 
OK 
ERROR 
Write Command  Responses 
AT+CGDATA=[ <L2P> ,[<ci
d>]] CONNECT [ <text> ] 
NO CARRIER  
OK 
SIMCom Confidential File
---

## Page 225

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 224 ERROR  
+CME ERROR: <err>  
Defined values  
<L2P>  
A string parameter that indicates the layer 2 protocol to be used between the TE and MT. 
PPP  Point- to-point protocol for a PDP such as IP 
<text>  
CONNECT result code string; the string formats plea se refer ATX/AT \V/AT&E command.  
<cid>  
A numeric parameter which specifies a particular PDP context definition (see AT +CGDCONT  
command). 
1…24,100…179 
Examples 
AT+CGDATA=?  
+CGDATA: ("PPP")  
OK 
AT+CGDATA="PPP",1  
CONNECT 115200  
9.12  AT+CGPADDR  Show PDP addr ess 
Description  
The write command returns a list of PDP addresses for the specified context identifiers.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGPADDR=?  [+CGPADDR: (list of defined <cid> s)] 
OK 
ERROR 
Write Command  Responses 
AT+CGPADDR= 
<cid> [,<cid> [,…]]  [+CGPADDR: <cid> ,<PDP_addr> [<CR><LF> 
+CGPADDR: <cid> ,<PDP_addr> [...]]]  
OK 
SIM card supports IPV4V6 type and the PDP_type of the command 
SIMCom Confidential File
---

## Page 226

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 225 “at+cgdcont” defined  is  ipv4v6 :  
[+CGPADDR: <cid> ,<PDP_addr_IPV4>,<PDP_addr_IPV 6>] 
+CGPADDR: <cid> ,<PDP_addr_IPV4>,<PDP_addr_IPV6>  [...]]]  
OK 
ERROR 
+CME ERROR: <err>  
Execution Command  Responses  
AT+CGPADDR  [+CGPADDR: <cid> ,<PDP_addr> ] 
+CGPADDR: <cid> ,<PDP_addr> [...]]]  
OK 
SIM card supports IPV4V6 type and the PDP_type of the command 
“at+cgdcont” defined  is  ipv4v6 :  
[+CGPADDR: <cid> ,<PDP_addr_IPV4>,<PDP_addr_IPV6> ] 
+CGPADDR: <cid> ,<PDP_addr_IPV4>,<PDP_addr_IPV6>  [...]]]  
OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<cid>  
A numeric parameter which specifies a particular PDP co ntext definition (see AT+CGDCONT  
command). If no <cid> is specified, the addresses for all defined contexts are returned. 
1…24,100…179  
<PDP_addr> 
A string that identifies the MT in the address space applicable to the PDP. The address may be static 
or dynamic. For a static address, it will be the one set by the AT+CGDCONT  command when the 
context was defined. For a dynamic address it will be the one assigned during the last PDP context 
activation that used the context definition referred to by <cid> . <PDP_ addr>  is omitted if none is 
available.  
<PDP_addr_IPV4> 
A string parameter that identifies the MT in the address space applicable to the PDP.  
<PDP_addr_IPV6> 
A string parameter that identifies the MT in the address space applicable to the PDP when the 
sim_card supports ipv6. The pdp type  must be set to “ipv6” or “ipv4v6” by the AT+CGDCONT  
command. 
Examples 
AT+CGP ADDR =?  
+CGP ADDR: (1)  
OK 
SIMCom Confidential File
---

## Page 227

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 226 AT+CGP ADDR=1  
+CGDCONT: 1,"IPV4V6","","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0,0,0  
 
OK 
AT+CGP ADDR  
+CGP ADDR: 1,10.195.1.140,36.9.136.148.128.48.134.218.173.205.47.44.88.174.123.200 
+CGP ADDR: 2,10.195.34.92,36.9.136.148.128.48.146.115.92.140.135.230.248.131.5.90 
+CGP ADDR: 3,0.0.0.0,0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0 
 
OK 
9.13  AT+CGCLASS   GPRS mobile station class 
Description  
This command is used to set the MT to operate according to the specified GPRS mobile class. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses  
AT+CGCLASS=?  +CGCLASS: (list of supported <class> s) 
OK 
ERROR 
Read Command  Responses 
AT+CG CLASS?  +CGCLASS:  <class>  
OK 
ERROR 
Write Command  Responses 
AT+CGCLASS= <class>  OK 
ERROR 
+CME ERROR: <err>  
Execution Command Responses  
AT+CGCLASS  Set default value:  
OK 
ERROR 
Defined values  
<class>  
A string parameter which indicates the GPRS mobile class (in descending order of functionality) 
SIMCom Confidential File
---

## Page 228

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 227 A  –  class A (highest)  
Examples 
AT+CGCLASS=?  
+CGCLASS: ("A")  
OK 
AT+CGCLASS?  
+CGCLASS: "A"  
OK 
9.14  AT+CGEREP  GPRS event reporting  
Description  
The write command enables or disables sending of unsolicited result codes, “+CGEV”  from MT to 
TE in the case of certain events occurring in the Packet Domain MT or the network. <mode>  
controls the processing of  unsolicited result codes specified within this command. <bfr>  controls 
the effect on buffered codes when <mo de> 1 or 2 is entered. If a setting is not supported by the MT, 
ERROR or +CME ERROR: is returned.  
Read command returns the current  <mode>  and buffer settings. 
Test command returns the modes and buffer settings supported by the MT as compound values. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CGEREP=?  +CGEREP: (list of supported <mode> s),(list of supported <bfr> s) 
OK 
ERROR  
Read Command  Responses  
AT+CGEREP?  +CGEREP: <mode> ,<bfr>  
OK 
ERROR 
Write Command  Responses 
AT+CGEREP=  
<mode> [,<bfr> ] OK 
ERROR  
+CME ERROR: <err>  
Execution Command Responses  
AT+CGEREP OK 
ERROR 
SIMCom Confidential File
---

## Page 229

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 228 Defined values  
<mode> 
0  –  buffer unsolicited result codes in the MT; if MT result code buffer is full, the oldest 
ones can be discarded. No codes are fo rwarded to the TE. 
1  –  discard unsolicited result codes when MT -TE link is reserved (e.g. in on- line data 
mode); otherwise forward them directly to the TE. 
2  –  buffer unsolicited result codes in the MT when MT -TE link is reserved (e.g. in on- line 
data mode) and flush them to the TE when MT -TE link becomes available; otherwise 
forward them directly to the TE.  
<bfr>  
0  –  MT buffer of unsolicited result codes defined within this command is cleared when 
<mode>  1 or 2 is entered. 
1  –  MT buffer of unsolicited result codes defined within this command is flushed to the TE 
when  <mode>  1 or 2 is entered (OK response shall be given before flushing the codes). 
The following unsolicited result codes and the corresponding events are defined:  
+CGEV: REJECT <PDP_t ype> , <PDP_addr>  
A network request for PDP context activation occurred when the MT was unable to 
report it to the TE with a +CRING unsolicited result code and was automatically 
rejected.  
+CGEV: NW REACT  <PDP_type> , <PDP_addr> , [<cid> ] 
The network has requested a context reactivation. The <cid> that was used to reactivate 
the context is provided if known to the MT. 
+CGEV: NW DEACT  <PDP_type> , <PDP_addr> , [<cid> ] 
The network has forced a context deactivation. The <cid> that was used to activate the 
context is provided if known to the MT. 
+CGEV: ME DEACT  <PDP_type> , <PDP_addr> , [<cid> ] 
The mobile equipment has forced a context deactivation. The <cid> that was used to 
activate the context is provided if known to the MT. 
+CGEV: NW DETACH 
The network has forced a Packet Domain detach. This implies that all active contexts 
have been deactivated. These are not reported separately.  
+CGEV: ME DETACH  
The mobile equipment has forced a Packet Domain detach. This implies that all active 
contexts have been deactivated. These are not reported separately.  
+CGEV: NW CLASS <class>  
The network has forced a change of MS class. The highest available class is reported 
(see AT+CGCLASS ). 
+CGEV: ME CLASS  <class>  
The mobile equipment has forced a change of MS class. The highest avail able class is 
reported (see A T+CGCLASS ). 
Examples 
SIMCom Confidential File
---

## Page 230

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 229 AT+CGEREP=?  
+CGEREP: (0 -2),(0 -1) 
OK 
AT+CGEREP?  
+CGEREP: 0,0  
OK 
9.15  AT+CGAUTH  Set type of authentication for PDP-IP connections of 
GPRS  
Description  
This command is used to set type of authentication for PDP-IP connections of GPRS. 
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses  
AT+CGAUTH=?  +CGAUTH :, ,127 ,127 (for CDMA1x -EvDo only)  
+CGAUTH:(range of supported <cid> s),(list of supported <auth _- 
type>  s),127,127 
(NOTE: the first line of the r esponse is for CDMA 1x and Evdo 
only) 
OK 
ERROR 
+CME ERROR: <err>  
Read Command  Responses 
AT+CGAUTH?  [+CGAUTH: ,," user ","passwd " (for CDMA1x -EvDo only )] 
+CGAUTH:[ <cid> ,<auth_type> [,<user> ,<passwd> ]]<CR><LF>  
… 
OK 
ERROR  
+CME ERROR: <err>  
Write Com mand  Responses 
AT+CGAUTH= <cid> [,<aut
h_type> [,<passwd> [,<user> ]
]] OK 
ERROR 
AT+CGAUTH= ,,<user> ,<pa
SIMCom Confidential File
---

## Page 231

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 230 sswd>  (for 
CDMA1x -EvDo)  +CME ERROR: <err>  
Execution Command  Responses  
AT+CGAUTH OK 
ERROR 
+CME ERROR: <err>  
Defined values  
<cid>  
Parameter specif ies a particular PDP context definition. This is also used in other PDP 
context- related commands.  
1…24,100…179 
<auth_type>  
Indicate the type of authentication to be used for the specified context. If CHAP is selected another 
parameter <passwd>  needs to be specified. If PAP is selected two additional parameters <passwd>  
and <user>  need to specified.  
0  –  none 
1  –  PAP 
2  –  CHAP  
3  –  PAP or CHAP  
<passwd>  
Parameter specifies the password used for authentication.  
<user>  
Parameter specifies the user name used for authentication.  
Examples 
AT+CGAUTH=?  
+CGAUTH: ,,127,127(for CDMA1x-EvDo only) 
+CGAUTH: (1 -24,100- 179),(0-3),127,127 
 
OK 
AT+CGAUTH=1,1,”123”,”SIMCOM”  
OK 
SIMCom Confidential File
---

## Page 232

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 231 10  Hardware Related Commands  
10.1  AT+CV ALARM  Low and high voltage Alarm 
Description  
This co mmand is used to open or close the low voltage alarm function. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CVALARM=?  +CVALARM: (list of supported <enable> s), (list of supported <  
<low voltage> s), (list of supported high < high voltage> s) 
OK 
Read Command  Responses  
AT+CVALARM?  +CVALARM : <enable> ,<low voltage>, <high voltage>  
OK 
Write Command  Responses 
AT+CVALARM= <enable>[,<l
ow voltage>],[<high voltage>]  OK 
ERROR  
Defined values  
<enable>  
0  –  Close  
1  –  Open. If voltage < < low v oltage> , it will report “UNDER -VOLTAGE W ARNNING”  
every 10s. If voltage > <high voltage>, it will report  “OVER -VOLTAGE 
WARNNING” every 10s.  
<low voltage>  
Between 3300mV and 4000mV. Default value is 3300. 
<high voltage>  
Between 4000mV and 4300mV. Default  value is 4300.  
NOTE：The three parameters will be saved automatically.  
Examples 
AT+CVALARM=1,3400,4300  
OK 
SIMCom Confidential File
---

## Page 233

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 232 AT+CVALARM?  
+CVALARM:  1,3400,4300 
OK 
AT+CVALARM=?  
+CVALARM: (0,1),(3300 -4000),(4000 -4300)  
OK 
 
10.2  AT+CV AUXS  Set state of the pin named VREG_AUX1 
Description  
This command is used to set state of the pin which is named VREG_AUX1. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CVAUXS=?  +CVAUXS: (list of supported <state> s) 
OK 
Read Command  Responses 
AT+CVAUXS?  +CVAUXS: <state>  
OK 
Write Command  Responses  
AT+CVAUXS= <state>  OK 
ERROR 
Defined values  
<state>  
0  –  the pin is closed.  
1  –  the pin is opend(namely, open the pin) 
Examples 
AT+CVAUXS=1  
OK 
AT+CVAUXS?  
+CVAUXS: 1  
OK 
 
 
SIMCom Confidential File
---

## Page 234

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 233  
 
10.3  AT+CV AUXV  Set voltage value of the pin named VREG_AUX1 
Descrip tion 
This command is used to set the voltage value of the pin which is named VREG_AUX1. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CVAUXV=?  +CVAUXV: (list of supported <voltage> s) 
OK 
Read Command  Responses 
AT+CV AUXV?  +CVAUXV: <volt age>  
OK 
Write Command  Responses  
AT+CVAUXV=<voltage>  OK 
ERROR 
Defined values  
<voltage>  
Voltage value of the pin which is named VREG_AUX1. The unit is in mV. And the value must the 
multiple of 50mv. 
Examples 
AT+CVAUXV=?  
+CVAUXV: (1700 -3050)  
OK 
AT+CV AUXV=2800 
OK 
AT+CVAUXV?  
+CVAUXV: 2800  
OK 
  
SIMCom Confidential File
---

## Page 235

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 234 10.4  AT+CADC  Read ADC value  
Description  
This command is used to read the ADC value from modem. ME supports 2 types of ADC, which 
are raw type and voltage type.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CADC=?  +CADC: (range of supported <adc> s) 
OK 
Write Command  Responses  
AT+CADC= <adc>  +CADC: <value>  
OK 
ERROR 
Defined values  
<adc>  
ADC type:  
0  –  raw type.  
2  –  voltage type(mv)  
<value>  
Integer type value of the ADC.  
Examples 
AT+CADC= ? 
+CADC: (0,2) 
OK 
AT+CADC=0  
+CADC: 187 
OK 
 
 
10.5  AT+CADC2  Read ADC2 value  
Description  
SIMCom Confidential File
---

## Page 236

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 235 This command is used to read the ADC2 value from modem. ME supports 2 types of ADC, which 
are raw type and voltage type.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Comm and Responses  
AT+CADC2=?  +CADC2: (range of supported <adc> s) 
OK 
Write Command  Responses  
AT+CADC2= <adc>  +CADC2: <value>  
OK 
ERROR 
Defined values  
<adc>  
ADC2 type:  
0  –  raw type.  
2  –  voltage type(mv)  
<value>  
Integer type value of the ADC2.  
Examples 
AT+CADC2=?  
+CADC2: (0,2) 
OK 
AT+CADC2=0  
+CADC2: 187 
OK 
 
 
10.6  AT+CMTE  Control the module whether power shutdown when 
the module’s temperature upon the critical temperature  
Description  
This command is used to control the module whether power shutdown when  the module’s 
temperature upon the critical temperature  
SIMCom Confidential File
---

## Page 237

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 236 SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CMTE=?  +CMTE: (list of supported <on/off>s) 
OK 
Read Command  Responses  
AT+CMTE?  +CMTE: < on/off >  
OK 
Write Command  Responses 
AT+CMTE= <on/off >  OK 
ERROR 
Defined values  
<on/off> 
0  –  Disable temperature detection  
1  –  Enable temperature detection  
Examples 
AT+CMTE?  
+CMTE: 1  
OK 
AT+CMTE=1  
OK 
AT+CMTE=?  
+CMTE: 1  
OK 
NOTE:  
 When temperature is extreme high or low, product will power off.  
 URCs indicating the alert level “+CMTE:- 1” or “+CMTE:1” are intended to enable the user 
to take appropriate  
precaution, such as protect the module from exposure to extreme conditions, or save or back 
up data etc.  
 Level “+CMTE: -2”or “+CMTE:2” URCs a re followed by immediate shutdown. 
 
SIMCom Confidential File
---

## Page 238

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 237 10.7  AT+CPMVT  Low and high voltage Power Off  
Description  
This command is used to open or close the low and high voltage power off function. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CPMVT=?  +CPMVT: ( list of supported <enable> s), (list of supported < low 
voltage> s), (list of supported < high voltage> s) 
OK 
Read Command  Responses  
AT+CPMVT?  +CPMVT : <enable> ,<low voltage>, <high voltage>  
OK 
Write Command  Responses 
AT+CPMVT= <enable>[,<low 
voltage>],[<high voltage>]  OK 
ERROR  
Defined values  
<enable>  
0  –  Close  
1  –  Open. If voltage < < low voltage> , it will report “UNDER -VOLTAGE WARNNING 
POWER DOWN”  and power off the module. If voltage > <high voltage>, it will report 
“OVER -VOLTAGE WARNNING POWER DOW N” and power off the module 
<low voltage>  
Between 3200mV and 4000mV. Default value is 3200. 
<high voltage>  
Between 4000mV and 4300mV. Default value is 4300. 
Examples 
AT+CPMVT=1,3400,4300 
OK 
AT+CPMVT?  
+CPMVT:  1,3400,4300  
OK 
AT+CPMVT=?  
+CPMVT: (0 -1),(3200 -4000),(4000 -4300)  
SIMCom Confidential File
---

## Page 239

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 238 OK 
 
10.8  AT+CDELTA  Set the module go to recovery mode  
Description  
This command is used to set the module go to recovery mode. 
SIM PIN  References  
NO Vendor 
Syntax 
Write Command  Responses 
AT+CDELTA  OK 
ERROR  
Defined values  
NOTE：the command will write flag to the module and reboot the module, then the module will 
reboot and read the flag and enter recovery mode to update the firmware. 
Examples 
AT+CDELTA  
OK 
 
 
10.9  AT+CRIIC  Read values from register of IIC device  
Description  
This c ommand is used to read values from register of IIC device. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CRIIC=?  OK 
Write Command  Responses 
SIMCom Confidential File
---

## Page 240

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 239 AT+CRIIC= 
<addr>,<reg> ,<len>  +CRIIC: <data>  
OK 
ERROR  
Defined values  
<addr> 
Device address.  Input format must be hex, such as 0xFF.  
<reg>  
Register address. Input format must be hex, such as 0xFF.  
<len>  
Read length. Range:1- 4; unit:byte.  
<data>  
Data read. Input f ormat must be hex, such as 0xFF. 
Examples  
AT+CRIIC=0x34, 0x0 2, 2 
+CRIIC: 0x01,0x5d 
OK 
10.10   AT+CWIIC  Write values to register of IIC device  
Description  
This command is used to write values to register of IIC device.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CWIIC=?  OK 
Write Command  Responses 
AT+CWIIC=  
<addr> ,<reg> ,<data> ,<len>  OK 
ERROR 
Defined values  
<addr> 
Device address. Input format must be hex, such as 0xFF.  
<reg>  
Register address. Input format must be hex, such as 0xFF.  
SIMCom Confidential File
---

## Page 241

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 240 <len>  
Read length. Range: 1 -4; unit: byte.  
<data>  
Data written. Input format must be hex, such as 0xFF – 0xFFFFFFFF.  
Examples 
AT+CWIIC=0x34, 0x0 3, 0x5d, 1  
OK 
10.11   AT+CBC  Read the voltage value of the power supply  
Description  
This command is used to read the voltage value of the power supply 
SIM PIN  References  
NO Vendor 
Syntax 
Read Command  Responses 
AT+CBC  +CBC:  <vol>  
OK 
ERROR  
Defined values  
<vol>  
The voltage value, such as 3.8. 
Examples 
AT+CBC  
+CBC: 3.591V 
OK 
10.12   AT+CPMUTEMP  Read the temperature of the module  
Description  
This command is used to read the temperature of the module 
SIM PIN  References  
NO Vendor 
SIMCom Confidential File
---

## Page 242

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 241 Syntax 
Read Command  Responses 
AT+CPMUTEMP  +CPMUTEMP : <temp>  
OK 
ERROR 
Defined values  
<temp>  
The Temperature value, such as 29.  
Examples 
AT+CPMUTEMP  
+CPMUTEMP: 29  
OK 
SIMCom Confidential File
---

## Page 243

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 242 11  AT Commands for SIM Application Toolkit  
11.1  AT+STIN  SAT Indication  
Description  
Every time the SIM Application issues a Proactive Command, via the ME, the TA will receive an 
indication. This indicates the type of Proactive Command issued. 
AT+STGI  must then be used by the TA to request the parameters of the Proactive Command from 
the ME. Upon receiving the +STGI  response from the ME, the TA must send AT+STGR  to confirm 
the execution of the Proactive Command and provide any required user response, e.g. a selected 
menu item.  
SIM PIN  References  
YES Vend or 
Syntax 
Test Command  Responses 
AT+STIN= ? OK 
Read Command  Responses  
AT+STIN ? +STIN: <cmd_id>  
 
OK 
Unsolicited Result Codes  
+STIN: <cmd_id>  
Proactive Command notification  
21   –   display text  
22   –   get inkey  
23   –   get input 
24   –   select item 
+STIN: 25  
Notification that SIM Application has returned to main menu. If user doesn’t do any action in 2 
minutes , application will return to main menu automatically. 
Defined values  
<cmd_id > 
21   –   display text  
22   –   get inkey  
SIMCom Confidential File
---

## Page 244

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 243 23   –   get input 
24   –  select item 
25   –   set up menu  
81   –   session end  (pdu mode only) 
0   –  none command 
Examples 
AT+STIN?  
+STIN: 24  
OK 
11.2  AT+STGI  Get SAT information  
Description  
Regularly this command is used upon receipt of an URC " +STIN " to request the parameters of  the 
Proactive Command. Then the TA is expected to acknowledge the  AT+STGI  response with 
AT+STGR  to confirm that the Proactive Command has been executed. AT+STGR  will also provide 
any user information, e.g. a selected menu item. The Proactive Command type value specifies to 
which " +STIN " the command is related.  
NOTE: Please check the format refered to AT+STKFMT  
SIM PIN  References  
YES Vendor  
Syntax 
Test Command  Responses 
AT+STGI= ? OK 
Write Command  Responses 
AT+ST GI=<cmd_id > PDU format 
+STGI: <cmd_id >,<tag>,<pdu_len >,<pdu_value > 
OK 
AT+ST GI=<cmd_id > NOT PDU format, listed below:  
If <cmd_id> =10: 
OK 
If <cmd_id> =21: 
+STGI:21,<prio> ,<clear_mode> ,<text_len> ,<text>  
OK 
If <cmd_id> =22: 
+STGI: 22,< rsp_format> ,< help> ,<text_len> ,<text>  
OK 
SIMCom Confidential File
---

## Page 245

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 244 If <cmd_id> =23:  
+STGI:23,<rsp_format> ,<max_len> ,<min_len> ,<help> ,<show> ,<t
ext_len> ,<text>  
OK 
If <cmd_id> =24: 
+STGI:24,<help> ,<softkey> ,<present> ,<title_len> ,<title> ,<item_n
um> 
+STGI:24,<item_id> ,<item_len> ,<item_data>  
[…] 
OK 
If <cmd_id> =25: 
+STGI:25,<help> ,<softkey> ,<title_len> ,<title> ,<item_num>  
+STGI:25,<item_id> ,<item_len> ,<item_data>  
[...] 
OK 
Defined values  
<cmd_id > 
21   –   display text  
22   –   get inkey  
23   –   get input 
24   –   select item 
25   –  set up menu  
<prio> 
Priority of display text  
0   –  Normal priori ty 
1   –  High priority 
<clear_mode>  
0   –  Clear after a delay  
1   –  Clear by user  
<text_len>  
Length of text 
<rsp_format>  
0   –  SMS default alphabet  
1   –  YES or NO  
2   –  numerical only 
3   –  UCS2 
<help>  
0   –  Help unavailable  
1   –  Help av ailable  
<max_len>  
Maximum length of input 
SIMCom Confidential File
---

## Page 246

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 245 <min_len> 
Minimum length of input  
<show>  
0   –  Hide input text 
1   –  Display input text 
<softkey>  
0   –  No softkey preferred  
1   –  Softkey preferred  
<present>  
Menu presentation format available for select item 
0   –  Presentation not specified  
1   –  Data value presentation 
2   –  Navigation presentation  
<title_len>  
Length of title  
<item_num> 
Number of items in the menu  
<item_id>  
Identifier of item 
<item_len>  
Length of item 
<title>  
Title in u cs2 format  
<item_data>  
Content of the item in ucs2 format 
<text>  
Text in ucs2 format.  
<tag>  
Not used now. 
<pdu_len> 
Integer type, pdu string length 
<pdu_value>  
String type, the pdu string.  
Examples 
AT+STGI=25  (NOT PDU format)  
+STGI:25,0,0,10,"7 95E5DDE884C59295730",15  
+STGI:25,1,8,"8F7B677E95EE5019" 
+STGI:25,2,8,"77ED4FE17FA453D1" 
+STGI:25,3,8,"4F1860E05FEB8BAF" 
+STGI:25,4,8,"4E1A52A17CBE9009" 
+STGI:25,5,8,"8D448D3963A88350" 
SIMCom Confidential File
---

## Page 247

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 246 +STGI:25,6,8,"81EA52A9670D52A1" 
+STGI:25,7,8,"8F7B677E5F6994C3" 
+STGI:25 ,8,8,"8BED97F367425FD7" 
+STGI:25,9,10,"97F34E506392884C699C" 
+STGI:25,10,8,"65B095FB59296C14" 
+STGI:25,11,8,"94C358F056FE7247" 
+STGI:25,12,8,"804A59294EA453CB" 
+STGI:25,13,8,"5F005FC34F1195F2" 
+STGI:25,14,8,"751F6D3B5E388BC6" 
+STGI:25,21,12,"00530049004D53614FE1606F"  
OK 
AT+STGI=24  (PDU format)  
+STGI:24,0,48,"D02E81030124008202818285098070ED70B963A883508F0A018053057F574E0
78C618F0C02809177917777ED6D88606F" 
OK 
11.3  AT+STGR  SAT respond  
Description  
The TA is expected to acknowledge the AT+STG I  response with AT +STGR  to confirm that the 
Proactive Command has been executed. AT+STG R  will also provide any user information, e.g. a 
selected menu item.  
NOTE: Please check the format refered to AT+STKFMT  
SIM PIN  References  
YES Vendor  
Syntax 
Test Command  Responses 
AT+ STGR= ? OK 
Write Command  Responses 
AT+STGR= <cmd_id> [,<dat
a>] NOT PDU format  
OK 
AT+STGR= <pdu_len>,<pdu
_value>  PDU format  
OK 
Defined values  
<cmd_id> 
22   –   get inkey  
23   –   get input 
SIMCom Confidential File
---

## Page 248

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 247 24   –   select item 
25   –   set up menu  
81   –   session end  
83   –   session end by user 
84   –   go backward  
<data>  
If <cmd_id> =22: 
Input a character  
If <cmd_id> =23: 
Input a string.  
If <rsp_format>  is YES or NO, input of a character in case of ANSI character set requests one 
byte, e.g. “Y”. 
If <rsp_format>  is numerical on ly, input the characters in decimal number, e.g. “123” 
If <rsp_faomat>  is UCS2, requests a 4 byte string, e.g. “0031” 
<rsp_faomat > refer to the response by AT+STGI =23 
If <cmd_id> =24: 
Input the identifier of the item selected by user  
If <cmd_id> =25: 
Input t he identifier of the item selected by user  
If <cmd_id>=83: 
<data>  ignore 
Note: It could return main menu during Proactive Command id is not 22 or 23 
If <cmd_id>= 84: 
<data>  ignore 
<pdu_len> 
Integer type, pdu string length 
<pdu_value>  
String type, the pdu string. 
Examples 
AT+STGR=25,1   (NOT PDU format)  
OK 
+STIN: 24  
AT+STGR=30,"810301240002028281830100900101"   (PDU format)  
OK 
11.4  AT+STK  STK switch  
Description  
This command is used to disable or enable the STK function. If the argument is 1, it is enabled. 
While if the argument is 0, it is disabled.  
SIMCom Confidential File
---

## Page 249

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 248 SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+STK= ? +STK: (list of supported  <value> s) 
OK 
Read Command  Responses  
AT+STK?  +STK: <value>  
OK 
Write Command  Responses  
AT+STK= <value>  OK  
ERROR 
Execution Command  Responses  
AT+STK  Set default value ( <value >=0): 
OK 
Defined values  
<value>  
0  –  Disable STK  
1  –  Enable STK 
Examples 
AT+STK=1  
OK 
11.5  AT+STKFMT  Set STK pdu format 
Description  
This command is used to disable or enable the STK pdu mode. If the argument is 1, it is enabled. 
While if the argument is 0, it is disabled.  
NOTE: Module should reboot to take effective. 
SIM PIN  References  
YES Vendor  
Syntax 
SIMCom Confidential File
---

## Page 250

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 249 Read Command  Responses  
AT+STKFMT?  +STKFMT: <value>  
OK 
Write Command  Responses 
AT+STKFMT= <value>  OK  
ERROR 
Defined values  
<value>  
0  –  Disable STK pdu format, decoded command mode. 
1  –  Enable STK pdu format 
Examples 
AT+STKFMT=1  
OK 
11.6  AT+ST ENV   Original STK PDU Envelope Command  
Description  
This command is used to original stk pdu envelope command. 
NOTE: PDU format supported only. 
SIM PIN  References  
YES Vendor  
Syntax 
Test Command  Responses 
AT+ST ENV =? OK 
Write Command  Responses 
AT+ST ENV =<len>,<pdu>  OK  
ERROR 
Defined values  
<len> 
Integer type, pdu string length 
<pdu> 
SIMCom Confidential File
---

## Page 251

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 250 String type, pdu value 
Examples 
AT+STENV= 18,"D30782020181900101"  
OK 
11.7  AT+ST SM  Get STK Setup Menu List with PDU Mode  
Description  
This command is used to get the stk setup menu list with pdu mode 
NOTE: PDU format supported only. 
SIM PIN  References  
YES Vendor  
Syntax 
Test Command  Responses 
AT+ST SM=? OK 
Read  Command  Responses  
AT+ST SM? +STSM: <cmd_id>,< tag>,<pdu_len>, <pdu_value>  
OK 
ERROR  
Defined values  
<cmd_id> 
Integer type, please refer to AT+STIN  
<tag> 
Not used now.  
<pdu_len> 
Integer type, pdu string length 
<pdu_value> 
String type, the pdu string. 
Examples 
AT+ST SM? 
+STSM:25,0,120,"D07681030125008202818285078065B052BF529B8F0A018070ED70B963A883
508F06028070AB94C38F0A03806D41884C77ED4FE18F0A048081EA52A9670D52A18F0A0580
624B673A97F34E508F0606808D854FE18F0A07805A314E50753162118F0A0880767E53D8751F
6D3B8F0A09806D596C5F98919053" 
SIMCom Confidential File
---

## Page 252

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 251 OK 
SIMCom Confidential File
---

## Page 253

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 252 12  AT Commands for Hardware  
12.1  AT+IPREX  Set local baud rate permanently  
Description  
This command sets the baud rate of module’s serial interface permanently, after reboot the baud rate 
is also valid . 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+IPREX=?  +IPREX: (list of supported <speed> s) 
OK 
Read Command  Responses 
AT+IPREX?  +IPREX: <speed>  
OK 
Write Command  Responses  
AT+IPREX= <speed>  OK 
ERROR 
Executi on Command Responses  
AT+IPREX  Set current value as default value: 
OK 
Defined values  
<speed>  
Baud rate per second:  
0, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 
3000000, 3200000, 3686400 
 
Note: LE20 doesn’ t sup port 0. 
Examples 
AT+IPREX?  
+IPREX: 115200 
OK 
SIMCom Confidential File
---

## Page 254

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 253 AT+IPREX=?  
+IPREX: (0,300,600,1200,2400,4800,9600,19200,38400,57600,115200,230400,460800,921600, 
3000000,3200000,3686400) 
OK 
AT+IPREX=115200  
OK 
AT+IPREX=0  
OK 
12.2  AT+CFGRI  Indicate RI when using URC  
Descri ption  
This command is used to configure whether pulling down <URC time >milliseconds the RI pin of 
UART when URC reported. If <status>  is 1, host may be wake up by RI pin, add setting <URC 
time>, <SMS time >pulling down time of RI pin. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CFGRI=?  +CFGRI: (range of supported <status> s), (range of supported 
<URC time> s), (range of supported <SMS time> s) 
OK 
Read Command  Responses 
AT+CFGRI?  +CFGRI: <status> ,<URC time >,<SMS time > 
OK 
Write Command  Responses 
AT+CFGRI=<status >,<URC 
time>,<SMS time > OK 
ERROR 
Execution Command Responses 
AT+CFGRI  Set <status> = 0  
Set <URC time> = 60  
Set <SMS time> = 120 
OK 
Defined values  
<status>  
0  off  
1  on  
<URC time>  
SIMCom Confidential File
---

## Page 255

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 254 a numeric parameter which is number of milliseconds to assert RI delay to reset RI. The range is 
10 to 6000. 
<SMS time>  
a numeric parameter which is number of milliseconds to assert RI delay to reset RI. The range is 
20 to 6000. 
Examples 
AT+CFGRI=?  
+CFGRI: (0 -1),(10-6000),(20-6000) 
OK 
AT+CFGRI?  
+CFGRI: 0,60,120  
OK 
AT+CFGRI=1  
OK 
AT+CFGRI  
OK 
12.3  AT+CSCLK Control UART Sleep  
Description  
This command is used to enable UART Sleep or always work, 
if set to 1, UART can sleep when DTR pull high if set to 0, UART always work  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CSCLK=?  +CSCLK: (range of supported <status> s) 
OK 
Read Command  Responses  
AT+CSCLK ? +CSCLK: <status>  
OK 
Write Command  Responses 
AT+CSCLK= <status > OK 
ERROR 
Execution Command  Responses  
AT+CSCLK  Set <status> = 0  
OK 
SIMCom Confidential File
---

## Page 256

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 255 Defined values  
<status>  
0  off  
1  on  
Examples 
AT+CSCLK =? 
+CSCLK : (0-1) 
OK 
AT+CSCLK ? 
+CSCLK : 0 
OK 
AT+CSCLK =1 
OK 
AT+CSCLK  
OK 
 
12.4  AT+CMUX  Enable the multiplexer over the UART 
Description   
This command is used to enable the multiplexer over the UART, after enabled four virtual ports can 
be used as AT command port or MODEM port, the physical UART can no longer transfer data 
directly under this case.  
By default all of the four virtual ports are used as AT command port. 
Second serial port is not support this command. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CMUX=?  +CMUX: (0),(0),(1 -8),(1 -1500),(0),(0),(2-1000) 
OK 
Read Command  Responses 
AT+CMUX ? +CMUX :<value >,<subset >,<port_speed>,< N1>,<T1>,<N2>,<T2> 
OK 
Write Command  Responses 
AT+CMUX=  OK 
SIMCom Confidential File
---

## Page 257

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 256 <value> [,<subset >[,<port_sp
eed>[,<N1>[,<T1>[,<N2>[,<
T2>]]]]]]  ERROR 
Defined values  
< value  >:  
  0 – currently only 0 is supported (basic operation mode). 
< subset  >:  
  Currently omitted  
< port_speed  >:  
  Currently omitted, you can set speed before enable multiplexer  
< N1>:  
  1-1500 
< T1>:  
  Currently omitted  
< N2>:  
  Currently omitted  
< T2>:  
  2-1000  
Examples 
AT+CMUX=?  
+CMUX: (0),(0),(1 -8),(1 -1500),(0),(0),(2-1000) 
OK 
AT+CMUX?  
+CMUX: 0,0,5,1500,0,0,600 
OK 
AT+CMUX=0  
OK 
NOTE: Currently only basic operation mode is supported . 
 
12.5  AT+CGFUNC Enable/disable the function for the special GPIO  
Description  
   SIM75 00/SIM7600 supplies many GPIOs, all of which can be used as General Purpose 
Input/Output pin, interrupt pin and some of them can be used as function pin.  
This command is used to enable/disable the function for the special GPIO. Please consult the 
document “SIM7500_SIM7600 Series_GPIO_Application_Note” for more details.  
The configuration will be saved automatically.  
SIMCom Confidential File
---

## Page 258

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 257 SIM PIN References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGFUNC=?  +CGFUNC : (list of supported <GPIO> s),(list of supported 
<function> s) 
OK 
Read Command  Responses 
AT+CGFUNC= <GPIO > +CGFUNC: <GPIO >,<function>  
OK 
ERROR 
Write Command  Responses 
AT+CGFUNC= <GPIO >,<fu
nction>  OK 
ERROR 
Defined values  
<GPIO > 
7500C/CE GPIO: 
3: GPIO3/Ethernet 
40: GPIO40/STATUS 
44: GPIO4 4/SD_DETECT 
 
7500A GPIO:  
40: GPIO40/STATUS 
 
<function> 
0 : gpio function. 
1 : function1 
Note:  
 GPIO40 default function is STATUS 
 GPIO44 default function is GPIO 
 If Ethernet hardware has been ready, GPIO3 default function is Ethernet. Instead, GPIO3 default function is GPIO. 
Examples 
AT+CGFUNC=40,1 
OK 
AT+CGFUNC=40  
+CGFUNC: 40,1 
SIMCom Confidential File
---

## Page 259

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 258 OK 
 
12.6  AT+CGDRT  Set the direction of specified GPIO  
Descrip tion  
This command is used to set the specified GPIO to input or output state. If setting to input state, 
then this GPIO can not be set to high or low value. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+ CGDRT =? +CGDRT : (list of support ed <GPIO> s),(list of supported < 
gpio_io > s) 
OK 
Write Command  Responses 
AT+CGDRT= <GPIO> , 
<gpio_io>  OK 
ERROR 
Read Command  Responses  
AT+CGDRT =<GPIO>  +CGDRT : <GPIO> ,<gpio_io>  
OK 
ERROR 
Defined values  
<GPIO>  
The value is GPIO ID, different hardware ve rsions have different values.  
<gpio_io> 
0  –  in  
 1  –  out 
NOTE:  The GPIO must be set to GPIO FUNCTION through AT+CGFUNC, then it will set success.  
Examples 
AT+CGDRT=43,0  
OK 
 
SIMCom Confidential File
---

## Page 260

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 259 12.7  AT+CGSETV  Set the value of specified GPIO  
Description  
This command is used to set the value of the specified GPIO to high or low. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CGSETV =? +CGSETV : (list of supported <GPIO> s),(list of supported < 
gpio_hl > s) 
OK 
Write Command  Responses  
AT+CGSETV= <GPIO> ,<gp
io_hl>  OK 
ERROR 
Defined values  
<GPIO>  
The value is GPIO ID, different hardware versions have different values.  
<gpio_hl> 
0  –  low  
 1  –  high 
NOTE:  The GPIO must be set to GPIO FUNCTION through AT+CGFUNC, then it will set success.  
Examples 
AT+CGSETV=43 ,0 
OK 
 
12.8  AT+CGGETV  Get the value of specified GPIO  
Description  
This command is used to get the value (high or low) of the specified GPIO. 
SIM PIN  References  
NO Vendor 
SIMCom Confidential File
---

## Page 261

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 260 Syntax 
Test Command  Responses 
AT+ CGGETV=?  +CGGETV : (list of supported <GPIO> s) 
OK 
Write Command  Responses 
AT+CGGETV= <GPIO>  +CGGETV: <GPIO> ,<gpio_hl>  
OK 
ERROR  
Defined values  
<GPIO>  
The value is GPIO ID, different hardware versions have different values.  
<gpio_hl> 
0  –  low 
1 –  high  
NOTE: The GPIO must be set to GPIO FUNCTION throu gh AT+CGFUNC, then it will set 
success.  
Examples 
AT+CGGETV=43  
+CGGETV: 43,0  
OK 
 
12.9  AT+CGISR  Set GPIO interrupt trigger condition  
Description  
The module supplies many GPIOs, all of which can be used as General Purpose Input/Oupt pin, 
interrupt pin and some of them can be used as function pin. This command is used to set one GPIO pin as an interrupt source, and then set the detect type[optional] and polarity type[optional], and enable interrupt. Please consult the document “SIM75 00_SIM7600 Series_GPIO_Appli cation_Note” for more details.  
SIM PIN  References  
No  
Syntax 
Test Command  Responses 
SIMCom Confidential File
---

## Page 262

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 261 AT+ CGISR =? +CGISR : (list of supported <GPIO> s), <detect >,<polarity >,<URC 
char [size(4 5)]> 
OK 
Read Command  Responses  
AT+CGISR=< GPIO > opened : 
+CGISR: < GPIO  >,<detect >,<polarity >,<URC > 
not opened: 
+CGISR: < GPIO  >,< detect  > 
OK 
Write Command  Responses 
AT+CGISR= <GPIO > ,<dete
ct>,<polarity >,[<URC >] OK 
Defined values  
< GPIO  > 
The value is GPIO ID, different hardware versions have different values.  
< detect  > 
0  –  no detect.  
1  –  level detection  
2  –  edge detection  
< polarity  > 
0  –  low level/edge detection  
1  –  high level/edge detection  
<URC  > 
Your ISR string, the max length of URC string is 45 bytes.  
If the length of string more than 45 bytes, it will be auto cute the string.  
If not set the string, it will be auto make a string for this setting, the string format is 
GPIO_<GPIO>_ISR!  
NOTE:  
1. if the interruption is triggered SIM7500/SIM7600 will send the following URC to host, URC is your 
ISR string or GPIO_ < GPIO  >_ISR  
2. If the GPIO use to interruption, before it must be setting on GPIO function and input mode.  
For example:  
AT+CGFUNC=41,0 
AT+CGDRT=41 ,0 
3. If set GPIO to no detect, it will be stop detect interruption and stop send URC. 
Examples 
SIMCom Confidential File
---

## Page 263

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 262 AT+CGISR=41  
+CGISR : 41, 1,1,GPIO_41_ISR!   If the pin ISR is opened 
OK 
+CGISR : 41,0   If the pin ISR is not opened 
OK 
AT+CGISR=41,2,1 
OK 
AT+CGISR=41,0  
OK 
SIMCom Confidential File
---

## Page 264

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 263 13  AT Commands for File System  
The file system is used to store files in a hierarchical (tree) structure, and there are so me definitions and 
conventions to use the Module. 
Local storage space is mapped to “C: ”, “D: ” for TF card, “ E:” for multimedia , “F:” for cache. 
NOTE:  General rules for naming (both directories and files): 
1 The length of actual fully qualified names of directories and files can not exceed 254.  
2 Directory and file names can not include the following characters:  
         \   :  *  ?  “  <  >  |  ,  ;  
3 Between directory name and file/directory name, use character “/” as list separator, so it can not 
appear in dire ctory name or file name.  
4 The first character of names must be a letter or a numeral or underline, and the last character can not be period “.” and oblique “/”. 
5 7600M1+1 can not support “D:”and “E:”, if all the following AT are executed, “ERROR” will be returned. 
13.1  AT+FSCD  Select directory as current directory  
Description  
This command is used to select a directory. The Module supports absolute path and relative path. 
Read Command will return current directory without double quotation marks. Support “C:” , “D:”, 
“E:” , “F:”. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+FSCD=?  OK 
Read Command  Responses  
AT+FSCD?  +FSCD: <curr_path>  
OK 
Write Command  Responses  
AT+FSCD=<path>  +FSCD: <curr_path>  
OK 
ERROR 
Defined values  
SIMCom Confidential File
---

## Page 265

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 264 <path>  
String without double quotes, directory for selection. 
NOTE:  If <path>  is “..”, it will go back to previous level of directory.  
<curr_path> 
String without double quotes, current directory. 
Examples 
AT+FSCD=C:  
+FSCD: C:/  
OK 
AT+FSCD=C:/  
+FSCD: C:/  
OK 
AT+FSCD?  
+FSCD: C:/  
OK 
AT+FSCD=..  
+FSCD: C:/  
OK 
AT+FSCD=D:  
+FSCD: D:/  
OK 
AT+FSCD?  
+FSCD:D:/  
OK 
13.2  AT+FSMKDIR  Make new directory in current directory 
Description  
This command is used to create a new directory in current directory.  Support “C:”, “D:”, “E:” , 
“F:”.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+FSMKDIR=?  OK 
Write Command  Responses  
AT+FSMKDIR=<dir> OK 
ERROR 
SIMCom Confidential File
---

## Page 266

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 265 Defined values  
<dir>  
String without double quotes, directory name which does not already exist in current directory. 
Examples  
AT+FSMKDIR= SIMTech  
OK 
AT+FSCD?  
+FSCD: C:/  
OK 
AT+FSLS  
+FSLS: SUBDIRECTORIES:  
SIMTech  
 
OK 
13.3  AT+FSRMDIR  Delete directory in current directory  
Description  
This command is used to delete existing directory in current directory. Support “C:”, “D:” , “E:” , 
“F:”.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+FSRMDIR=?  OK 
Write Command  Responses 
AT+FSRMDIR= <dir>  OK 
ERROR 
Defined values  
<dir>  
String without double quotes.  
Examples 
AT+FSRMDIR=SIMTech  
OK 
SIMCom Confidential File
---

## Page 267

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 266 AT+FSCD?  
+FSCD: C:/  
OK 
AT+FSLS  
+FSLS: SUBDIRECTORIES:  
Audio 
Picture  
Video  
VideoCall 
OK 
13.4  AT+FSLS  List directories/files in current directory  
Description  
This command is used to list informations of directories and/or files in current directory. Support 
“C:”, “D:” , “E:” , “F:” . 
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+FSLS=?  +FSLS: (list of supported <type> s) 
OK 
Read Command  Responses 
AT+FSLS?  +FSLS: SUBDIRECTORIES: <dir_num> ,FILES: <file_num> 
OK 
Write Command  Responses 
AT+FSLS= <type>  [+FSLS: SUBDIREC TORIES:  
<list of subdirectories>  
<CR><LF>]  
[+FSLS: FILES:  
<list of files>  
<CR><LF>]  
OK 
Execution Command Responses 
SIMCom Confidential File
---

## Page 268

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 267 AT+FSLS  [+FSLS: SUBDIRECTORIES:  
<list of subdirectories>  
<CR><LF>]  
[+FSLS: FILES:  
<list of files>  
<CR><LF>]  
OK 
Defined values  
<dir_num>  
Integer type, the number of subdirectories in current directory. 
<file_num> 
Integer type, the number of files in current directory.  
<type>  
0  –  list both subdirectories and files  
1  –  list subdirectories only  
 2  –  list files only  
Examples 
AT+FSLS?  
+FSLS: SUBDIRECTORIES:2,FILES:2  
OK 
AT+FSLS  
+FSLS: SUBDIRECTORIES:  
FirstDir  
SecondDir 
 
+FSLS: FILES:  
image_0.jpg 
image_1.jpg 
 
OK 
AT+FSLS=2  
+FSLS: FILES:  
image_0.jpg 
image_1.jpg 
 
OK 
SIMCom Confidential File
---

## Page 269

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 268 13.5  AT+FSDEL  Delete file in current directory 
Description  
This command is used to delete a file in current directory. Before do that, it needs to use AT+FSCD  
select the father directory as current directory. Support “C:”, “D:”, “E:” , “F:”. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+FSDEL=?  OK 
Write Com mand  Responses  
AT+FSDEL=<filename>  OK 
ERROR 
Defined values  
<filename > 
String with or without double quotes, file name which is relative and already existing. 
If <filename> is *.*, it means delete all files in current directory.  
If the file path contai ns non -ASCII characters, the filename parameter should contain a prefix of 
{non -ascii} and the quotation mark.  
Examples 
AT+FSDEL=image_0.jpg 
OK 
13.6  AT+FSRENAME  Rename file in current directory 
Description  
This command is used to rename a file in current directory.  Support “C:”, “D:” , “E:”, “F:”.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+FSRENAME=?  OK 
SIMCom Confidential File
---

## Page 270

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 269 Write Command  Responses  
AT+FSRENAME=  
<old_name> ,<new_name>  OK 
ERROR 
Defined values  
<old_name> 
String with or without double quotes, file name which is existed in current directory. If the file path 
contains non- ASCII characters, the file path parameter should contain a prefix of {non- ascii} and 
the quotation mark. 
<new_name>  
New name of specified file, string with or without double quotes. If the file path contains 
non-ASCII characters, the file path parameter should contain a prefix of {non- ascii} and the 
quotation mark.  
Examples 
AT+FSRENAME=image_0.jpg, image_1.jpg 
OK 
AT+FSRENAME=  "my test.jpg", {non -ascii}"E6B58BE8AF95E9998 4E4BBB62E6A7067"  
OK 
13.7  AT+FSATTRI  Request file attributes  
Description  
This command is used to request the attributes of file which exists in current directory. Support 
“C:”, “D:” , “E:” , “F:”.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+FSATTRI=?  OK 
Write Command  Responses 
AT+FSATTRI= <filename>  +FSATTRI: <file_size> , <create_date>  
OK 
Defined values  
<filename>  
String with or without double quotes, file name which is in current directory. If the file path 
SIMCom Confidential File
---

## Page 271

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 270 contains non- ASCII characters, the file path parameter should contain a prefix of {non- ascii} and 
the quotation mark.  
<file_size>  
The size of specified file, and the unit is in Byte.  
<create_date>  
Create date and time of specified file, the format is YYYY/MM/DD HH/MM/SS Week.  
Week  –  Mon, Tue, Wed, Thu, Fri, Sat, Sun  
Examples 
AT+FSATTRI=image_0.jpg  
+FSATTRI: 8604, 2008/04/28 10:24:46 Tue 
OK 
AT+FSATTRI={non -ascii}"E6B58BE8AF95E99984E4BBB62E6A7067" 
+FSATTRI: 6296, 2012/01/06 00:00:00 Sun 
OK 
13.8  AT+FSMEM  Check the size of available memory  
Description  
This command is used to check the size of available memory. The response will list total size and 
used size of local storage space if present and mounted. Support “C:”, “D:”, “E:” , “F:”. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Co mmand  Responses 
AT+ FSMEM= ? OK 
Execution Command Responses 
AT+ FSMEM  +FSMEM: C:( <total> , <used> ) 
OK 
Defined values  
<total>  
The total size of local storage space.  
<used>  
The used size of local storage space.  
NOTE:  The unit of storage space size is in Byte.  
Examples 
SIMCom Confidential File
---

## Page 272

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 271 AT+FSMEM  
+FSMEM: C:(11348480, 2201600) 
OK 
13.9  AT+FSLOCA  Select storage place  
Description  
This command is used to set the storage place for media files. Support  “ C:”. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+FSLOCA= ? +FSLOCA: (list of supported <loca> s) 
OK 
Read Command  Responses 
AT+FSLOCA?  +FSLOCA: <loca>  
OK 
Write Command  Responses 
AT+FSLOCA= <loca>  OK 
ERROR 
Defined values  
<loca>  
0  –  store media files to local storage space (namely “C:/”)  
Examples 
AT+FSLOCA =0 
OK 
AT+FSLOCA?  
+FSLOCA: 0  
OK 
13.10   AT+FSCOPY  Copy an appointed file  
Description  
This command is used to copy an appointed file on C:/ to an appointed directory on C:/, the new file 
name should give in parameter.  Support “C:”, “D:” , “E:” , “F:”.  
SIMCom Confidential File
---

## Page 273

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 272 SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+FSCOPY=?  OK 
Write Command  Responses 
AT+FSCOPY=<file1> ,<file
2>[<sync_mode> ] +FSCOPY: <percent>  
[+FSCOPY: <percent> ] 
OK 
OK 
+FSCOPY: <percent>  
[+FSCOPY: <percent> ] 
+FSCOPY: END 
If found any error:  
SD CARD NOT PLUGGED IN 
FILE IS EXISTING  
FILE NOT EXISTING  
DIRECTORY IS EXISTED  
DIRECTORY NOT EXISTED  
FORBID CREATE DIRECTORY UNDER \"C:/\" 
FORBID DELETE DIRECTORY  
INVALID PATH NAME  
INVALID FILE NAME  
SD CARD HAVE NO ENOUGH MEMORY 
EFS HAVE NO ENOUGH MEMORY  
FILE CREATE ERROR  
READ FILE ERROR  
WRITE FILE ERROR  
ERROR 
Defined values  
<file1>  
The sources file name or the whole path name with sources file name. If the file path contains 
non-ASCII characters, the file path parameter should contain a prefix of {non-a scii} and the 
quotation mark. 
<file2>  
The destination file name or the whole path name with destination file name. If the file path 
contains non- ASCII characters, the file path parameter should contain a prefix of {non- ascii} and 
the quotation mark. 
SIMCom Confidential File
---

## Page 274

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 273 <percent>  
The percent of copy done. The range is 0.0 to 100.0  
<sync_mode>  
The execution mode of the command: 
0  –  synchronous mode 
1  –  asynchronous mode 
NOTE:    
1. The <file1>  and <file2>  should give the whole path and name, if only given file name, it  will 
refer to current path (AT+FSCD) and check the file’s validity. 
2. If  <file2>  is a whole path and name, make sure the directory exists, make sure that the file 
name does not exist or the file name is not the same name as the sub folder name, otherwis e return 
error.  
3. <percent>  report refer to the copy file size. The big file maybe report many times, and little 
file report less.  
4. If <sync_mode>  is 1, the command will return OK immediately, and report final result with 
+FSCOPY: END.  
Examples 
AT+FSCD ? 
+FSCD: C:/  
OK 
AT+FSCOPY= C:/TESTFILE,COPYFILE  ( Copy file TESTFILE on C:/ to C:/COPYFILE ) 
+FSCOPY: 1.0 
+FSCOPY: 100.0 
OK 
AT+FSCOPY=  "my test.jpg", {non-ascii}"E6B58BE8AF95E99984E4BBB62E6A7067" 
+FSCOPY:1.0  
+FSCOPY:100.0 
OK 
SIMCom Confidential File
---

## Page 275

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 274  
14  AT Commands for File Transmission 
14.1  AT+CFTRANRX  Transfer a file to EFS  
Description  
This command is used to transfer a file to EFS.Support SDcard. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CFTRANRX=?  +CFTRANRX: [{non -ascii}]"FILEPATH"  
OK 
Write Command  Responses  
AT+CFTRANRX= “<filepat
h>”,<len>  > 
OK 
> 
ERROR 
ERROR 
Defined values  
<filepath>  
The path of the file on EFS. 
<len>  
The length of the file data to send. The range is from 0 to 2147483647. 
NOTE  
The <filepath> must be a full path with the directory path. 
Examples 
AT+CFTRANRX=”c:/MyDir/t1.txt”,10  
>testcontent  
OK 
AT+CFTRANRX=”d:/MyDir/t1.txt”,10  
>testcontent 
OK 
SIMCom Confidential File
---

## Page 276

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 275 14.2  AT+CFTRANTX  Transfer a file from EFS to host  
Description  
This command is used to transfer a file from EFS to host. Before using th is command, the 
AT+CA TR  must be used to set the correct port used. Support SDcard.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CFTRANTX=?  +CFTRANTX: [{non -ascii}]"FILEPATH"  
OK 
Write Command  Responses 
AT+CFTRANTX= “<filepath
>”[,<locat ion>,<size> ] [+CFTRANTX: DATA, <len>  
… 
+CFTRANTX: DATA, <len> ] 
+CFTRANTX: 0  
OK 
ERROR 
Defined values  
<filepath>  
The path of the file on EFS. 
<len>  
The length of the following file data to output. 
<location>  
The beginning of the file data to output. 
<size>  
The length of the file data to output.  
NOTE 
The <filepath> must be a full path with the directory path.  
Examples 
AT+CFTRANTX=”c:/MyDir/t1.txt”  
+CFTRANTX: DATA, 11  
Testcontent  
+CFTRANTX: 0  
OK 
AT+CFTRANTX=”d:/MyDir/t1.txt”  
SIMCom Confidential File
---

## Page 277

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 276 +CFTRANTX: DATA, 11  
Testcontent 
+CFTRANTX: 0  
OK 
AT+CFTRANTX=”d:/MyDir/t1.txt”,1,4  
+CFTRANTX: DATA, 4  
estc 
+CFTRANTX: 0  
OK 
SIMCom Confidential File
---

## Page 278

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 277 15  AT Commands for Internet Service 
15.1  DNS&PING  
15.1.1  AT+CDNSGIP  Query the IP address of given domain name  
Description  
This command is used to query the IP address of given domain name.  
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CDNSGIP=?  OK 
ERROR  
Write Command  Responses 
AT+CDNSGIP= <domain 
name>  If successful,return:  
+CDNSGIP: 1 ,<domain name> ,<IP address>  
OK 
If fail,return:  
+CDNSGIP : 0,<dns error code>  
ERROR 
ERROR  
Defined values  
<domain name>  
  A string parameter (string should be included in quotation marks) which indicates the do
ma-in name.  
<IP address>  
  A string parameter (string should be included in quotation marks) which indicates the IP 
address corresponding to the domain name.  
<dns error code> 
  A numeric parameter which indicates the error code.  
    10   DNS GENERAL ERROR  
SIMCom Confidential File
---

## Page 279

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 278 Examples 
AT+CDNSGIP=?  
OK 
AT+CDNSGIP=”www.google.com”  
+CDNSGIP: 1,"www.google.com","203.20 8.39.99" 
OK 
15.1.2  AT+CDNSGHNAME  Query the domain name of given IP 
address  
Description  
This command is used to query the domain name of given IP address.  
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CDNSGHNAME=?  OK 
ERROR 
Write Comman d Responses 
AT+CDNSGHNAME= <IP 
address>  If successful,return:  
+CDNSGHNAME: <index> ,<domain name> ,<IP address>  
OK 
If fail,return:  
+CDNSGHNAME: 0, <dns error code>  
ERROR 
ERROR 
Defined values  
<domain name> 
  A string parameter (string should be included in quotation marks) which indicates the do
ma-in name.  
<IP address>  
  A string parameter (string should be included in quotation marks) which indicates the IP 
address corresponding to the domain name.  
<dns error code>  
  A numeric parameter which indicates the error code.  
SIMCom Confidential File
---

## Page 280

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 279     10   DNS GENERAL ERROR  
<index>  
  A numeric parameter which indicates DNS result index. This value is always 1 if performing 
successfully. Currently only the first record returned from the DNS server will be reported.  
Examples 
AT+CDNSGHNAME=?  
OK 
AT+CDNSGHNAME=”  58.32.231.148”  
+CDNSGHNAME: 1,"mail.sim.com","58.32.231.148"  
 
OK 
15.1.3  AT+CPING   Ping destination address  
Description   
This command is used to ping destination address. 
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CPING =? +CPING : IP address,  (list of supported 
<dest_addr_type> s),(1-100),(4-188),(1000-10000),(10000-10
0000), (16-255) 
OK 
ERROR 
Write Command  Responses 
AT+CPING= <dest_addr>,<dest_ad
dr_type> 
[,<num_pings>[,<data_packet_size
>[,<interval_time>[,<wait_time> 
[,<TTL>]]]]]  OK 
 
If ping’s result_type = 1 
+CPING: 
<result_type>,<resolved_ip_addr>,<data_packet_size>,<rtt>,
<TTL>  
 
If ping’s result_type = 2 
+CPING: <result_type>  
 
If ping’s result_type = 3 
SIMCom Confidential File
---

## Page 281

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 280 +CPING: 
<result_type>,<num_pkts_sent>,<num_pkts_recvd>,<num_p
kts_lost>,<min_rtt>,<max_rtt>,<avg_rtt> 
ERROR 
Defined values  
<dest_addr > 
The destination is to be pinged; it can be an IP address or a domain name. 
<dest_addr_type>  
Integer type. Address family type of the destination address 
1 – IPv4.  
2 – IPv6 (reserved)  
<num_pings>  
Integer type. The num_pings specifies the number of times the ping request (1- 100) is to be sent. 
The default value is 4.  
<data_packet_size>  
Integer type. Data byte size of the ping packet (4 -188). The default value is 64 bytes.  
<interval_time>  
Integer type. Interval between each ping. Value is specified in milliseconds (1000ms-10000ms). The 
default value is 2000ms. 
<wait_time>  
Integer type. Wait time for ping response. An ping response received after the timeout shall not be 
processed. Value specified in milliseconds (10000ms-100000ms). The default value is 10000ms. 
<TTL>  
Integer type. TTL(Time -To-Live) value for the IP packet over which the ping(ICMP ECHO 
Request message) is sent (16 -255), the default value is 255. 
<result_type>  
1 – Ping success  
2 – Ping time out 
3 – Ping result 
<num_pkts_sent>  
Indicates the number of ping requests that were sent out. 
<num_pkts_recvd>  
Indicates the number of ping responses that were received.  
<num_pkts_lost>  
Indicates the number of ping requests for which no response was received. 
<min_rtt>  
Indicates the minimum Round Trip Time(RTT). 
<max_rtt>  
Indicates the maximum RTT.  
<avg_rtt>  
Indicates the average RTT.  
SIMCom Confidential File
---

## Page 282

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 281 <resolved_ip_addr> 
Indicates the resolved ip address.  
< rtt> 
Round Trip Time. 
Examples 
AT+CPING= ? 
+CPING:IP address,(1,2), (1 -100), (4-188),(1000-10000),(10000-100000), (16-255) 
OK 
AT+CPING="www.baidu.com",1,4,64,1000,10000,255  
OK 
 
+CPING: 1,119.75.217.56,64,410,255 
 
+CPING: 1,119.75.217.56,64,347,255 
 
+CPING: 1, 119.75.217.56,64,346,255 
 
+CPING: 1,119.75.217.56,64,444,255 
 
+CPING: 3,4,4,0,346,444,386 
15.1.4  AT+CPINGSTOP  Stop an ongoing ping session  
Description   
This command is used to stop an ongoing ping session.  
SIM PIN  References  
YES  Vendor  
Syntax 
Test Command  Responses 
AT+CPINGSTOP=?  OK 
Write Command  Responses 
AT+CPINGSTOP  +CPING: 
<result_type>,<num_pkts_sent>,<num_pkts_recvd>,<num_p
kts_lost>,<min_rtt>,<max_rtt>,<avg_rtt> 
OK 
OK 
ERROR 
SIMCom Confidential File
---

## Page 283

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 282 Defined values  
<result_type>  
1 – Ping success  
2 – Ping time out 
3 – Ping result 
<num_pkts_sent>  
Indicates the number of ping requests that were sent out. 
<num_pkts_recvd>  
Indicates the number of ping responses that were received.  
<num_pkts_lost>  
Indicates the number of ping requests for which no response was received. 
<resolved_ip_addr> 
Indicates the resolved ip address.  
<min_rtt>  
Indicates the minimum Round Trip Time (RTT).  
<max_rtt>  
Indicates the maximum RTT.  
<avg_rtt>  
Indicates the average RTT.  
Examples 
AT+CPINGSTOP  
OK 
15.2  HTP 
These AT Commands of HTP relate d are used to synchronize system time with HTTP server.  
15.2.1  AT+CHTPSERV  Set HTP server info  
Description  
This command is used to add or delete HTP server information. There are maximum 16 HTP 
servers.  
SIM PIN  References  
YES  Vendor  
Syntax 
Test Command  Respo nses 
AT+CHTPSERV=?  +CHTPSERV:"ADD","HOST",(1 -65535), 
SIMCom Confidential File
---

## Page 284

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 283 (0-1)[,"PROXY",(1 -65535)] 
+CHTPSERV: "DEL",(0 -15) 
OK 
Read Command  Responses  
AT+CHTPSERV ? +CHTPSERV: <index> "<host> ",<port> ,<http_version>  
[,"<proxy> ",<proxy_port> ] 
… 
+CHTPSERV: <index> "<host> ",<port> [,"<proxy> ",< proxy_port> ] 
OK 
OK  (if HTP server not setted) 
Write Command  Responses  
AT+CHTPSERV= "<cmd> ",
"<host_or_idx> "[,<port> ,<ht
tp_version> [,"<proxy> ",<pro
xy_port> ]] OK 
ERROR  
Defined values  
<cmd>  
This command to operate the HTP server list . 
  “ADD ”: add a HTP server item to the list  
  “DEL”: delete a HTP server item from the list  
<host_or_idx> 
If the <cmd> is “ADD”, this field is the same as <host>, needs quotation marks; If the <cmd> is 
“DEL”, this field is the index of the HTP server item to be  deleted from the list, does not need 
quotation marks.  
<host> 
The HTP server address.  Max length is 254. 
<port>  
The HTP server port.  
<http_version>  
The HTTP version of the HTP server:  
0- HTTP 1.0  
1- HTTP 1.1  
<proxy> 
The proxy address,  the maximum length is 254.  
<proxy_port> 
The port of the proxy 
<index>  
The HTP server index.  
Examples 
SIMCom Confidential File
---

## Page 285

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 284 AT+CHTPSERV=”ADD”,”www.google.com”,80,1 
OK 
 
15.2.2  AT+CHTPUPDATE  Updating date time using HTP protocol 
Description  
This command is used to updating date time using HTP protocol. 
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CHTPUPDATE=?  OK 
Read Command  Response 
AT+CHTPUPDATE?  +CHTPUPDATE:<status>  
OK 
Execute Command  Responses 
AT+CHTPUPDATE  OK 
+CHTPUPDATE: <err>  
ERROR  
Defined values  
<status>  
The st atus of HTP module: 
  Updating: HTP module is synchronizing date time 
  NULL: HTP module is idle now  
<err>  
The result of the HTP updating 
Examples 
AT+CHTPUPDATE  
OK 
+CHTPUPDATE: 0  
 
SIMCom Confidential File
---

## Page 286

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 285 15.2.3  Unsolicited HTP Codes  
Code of <err>  Description  
0 Operation succeeded  
1 Unknown error 
2 Wrong parameter  
3 Wrong date and time calculated  
4 Network error  
15.3  NTP  
These A T Commands of NTP related are used to synchronize system time with NTP server.  
15.3.1  AT+CNTP  U pdate system time  
Description  
This command is used to update sys tem time with NTP server.  
SIM PIN  References  
YES Vendor 
Syntax 
Test Command  Responses 
AT+CNTP=?  +CNTP: 255 ,(-96~96) 
OK 
Read Command  Responses 
AT+CNTP?  +CNTP: < host>,<timezone>  
OK 
Write Command  Responses  
AT+CNTP =”<host> ”[,<tim
ezone> ] OK 
ERROR 
Write Command  Responses 
AT+CNTP  OK 
+CNTP:< err_code > 
ERROR  
Defined values  
<host>  
SIMCom Confidential File
---

## Page 287

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 286 NTP server address,length is 255. 
<timezone>  
Local time zone,the range is( -96 to 96), default value is 0.  
Examples 
AT+CNTP="202.120.2.101",32 
OK 
AT+CNTP  
OK 
+CNTP: 0  
15.3.2  Unsolicited NTP Codes  
Code of <err>  Description  
0 Operation succeeded  
1 Unknown error  
2 Wrong parameter  
3 Wrong date and time calculated  
4 Network error  
5 Time zone error  
6 Time out error 
 
SIMCom Confidential File
---

## Page 288

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 287 16  AT Commands for Open/Close Network 
16.1  AT+CNETSTART  Open netw ork 
Description  
This command opens packet network. 
SIM PIN  References  
YES Vendor 
Syntax 
Read Command  Responses 
AT+CNETSTART?  +CNETSTART: <net_state>  
 
OK 
ERROR 
Execution Command  Responses  
AT+CNETSTART OK 
 
+CNETSTART: <err>  
+CNETSTART: <err>  
 
OK 
+CNETSTART: <err>  
 
ERROR 
ERROR 
Defined values  
<net_state>  
a numeric parameter that indicates the state of PDP context activation:  
0   network close (deactivated)  
1 network is opening 
2 network open(activated) 
3 network is closing 
<err >  
SIMCom Confidential File
---

## Page 289

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 288 The result of operation, 0 is success, other value is failure. 
Examples 
AT+CNETSTART  
OK 
 
+CNETSTART : 0 
AT+CNETSTART ? 
+CNETSTART : 2 
 
OK 
 
16.2  AT+CNETSTOP  Close network  
Description  
This command closes network. Before calling this command, all opened sockets must be closed 
first. 
SIM PIN  References  
YES  Vendor  
Syntax 
Execution Command  Responses 
AT+CNETSTOP  OK 
 
+CNETSTOP : <err>  
+CNETSTOP : <err>  
 
OK 
+CNETSTOP : <err>  
 
ERROR 
ERROR 
Defined values  
<err>  
The result of operation, 0 is success, other value is failure.  
Examples  
SIMCom Confidential File
---

## Page 290

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 289 AT+CNETSTOP  
OK 
 
+CNETSTOP: 0  
16.3  AT+CNETIPADDR  Inquire PDP address 
Description  
This command inquires the IP address of current active PDP.  
SIM PIN  References  
YES  Vendor  
Syntax 
Read Command  Responses  
AT+CNETIPADDR?  +CNETIPADDR: < ip_address> 
 
OK 
+CNETIPADDR : <err_info>  
 
ERROR  
ERROR 
Defined values  
<ip_address>  
A string parameter that identifies the IP address of current active socket PDP.  
<err_info>  
A string parameter that displays the cause of occurring error. 
Examples 
AT+CNETIPADDR?  
+CN ETIPADDR: 10.71.155.118  
 
OK 
16.4  Unsolicited Open/Close network command <err> Codes  
Code of <err>  Description  
0 Operation succeeded  
SIMCom Confidential File
---

## Page 291

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 290 1 Unknown error  
2 Open network failed  
3 Close network failed  
4 
5 
6 
7 
8 Network not opened 
Operation not support 
Busy  
Netwo rk has been opened  
Network is also in use 
 
SIMCom Confidential File
---

## Page 292

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 291 17  AT Commands for GPS  
17.1  AT+CGPS  Start/Stop GPS session  
Description  
This command is used to start or stop GPS session. 
NOTE :   
1. Output of NMEA sentences is automatic; no control via AT commands is provided. If 
executing AT+CGPS =1, the GPS session will choose cold or hot start automatically. 
       2. UE-based and UE -assisted mode depend on URL ( AT+CGPSURL ). When UE -based 
mode fails, it will switch standalone mode.  
       3. UE-assisted mode is singly fixed. Standalone and UE -based mode is consecutively 
fixed. 
       4. After the GPS closed, it should to wait about 2s~30s for start again. Reason： If the 
signal conditions are right (strong enough signals to allow ephemeris demodulation) or 
ephemeris demodulation is on going, sometimes MGP will stay on longer in or der to 
demodulate more ephemeris.   This will help the engine provide faster TTFF and 
possibly better yield later (up to 2 hours), because it has the benefit of more ephemeris available.  
 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGP S=? +CGPS: ( list of supported <on/off> s),( list of supported <mode> s) 
OK 
Read Command  Responses 
AT+CGPS?  +CGPS: <on/off >,<mode > 
OK 
Write Command  Responses 
AT+CGPS= <on/off> 
[,<mode> ] OK 
If UE -assisted mode, when fixed will report indication: 
+CAGPSINFO: <lat> ,<lon> ,<alt> ,<date> ,<time>  
If <off>, it will report indication:  
+CGPS: 0  
ERROR 
SIMCom Confidential File
---

## Page 293

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 292 Defined values  
<on/off> 
0  –  stop GPS session  
1  –  start GPS session  
<mode> 
Ignore -   standalone mode 
1  –  standalone mode 
2  –  UE-based mode 
3  –  UE-assisted mo de 
<lat>  
Latitude of current position. Unit is in 10^8 degree 
<log> 
Longitude of current position. Unit is in 10^8 degree 
<alt>  
MSL Altitude. Unit is meters.  
<date>  
UTC Date. Output format is ddmmyyyy 
<time>  
UTC Time. Output format is hhmmss.s  
< unconfidence > 
Unconfidence of the location, GPS fixed report 39, cell fixed report 100. 
< uncertainty_meter >  
Uncertainty meters.  
Examples 
AT+CGPS?  
OK 
AT+CGPS=1,1 
OK 
17.2  AT+CGPSINFO  Get GPS fixed position information  
Description  
This command is used to get current position information. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CGPSINFO=?  +CCGPSINFO:   (scope of <time> ) 
SIMCom Confidential File
---

## Page 294

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 293 OK 
Read Command  Responses 
AT+CGPSINFO?  +CCGPSINFO:   <time>  
OK 
Write Command  Responses 
AT+CGPSINFO=< time> OK 
+CGPSINFO: [ <lat> ],[<N/S> ],[<log> ],[<E/W> ],[<date> ],[<UTC 
time> ],[<alt> ],[<speed> ],[<course> ] 
OK (if <time >=0) 
Execution Command Responses 
AT+CGPSINFO  +CGPSINFO: [ <lat> ],[<N/S> ],[<log> ],[<E/W> ],[<date> ],[<UTC 
time> ],[<alt> ],[<speed> ],[<course> ] 
OK 
Defined values  
<lat>  
Latitude of current position. Output format is ddmm.mmmmmm  
<N/S> 
N/S Indicator, N=north or S=south 
<log> 
Longitude of current position. Output format is dddmm.mmmmmm 
<E/W>  
E/W Indicator, E=east or W=west  
<date>  
Date. Output f ormat is ddmmyy  
<UTC time>  
UTC Time. Output format is hhmmss.s 
<alt>  
MSL Altitude. Unit is meters.  
<speed>  
Speed Over Ground. Unit is knots.  
<course>  
Course. Degrees.  
<time>  
The range is 0 -255, unit is second, after set <time>  will report the GPS  information every the 
seconds. 
Examples 
AT+CGPSINFO=?  
+CGPSINFO: (0 -255) 
SIMCom Confidential File
---

## Page 295

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 294 OK 
AT+CGPSINFO?  
+CGPSINFO: 0  
OK 
AT+CGPSINFO  
+CGPSINFO:3113.343286,N,12121.234064,E,250311,072809.3,44.1,0.0,0 
OK 
17.3  AT+CGPSCOLD  Cold start GPS  
Description  
This command is used to cold start GPS session.  
NOTE : Before using this command,it must use AT+CGPS =0 to stop GPS session.  
 
Syntax 
Test Command  Responses 
AT+CGPSCOLD=?  OK 
Execution Command Responses 
AT+CGPSCOLD  OK 
Examples 
AT+CGPSCOLD=?  
OK 
AT+CGPSCOLD  
OK 
17.4  AT+CGPSHOT  Hot start GPS  
Description  
This command is used to hot start GPS session 
NOTE:  Before using this command, AT+CGPS =0 must be used to stop GPS session.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CGPSHOT=?  OK SIM PIN  References  
NO Vendor 
SIMCom Confidential File
---

## Page 296

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 295 Execution Command  Responses  
AT+CGPSHOT  OK 
Examples 
AT+CGPSHOT=?  
OK 
AT+CGPSHOT  
OK 
17.5  AT+CGPSURL  Set AGPS default server URL  
Description  
This command is used to set AGPS default server URL. It will take effect only after restarting.  
SIM PIN  Refere nces 
NO Vendor  
Syntax 
Test Command  Responses 
AT+CGPSURL= ? OK 
Read Command  Responses  
AT+CGPSURL ? +CGPSURL: <URL> 
OK 
Write Command  Responses  
AT+CGPSURL= <URL> OK 
ERROR 
Defined values  
<URL > 
AGPS default server URL. It needs double quotation marks.  
Examples 
AT+CGPSURL=”123.123.123.123:8888” 
OK 
AT+CGPSURL?  
+CGPSURL: ”123.123.123.123:8888” 
OK 
SIMCom Confidential File
---

## Page 297

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 296 17.6  AT+CGPSSSL  Set AGPS transport security  
Description  
This command is used to select transport security, used certificate or not. The certificate gets from 
local carrier. If the AGPS server doesn’t need certificate, execute AT+CGPSSSL =0. 
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CGPSSSL= ? +CGPSSSL: ( list of supported <SSL> s) 
OK 
Read Command  Responses 
AT+CGPSSSL ? +CGPSSSL: <SSL>  
OK 
Write Command  Responses  
AT+CGPSSSL =<SSL>  OK 
ERROR 
Defined values  
<SSL> 
0   –  don’t use certificate  
1   –  use certificate  
Examples 
AT+CGPSSSL=0  
OK 
17.7  AT+CGPSAUTO  Start GPS automatic  
Description  
This command is used to start GPS automaticly when module powers on, GPS is closed defaultly. 
NOTE : If GPS start automatically, its operation mode is standalone mode. 
SIM PIN  References  
NO Vendor  
Syntax 
SIMCom Confidential File
---

## Page 298

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 297 Test Command  Responses  
AT+CGPSAUTO=? +CGPSAUTO:( list of supported <auto>s)  
OK 
Read Command  Responses 
AT+ CGPSAUTO? +CGPSAUTO: <auto>  
OK 
Write Command  Responses 
AT+CGPSAUTO= <auto>  OK 
ERROR 
Defined values  
<auto> 
0   –  Non- automatic  
    1   –  automatic  
Examples 
AT+CGPSAUTO=1  
OK 
17.8  AT+CGPSNMEA  Configure NMEA sentence type  
Description  
This command is used to configure NMEA output sentences which are generated by the gpsOne 
engine when position data is available.  
NOTE : If nmea bit 2 GPGSV doesn’t configure, GPGSV  sentence also doesn’t output on 
AT/modem port even set AT+CGPSFTM=1. 
Module should reboot to t ake effect.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CGPSNMEA=?  +CGPSNMEA :  (scope of <nmea> ) 
OK 
Read Command  Responses  
AT+CGPSNMEA?  +CGPSNMEA :  <nmea>  
OK 
Write Command  Responses 
SIMCom Confidential File
---

## Page 299

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 298 AT+CGPSNMEA= <nmea>  OK 
If GPS engine is running: 
ERROR 
Defined values  
<nmea>  
Range – 0 to 262143  
Each bit enables an NMEA sentence output as follows:  
  Bit 0  – GPGGA (global positioning system fix data) 
  Bit 1  – GPRMC (recommended minimum specific GPS/TRANSIT data)  
  Bit 2  – GPGSV (GPS satellites in  view)  
  Bit 3  – GPGSA (GPS DOP and active satellites)  
  Bit 4  – GPVTG (track made good and ground speed) 
Bit 5  – PQXFI (Global Positioning System Extended Fix Data.) 
Bit 6  – GLGSV (GLONASS satellites in view GLONASS fixes only)  
Bit 7  – GNGSA (1. GPS/2. Glonass/3. GALILE  DOP and Active Satellites.)  
Bit 8  – GNGNS (fix data for GNSS receivers;output for GPS,GLONASS,GALILEO) 
Bit 9 – Reserved  
Bit 10 – GAGSV (GALILEO satellites in view)  
Bit 11 – Reserved  
Bit 12 – Reserved  
Bit 13 – Reserved  
Bit 14 – Reserved  
Bit 15 – Reserved,  
Bit 16  –BDGSA/PQGSA (BEIDOU/QZSS DOP and active satellites)  
Bit 17  –BDGSV/PQGSV (BEIDOUQZSS satellites in view)  
Set the desired NMEA sentence bit(s). If multiple NMEA sentence formats are desired, “OR” the 
desired bits together. 
NOTE: Reserved d efault 0, set invalid.  
Examples 
AT+CGPSNMEA=200191  
OK 
17.9  AT+CGPSNEMARATE   Set NMEA output rate  
Description  
This command is used to set nmea output rate  
NOTE: send the command before open gps  
SIM PIN  References  
SIMCom Confidential File
---

## Page 300

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 299 NO Vendor  
Syntax 
Test Command  Responses 
AT+CGPSNMEARATE=?  +CGPSNMEARATE : (scope of < rate > ) 
OK 
Read Command  Responses  
AT+CGPSNMEARATE?  +CGPSNMEARATE : <rate>  
OK 
Write Command  Responses  
AT+CGPSNMEARATE= <r
ate> OK 
ERROR 
Defined values  
<rate>  
0     output rate 1HZ 
1     output rate 10HZ  
Examples 
AT+CGPSNMEARATE  =1 
OK 
17.10   AT+CGPSMD  Configure AGPS MO method  
Description  
This command specifies if the Mobile -Originated (MO) GPS session should use the control plane 
session or user plane session.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Comma nd Responses 
AT+CGPSMD=?  +CGPSMD :  (scope of <method> ) 
OK 
Read Command  Responses 
AT+CGPSMD?  +CGPSMD :  <method>  
OK 
SIMCom Confidential File
---

## Page 301

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 300 Write Command  Responses  
AT+CGPSMD= <method>  OK 
If GPS engine is running: 
ERROR  
Defined values  
<method> 
  0 – Control plane  
  1 – User plane  
Examples 
AT+CGPSMD=1  
OK 
17.11   AT+CGPSFTM  Start GPS test mode 
Description  
This command is used to start GPS test mode.  
NOTE :  
1. If test mode starts, the URC will report on AT port, Modem port and UART port. 
2. If testing on actual signal, <SV>  should be ignored, and GPS must be started by AT+CGPS, 
AT+CGPSCOLD or AT+CGPSHOT.  
3. If testing on GPS signal simulate equipment, <SV> must be choiced , and GPS will start 
automatically.  
4. URC sentence will report every 1 second. 
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses  
AT+CGPSFTM= ? OK 
Read Command  Responses 
AT+CGPSFTM ? +CGPSFTM: <on/off>  
OK 
Write Command  Responses 
AT+CGPSFTM= <on/off> OK 
ERROR 
SIMCom Confidential File
---

## Page 302

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 301 Defined values  
<on/off> 
0   –  Close test mode  
    1   –  Start test mode  
<CNo> 
Satellite  CNo value. Floating value. 
URC format  
$GPGSV[,<SV>,<CNo>][...]  
$GLGSV[,<SV>,<CNo>][...]  
$BDGSV[,<SV>,<CNo>][...] 
$GAGSV[,<SV>,<CNo>][...] 
$PQGSV[,<SV>,<CNo>][...]  
Examples 
AT+CGPSFTM=1  
OK 
$GLGSV,78,20.6,66,25.6,77,21.6,79,21.9,67,26.2,68,23.6 
 
$GPGSV, 10,36.3,12,33.5,14,26.5,15,27.0,18,30.6,20,29.4,21,14.9,24,32.8,25,30.6,31,29.1,32,27.0 
 
$BDGSV,201,28.7,204,29.0,206,27.3,207,25.9,209,25.0,210,18.5 
17.12   AT+CGPSDEL  Delete the GPS information  
Description   
This command is used to delete the GPS information. After executing the command, GPS start is 
cold start.  
NOTE: This command must be executed after GPS stopped. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGPSDEL=?  OK 
Execution Command  Responses  
AT+CGPSDEL  OK 
ERROR 
Examples 
SIMCom Confidential File
---

## Page 303

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 302 AT+CG PSDEL=?  
OK 
AT+CGPSDEL  
OK 
  
17.13   AT+ CGPSXE  Enable/Disable GPS XTRA function  
Description  
This command is used to enable/disable the GPS XTRA function. 
NOTE: XTRA function must download the assistant file from network by HTTP, so the APN must 
be set by AT+C GDCONT  command. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CGPSXE=?  +CGPSXE: (list of supported <on/off> s) 
OK 
Read Command  Responses 
AT+ CGPSXE ? +CGPSXE : <on/off>  
OK 
Write Command  Responses 
AT+CGPSXE= <on/off>  OK 
ERROR 
Defined values  
<on/off> 
0  –  Disable GPS XTRA  
1  –  Enable GPS XTRA 
Examples 
AT+CGPSXE=?  
+CGPSXE: (0,1)  
OK 
AT+CGPSXE =0 
OK 
SIMCom Confidential File
---

## Page 304

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 303 17.14   AT+CGPSXD  Download XTRA assistant file  
Description  
This command is used to download the GPS XTRA assistant file from network through http 
protocol. Module will download the latest assistant file form server and write the file into module.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CGPSXD=?  +CGPSXD: ( list of supported < server> s) 
OK 
Read Command  Responses 
AT+CGPSX D? +CGPSXD: <server>  
OK 
Write Command  Responses 
AT+CGPSXD =<server > OK 
+CGPSXD: <resp>  
+CGPSXD: <resp>  
ERROR 
Defined values  
<server > 
0  –  XTRA primary server (precedence)  
1  –  XTRA secondary server  
2  –  XTRA tertiary server  
<resp> 
refer to Unsoli cited XTRA download Codes  
Examples 
AT+CGPSXD =? 
+CGPSXD: (0 -2)  
OK 
AT+CGPSXD=0  
OK 
+CGPSXD: 0 
SIMCom Confidential File
---

## Page 305

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 304 17.15   AT+CGPSXDAUTO  Download XTRA assistant file automatically  
Description  
This command is used to control download assistant file automatically or not when GPS s tart. 
XTRA function must enable for using this command. If assistant file doesn’t exist or check error , 
the module will download and inject the assistant file automatically.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGPSXDAUTO=?  +CG PSXDAUTO: ( list of supported <on/off >s) 
OK 
Read Command  Responses 
AT+CGPSXDAUTO?  +CGPSXDAUTO: <on/off>  
OK 
Write Command  Responses  
AT+CGPSXDAUTO =<on/o
ff> OK 
ERROR 
Defined values  
<on/off> 
0  –  disable download automatically 
1  –  enable download aut omatically  
NOTE: Some URCs will report when downloading, it’s same as AT+CGPSXD  command. 
Examples 
AT+CGPSXDAUTO =? 
+CGPSXDAUTO: (0,1)  
OK 
AT+CGPSXDAUTO=0  
OK 
17.16   AT+CGPSINFOCFG  Report GPS NMEA-0183 sentence  
Description  
This command is used to report NMEA-0183 sentence. 
SIMCom Confidential File
---

## Page 306

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 305 SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGPSINFOCFG=?  +CGPSINFOCFG:  (scope of <time> ),(scope of <config> ) 
OK 
Read Command  Responses 
AT+CGPSINFOCFG?  +CGPSINFOCFG:  <time> ,<config>  
OK 
Write Command  Responses  
AT+CG PSINFOCFG=< time
>[,<config> ] OK 
(NMEA -0183 Sentence)  
…… 
OK (if <time>=0)  
Defined values  
<time>  
The range is 0 -255, unit is second, after set <time>  will report the GPS NMEA sentence every the 
seconds. 
If <time>=0, module stop reporting the NMEA sentence. 
<config > 
Range – 0 to 262143  
Each bit enables an NMEA sentence output as follows:  
  Bit 0  – GPGGA (global positioning system fix data) 
  Bit 1  – GPRMC (recommended minimum specific GPS/TRANSIT data)  
  Bit 2  – GPGSV (GPS satellites in view)  
  Bit 3  – GPGSA (GPS DOP and active satellites)  
  Bit 4  – GPVTG (track made good and ground speed) 
Bit 5  – PQXFI  (Global Positioning System Extended Fix Data.) 
Bit 6 – GLGSV (GLONASS satellites in view GLONASS fixes only)  
Bit 7 – GNGSA ( 1. GPS/ 2. Glonass /3. GALILE  DOP  and Active Satellites.)  
Bit 8 – GNGNS (fix data for GNSS  receivers; output for GPS,GLONASS,GALILEO) 
Bit 9 – Reserved  
Bit 10 – GAGSV  (GALILEO  satellites in view)  
Bit 11 – Reserved  
Bit 12 – Reserved  
Bit 13 – Reserved  
Bit 14 – Reserved  
Bit 15 – Reserved,  
SIMCom Confidential File
---

## Page 307

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 306 Bit 16 – BDGSA/PQGSA ( BEIDOU/QZSS  DOP and active satellites ) 
Bit 17 – BDGSV/PQGSV ( BEIDOUQZSS  satellites in view ) 
Set the desired NMEA sentence bit(s). If multiple NMEA sentence formats are desired, “OR” the  
desired bits together. 
NOTE:  Reserved  default 0, set invali d. 
  
For example:  
If want to report GPRMC sentence by 10 seconds, should execute AT+CGPSINFOCFG=10,2 
Examples 
AT+CGPSINFOCFG=?  
+CGPSINFO: (0 -255),(0 -262143)  
OK 
AT+CGPSINFOCFG=10,31 
OK 
$GPGSV ,4,1,16,04,53,057,44,02,55,334,44,10,61,023,44,05,45,253,43*7D 
$GPGSV ,4,2,16,25,10,300,40,17,25,147,40,12,22,271,38,13,28,053,38*77 
$GPGSV ,4,3,16,26,09,187,35,23,06,036,34,24,,,,27,,,*7A 
$GPGSV ,4,4,16,09,,,,31,,,,30,,,,29,,,*7D 
$GPGGA,051147.0,3113.320991,N,12121.248076,E,1,10,0.8,47.5,M,0,M,,*45 
$GPVTG ,NaN,T,,M,0.0,N,0.0,K,A*42 
$GPRMC,051147.0,A,3113.320991,N,12121.248076,E,0.0,0.0,211211,,,A*66 
$GPGSA,A,3,02,04,05,10,12,13,17,23,25,26,,,1.4,0.8,1.2*3B 
17.17   AT+CGPSPMD  Configure positioning mode  
Description  
This command is used to configure the positioning modes support.  
NOTE : Need to restart the module after setting the mode.  
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGPSPMD=?  +CGPSPMD : (scope of <mode> ) 
OK 
Read Command  Responses 
AT+CGPSPMD?  +CGPSPMD : <mode>  
OK 
SIMCom Confidential File
---

## Page 308

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 307 Write Command  Responses  
AT+CG PSPMD= <mode>  OK 
ERROR  
Defined values  
<mode>  
Default  - 65407 
Range - 1 to 65407 
Each bit enables a supported positioning mode as follows: 
Bit 0 – Standalone 
Bit 1 – UP MS -based  
Bit 2 – UP MS -assisted  
Bit 3 – CP MS -based (2G) 
Bit 4 – CP MS -assisted (2G)  
Bit 5 – CP UE -based (3G) 
Bit 6 – CP UE -assisted (3G)  
Bit 7 – NOT USED  
Bit 8 – UP MS -based (4G) 
Bit 9 – UP MS -assisted(4G) 
Bit 10 – CP MS -based (4G) 
Bit 11 – CP MS -assisted (4G) 
Set the desired mode sentence bit(s). If multiple modes are desired, “OR” the desired bits together.  
Example, support standalone, UP MS -based and UP MS -assisted, set Binary value 0000 0111, is 7. 
Examples 
AT+CGPSPMD=127 
OK 
17.18   AT+CGPSMSB  Configure based mode switch to standalone  
Description  
This command is used to configure AGPS ba sed mode switching to standalone mode automatically 
or not. 
NOTE : This command must be executed after GPS stopped. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
SIMCom Confidential File
---

## Page 309

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 308 AT+CGPSMSB=?  +CGPSMSB : (scope of <mode> ) 
OK 
Read Command  Responses 
AT+CGPSMSB?  +CGPSMSB : <mode>  
OK 
Write Command  Responses  
AT+CGPSMSB= <mode>  OK 
ERROR 
Defined values  
<mode> 
0  –  Don’t switch to standalone mode automatically 
1  –  Switch to standalone mode automatically 
Examples 
AT+CGPSMSB=0 
OK 
17.19   AT+CGPSHOR  Configure posit ioning desired accuracy  
Description  
The command is used to configure the positioning desired accuracy threshold in meters. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGPSHOR=?  +CGPSHOR :  (scope of <acc> ), (scope of < acc_f  >) 
OK 
Read Command Responses 
AT+CGPSHOR?  +CGPSHOR : <acc>,<acc_f>  
OK 
Write Command  Responses  
AT+CGPSHOR=<acc>[,<ac
c_f>]  OK 
ERROR 
Defined values  
SIMCom Confidential File
---

## Page 310

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 309 <acc>  
Range – 0 to 1800000  
Default value is 50  
<acc_f>  
Reserved  
Examples 
AT+CGPSHOR=50  
OK 
17.20   AT+CGPSNOTIFY  LCS  respond positioning request  
Description   
This command is used to respond to the incoming request for positioning request message. 
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses 
AT+CGPSNOTIFY=?  +CGPSNOTIFY: (list of supported <resp> s) 
OK 
Write Command  Responses 
AT+CGPSNOTIFY= <resp>  OK 
ERROR  
Defined values  
<resp>  
0  –  LCS notify verify accept  
1  –  LCS notify verify deny 
2  –  LCS notify verify no response 
Examples 
AT+CGPSNOTIFY=?  
+CGPSNOTIFY: (0 -2) 
OK 
AT+CGPSNOTIFY=0  
OK 
 
SIMCom Confidential File
---

## Page 311

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 310 17.21   AT+CGNS SINFO  Get GNSS fixed position information  
Description  
This command is used to get current position related information. 
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses  
AT+CGNSSINFO=?  +CGNSSINFO:   (scope of <time> ) 
OK 
Read Command  Response s 
AT+CGNSSINFO?  +CGNSSINFO:   <time>  
OK 
Write Command  Responses 
AT+CGNSSINFO=< time> OK 
+CGNSSINFO: 
[<mode> ],[<GPS -SVs> ],[<GLONASS -SVs> ],[BEIDOU -SVs], 
[<lat> ],[<N/S> ],[<log> ],[<E/W> ],[<date> ],[<UTC -time> ],[<alt> ], 
[<speed> ],[<course> ],[<PDOP> ],[HDOP ],[VDOP ] 
OK (if <time >=0) 
Execution Command  Responses  
AT+CGNSSINFO  +CGNSSINFO: 
[<mode> ],[<GPS -SVs> ],[<GLONASS -SVs> ],[BEIDOU -SVs], 
[<lat> ],[<N/S> ],[<log> ],[<E/W> ],[<date> ],[<UTC -time> ],[<alt> ], 
[<speed> ],[<course> ],[<PDOP> ],[HDOP ],[VDOP ] 
OK 
Defined values  
<mode> 
Fix mode   2=2D fix   3=3D fix  
<GPS -SVs>  
GPS satellite valid numbers         scope: 00 -12 
< GLONASS -SVs >  
GLONASS satellite valid numbers    scope: 00 -12 
<BEIDU -SVs>  
BEIDOU satellite valid numbers      scope: 00 -12 
<lat>  
SIMCom Confidential File
---

## Page 312

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 311 Latitude of current position. Output format is ddmm.mmmmmm 
<N/S> 
N/S Indicator, N=north or S=south  
<log> 
Longitude of current position. Output format is dddmm.mmmmmm 
<E/W>  
E/W Indicator, E=east or W=west  
<date>  
Date. Output format is ddmmyy 
<UTC time>  
UTC Time. Outpu t format is hhmmss.s  
<alt>  
MSL Altitude. Unit is meters.  
<speed>  
Speed Over Ground. Unit is knots. 
<course>  
Course. Degrees.  
<time>  
The range is 0 -255, unit is second, after set <time>  will report the GPS information every the 
seconds. 
<PDOP>  
Position Dilution Of Precision.  
<HDOP>  
Horizontal Dilution Of Precision.  
<VDOP>  
Vertical Dilution Of Precision.  
Examples 
AT+CGNSSINFO=?  
+CGNSSINFO: (0 -255) 
OK 
AT+CGNSSINFO?  
+CGPSINFO: 0  
OK 
AT+CGNSSINFO  
+CGNSSINFO: 
2,09,05,00,3113.330650,N,12121.262554,E,131117,091918.0,32.9,0.0,255.0,1.1,0.8,0.7 
OK 
AT+CGNSSINFO   (if not fix,will report null)  
+CGNSSINFO: ,,,,,,,,,,,,,,,  
OK 
SIMCom Confidential File
---

## Page 313

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 312 17.22   AT+CGNSSMODE  Configure GNSS support mode  
Description  
This command is used to configure GPS, GLONASS, BEIDOU and QZSS support mode. 
And DPO(Dynamic power optimization) status  
Module should reboot to take effective. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CGNSSMODE=?  +CGNSSMODE : (scope of <gnss_mode> ),(scope of <dpo_mode> ) 
OK 
Read Command  Responses 
AT+CGNSSMODE?  +CGNSSMODE : <gnss_mode>,<dpo_mode>  
OK 
Write Command  Responses  
AT+CGNSSMODE=<mode
>[,<dpo_mode>]  OK 
ERROR 
Defined values  
<gnss_mode>  
Range – 0 to 15  
Bit0: GLONASS  
Bit1: BEIDOU 
Bit2: GALILEO  
Bit3: QZSS  
1: enable  0:disable  
GPS always support  
<dpo_mode> 
1: enable DPO  
0: disable DPO  
Examples 
AT+CGNSSMODE=15,1 
OK 
SIMCom Confidential File
---

## Page 314

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 313 17.23   Unsolicited XTRA download Codes  
Code of <err>  Description  
0 Assistant file download successfully  
1 Assistant file doesn’t exist 
2 Assistant file check error  
220 Unknown error for HTTP  
221 HTTP task is busy  
222 Failed to resolve server address  
223 HTTP timeout  
224 Failed to transfer data  
225 Memory error  
226 Invalid parameter  
227 Network error  
220~227 codes are same as Unsolicited HTTP codes 
17.24   AT+CLBS  Base station location  
Description  
The write command is used to base station location. 
NOTE:  
    1. The LBS is only support in GSM/WCDMA/CDMA/LTE net mode. 
    2. It needs to execute AT+CNETSTART to open network before execute the AT+CLBS write 
command. It needs to execute AT+CNETSTOP to close network after complete the LBS operation.  
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CLBS=?  +CLBS: 
(1,2,3,4,9),(1-24,100-179),(-180.000000-180.000000),(-90.000000-
90.000000),(0,1) 
  
OK 
Write Command  Responses 
AT+CLBS=<type> [,<cid> [, 
[<longitude> ,<latitude> ],[<l
on_type> ]]] OK 
 
1)type = 1,get longitude and latitude 
SIMCom Confidential File
---

## Page 315

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 314 +CLBS: <ret_code> [,<latitude> ,<longitude> ,<acc> ] 
 
2)type = 2,get detail address 
+CLBS: <ret_code> [,<detail_addr> ] 
 
3)type = 3,get access times 
+CLBS: <ret_code> [,<times> ] 
 
4)type = 4,get longitude latitude and date time 
+CLBS: 
<ret_code> [,<latitude> ,<longitude> ,<acc> ,<date> ,<time> ] 
 
5)type = 9, report positioning error 
+CLBS: <ret_code>  
ERROR 
+CLBS: <ret_code>  
 
ERROR 
Defined values  
<type>  
A numeric parameter which specifies the location type.  
1 use 3 cell’s information  
2  get detail address  
3  get access times  
4  get longitude latitude and date time  
9  report positioning error 
NOTE: For LE22  (new baseline), this parameter could use 1 and 2 o nly!  
<cid>  
A numeric parameter which specifies a particular PDP context definition (see AT+CGDCONT  
command). 
1…24,100…179 
NOTE：This parameter takes no effect in SIM7500/SIM7600, it’s only in order to keep compatible 
with the previous software version and other projects, support convenience for the customers. 
<longitude> 
Current longitude in degrees . 
<latitude > 
Current latitude in degrees . 
<detail_addr> 
Current detail address . It based the UCS2 coding. Each 4 characters in the URC is for one 
UCS2 ch aracter.  
<acc> 
SIMCom Confidential File
---

## Page 316

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 315 Positioning accuracy. 
<lon_type > 
The type of longitude and latitude  
0  WGS84 ，the default type  
1  GCJ02.  
<times > 
access service times . 
<data> 
service date(UTC, the format is YYYY/MM/DD).  
<time> 
service time(UTC, the format is HH:MM:SS ). 
<ret_code > 
The result code.  
0   Success  
1  Parameter error returned by server.  
2  Service out of time returned by server. 
3  Location failed returned by server.  
4  Query timeout returned by server. 
5  Certification failed returned by server.  
6  Server LBS error success.  
7  Server LBS error failed.  
80  Report LBS to server success 
81  R eport LBS to server parameter error  
82  Report LBS to server failed  
110  Other Error  
 
8   LBS is busy.  
9   Open network error. 
10  Close network error. 
11  Operation timeout. 
12  DNS  error.  
13  Create socket error.  
14  Connect socket error. 
15  Close socket error. 
16  Get cell info error. 
17  Get IMEI error.  
18  Send data error. 
19  Receive data error.  
20  NONET error. 
21  Net not opened. 
Examples 
SIMCom Confidential File
---

## Page 317

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 316 AT+CLBS=?  
+CLBS: (1,2,3,4,9),(  1-24,100-179),( -180.000000-180.000000),(-90.000000-90.000000),(0,1) 
 
OK 
AT+CLBS=1  
OK 
 
+CLBS: 0,31.228525,121.380295,500 
AT+CLBS=2  
OK 
 
+CLBS: 0, 
4e0a6d775e020020957f5b81533a002091d1949f8def002097608fd166688baf79d162805927697c 
AT+CLBS=3  
OK 
 
+CLBS: 0 ,22 
AT+CLBS=4  
OK 
 
+CLBS: 0,31.228525,121.380295,500,2025/06/07,10:49:08 
AT+CLBS=9  
OK 
 
+CLBS: 80 
17.25   AT+CLBSCFG  Base station location configure  
Description  
The write command is used to set and query the base station location configure. 
SIM PIN  References 
YES 3GPP TS 27.007 
Syntax 
Test Command  Responses 
AT+CLBSCFG=?  +CLBSCFG: (0 -1), 3,”Param Value” 
  
OK 
Write Command  Responses 
AT+CLBSCFG= <operate> ,<+CLBSCFG: 0, <para> ,<value>  
SIMCom Confidential File
---

## Page 318

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 317 para> [,<value> ]  
OK 
OK 
ERROR 
+CLBSCFG: <ret_code>  
 
ERROR 
Defined values  
<operate>  
A numeric parameter which specifies the operator.  
0  read operator  
1  write operator  
<para>  
A numeric parameter which specifies the operator parameter.  
3  Server’s address  
lbs-simcom.com:3002 
<value>  
The value of parameter. 
The allowed <value>  is "lbs -simcom.com:3002". 
Server’s address  of "lbs-simcom.com:3002" is free.  
<ret_code> 
Please refer to the <ret_code> of AT+CLBS.  
Examples 
AT+CLBSCFG=?  
+CLBSCFG: (0 -1),3,"Param Value"  
 
OK 
AT+CLBSCFG=0,3 
+CLBSCFG: 0,3,"lbs -simcom.com:3002"  
 
OK 
AT+CLBSCFG=1,3,”lbs-simcom.com:3002” 
OK 
17.26   AT+CASSISTLOC  Base station location of LTE/CDMA1x mode  
Description  
The write command is used to base station location. This command only is applicable to CDMA 
SIMCom Confidential File
---

## Page 319

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 318 only or CDMA and LTE hybrid network or CDMA and EVDO hybrid network. 
SIM PIN  References  
YES 3GPP TS 27.007 
Syntax 
Write Command  Responses 
AT+CASSISTLOC= <mode>  +CASSISTLOC: <longitude> ,<latitude> ,, 
 
+CASSISTLOC:  <ret_code>  
 
OK 
+CASSISTLOC: ,,, 
 
OK 
ERROR 
Defined values  
<mode> 
1 – get longitude and latitude.  
<longitude> 
Current  east longitude in degrees. 
<latitude > 
Current north latitude in degrees. 
<ret_code> 
The result code.  
0   Success  
Examples 
AT+CASSISTLOC=1  
+CASSISTLOC:31.220278,121.353058,, 
 
+CASSISTLOC:0 
 
OK 
 
17.27   AT+CGPSIPV6   Set AGPS IPV6 ADDR & PORT  
Description  
SIMCom Confidential File
---

## Page 320

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 319 This command is used to set AGPS IPV6 addr and port . It will take effect only after restarting.  
SIM PIN  References  
NO Vendor  
Syntax 
Test Command  Responses  
AT+CGPS IPV6 =? OK 
Read Command  Responses 
AT+CGPS IPV6 ? +CGPS IPV6 : <ipv6_addr>,<port>  
OK 
Write Command  Responses 
AT+CGPS IPV6 =<ipv6_addr
>,<port>  OK 
ERROR  
Defined values  
<ipv6_addr > 
AGPS  IPV6 addr . It needs double quotation marks.  
<port> 
AGPS IPV6 port.  
Examples 
AT+CGPS IPV6 =”2001:0268:1AFF:0000:0000:0000:B6F8:A5D2”,7275 
OK 
AT+CGPS IPV6 ? 
+CGPS IPV6 : ”2001:0268:1AFF:0000:0000:0000:B6F8:A5D2”,7275 
OK 
17.28   AT+ CGPSXTRADATA   Query  The Validity Of The Current gpsOne 
Xtra Data 
Description  
This command is used to query the validity of the current gpsOne xtra data. 
NOTE:  It needs to e xecute AT+C GPSXE  to enable before execute the AT+C GPSXTRADATA 
read.  
SIM PIN  References  
NO Vendor  
Syntax 
SIMCom Confidential File
---

## Page 321

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 320 Test Command  Responses  
AT+CGPSXTRADATA =? OK 
Read Command  Responses  
AT+CGPSXTRADATA ? +CGPS XTRADATA : <xtradatadurtime >,<injecteddatatime > 
OK 
Defined values 
<xtradatadurtime > 
Valid time of injected gpsOneXTRA data,unit:minute  
0            No gpsOneXTRA file or gpsOneXTRA file is overdue  
1-10080      Valid time of gpsOneXTRA file  
<injecteddatatime > 
Starting time of the valid time of XTRA data, format:  
“YYYY/MM/DD,hh:mm:ss ”,e.g. “2019/09/26,15:31:20” 
Examples 
AT+CGPS XTRADATA =? 
OK 
AT+CGPS XTRADATA ? 
+CGPSXTRADATA:168,"2019/09/25,05:00:00"  
OK 
 
SIMCom Confidential File
---

## Page 322

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 321 18  Audio Application Commands  
18.1  AT+CREC   R ecord wav audio file  
Description  
This command is used to record a wav audio file. It can record wav file during a call or not, the 
record file should be put into the “E:/”.  
SIM PIN  References  
NO Vendor 
Syntax 
Read Command  Responses  
AT+CREC?  +CREC : <status>  
OK 
Write Command  Responses  
AT+CREC=<record_path>,<filenam
e> +CREC:1  
OK 
AT+CREC=<mode>  +CREC:0  
OK 
+RECSTATE: crec stop  
Defined values  
<file_name>  
The name of wav audio file. M aximum file_name  length is 240 characters . (including " ") 
< record  _path> 
 1  –  local path  
 2  –  remote path  
    3  –  local and remot e sound mixing 
<status>  
0 –  free  
1 –  busy  
<mode> 
    0  –  stop record  
Examples 
AT+CREC=1,” E:/record.wav”  
SIMCom Confidential File
---

## Page 323

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 322 +CREC: 1  
OK 
AT+CREC=0  
+CREC: 0  
OK 
+RECSTATE: crec stop  
 
18.2  AT+CCMXPLAYWA V   Play wav audio file  
Description  
This command is used to play a wav audio file. It can play wav file during a call or not. 
NOTE  Wav file format require mono channel, 8kHz sampling frequency, 16bit sampling size, 
128kbps. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CCMXPLAYWAV=?  +CCMXPLAYWAV: (list of supported <play_path> s),(list of 
supported <repeat> s) 
 
OK 
Write Command  Responses 
AT+CCMXPLAYWAV=<fi
le_name> ,<play_path> [,<rep
eat>] +WAVSTATE: wav play 
 
OK 
Report URC automatically after playing end 
+WA VSTATE: wav play stop  
 
ERROR 
Defined values  
<file _name>  
The name of wav audio file. Maximum file_name  length is 240 characters . (including "") 
<play_path> 
 1  –  remote path  
 2  –  local path  
<repeat>  
SIMCom Confidential File
---

## Page 324

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 323 This parameter is reserved , not used at present, you can input this parameter or not. (0-- 255) 
Examples  
AT+CCMXPLAYWAV=”E:/record.wav”,2  
+WAVSTATE: wav play  
OK 
+WAVSTATE: wav play stop 
 
18.3  AT+CCMXSTOPWA V   Stop playing wav audio file  
Description  
This command is used to stop playing wav audio file. Execute this command during wav audio 
playing. If wav audio file was played end in the past, when you execute “ AT+CCMX STOPWAV ”, 
there is no “ +WAVSTATE: wav play stop ”. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses 
AT+CCMXSTOPWAV=?  OK 
Execution Command Responses 
AT+CCMXSTOPWAV +CCMXSTOPWAV:  
OK 
+WAVSTATE: wav play stop  
Examples 
AT+CCMXSTOPWAV  
+CCMXSTOPW A V:  
OK 
+WA VSTATE: wav play stop  
 
18.4  AT+ CCMXPLAY  Play audio file  
Description  
SIMCom Confidential File
---

## Page 325

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 324 The command is used to play an audio file. 
SIM PIN  References  
NO Vendor 
Syntax 
Test Command  Responses  
AT+CCMX PLAY=?  +CCMXPLAY: (list of supported <play_path> s),(list of supported 
<repeat> s) 
 
OK 
Write Command  Responses 
AT+CCMXPLAY=<file_na
me>[,<play_path> [,<repeat>
]] +CCMXPLAY:  
OK 
+AUDIOSTATE: audio play  
+AUDIOSTATE: audio play stop  
+CCMXPLAY:  
OK 
+AUDIOSTATE: audio play error  
ERROR 
Defined values  
<file_name>  
The name of audio file. Support audio file format  mp3, aac, amr, wav. M aximum file_name length 
is 240 characters . (including " ") 
<play_path>[optional] 
0  –  local path  
2 –  remote path  
NOTE: audio file format mp3 and aac can ’t play to remote path  
<repeat> [optional] 
0  –  don’t play repeat. Play only once. 
 1…255  –  play repeat times. E.g. <repeat> =1, audio will play twice.  
Examples 
at+ccmxplay="E:/ring.mp3",0,255  
+CCMXPLAY:  
OK 
+AUDIOSTATE: audio pl ay 
SIMCom Confidential File
---

## Page 326

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 325 +AUDIOSTATE: audio play stop 
 
18.5  AT+ CCMXSTOP  Stop playing audio file  
Description  
The command is used to stop playing audio file. Execute this command during audio playing. If 
audio file was played end in the past, when you execute “ AT+CCMX STOP ”, there i s no 
“+AUDIOSTATE: audio play stop”. 
SIM PIN  References  
NO Vendor 
Syntax 
Execution Command Responses 
AT+CCMXSTOP  +CCMXSTOP :  
OK 
+AUDIOSTATE: audio play stop  
Test Command  Responses 
AT+C CMXSTOP=?  OK 
Examples 
AT+CCMXSTOP  
+CCMXSTOP:  
OK 
+AUDIOSTATE: aud io play stop  
18.6  AT+CRECAMR   Record amr  audio file  
Description  
This command is used to record an amr audio file. It can record amr  file during a call or not, the 
record file should be put into the “E:/”. 
SIM PIN  References  
NO Vendor  
Syntax 
Read Command  Responses  
AT+CREC AMR ? +CREC AMR : <status>  
SIMCom Confidential File
---

## Page 327

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 326 OK 
Write Command  Responses 
AT+CREC AMR =<record_path> ,<fil
ename>  +CREC AMR : <status>  
OK 
AT+CREC AMR =<mode>  +CREC AMR : <status>  
OK 
+RECSTATE: crecamr stop  
Defined values  
<file_name>  
The name of amr audio file. Maxim um file_name  length is 240 characters . (including "") 
<record _path> 
 1  –  local path  
 2  –  remote path  
<status>  
0 –  free  
1 –  busy 
<mode> 
    0  –  stop record  
Examples 
AT+CREC AMR =1,” E:/record. amr” 
+CREC AMR : 1 
OK 
AT+CREC AMR =0 
+CREC AMR : 0 
OK 
+RECST ATE: crecamr stop  
 
SIMCom Confidential File
---

## Page 328

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 327 19  Appendixes 
19.1  Verbose code and numeric code  
Verbose result code  Numeric (V0 set)  Description  
OK 0 Command executed, no errors, Wake up after reset 
CONNECT  1 Link established  
RING  2 Ring detected  
NO CARRIER  3 Link not established or disconnected  
ERROR  4 Invalid command or command line too long  
NO DIALTONE  6 No dial tone, dialing impossible, wrong mode 
BUSY  7 Remote station busy 
NO ANSWER  8 Connection completion timeout 
19.2  Response string of AT+CEER  
Number  Response string  
CS intern al cause  
0 Phone is offline 
21 No service available  
25 Network release, no reason given  
27 Received incoming call  
29 Client ended call  
34 UIM not present 
35 Access attempt already in progress  
36 Access failure, unknown source 
38 Concur service no t supported by network  
29 No response received from network  
45 GPS call ended for user call  
46 SMS call ended for user call  
47 Data call ended for emergency call  
48 Rejected during redirect or handoff  
100 Lower -layer ended call  
101 Call origination request failed 
102 Client rejected incoming call  
103 Client rejected setup indication  
104 Network ended call  
105 No funds available 
SIMCom Confidential File
---

## Page 329

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 328 106 No service available 
108 Full service not available  
109 Maximum packet calls exceeded  
301 Video connection lost 
302 Video call setup failure  
303 Video protocol closed after setup  
304 Video protocol setup failure 
305 Internal error  
 
CS network cause   
1 Unassigned/unallocated number 
3 No route to destination  
6 Channel unacceptable  
8 Operator determined barri ng 
16 Normal call clearing  
17 User busy  
18 No user responding  
19 User alerting, no answer  
21 Call rejected  
22 Number changed  
26 Non selected user clearing  
27 Destination out of order 
28 Invalid/incomplete number  
29 Facility rejected  
30 Response to Status Enquiry  
31 Normal, unspecified 
34 No circuit/channel available  
38 Network out of order 
41 Temporary failure  
42 Switching equipment congestion 
43 Access information discarded  
44 Requested circuit/channel not available  
47 Resources unavaila ble, unspecified  
49 Quality of service unavailable 
50 Requested facility not subscribed  
55 Incoming calls barred within the CUG 
57 Bearer capability not authorized  
58 Bearer capability not available  
63 Service/option not available  
65 Bearer service not implemented  
68 ACM >= ACMmax  
69 Requested facility not implemented  
70 Only RDI bearer is available  
SIMCom Confidential File
---

## Page 330

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 329 79 Service/option not implemented  
81 Invalid transaction identifier value  
87 User not member of CUG  
88 Incompatible destination  
91 Invalid transit network selection  
95 Semantically incorrect message  
96 Invalid mandatory information 
97 Message non -existent/not implemented  
98 Message type not compatible with state  
99 IE non- existent/not implemented  
100 Conditional IE error 
101 Message not comp atible with state  
102 Recovery on timer expiry  
111 Protocol error, unspecified 
117 Interworking, unspecified 
 
CS network reject   
2 IMSI unknown in HLR  
3 Illegal MS  
4 IMSI unknown in VLR 
5 IMEI not accepted  
6 Illegal ME  
7 GPRS services not allowe d 
8 GPRS & non GPRS services not allowed 
9 MS identity cannot be derived 
10 Implicitly detached  
11 PLMN not allowed  
12 Location Area not allowed  
13 Roaming not allowed 
14 GPRS services not allowed in PLMN  
15 No Suitable Cells In Location Area 
16 MSC temporarily not reachable  
17 Network failure  
20 MAC failure  
21 Synch failure 
22 Congestion 
23 GSM authentication unacceptable 
32 Service option not supported  
33 Requested service option not subscribed 
34 Service option temporarily out of orde 
38 Call cannot be identified  
40 No PDP context activated  
95 Semantically incorrect message  
SIMCom Confidential File
---

## Page 331

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 330 96 Invalid mandatory information 
97 Message type non -existent  
98 Message type not compatible with state  
99 Information element non- existent  
101 Message not com patible with state  
161 RR release indication  
162 RR random access failure  
163 RRC release indication  
164 RRC close session indication  
165 RRC open session failure  
166 Low level failure  
167 Low level failure no redial allowed  
168 Invalid SIM  
169 No service  
170 Timer T3230 expired  
171 No cell available  
172 Wrong state  
173 Access class blocked  
174 Abort message received  
175 Other cause  
176 Timer T303 expired  
177 No resources  
178 Release pending  
179 Invalid user data  
 
PS internal cause look up  
0 Invalid connection identifier  
1 Invalid NSAPI  
2 Invalid Primary NSAPI  
3 Invalid field  
4 SNDCP failure  
5 RAB setup failure  
6 No GPRS context  
7 PDP establish timeout  
8 PDP activate timeout  
9 PDP modify timeout 
10 PDP inactive max timeout  
11 PDP lowerlayer error  
12 PDP duplicate  
13 Access technology change 
14 PDP unknown reason 
 
PS network cause   
SIMCom Confidential File
---

## Page 332

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 331 25 LLC or SNDCP failure  
26 Insufficient resources  
27 Missing or unknown APN  
28 Unknown PDP address or PDP type  
29 User Aauthentication fai led 
30 Activation rejected by GGSN  
31 Activation rejected, unspecified  
32 Service option not supported  
33 Requested service option not subscribed 
34 Service option temporarily out of order 
35 NSAPI already used (not sent) 
36 Regular deactivation  
37 QoS not accepted  
38 Network failure  
39 Reactivation required 
40 Feature not supported 
41 Semantic error in the TFT operation  
42 Syntactical error in the TFT operation  
43 Unknown PDP context  
44 PDP context without TFT already activated  
45 Semantic errors in packet filter  
46 Syntactical errors in packet filter  
81 Invalid transaction identifier  
95 Semantically incorrect message  
96 Invalid mandatory information 
97 Message non -existent/not implemented  
98 Message type not compatible with s tate 
99 IE non- existent/not implemented  
100 Conditional IE error 
101 Message not compatible with state  
111 Protocol error, unspecified 
19.3  Summary of CME ERROR codes 
Description  
This result code is similar to the regular ERROR result code. The format of <err>  can be either 
numeric or verbose string, by setting AT+CMEE command. 
SIM PIN  References  
NO 3GPP TS 27.007 
Syntax 
SIMCom Confidential File
---

## Page 333

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 332 +CME ERROR: <err>  
Defined values  
<err>  
Values (numeric format followed by verbose format): 
0  phone failure 
1  no connection to phone 
2  phone adaptor link reserved 
3  operation not allowed 
4  operation not supported 
5  PH-SIM PIN required  
6  PH-FSIM PIN required  
7  PH-FSIM PUK required  
10  SIM not inserted  
11  SIM PIN required  
12  SIM PUK required  
13  SIM failure  
14  SIM busy 
15  SIM wrong 
16  incorrect password  
17  SIM PIN2 required  
18  SIM PUK2 required  
20  memory full  
21  invalid index  
22  not found 
23  memory failure  
24  text string too long 
25  invalid characters in text string  
26  dial string too long 
27  invalid characters in di al string  
30  no network service 
31  network timeout 
32  network not allowed - emergency calls only  
40  network personalization PIN required 
41  network personalization PUK required 
42  network subset personalization PIN required 
43  network subset personalization PUK required  
44  service provider personalization PIN required  
45  service provider personalization PUK required  
46  corporate personalization PIN required  
47  corporate personalization PUK required  
100  Unknown 
SIMCom Confidential File
---

## Page 334

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 333 103  Illegal MESSAGE  
106  Illegal M E 
107  GPRS services not allowed  
111  PLMN not allowed  
112  Location area not allowed  
113  Roaming not allowed in this location area  
132  service option not supported  
133  requested service option not subscribed  
134  service option temporarily out of order 
148  unspecified GPRS error  
149  PDP authentication failure  
150  invalid mobile class  
257  network rejected request  
258     retry operation  
259  invalid deflected to number 
260     deflected to own number    
261  unknown subscriber 
262   service not  available  
263  unknown class specified  
264     unknown network message  
273     minimum TFTS per PDP address violated 
274     TFT precedence index not unique 
275     invalid parameter combination 
“CME ERROR” codes of MMS:  
170     Unknown error for mms 
171     MMS task is busy now 
172     The mms data is over size  
173     The operation is overtime 
174     There is no mms receiver  
175     The storage for address is full 
176     Not find the address 
177     Invalid parameter  
178     Failed to read mss  
179     There is not a mms push message 
180     Memory error  
181     Invalid file format  
182     The mms storage is full 
183     The box is empty 
184     Failed to save mms  
185     It’s busy editing mms now  
186     It’s not allowed to edit now 
187     No content i n the buffer 
188     Failed to receive mms  
SIMCom Confidential File
---

## Page 335

                                                                  Smart Machine Smart Decision  
SIM7 500_SIM7600 Series_AT Command Manual_V1 .12                                           2019- 10-25 334 189     Invalid mms pdu 
190     Network error  
191     Failed to read file  
192     None  
“CME ERROR” codes of  FTP:  
201 Unknown error for FTP 
202 FTP task is busy  
203 Failed to resolve server address  
204 FTP timeout  
205 Failed to read file  
206 Failed to write file  
207 It’s not allowed in current state  
208 Failed to login  
209 Failed to logout 
210 Failed to transfer data  
211 FTP command rejected by server  
212 Memory error  
213 Invalid parameter  
214 Network error  
Examples 
AT+CPIN="1234","1234"  
+CME ERROR: incorrect password  
19.4  Summary of CMS ERROR codes 
Description  
Final result code +CMS ERROR: <err>  indicates an error related to mobile equipment or network. 
The operation is similar to ERROR result code. None of the following commands in the same 
command line is executed. Nei ther ERROR nor OK result code shall be returned. ERROR is 
returned normally when error is related to syntax or invalid parameters. The format of <err>  can be 
either numeric or verbose. This is set with command AT+CMEE . 
SIM PIN  References  
--- 3GPP TS 27.005 
Syntax 
+CMS ERROR: <err>  
Defined values  
<err>  
SIMCom Confidential File