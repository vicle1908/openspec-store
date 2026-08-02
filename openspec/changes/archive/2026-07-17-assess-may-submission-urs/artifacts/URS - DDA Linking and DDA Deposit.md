Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

             PHILLIP SECURITIES PTE LTD 

User Requirement Specifications 

DDA Linking and DDA Deposit Project 

Project/Product BU/ BU driver:    Alvin Ter, Wee Kiat/Tsui Yin 
CX: Esther Tian 
Phase 1   - Main  (For GBO supported Trading acct only - M,C,KC,CC, V) 
System / Platform  

IT Team 

ITSR 

P3 mobile app (FE and API)   
+ iFrame (Central UI) + some Native 
+ Push notification to P3 (via poems engine 
api) 
Central UI   /    
Central UI exposed to **P2 Web** 

CIS / CIS API    (existing) 
Enhancement: 
RPS Process 
GBO Process  / GBO Posting (M,C,KC,CC) 
+ Push notification to P3 (via poems engine 
api) 
DBS Vendor - API 
Generate Finance Report send to Finance 
Check with Finance Katherine whether 
need finance report 

319991 

Ronnie/ Makara 
/ Thu Ta 

319992 

319999 
320736 

FE - Sibi / Myo 
API – Lam / Thu 
Ta 
Arasu / Gini 
Sundari 

Estimation  
(man-days) 
API – Thu Ta 
FE - Gilbert  
Poems engine – 
Thu Ta 
Sibi 

NA 
Sundari 

NA 
319992 

Aileen (DBS) 
FE - Sibi / Myo 

booking ahead 
TBC 

Phase 2    (For Synergy acct  - S2, UTW allowed) 
System / Platform  
MyWealth mobile app app 
+ iFrame (Central UI) + some Native 
SynergyBO Process  / SynergyBO Posting (S2, UTW) 

ITSR 

IT Team 

For: 
Author: 

Phillip Securities Pte Ltd 
Vincent (ITBA) 

Date: 
To :          
Alvin, Chee Wee (Payment, Project Owner) 

Project Ref: 
Doc Ref: 
Version: 
Classification: 
Cc:                  Carina Goh 

V1.0 
Requirement 

_____________________________________________________________________________________________ 
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 41 

            
 
 
 
 
 
 
 
 
 
 
 
 
 
 
            
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Esther (CX / CEU / P3) 
Tsui Yin (P2) 
Shawn (MyWealth) 
Gini (APU/CIS) 

_____________________________________________________________________________________________ 
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 41 

            
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Table of Contents 

Table of Contents ..................................................................................................................................................3 

1 

INTRODUCTION ..................................................................................................................................... 5 

1.1 
1.2 
1.3 
1.4 

PURPOSE OF DOCUMENT ..................................................................................................................................5 
DOCUMENT CONVENTIONS ................................................................................................................................5 
INTENDED AUDIENCE AND READING SUGGESTIONS ................................................................................................5 
GLOSSARY ......................................................................................................................................................6 

2 

PROBLEM/PURPOSE STATEMENT ........................................................................................................... 6 

2.1 
2.2 
2.3 
2.4 

BACKGROUND / PROBLEM .................................................................................................................................6 
PURPOSE ........................................................................................................................................................6 
PROJECT SCOPE ...............................................................................................................................................6 
USER CLASSES AND CHARACTERISTICS ..................................................................................................................7 

3 

SYSTEM FEATURES ................................................................................................................................. 1 

3.1 
3.2 
3.3 
3.4 
3.5 
3.6 

PRIORITY ON SYSTEM TO BUILD AND IMPLEMENT FOR DDA DEPOSIT .........................................................................1 
ELIGIBLE ACCOUNTS FOR DDA LINKING APPLICATION AND DDA DEPOSIT:..................................................................1 
UI UX PROTOTYPE ON FIGMA (P2/P3) ...............................................................................................................1 
DDA LINKING APPLICATION ...............................................................................................................................2 
DDA DEPOSIT (DEPOSIT FUND VIA DDA) ..........................................................................................................16 
DELINK DDA LINKING .....................................................................................................................................26 

