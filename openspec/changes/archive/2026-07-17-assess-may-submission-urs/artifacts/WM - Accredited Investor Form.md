# WM   Accredited Investor Form
Source: `WM - Accredited Investor Form.pdf` (17 pages)
Extracted: 2026-06-09

---

## Page 1

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 17

PHILLIP SECURITIES PTE LTD

<Accredited Investor Form for P3>

User Requirement Specifications

For: Phillip Securities Pte Ltd Project Ref: ITSR 000000
Author: Nizam Shariff Doc Ref: URS
Proj Mgr: Nizam Shariff, Allen
Chen, Aliaa Syarida

Version: 1.0
Date: 13 May 2026 Classification: <New/Major
Enhancement/Minor
Enhancement>
To :    Esther Cc:           Ronnie

---

## Page 2

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 17

---

## Page 3

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 17

Table of Contents

Table of Contents .......................................................................................................................................................... 1
Document Revision History .......................................................................................................................................... 2
1 INTRODUCTION ........................................................................................................................................................ 3
1.1 PURPOSE OF DOCUMENT ................................................................................................................................... 3
1.2 DOCUMENT CONVENTIONS ................................................................................................................................. 3
1.3 INTENDED AUDIENCE AND READING SUGGESTIONS .......................................................................................... 3
1.4 COMMITTEE ......................................................................................................................................................... 3
1.5 GLOSSARY........................................................................................................................................................... 3
2 PROBLEM/PURPOSE STATEMENT .................................................................................................................... 4
2.1 BACKGROUND ..................................................................................................................................................... 4
2.2 PROBLEM............................................................................................................................................................. 4
2.3 PURPOSE............................................................................................................................................................. 4
2.4 PROJECT SCOPE ................................................................................................................................................. 4
2.5 USER CLASSES AND CHARACTERISTICS ............................................................................................................ 4
3 SYSTEM FEATURES ............................................................................................................................................... 4
3.1 FEATURE 1 .......................................................................................................................................................... 4
3.1.1 Description ..................................................................................................................................................... 5
3.1.2 Functional Requirement ................................................................................................................................. 5
4 INTERFACE REQUIREMENTS .............................................................................................................................. 5
5 NON-FUNCTIONAL REQUIREMENTS ................................................................................................................. 5
5.1 PERFORMANCE ................................................................................................................................................... 5
5.2 OPERATIONAL REQUIREMENTS .......................................................................................................................... 6
5.3 SECURITY/CONTROL REQUIREMENTS ............................................................................................................... 6
5.4 SERVICE REQUIREMENTS ................................................................................................................................... 6
5.5 USER TRAINING REQUIREMENTS ....................................................................................................................... 6
6 ASSUMPTIONS AND LIMITATIONS..................................................................................................................... 7
7 REFERENCE .............................................................................................................................................................. 7
8 ACCEPTANCE FORM .............................................................................................................................................. 7
9 DISCLAIMER ............................................................................................................................................................. 7

---

## Page 4

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 17

Document Revision History

Document Title: ITSR 000000<Accredited Investor Form for P3> URS

Version Revised
by
Effective
Date
Summary of Change Reason for
change
1.0

---

## Page 5

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 17

1 Introduction
1.1  Purpose of Document
This document records the requirements, both functional and non -functional, of the
product to be developed. It serves as a contract between the customer/user and the
developers. It is also an essential input to activities in analysis, design and testing.

1.2 Document Conventions
The following font colors shall have the corresponding meanings.
Format Convention
Blue Reference to an external document or file
Red Important/critical point
Green Unconfirmed or undetermined point
Purple New or changed points from previous document version
%Variable% Application Variables

1.3 Intended Audience and Reading Suggestions
This document is for various channel and product departments to document the
requirement to <requirement>.  System Owners of <systems> are also required to read
the document for them to confirm on  functional features that will be available for the
system.

1.4 Committee
The following committee will need to provide their approval for this project to commence.
Name Position Signature Date
Nizam Shariff Product Manager
Aliaa Syarida Business Analyst
Allen Chen Business Unit
Eileen Ng Business Unit
Edwin Almados CQB

