# Gami   Cash Coupon Global Admin
Source: `Gami - Cash Coupon Global Admin.pdf` (15 pages)
Extracted: 2026-06-09

---

## Page 1

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 15

PHILLIP SECURITIES PTE LTD

<Gami – Cash Coupon – Global Admin>

User Requirement Specifications

For: Phillip Securities Pte Ltd Project Ref: ITSR ???
Author: Nizam Shariff Doc Ref: URS
Proj Mgr: Nizam Shariff & Aliaa

Version: 1.0
Date: 11 May 2026 Classification: <Newb Minor
Enhancement>
To :    Edwin Soh, Takako, Vernice Cc:           Ronnie

---

## Page 2

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 15

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

## Page 3

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 15

Document Revision History

Document Title: ITSR 328459 <Project Title> URS

Version Revised
by
Effective
Date
Summary of Change Reason for
change
1.0

---

## Page 4

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 15

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
The following committee will need to provide their approval for this project to
commence.
Name Position Signature Date
Edwin Soh Marketing Executive
Vernice Assistant Marketing Manager
Masumura Takako Director Marketing
Hein Myo Than System Analyst

1.5 Glossary
No Term Meaning
1 Cash coupon A product coupon that will give client cash
rebate into their account, Available in SGD,
HKD and USD
2

---

## Page 5

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 15

2 Problem/Purpose Statement
2.1 Background
• A new product coupon that will give cash credit to the client . Cash coupon has
already been completed in UAT. We need a mechanism to allow the marketing team
to approve or reject a cash coupon. In case there is any error, we have the option
to stop the reject the cash coupon.
• Cash coupon was developed in ticket https://psplit.atlassian.net/browse/GAMI-1446
2.2 Problem
• Incase there is human error or the wrong amount is given, then via Global Admin,
we have an option to accept or reject coupon
2.3 Purpose
• Cash coupon is a form of reward to encourage clients to make more trades with us.
The Admin portal will safe guard the coupons being given out

2.4 Project Scope
• Develop Global Admin portal for cash coupon, liaise with P3 and GBO for data
pull/push
2.5 User Classes and Characteristics
The following table describes the user roles, which will use the system
User Class Activities
P3 Multiple coupon transaction in push to Global Admin

3 System Features
3.1 The New Journey
Global Admin

3.1.1 P3 to cash coupon
Figma: n/a

---

## Page 6

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 15

JIRA: n/a
PC Case:
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/cases#/de
tail/29290/555885
Overview: Cash coupon was developed in ticket
https://psplit.atlassian.net/browse/GAMI-1446 , We also added GBO validation in ticket:
https://psplit.atlassian.net/browse/GAMI-1521 ,
This new project is to add a journey to minise risk when issueing cash coupon, where
by from P3 to Global Admin to GBO. This is to add a layer of risk management for cash
coupon approval.

Acceptance Criteria:

AC1 – P3 to send Cash Coupon data to Global admin
AC2 – In Global Admin, Marketing team can approve or reject the Cash Coupon
AC3 – If Global Admin approve then send data to GBO
AC4 – If Global Admin reject then send data to P3 , marketing team will update the user
AC5 – GBO will credit the user $X amount,
AC6 – if GBO reject the cash coupon or has error, then update marketing team via email
Steps UI/UX Description
1 n/a Coupon flow:
From P3
• User awarded a coupon
• User redeem a coupon
o While waiting for approval – in P3 show coupon status as
“pending”
o If rejected Coupon will remain as Pending status >
marketing will contact user directly

Global Admin
• Marketing team approve – send to GBO
• In GA When approve show – Approved
• Marketing team reject – send to P3 (no need to send to GBO)
• In GA When rejected show – Rejected

GBO
• Credit user account with cash $x amount
• If GBO reject then send email with error and reason
o If rejected Coupon will remain as Pending status  >
marketing will contact user directly
• If GBO is down then do retry mechanism
• GBO will send email if error for any coupon

Note:
• Marketing will only have access to Gamification module
• All Cash Coupon will be manually approved. No Auto approval
needed for this URS
• Use Current login account

---

## Page 7

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 15

  User flow:  P3 to Global admin to GBO