4 

NON FUNCTIONAL REQUIREMENTS ...................................................................................................... 32 

4.1 
4.2 
4.3 
4.4 
4.5 

PERFORMANCE ..............................................................................................................................................32 
OPERATIONAL REQUIREMENTS .........................................................................................................................32 
SECURITY/CONTROL REQUIREMENTS .................................................................................................................32 
SERVICE REQUIREMENTS .................................................................................................................................32 
USER TRAINING REQUIREMENTS .......................................................................................................................32 

ASSUMPTIONS AND LIMITATIONS ........................................................................................................ 32 

APPENDIX ............................................................................................................................................ 33 

ACCEPTANCE FORM ............................................................................................................................. 33 

5 

6 

7 

_____________________________________________________________________________________________ 
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 41 

            
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

DOCUMENT REVISION HISTORY  

Document Title:  

Version  Revised by 

Effective 
Date 

Summary of Change 

1.0 

Vincent (ITBA)  17/11/2025  New Creation 

Reason 
for 
change 

_____________________________________________________________________________________________ 
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 41 

            
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

1  Introduction 

1.1  Purpose of Document 

This document records the requirements, both functional and non-functional, of the product to 
be developed. It serves as a contract between the customer/user and the developers. It is also an 
essential input to activities in analysis, design and testing. 

1.2  Document Conventions 

The following font colours shall have the corresponding meanings: 

•  Blue 
•  Red 
•  Green 
•  Highlight  

- 
-  
- 
- 

Reference to an external document or file 
Important/critical point 
Unconfirmed or undetermined point 
New or changed point from previous document version 

1.3  Intended Audience and Reading Suggestions 

This document provides a reference for the project team members. It is meant for, but not limited 
to: 

• 
• 
• 
• 
• 
• 
• 
• 

Project Steering Committee 
Project Sponsor 
Quality Assurance Engineers 
Business Analysts  
System Owners  
Users  
Functional Managers with employees assigned to project teams 
and IT development team. 

Reader Group 
Project Steering Committee 
Project Sponsor 
Quality Assurance Engineers 

Business Analysts  

System Owners  
Users  
Functional Managers  
IT Development Team 

Sections  
Problem\Purpose Statement 
Problem\Purpose Statement 
System  Features,  Interface  Requirements,  Non-functional 
Requirements 
System  Features,  Interface  Requirements,  Non-functional 
Requirements 
System Features 
System Features 
System Features 
System  Features,  Interface  Requirements,  Non-functional 
Requirements 

_____________________________________________________________________________________________ 
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 41 

            
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

1.4  Glossary 
No  Term 
1 
2 

eGIRO 
eDDA 

Meaning 
Electronic GIRO 
Electronic Direct Debit Authorization 
Direct Debit Authorisation 
Direct Debit Authorisation (“DDA”) - GIRO  
DDA 
Phillip - Central Information System 
CIS 
FO 
Front-Office Platform 
FO API System  Front-Office – API / API System server 
Regular Saving Plan 
RSP 
Share Builders Plan | Regular Savings Plan 
SBP RSP 
Unit Trust | Regular Savings Plan 
UT RSP 

3 
3 
4 
5 
6 
7 
8 
2  Problem/Purpose Statement 

2.1  Background / Problem 
Currently, POEMS and the MyWealth app support two payment methods — PayNow 
and eNETS. 

eNETS offers secure transfers but requires a minimum deposit of $1,000. Each 
transaction also requires users to log in to their banking portal to authenticate the 
transfer, which adds extra steps. 

PayNow is convenient but still requires users to switch to their mobile banking app, 
scan/upload the QR code, or manually enter PSPL’s UEN. This extra navigation outside 
the app creates friction, especially for elderly or less tech-savvy users, making the 
payment process less seamless. 