1.5 Glossary
No Term Meaning
1
2

2 Problem/Purpose Statement

---

## Page 6

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 17

2.1 Background
The Accredited Investor (AI) Form in POEMS Singapore is a documentation process
used by Phillip Securities to recognize individuals, joint accounts, or corporate clients
who meet specific high-net-worth or income criteria, granting them access to exclusive
investment products, higher leverage, and specialized financial services
Only for individual and joint account applicants.
AI eligibility criteria:
o ≥ SGD 300,000 income (last 12 months)
o OR ≥ SGD 2M personal assets
o OR ≥ SGD 1M financial assets
• Successful applicants gain access to exclusive/high-net-worth investment products

Status & Lifecycle:
• AI status validity: 2 years
• Users can:
o Renew anytime (before expiry)
o New submission resets the validity period
o Reminder is sent via email (MoEngage)

Web link:
https://www.poems.com.sg/accredited-investor/
https://www.poems.com.sg/faq/general/online-forms/accredited-investor-application-
individual/
2.2 Problem
• Current State: There is no AI form available on P3
• The Gap: User have to go on web to complete the form
• The Solution: Create the form in the Me tab on P3 so that clients can complete the
form within P3

2.3 Purpose
To allow P3 clients to complete the AI form, so the clients can have access to exclusive
investment products, higher leverage, and specialized financial services

2.4 Project Scope
Includes, TDT, CQB, Web and Risk & Quality Department
Individual account and joint accounts only. Corporate accounts will not be included
2.5 User Classes and Characteristics
The following table describes the user roles, which will use the system
User Class Activities

---

## Page 7

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 17

P3 Client able to access Accredited Investor form
Risk and Quality Service
Department
Business Unit to Form information
CBQ Create the form
Web team Kevin – Iframe the form

---

## Page 8

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 17

3 System Features
3.1 The New Journey - Accredited Investor Form

3.1.1 Accredited Investor Form
Figma: n/a
Jira: https://psplit.atlassian.net/browse/PWM-1639
Web link: https://www.poems.com.sg/accredited-investor/
Overview:
User will navigate to the Me tab > Forms, Then click the Accredited Form icon and submit

Ste
ps
UI/
UX
Description
  Current form on WEB:
https://www.poems.com.sg/HelpCentre/OnlineForms/Declaration%20of%20Ac
credited%20Investor%20Status%20_Individual_.pdf

3.1.2 Acceptance Criteria
Acceptance Criteria
1
To Do:
In Me Tab > Form > Add Accredited Investor Form Icon, user will be
able to click into the form.
• Form will be iFrame (Internal web view or External browser) from
Web( Kevin Ng team )
• Only call the api when user opening the form
• For ApplCode please use: P3wealth
• CQB will handle the processing and approvals
• Add Back button to go back to Me tab
Note: AI Form Integration.docx

2  AI Form Integration Instructions
1. Call AI API method ‘CreateSessionToken’ to generate token. Input
and output parameters are described below.

---

## Page 9

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 17

2. Use AI form URL mentioned below in iFrame with url parameters
token and platform.

  AI Form URL
Environment URL
DEV https://aideclaration.dev.itsd/aideclaration
UAT https://aideclaration.test.itsd/aideclaration
PROD https://openacct.poems.com.sg/aideclaration

3  AI API URL
Environment URL
DEV https://10.30.21.163:9080/AIDeclarationFormService.svc
UAT https://10.30.26.82:9082/AIDeclarationFormService.svc
PROD https://172.17.3.35:9020/AIDeclarationFormService.svc

4  Create Session
URL: AI API URL/CreateSessionToken
Input
parameter
name
Type Nullable Description
AccountNo String Yes Account number if has
ApplCode String No Application Code “P3Wealth” for
P3 platform
ClientName String No Name of the client
EmailAddress String No Client email
JointClientNRIC String No Joint client NRIC/Passport
number if joint application
JointClientName String No Joint client name number if joint
application
NRICPassportNo String No NRIC/Passport number of client
SessionToken Guid No Empty guide

5
Output
parameter name
Type Description
MsgCode Int 1 is success. Other
values are errors
MsgDescription String Success message or
error details
datetime String Transaction date and
time
transactionLogID String Transaction id
Data Object Return data object

