# UT Enhancements   Phase 2 2026
Source: `UT Enhancements - Phase 2 2026.pdf` (12 pages)
Extracted: 2026-06-09

---

## Page 1

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 12

PHILLIP SECURITIES PTE LTD

<UT enhancements Phase 2, 2026>

User Requirement Specifications

For: Phillip Securities Pte Ltd Project Ref: ITSR ???
Author: Nizam Shariff Doc Ref: URS
Proj Mgr: Nizam Shariff & Aliaa

Version: 1.0
Date: 11 May 2026 Classification: <Newb Minor
Enhancement>
To :    Yi Qing, Darius Lee Cc:           Ronnie

---

## Page 2

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 12

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
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 12

Document Revision History

Document Title: ITSR 328459 UT Enhancements Phase 2 URS

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
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 12

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
Darius Lee Business Development Manager –
Investment Solutions

Yi Qing Executive Digital Marketing
Michele Chee Assistant Manager – Investment
Solutions

1.5 Glossary
No Term Meaning
1 UT Unit Trust
2

---

## Page 5

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 12

2 Problem/Purpose Statement
2.1 Background
• This URS to keep ongoing minor/small improvements for the UT vertical in P3 for H2
2026

2.2 Problem
• Old or incorrect information/features that needs to be updated

2.3 Purpose
• P3 app needs to be kept up-to-date with the best UI/UX experience for UT features

2.4 Project Scope
• On going minor feature and fixes for UT vertical, scope will be address when new
items are discovered to be built.
2.5 User Classes and Characteristics
The following table describes the user roles, which will use the system
User Class Activities
P3 Enhancing UT journey
CQB Process the CKA/CAR form
CIS Trigger email reporting
UTIBO UT admin portal for newsfeed
3 System Features
3.1 The New Journey
Minor enhancements
1. Complete CKA/CAR testing and bug fix for P3
2. Add Fund Screener into Trade > UT Tab
3. UT news section – automate the updates for news (announcements) article
4. Hide minutes and hours for UT chart Filter

3.1.1 Complete CKA/CAR testing report issue – released in v50
Figma: n/a
JIRA: n/a

---

## Page 6

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 12

PC Case:
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/cases#/de
tail/25837
Overview: CKA/CAR form was released into P3 in v50.  It is not flagged off. There was
an issue with the reporting email that needed to be resolve.

Acceptance Criteria:

AC1 – As a user i want to complete the CKA/CAR form so that I can invest in Unit Trust
Steps UI/UX Description
1 n/a To do:
• Between AOP, CQB and CIS team to fix – there
is an error in the email report that should be fired
from CIS and goes to the AUP team.
• CQB team to process
• P3 only need to test once report is fixed.

Note:
• See Phillip Connect Case for reference
 n/a Logic to check - Daily Web CAR CKA email send to APU:

Daily > there is two job:

1.
PSPL_Clinfo_Daily_Send_CAR_Pending_To_APU_1
 Email Subj : [ .. ] Online assessment form answers -
{date}
 Logic : We fetch all value with [CARStatus = 'D' OR
CKACFDStatus = 'D' OR CKAUTStatus = 'D' OR
CKAForexStatus = 'D' OR CKASDDCStatus = 'D'
OR CKASPStatus = 'D']
 via SP : AcctMgmt_WS_GetCARPendingClients

 Then pass to another SP to fetch the necessary
Client's submitted data, Logic details only above,
we fetch all by that filter

2. PSPL_Clinfo_Daily_Send_CAR_Pending_To_APU_2
 Email Subj : [SIP Assessment] Pending Client List -
{date}
 Logic : We fetch all value with [CARStatus = 'D' OR
CKACFDStatus = 'D' OR CKAUTStatus = 'D'  OR
CKAForexStatus = 'D' OR CKASDDCStatus = 'D'

---

## Page 7

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 12

OR CKASPStatus = 'D']

 Based on the code, only pending status clients are
included.

•  Job 1 calls AcctMgmt_WS_GetCARPendingClients →
gets only CAR Pending NRICs, then passes them to
AcctMgmt_WS_GetCARPendingClientList → retrieves
details for those pending clients only.

•  Job 2 calls AcctMgmt_WS_GetCARPendingAllClients
→ the SP name itself indicates it returns only pending
clients (not all statuses).

  Note:
It may depend on upcoming regulatory changes
(Singapore MOF)

3.1.2 Add fund Screener into Trade > UT tab
Figma: https://www.figma.com/design/bHUGVbCzcHAR3XVB4j9f5t/DIY-Wealth?node-
id=3561-41906&t=M4F6LGJpyh7iv67V-0
Jira: n/a
PC Case:
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/cases#/de
tail/28798
Overview: The Screener is now available in me tab but lacking visibility for UT clients. So
the purpose to have this in UT tab is to Improve accessibility (no change in functionality)