2.2  Purpose 
The current eGIRO (Electronic Direct Debit Authorization / eDDA) is primarily supports 
Regular Savings Plans (RSP) and cash trading accounts (non-cash ledger). 
With eGIRO/eDDA, clients complete a one-time bank setup, after which GIRO 
deductions and collections are collect by Operations—no further client action is 
required except maintaining sufficient bank balance. 

In this project, by expanding eDDA as a general payment method in this project, 
clients would only need to set up the linkage once. They could then top up or deposit 
into their ledger accounts directly from the linked bank, without leaving the our Front-
end system. 

The key objective is to enhance and streamline the client payment experience across 
our app and web platforms. 

2.3  Project Scope 

_____________________________________________________________________________________________ 
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 41 

            
 
 
 
 
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

This project enables customers to first link their bank accounts through Direct Debit 
Authorization (DDA) and subsequently make seamless deposits using the established 
DDA linkage. 

Scope includes: 
•  DDA linkage application and confirmation process 
•  Bank-side verification and ongoing status tracking 
•  Deposits and collections via the linked DDA account, including confirmation 
• 

In-app push notifications for relevant updates 

2.4  User Classes and Characteristics 

System 

Role 
Client  Front-end 
Platforms 
(P2 / P3 / 
MyWealth) 

Activities 
•  Submit DDA linking application 
•  View DDA Linking application status  
(Pending / Approved / Rejected) 

•  Make Deposit funds via linked DDA account 
•  Delink the linked DDA account 
• 

• Receive and view in-app push notifications 

_____________________________________________________________________________________________ 
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 41 

            
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

3  System Features 

3.1  Priority on System to build and implement for DDA Deposit 
• 

In Phase 1 - Priority is to build on P3 and all related system that if its dependency (e.g. CIS API, P3 API, P2 Central UI) 

Note: edda project is part of the OKR custody care project that allow client to fund unitize their account instantly 

•  After P3 implemented, we can build P2 and MyWealth in subsequent phase 

3.2  Eligible Accounts for DDA linking application and DDA Deposit: 
Include all Ledger account types below: 

Phase 1 

GBO supported Trading account (M,C=(CU,KC,CC)) 

CFD (sub-system) supported Trading account (CFD) 

PFN (sub-system) supported Trading account (V) 

Synergy (sub-system) supported Advisory account (S2,UTW) 

Advisory (S2+UTW)  -> S2 (linking) or UTW (linking)? 

Advisory (UTW)   -> UTW (linking) 

Phase 2 

SynergyBO supported wealth account (S2, UTW) 

Current – Egiro linking 

DDA – linking 

MA (S2+UT)  -> UT (Linking) 

MA (S2+UT)  -> ? 

Advisory (S2+UTW)  -> UTW (Linking) 

Advisory (S2+UTW)  -> ?  <Shawn / Jamie to decide> 

Advisory (UTW) -> UTW (Linking) 

Advisory (UTW) -> UTW (Linking) 

  Phillip Securities Pte Ltd                                                                                                          Page 1 of 41 

_____________________________________________________________________________________________ 

            
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Separate project enhancement requested by Carina on egiro project: 

To enable for  KC account and CU (Custodian) account for egiro application – when want to implement. Carina; By early Q4 

(This is to phase out the cash account) 

Excluded account types below: 

•  SBP account (SBP) 

•  Cash account (T) 

3.3  UI UX Prototype on Figma (P2/P3) 
https://www.figma.com/design/6MtLrIoT6Cmp4k3i7GUKYm/Me-Tab?node-id=401-13037 

  Phillip Securities Pte Ltd                                                                                                          Page 2 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

3.4  DDA Linking Application 

  Phillip Securities Pte Ltd                                                                                                          Page 3 of 41 

_____________________________________________________________________________________________ 

            
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Deposit Fund > Currency Selection > Deposit methods 
Functions/ Features 

Requirement / Criteria to apply 

Deposit Fund & Currency 
Selection 

Deposit Fund menu 

•  User login into P2/P3/MyWealth platform 