SessionToken
Guid /String Token to pass to AI
Form URL
                AccountNo String
                ApplCode  String
                ClientName String

---

## Page 10

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 17

EmailAddress
String

JointClientNRIC
String

JointClientName
String

NRICPassportNo
String

6  AI Form Iframe URL to use in Platform

URL:  AI Form URL/AIDeclaration/InitAI/?token={token received from
session creation}&platform=Wealth

7  Design:
• Update ME Tab
• User same icon as Corporate Actions
• Have ‘Back” button so that the user can click back to the Me tab
8  Rules:

User Type Access
Individual Allowed
Joint Account Allowed (client-level eligibility)
Corporate Not allowed
Registered User (no
account)
Not allowed
Status & Lifecycle
• AI status validity: 2 years
• Users can:
o Renew anytime (before expiry)
o New submission resets the validity period
o Reminder is sent via email (MoEngage)

Accounts:

  Rules:
• AI form is only for individual and joint (client level eligibility)
• When account switching, the AI form covers at client level. Any of
the accounts be used for AI.
• AI form is valid for 2 years
• Eligible only for account holders
• Registered Users are NOT eligible
• Form is not available for Corporate Accounts
• Client-level AI status (linked via NRIC)

---

## Page 11

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 17

• Joint accounts: Can declare if both eligible
• Auto-filled fields:  Name, NRIC, Email (cannot be empty)
• When the form is open and idle for X amount of time.
• API triggered only when user opens form
• When submit AI form :
o Data team – Gek Seng checks – amount of asset
o AO team – checks, must have 1m in assets

<Illustration>

UI Controls:
UI Control
/ Purpose Defaults / Remarks

4 Interface Requirements
Example Web form:

---

## Page 12

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 11 of 17

Example Web form:

---

## Page 13

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 12 of 17

---

## Page 14

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 13 of 17

---

## Page 15

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 14 of 17

NOTE: There is a general misconception that interface requirements refer to user
interface design instead of cross system interfaces like API’s>

5 Non-Functional Requirements

N/A

5.1 Performance

---

## Page 16

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 15 of 17

Fast Loading of pages – each page is expected to complete loading no more than 3
seconds.  During the loading period, P3 must provide animated loading image to inform
users that page is still loading.

Pages that has grid or table and expected to have huge amount of data to be loaded,
lazy loading or pagination must be applied.

For exporting of data where loading time may expect to hear more than 3 seconds,
website must show a progress bar to provide meaningful info on how much percentage
of data has been downloaded.

Scalable – to meet the 10x demand, website must remain stable and fast regardless
whether number of simultaneous users grow by 10 times.  Scalability is all about
handling growth. Web App, APIs and database architecture must be in line with this
concept.

5.2 Operational Requirements

High-availability – system must remain online 24/7 .  Hardware and software are
expected to fail due to unforeseen circumstances, but applying HA concept by having
multiple instance of the application will help reduce or avoid the possibility of downtime
due to run-time errors.

5.3 Security/Control Requirements
<System Name> is expected to have:

Secured – system is exposed to the internet therefore P3 and APIs and databases must
be well -protected against different security threats that exploit vulnerabilities in an
application's code

5.4 Service Requirements

<This section describes the Service delivery requirements of the system, including
archiving, backup & Recovery and BCP etc. List down the reports, which required the
tape backup. >

5.5 User Training Requirements

<Any user training required for this project?>

---

## Page 17

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 16 of 17

6 Assumptions and Limitations

<List down all the assumptions and Limitations for this project.>

7 Reference
Use below as reference:

1. Phillip Connect Case:

2. Mock-up Layout and Design:

8 Acceptance Form
Project Name: <Project Name>
Document Name ITSR 000000 <Project Name> URS
Company Name: Phillip Securities Pte Ltd
Name of Management:
Requested By:
Requested By Signature/Date:
Approved By (System Owner):
Designation :

9 Disclaimer
<If the project has been submitted by business users, the affected business department
is willing to accept the risks involved in skipping section 4 & 5 in the document.>
