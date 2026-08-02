P3 URS for Upcoming SGX Shareholders' Meeting 
(Click here to view Figma)  

1.  Within the existing Corporate Actions module, create a new “Shareholder Meeting” sub-module 

1.1.  Compare client’s portfolio to Data Source = Refinitiv 

If any of the holdings as upcoming Shareholder Meeting, show ‘A’, else show ‘B’ below 

A 

B 

 
 
 
 
 
 
 
 
 
1.2.  Fields to read from Refinitiv Data 

Download from Refinitiv Monday to Friday including public holidays  
File name: General_Meetings_Daily 

Show in 
POEMS? 
No 
No 

Yes, 
show 
full  

Refinitiv Field 

Logic / Available Values 

MessageReference 
PreviousReference 

For internal 
For internal 

EventType 

MEET  Annual General Meeting 
XMET   Extraordinary or Special General Meeting 
OMET  Ordinary General Meeting 
CMET  Court Meeting 
NEWM  New 
CANC 
REPL 

Cancellation 
Replace 

Fields Example  

2000000068406010 
2000000067049450 

MEET 

No 

MessageFunction 

If MessageFunction = NEWM, create record in POEMS 
If MessageFunction = CANC, update record with 
“CANCELLED” next to instrument name and disable 
“Submit Proxy Instruction” button 
If MessageFunction = REPL, refer to Header 
PreviousReference, use the value and search under 
Header MessageReference and overwrite record 

NEWM 

No 

Status 

No 

ISIN 

APPD  Approved 
SUAP 

Subject to approval 

If Status = APPD, create record in POEMS 
If Status = SUAP, no action 

APPD 

SG1U48933923 

 
 
 
 
 
Yes 

SecurityDescription 

No 

Yes 

No 

Exchange 

Only show records with “XSES” in POEMS 

MeetingDate 

Show full information 

RecordDate 

Yes 

Location 

Show full information 

ISIN 
SG1U48933923/GB/
B1P31B8Keppel Infra 
Unit 
XSES 
11 Nov 2025, 
2:30pm 

31 Oct 2025  

Suntec Singapore 
Convention and 
Exhibition Centre, 
Summit 1,Level 3, 1 
Raffles 
Boulevard,SINGAPOR
E,SINGAPORE,Singap
ore,039593 

Yes 

Narrative 

Show under Remarks if available, else hide 

Virtual Meeting 

1.3.  Additional Fields to create (not from Refinitiv) 

Show in 
POEMS? 

Header 

Logic / Available Values 

Fields Example  

Yes 

Submission Cut-off  Minus 8 business days from MeetingDate 

03 Nov 2025,5:00pm 

 
 
 
 
 
 
1.4.  Additional Requirements  

Requirement 

Event should be removed from P3 on Meeting Date +1 

Reason 

Meeting is over, no longer need to view 
information 

Add important notes at bottom of page: 

1.  Please refer to the following website for more 

information: 
https://www.sgx.com/securities/meeting-schedules. 

2.  Kindly note that only meetings of SGX listed 

companies are available. 

3.  Selling the shares referenced in the proxy instruction 
will automatically revoke the instruction. To ensure 
the instruction remains valid, please retain the 
shares until after the respective meeting date. 
4.  Only shares held with ‘free’ status in the Register 72 

hours before meeting are eligible for proxy 
appointment and voting. 

 
 
 
1.5.  Clicking on the event will lead to the below page 

Figma Screenshot 

Description 

Hyperlink to “SGX website” - 
https://www.sgx.com/securities/meeting-schedules  

Click on ‘GET STARTED’ to proceed 

 
 
 
 
2.  Attend-in-person 

2.1.  Non-Joint Account 

Figma Screenshot 

Description 

2.1.1 
Client to select between the 2 available options of: 

a)  Attend-in-person 
b)  Vote only 

If Attend-in-person is selected, validate whether account is a joint account 

2.1.2 
If non-joint account, show 2 options: 

a)  Myself 
b)  Appoint proxy 

2.1.3 
Auto-populate account holder’s particulars from database (CIS?) 
Only Email address and Residential address can be edited 
(No validation required) 

 
 
 
 
 
 
2.1.4 
Show Share Quantity under “Available shares to vote” 

Two options for clients to select: 
a)  Vote with all shares 
b)  Vote with some shares 

Selecting “Vote with all shares” will use all quantity reflected under “Available 
shares to vote” 

Selecting “Vote with some shares” will reveal a field for entering of digit value 

Validation: if a number higher than “Available shares to vote” is entered, do 
not allow submission and show message “You can only vote up to <Available 
shares to vote> shares” 

 
 
 
 
 
 
 
 
 
2.1.5 Show final confirmation prompt for client to confirm 