•  User can navigates to the Deposit Fund menu 

P2 

P3 

Currency Selection 

•  Under Deposit Fund, user can able to choose/select between SGD or Non-SGD currencies. 

Non-SGD currencies are: USD, HKD, AUD, EUR, GBP, CNH, JPY, MYR, GBP, EUR, CAD, CNY 

•  The system should display each currency as a separate tab for selection  

•  SGD tab selected by default 

  Phillip Securities Pte Ltd                                                                                                          Page 4 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Deposit methods: 

•  Based on the currency selected, system do following: 

Currency 
SGD  

Requirement 
SGD Deposit method: 

The system should allow the selection of the following SGD deposit methods: 

• 

Instant Deposit via DDA 

•  PayNow (existing) 

•  eNETS (existing) 

Note: Only SGD deposits are eligible for DDA Deposit 

P2 

P3 

Upon select [Instant Deposit via DDA] method,  

FO API must check account’s DDA/GIRO linking status (via call P3 API to check) 

Non-SGD  

Non-SGD Deposit method: 

The system should allow the selection of the following Non-SGD deposit methods: 

•  Fund Transfer from DBS Bank 

  Phillip Securities Pte Ltd                                                                                                          Page 5 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

      (Supported currencies: USD, HKD, AUD, EUR, GBP, CNH) 

•  Telegraphic Transfer 

      (Supported currencies: USD, HKD, JPY, MYR, AUD, GBP, EUR, CAD, CNY) 

When a method is selected, the system must display the corresponding deposit 

instructions. 

Non-SGD Deposit Instruction: 

The deposit instructions should be embedded from our existing POEMS payment 

instruction webpage (mobile responsive UI), using the following links: 

•  Fund Transfer from DBS Bank: https://www.poems.com.sg/payment/#mca 

•  Telegraphic Transfer: https://www.poems.com.sg/payment/#tt 

  Phillip Securities Pte Ltd                                                                                                          Page 6 of 41 

_____________________________________________________________________________________________ 

            
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Fund Transfer from DBS Bank 

Telegraphic Transfer (TT) 

DDA/GIRO Linking Status Check 
Functions/ Features 

Requirement / Criteria to apply 

DDA/GIRO Linking 

DDA/GIRO Linking Status Check 

Status Check 

When the [Instant Deposit via DDA] method is selected: 

•  FO API must check the account’s DDA/GIRO Linking status. 

•  FO API will call CIS API (current account no.) to get the DDA/GIRO Linking status. 

•  Based on the status, system will do following: 

Status 

Requirement 

  Phillip Securities Pte Ltd                                                                                                          Page 7 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Pending Approval 

Display the 'DDA Linking - Application In-Progress' page  

(Central UI) 

Click [Done] button redirect user to main homepage of system 

( P2 homepage, P3 Me tab, MyWealth homepage) 

Approved 

Proceed to DDA deposit process 

Redirected user to -> DDA Deposit Form  

(Central UI) 

No Linkage 

Redirected user to -> DDA Linking Application Form (Central UI) 

DDA Linking Application Form 
Functions/ Features 

Requirement / Criteria to apply 

  Phillip Securities Pte Ltd                                                                                                          Page 8 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

DDA Linking 

DDA Linking Application Form: 

Application Form 

•  Displays the ‘DDA Linking Application Form’ (Central UI) 

•  The Form allows the user to select a bank. 

(Central UI embedded 

in P2/P3/MyWealth) 

P2 

P3 

Form Fields: 

Name 

Type 

Criteria 

Account 

Label (read-only) 

Display the current <account no. and account service type name> 

For example: 

1000001 

Cash Management (KC) 

1000002 

Margin (M) 

  Phillip Securities Pte Ltd                                                                                                          Page 9 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

1000003 

Cash plus (M) 

1000004 

Custodian C) 

1000005 

Prepaid Custodian (CC)  

1000006 

Phillip Finance account (V) 

1000007 

S2 + UT account (S2+UT) 