APIs and Database:
P3:
• Gami API
• Task API
• P3 Db
• Mambo API
• GBO API
Global Admin:
• task/gamification/pendingrequests
• task/gamification/approverequest
GBO
• task/gamification/updatestatus

---

## Page 8

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 15

---

## Page 9

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 15

NEW FLOW - LINK

3.1.2 Global Admin Portal
Jira: n/a

---

## Page 10

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 15

Figma: n/a
Overview: Global Admin to build a section for Gamification to allow marketing team to
approve or reject a cash coupon

Acceptance Criteria:

AC1 – Create a section for Gamification in menu bar, marketing team can only access this section, access
given by Global Admin team
AC2 – When user clicks on gamification, there will see the following fields
• Phillip ID
• UUIID
• Date
• Time
• Coupon Name
• Amount
• Currency
• Fullname of user
• Email of user
• Approve/Reject dropdown menu

AC3 – User can click on dropdown menu, choose to approve or reject the cash coupon
• When Approved > send to GBO > click Submit
• When Approved > high light Approved in Green
• When Rejected > Send to P3 > marketing team will inform the user > Click Submit
• When Rejected > highlight Rejected in Red
• If user has not click submit, then user can change the status

AC4 – To help search, Add Filter by:
a. Username
b. Email
c. UUID
d. Coupon Name
e. Amount
f. Data
g. Time
Add Sort By:
h. Old to new
i. Alphabetical
j. Amount high to low
k. Amount low to high
AC5 – Page filter can show up to 10 rows per page.
AC6 - The user can choose page 1,2,3 ... or click < or > to move to next page or return to previous page

Other requirements:
1. Data is sent in real time from P3 to Global Admin
2. Marketing team can log in anytime to approve or reject the cash coupon
3. Data is stored in P3 database
4. For rejection from GBO, GBO will handle it internally.
5. For any validation error, P3 API will receive the validation error message under ‘errorTransactions’
section.
6. Marketing team can only access Gamification section (Permission Control)

---

## Page 11

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 15

Design: (Canva)

When Approved:

When Rejected:

---

## Page 12

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 11 of 15

Coupon Flow:

<Illustration>

---

## Page 13

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 12 of 15

UI Controls:
UI Control
/ Purpose Defaults / Remarks

4 Interface Requirements

New updates for Global Admin. All other work is back end – P3, Global Admin and GBO.

NOTE: There is a general misconception that interface requirements refer to user
interface design instead of cross system interfaces like API’s

5 Non-Functional Requirements

N/A

5.1 Performance

P3 and Global Admin is expected to have:

Fast Loading of pages  – each page is expected to complete loading no more than 3
seconds.  During the loading period, P3 must provide animated loading image to inform
users that page is still loading.

Pages that has grid or table and expected to have huge amount of data to be loaded,
lazy loading or pagination must be applied.

For exporting of data where loading time may expect to hear more than 3 seconds,
website must show a progress bar to provide meaningful info on how much percentage
of data has been downloaded.

---

## Page 14

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 13 of 15

Scalable – to meet the 10x demand, P3 must remain stable and fast regardless whether
number of simultaneous users grow by 10 times.  Scalability is all about handling growth.
Web App, APIs and database architecture must be in line with this concept.

5.2 Operational Requirements

P3 and Global Admin is expected to have:

High-availability – system must remain online 24/7 .  Hardware and software are
expected to fail due to unforeseen circumstances, but applying HA concept by having
multiple instance of the application will help reduce or avoid the possibility of downtime
due to run-time errors.

5.3 Security/Control Requirements
P3, Global Admin and GBO is expected to have:

Secured – system is exposed to the internet therefore P3, Global Admin and GBO APIs
and databases must be well -protected against different security threats that exploit
vulnerabilities in an application's code

5.4 Service Requirements

n/a

5.5 User Training Requirements

n/a

6 Assumptions and Limitations

n/a

7 Reference
Use below as reference:

---

## Page 15

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 14 of 15

1. Phillip Connect Case:

2. Mock-up Layout and Design:

8 Acceptance Form
Project Name: Gami – Cash Coupon - Global Admin
Document Name ITSR 000000 Cash Coupon - Global Admin URS
Company Name: Phillip Securities Pte Ltd
Name of Management:
Requested By:
Requested By Signature/Date:
Approved By (System Owner):
Designation :

9 Disclaimer
n/a