Acceptance Criteria:

AC1 – Have the screener tool in the UT tab section
AC2 – When clicked, the screener tool will have the same functionality and UI/UX as the
current Screener tool in Me Tab

Steps UI/UX Description

---

## Page 8

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 12

1

To Do:
1. Add Screener (same as me tab) in
the to the Trade > UT tab.
2. Add alongside Transaction history,
outstanding positions, Cash
3. Screener Functionality will be
same as Screener in Me tab
Note:
• Be available regardless of RU
(Registered User) status

3.1.3 UT news section auto update
Figma: n/a
Jira: https://psplit.atlassian.net/browse/PWM-1909 (in UAT)
PC Case:
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/cases#/de
tail/28798
Overview: Under Markets > News > UT , the feed is broken, it does not update
automatically. The feed should come from: https://unittrust.poems.com.sg/all-about-
funds/fund-announcements/ . It has been agreed that the UT team can upload their
announcements and articles in UT admin portal which will update in P3 in realtime.

Acceptance Criteria:

AC1 – When i view, the announcements, then it should show the latest articles
AC2 – News articles and accouchements, uploaded via UT Admin Portal will be sent to
P3 in real time

Steps UI/UX Description

---

## Page 9

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 12

1

The news -article/announcements will be
uploaded into UT Admin Portal

To do:

• UT team to build new API to push
the news article into P2 Web (Kevins
Team) to ensure same article is
published in P3 and Web.

Note:
• No changes for P3 side – already
have existing API

3.1.4 Hide minutes and hours in UT chart filter
Figma:
PC Case:
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/cases#/de
tail/28798
Overview: Unit Trust updates daily, hence there is no need to show minutes and hourly
option in the filter.

Acceptance Criteria:

AC1 – When I view an UT counter then the filter options will not have minutes and hours

Steps UI/UX Description
1

To do:
• In Markets > UT. Select counter >
view chart filter.
o Remove: Minutes and Hours
o Keep: Days and Months
Note: Only for UT counter charts

---

## Page 10

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 12

As discussed with Rajesh, the charting
team will create a new screen which will
only display Days and Months

<Illustration>

UI Controls:
UI Control
/ Purpose Defaults / Remarks

4 Interface Requirements

All fixes are as per Figma design.

NOTE: There is a general misconception that interface requirements refer to user
interface design instead of cross system interfaces like API’s

5 Non-Functional Requirements

N/A
<This section describes the non -functional requirements related to activities such as
security, audit and system housekeeping. >

5.1 Performance

P3 is expected to have:

Fast Loading of pages  – each page is expected to complete loading no more than 3
seconds.  During the loading period, P3 must provide animated loading image to inform
users that page is still loading.

---

## Page 11

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 12

Pages that has grid or table and are expected to have huge amount of data to be loaded,
lazy loading or pagination must be applied.

For exporting of data where loading time may expect to hear more than 3 seconds,
website must show a progress bar to provide meaningful info on how much percentage
of data has been downloaded.

Scalable – to meet the 10x demand, P3 must remain stable and fast regardless whether
number of simultaneous users grow by 10 times.  Scalability is all about handling growth.
Web App, APIs and database architecture must be in line with this concept.

5.2 Operational Requirements

P3 is expected to have:

High-availability – system must remain online 24/7 .  Hardware and software are
expected to fail due to unforeseen circumstances, but applying HA concept by having
multiple instance of the application will help reduce or avoid the possibility of downtime
due to run-time errors.

5.3 Security/Control Requirements

N/A
P3  is expected to have:

Secured – system is exposed to the internet therefore P3, APIs and databases must be
well-protected against different security threats that exploit vulnerabilities in an
application's code

5.4 Service Requirements

<This section describes the Service delivery requirements of the system, including
archiving, backup & Recovery and BCP etc. List down the reports, which required the
tape backup. >

5.5 User Training Requirements

---

## Page 12

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 11 of 12

<Any user training required for this project?>

6 Assumptions and Limitations

<List down all the assumptions and Limitations for this project.>

7 Reference
Use below as reference:

1. Phillip Connect Case:

2. Mock-up Layout and Design:

8 Acceptance Form
Project Name: <UT Enhancements Phase 2>
Document Name ITSR 000000 <Project Name> URS
Company Name: Phillip Securities Pte Ltd
Name of Management:
Requested By: UT BU
Requested By Signature/Date:
Approved By (System Owner):
Designation :

9 Disclaimer
<If the project has been submitted by business users, the affected business department
is willing to accept the risks involved in skipping section 4 & 5 in the document.>