1000008 

Advisory account (UTW) 

Account 

Label (read-only) 

Based on current account: 

Holder 

Name 

•  FO should auto-display account name of account holder (text)  

• 

If account is a Joint account -  FO should show account name of 

both Joint account holder 

For example: 

Joint account (1000001) have 2 account holder (Vincent Tiong 

and Jason Lau): 

•  FO should show both name on account holder name with 

comma delimitator  e.g. “Vincent Tiong , Jason Lau” 

NRIC/ 

Label (read-only) 

Based on current account: 

Passport ID 

•  FO should auto-display NRIC / Passport ID of account holder 

(text) 

• 

If account is a Joint account -  FO should show NRIC / Passport 

ID of both Joint account holder 

  Phillip Securities Pte Ltd                                                                                                          Page 10 of 41 

_____________________________________________________________________________________________ 

            
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

For example: 

Joint account (1000001) have 2 account holder NRIC/Passport ID 

(S1234567A and A1212121): 

•  FO should show both NRIC/Passport ID with comma delimitator  

e.g. “S1234567A, A1212121” 

Deposit 
Bank 

Drop Down list 
(single selection) 

Display the current eGIRO participant bank list as maintained in the 
system. 

Default: <Please Select> 

Mandatory: Yes 

Current eGIRO Participant Bank List: 

1.  DBS / POSB 

2.  OCBC 

3.  UOB 

4.  Standard Chartered 

5.  HSBC 

6.  ICBC 

Proceed button: 

The Proceed button is disabled if no bank is selected. 

The Proceed button is enabled once a bank is selected. 

  Phillip Securities Pte Ltd                                                                                                          Page 11 of 41 

_____________________________________________________________________________________________ 

            
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

The Mapping table – Bank Code (CIS) and BIC Code (DBS): 

Bank 
Code 
7171 
7339 

7375 
9496 

7232 
8712 

Bank Name 

DBS Bank Ltd 
Oversea-Chinese Banking 
Corporation Ltd 
United Overseas Bank Ltd 
Standard Chartered Bank (Singapore) 
Limited 
HSCB Bank (Singapore) Ltd 
Industrial & Commercial Bank Of 
China 

BIC Code 
DEV/ UAT  
DBSSSGS0XXX 
OCBCSGS0XXX 

UOVBSGS0XXX 
SCBLSG20XXX 

ZYFISGS0XXX 
ICBKSGS0XXX 

• 

• 

[Bank Code] - is the Bank Code in our current CIS GIRO Bank 

table 

[BIC Code] - is the SWIFT Code required by DBS Vendor API for 

eGIRO application. 

Proceed 

Button 

Submit DDA Linking Application Form to the backend system via P3 

API 

Upon DDA Linking Application Form submission:  

P3 API sends request to DBS API, which will redirect user to the bank’s iBanking portal for user to complete 

the DDA Linking application at iBanking portal side (follow same process as the current eGIRO flow) 

  Phillip Securities Pte Ltd                                                                                                          Page 12 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

P3 

P2 

Upon user completed DDA Linking application process at iBanking portal side:  

#  Requirement 

1 

2 

System updated DDA Linking status as “Pending Approval” in FO table 

The system should displays “DDA Linking - Application In-Progress” page (P2 Central UI) to 

user. 

  Phillip Securities Pte Ltd                                                                                                          Page 13 of 41 

_____________________________________________________________________________________________ 

            
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

P2 

P3 

3 

System should send push Notification  

(DDA Linking – Request Submitted OK - Application In-Progress) to user 

4  DBS will processes request and sends DBS API message result back to P3 API System. 

(The DBS API update is not real-time (asynchronous); DBS will sends response once their 

processing completes) 

After Submission 

The approval of DDA linkage is based on the processing results returned by DBS. 

P3 API Interaction with 

DBS 