2.2.  Joint Account 

If joint account is detected, show names of joint account holders and option 
to appoint proxy 

When either of the names is selected, steps will be same as 2.1.3 to 2.1.5 

 
 
 
 
 
 
 
 
 
 
2.3.  Appoint proxy 

2.3.1  
If “Appoint proxy” was selected in 2.1.2 and 2.2 above, client will be allowed 
to enter particulars of the person appointed.  
(No validation required) 

Clicking on NEXT will lead to 2.1.4  

 
 
 
 
3.  Vote Only 

3.1.  Non-Joint and Joint Accounts 

3.1.1 
Selecting “Vote only” will lead to 2 options: 

a)  Vote in my own capacity 
b)  Appoint chairman of meeting 

3.1.2 
Selecting “Vote in my own capacity” 
Auto-populate account holder’s particulars from database (CIS?) 

 
 
 
 
 
 
 
Selecting “Appoint chairman of meeting” will come straight to this page 

3.1.3 Clicking on “Add Resolution” will create Resolution 2 with another set of 
“Your vote” and “Representing share quantity” sections 

Clicking on bin symbol will delete the resolution. A pop up will appear to seek 
confirmation 

3.1.4 “Your vote” dropdown 
Options available in the dropdown: 

a)  For 
b)  Against 
c)  Abstain 
d)  Default 

 
 
 
    
 
 
 
 
3.1.5 
For each resolution, client can indicate whether to “Vote with all shares” or 
“Vote with some shares” 

For “Vote with all shares”, all quantity under “Shares available to vote” will be 
applied 

For “Vote with some shares”, text field will appear for client to enter digit 
value.  

Validation: if a number higher than “Available shares to vote” is entered, do 
not allow submission and show message “You can only vote up to <Available 
shares to vote> shares” 

Clicking on submit will bring client to the page shown in 2.1.5 above 

 
 
 
 
 
 
 
 
 
4.  View Submitted Instructions 

4.1 A green box with “Submitted” will appear in the meeting listing 
Clicking on event will lead to a review of submitted instructions 
Refer to Figma for all examples 

 
 
   
 
 
 
5.  Receipt of Information for Back-Office 

5.1.  If creating a UI in Withdrawal Admin is possible, above is the proposed interface. Boxes in orange are filters for searching submitted entries 

Fields 
Mode of Participate 

Function 
Search between: 
a)  Vote Only 
b)  Attend-in-Person 

Date Received 
Meeting Date 
Instrument Name 
Meeting Representative 

For searching when instruction was submitted by client 
For searching based on date of meeting 
Search based on instrument name 
Possible Values: 

a)  Account Holder 
b)  Joint Account Holder 
c)  Appointed Proxy 
d)  Chairman of meeting 

Client’s registered name 
PSPL trading account number 
Client’s registered NRIC 
Client’s registered email address 
Download table in CSV format 

Client Name 
Client Account No 
Client ID 
Client Email Address 
Download CSV 

 
 
5.2.  Whenever there is a submission by client, an email with the below information in excel should be 

sent to proxy@phillip.com.sg. The information will be based on inputs by clients in P3 

5.2.1. Attend-in-Person 

Column Header 
Request Received Date-Time 
Instrument Name 

Value 
23 Oct 2025, 3:00 PM 
Keppel Infrastructure Fund Management Pte Ltd 

Meeting Date_Time 
Mode of Participation 
Representative 
Name 
Trading Account No. 
Gender 
ID / Passport No. 
Email Address 
Residential Address 
Representing Share Qty 

11 Nov 2025, 2:30 PM 
Attend-in-Person 
Account Holder 
Daniel Cheng Boon Keng 
2584354 
Male 
S8856857H 
danielcheng@gmail.com 
1 Sims Lane #01-01, Singapore 380052, Singapore 
1,600 

5.2.2. Vote Only 

Column Header 
Request Received Date-Time 
Instrument Name 
Meeting Date_Time 
Mode of Participation 
Representative 
Name 
Trading Account No. 
Gender 
ID / Passport No. 
Email Address 
Residential Address 
Resolution_01 
Representing Share Qty_01 
Resolution_02 
Representing Share Qty_02 

Value 
23 Oct 2025, 3:00 PM 
Keppel Infrastructure Fund Management Pte Ltd 
11 Nov 2025, 2:30 PM 
Vote only 
Account Holder 
Daniel Cheng Boon Keng 
2584354 
Male 
S8856857H 
danielcheng@gmail.com 
1 Sims Lane #01-01, Singapore 380052, Singapore 
For 
1,600 
Against 
500 

 
 
 