DBS will processes request and sends DBS API result message back to P3 API System. 
(The DBS API update is not real-time (asynchronous);  

  Phillip Securities Pte Ltd                                                                                                          Page 14 of 41 

_____________________________________________________________________________________________ 

            
 
 
  
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

DBS will sends response once their processing completes) 

Based on received DBS API result message on DDA Linking status, P3 API System do following: 
Status 
Approved 

Action 
•  System call the CIS API to insert the 

In-App Notification 
Once CIS API insert OK,  
System send Push Notification (Approved) 

DDA linking into CIS 
•  Once CIS API insert OK,  

system update status to FO table 

Rejected 

System updated status to FO table 

System send Push Notification (Rejected) 

Note: 
DBS API System – responsible for processing DDA Linking application requests. 
P3 API System – handles DDA linkage requests and updates DDA Linking result status to FO table. 
CIS API – Inserts approved DDA linking record into CIS. 

Push Notification (In-App Notification)   -  (P2/P3/MyWealth) 

DDA Linking Application: 

System should send Push Notification (in-app notification) to user based on DDA Linking Application Status: 

Push Notification 

Push Notification Center 

Tap on push notification,  

go to page below 

  Phillip Securities Pte Ltd                                                                                                          Page 15 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Request 
Submitted 

- 

DDA Linking 

(Approved) 

  Phillip Securities Pte Ltd                                                                                                          Page 16 of 41 

_____________________________________________________________________________________________ 

DDA Deposit page 

            
 
 
 
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

3.5  DDA Deposit (Deposit Fund via DDA) 

  Phillip Securities Pte Ltd                                                                                                          Page 17 of 41 

_____________________________________________________________________________________________ 

            
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

  Phillip Securities Pte Ltd                                                                                                          Page 18 of 41 

_____________________________________________________________________________________________ 

            
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

DDA Deposit Form 

Functions/ Features 

Requirement / Criteria to apply 

DDA Deposit Form 

•  When user selects the “Deposit Fund via DDA” method, system checks if the user's account has an 

(P2 Central UI 

embedded in 

P2/P3/MyWealth) 

active DDA/GIRO Linking 

• 

If DDA/GIRO Linking exists, the DDA Deposit Form will be displayed. 

Information prompt message: 

Before displaying the DDA Deposit form, the system shall always show an Info prompt message: 

"DDA Deposit uses your GIRO linkage, you may proceed to submit the deposit request." 

P2 

P3 

The prompt shall contain a "PROCEED" button. 

Only after the user clicks "PROCEED", the system shall display the DDA Deposit form. 

  Phillip Securities Pte Ltd                                                                                                          Page 19 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

DDA Deposit Form 

P2 

P3 

DDA Deposit Form Fields: 

Field 

Account 

Type 

Criteria 

Label (read-only)  Display the current account  

linked bank name 

Label (read-only)  Display the account’s DDA/GIRO Linked bank name and 

and bank account 

bank account number 

number 

Currency 

Deposit 

Amount 

(Retrieved from CIS API (account)) 

Label (read-only)  Always show “SGD” 

Textbox input 

Format: Numeric 

  Phillip Securities Pte Ltd                                                                                                          Page 20 of 41 

_____________________________________________________________________________________________ 

            
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Default: Empty 

Mandatory: Yes 

Amount must be greater than 0 

Decimal: Up to 2 decimal allowed 

Maximum $200,000 per transaction allowed only. 

System need to validate up to maximum of $200,000 

allowed only with message “Maximum deposit amount per 

transaction is SGD 200,000.” 

Proceed 

Button 

Proceed button shall be enabled only when a valid deposit 

amount is entered. 

Upon click Proceed, the system shall validate the deposit 

amount input and proceed with the deposit submission 

process. 

Deposit Form 

Submission 

Upon Deposit Form Submission: 

•  The system sends the DDA Deposit form data to the P3 API (DDA Deposit). 

•  The P3 API sends the deposit request to DBS FAST Collection API for DDA deposit processing 

P3 API Interaction with 

•  The interaction between the P3 API and DBS FAST Collection API is a key component of the DDA 

DBS 

deposit process.  

The following outlines the flow and criteria: 

DBS API send result msg (Synchronous)  

Step 

Description 

  Phillip Securities Pte Ltd                                                                                                          Page 21 of 41 

_____________________________________________________________________________________________ 

            
   
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

1. Request Submission  The P3 API processes the deposit form data submitted by the user and 

sends the deposit request to DBS FAST Collection API for further 

processing. 

2. Request Handling 

The DBS system receives the request through its FAST Collection API and 

processes the DDA deposit transaction. 

3a. Status Response 

DBS returns the API response with transaction status = Request Submitted 

back to the P3 API 

System display [Deposit Request Submitted Page] (P2 Central UI) to user 

P3 

P2 

DBS API send result msg (Asynchronous) 

Step 

Description 

3b. Status Response 

After DBS API System processed, DBS API system will send the result msg 

with transaction status back to the P3 API System, which may include one 

of the following outcomes:  

- Approved  

  Phillip Securities Pte Ltd                                                                                                          Page 22 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

- Rejected 

The P3 API System is responsible for interpreting and responding to the deposit status returned by DBS. 

The system handles each status scenario on below: 

DDA Deposit Status 

P3 API system do below 

Request Submission 

Send Push Notification 

System send push notification (DDA Deposit – Request Submission) to user 

Approved 

Call GBO API to posting transaction 

Rejected 

Send Push Notification 

Send Push Notification 

Push Notification (In-App Notification)  -  (P2/P3/MyWealth) 

DDA Deposit: 

System should send Push Notification (in-app notification) to user based on DDA Deposit Status: 

Push Notification 

Push Notification Center 

Tap on push notification,  

go to page below 

  Phillip Securities Pte Ltd                                                                                                          Page 23 of 41 

_____________________________________________________________________________________________ 

            
 
  
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Deposit 

Request 
Submitted 

Deposit 
Received 

(Unsuccessful) 

Live Cash Balance page 

Click “Contact Info” button 

Contact us page 

  Phillip Securities Pte Ltd                                                                                                          Page 24 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Deposit 
Received 

(Successful) 

Click “View Details” button 

Live Cash Balance page 

  Phillip Securities Pte Ltd                                                                                                          Page 25 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
 
   
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

GBO Posting Transactions 

DDA Deposit: 

Functions/ 

Requirement / Criteria to apply 

Features 

GBO 
Posting 
Transactions 

Upon received DDA Deposit “approved” status response from DBS API: 

•  Front Office (FO) system / P3 API system will call  GBO API to proceed with posting transaction 

•  Upon receiving the request, GBO API shall call RPS API to insert the transaction into the RPS placeholder 

•  The RPS job shall process the transaction every 5 minutes  

•  The respective system shall do posting transactions according to their supported account type: 

o  For M, C, KC, CC accounts → GBO shall posting to GBO system (Phase 1) 

o  For S2, UTW accounts → Synergy BO shall posting to Synergy BO (Phase 2)  

o  For V accounts → PFN system shall posting to PFN (Phase 2) 

DDA deposit - 24 hours deposit  

  Phillip Securities Pte Ltd                                                                                                          Page 26 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

3.6  Delink DDA Linking 

  Phillip Securities Pte Ltd                                                                                                          Page 27 of 41 

_____________________________________________________________________________________________ 

            
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Functions/ Features  Requirement / Criteria to apply 

Bank A/C Information 

User can navigate to Bank A/C Information page to view DDA detail and to Delink the DDA 

P3 

Bank A/C Information page 

P2 

P3 

P2 

  Phillip Securities Pte Ltd                                                                                                          Page 28 of 41 

_____________________________________________________________________________________________ 

            
 
 
 
 
 
 
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Field 

Type 

Criteria 

GIRO / DDA Bank A/C 

Label (read-only) 

Display GIRO/DDA Linked bank account no. 

GIRO / DDA Bank  

Label (read-only) 

Display GIRO/DDA Linked bank name. 

Delink DDA 

Button 

[Delink DDA] button should be displayed only when 

current acct had GIRO/DDA Linking 

Upon click [Delink DDA], the system redirected to  

DDA Details Page 

DDA Details Page 

 (Data source of GIRO/DDA of account get from CIS) 

Field 

Type 

Criteria 

Bank Country / Region 

Label (read-only) 

Display as “Singapore” 

  Phillip Securities Pte Ltd                                                                                                          Page 29 of 41 

_____________________________________________________________________________________________ 

            
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Bank Name 

Label (read-only) 

Display the current acct 

GIRO/DDA Linked bank name. 

SWIFT Code 

Label (read-only) 

Display the current acct 

Bank Account Number 

Label (read-only) 

Display the current acct 

GIRO/DDA Linked bank account no. 

Delink 

Button 

Click [Delink] shall prompt a confirmation pop-up 

GIRO/DDA Linked bank SWIFT Code 

Delink Confirmation 

On click of Delink button, system shall: 

Pop-Up 

P3 

P2 

Prompt user with confirmation Pop-Up message: “Are you sure you want to remove the linked DDA bank 

account?” 

Provide user actions: Confirm or Cancel. 

On Cancel, the system shall close the pop-up without changes. 

On Confirm, the system shall proceed submit delink DDA 

Delink Submission 

Upon the user clicks confirm to Delink: 

•  FO API shall call CIS API to remove the DDA/GIRO linkage in CIS 

  Phillip Securities Pte Ltd                                                                                                          Page 30 of 41 

_____________________________________________________________________________________________ 

            
  
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

•  On success delink: 

o  FO API should update DDA/GIRO status in FO DB 

o  User shall be redirected back to Bank A/C Information Page. 

o  System display Toast Message: “You have successfully delinked your DDA bank account.” 

P3 

P2 

3.7  Finance Report Requirement (To discuss with Finance staff) 

Functions/ Features  Requirement / Criteria to apply 

  Phillip Securities Pte Ltd                                                                                                          Page 31 of 41 

_____________________________________________________________________________________________ 

            
 
 
     
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

Finance Report for 

Current eNETS: 

Finance 

FO -> generate recon report -> Finance staff and Ops staff    (get requirement from finance Katherine and 

alvin) - for recon 

eDDA: 

Finance report to be discuss with Finance staff 

  Phillip Securities Pte Ltd                                                                                                          Page 32 of 41 

_____________________________________________________________________________________________ 

            
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

4  Non Functional Requirements 

4.1  Performance 

NA 

4.2  Operational Requirements 

NA 

4.3  Security/Control Requirements 

NA 

4.4  Service Requirements 

NA 

4.5  User Training Requirements 

   NA 

5  Assumptions and Limitations 

NA 

  Phillip Securities Pte Ltd                                                                                                          Page 33 of 41 

_____________________________________________________________________________________________ 

            
 
 
Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1 

6  Appendix 

DBS API 
DBS 
FAST Collection API  
(DDA Deposit) 

7  Acceptance Form  
Project Name : 
Document Name 
Company Name : 
Name of Management : 
Requested By* : 

DBS API Spec 

DDA Linking and DDA Deposit Project 
URS  DDA Linking and DDA Deposit 
Phillip Securities Pte Ltd 

Alvin Ter, Chee Wee (Payment, Project Owner) 
Esther (CX / CEU/ P3) 
Tsui Yin (P2) 
Shawn (MyWealth) 
Gini (APU/CIS) 
Carina Goh 

Designation : 
Requested By Signature/Date : 
Requirement Documented & 
Designed By: 
Designation : 
Approved By (System Owner): 
Designation : 

Vincent Tiong (ITBA) 

Business Analyst (ITBA) 

  Phillip Securities Pte Ltd                                                                                                          Page 34 of 41 

_____________________________________________________________________________________________ 

DBS SG Fast and Paynow Spec_v4.2.0 1 (1).pdf            
  
 
 
 
 
 
 
 
 
