# Gami   Amalgamated Trade
Source: `Gami - Amalgamated Trade.pdf` (13 pages)
Extracted: 2026-06-09

---

## Page 1

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 13

PHILLIP SECURITIES PTE LTD

<Gami – Amalgamated Trade>

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
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 13

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
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 13

Document Revision History

Document Title: ITSR 328459 Gami – Amalgamated Trade URS

Version Revised
by
Effective Date Summary of Change Reason for
change
1.0

---

## Page 4

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 13

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
Anita Chavan Senior System Analyst

1.5 Glossary
No Term Meaning
1 Amalgamated An "amalgamated trade" refers to the
combining of multiple, separate buy or sell
orders for the same asset made within a single
trading day into one consolidated transaction.
This process primarily helps investors save

---

## Page 5

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 13

money on brokerage fees and simplifies
portfolio management.

2

2 Problem/Purpose Statement
2.1 Background
An "amalgamated trade" refers to the combining of multiple, separate buy or sell orders for
the same asset made within a single trading day into one consolidated transaction. This
process primarily helps investors save money on brokerage fees and simplifies portfolio
management
Each product coupon should only count for 1 trade. Amalgamated trade = 1 trade. Currently,
client can make e.g. 10 separate trades of the same stock, and it will count for each coupon.
At the end of the day, only 1 trade is made, but 10 coupons are redeemed. This is not the
correct use case of coupons as it is supposed to be 1 coupon for 1 settled trade.
2.2 Problem
• We want to prevent clients from trading same stock in one day and claim coupons
with it.
2.3 Purpose
• A form of reward to encourage clients to make more trades with us.

2.4 Project Scope
• Update the GBO processing to allow Amalgamated trade. Coupons that are not used
will be reset
2.5 User Classes and Characteristics
The following table describes the user roles, which will use the system
User Class Activities
P3 Multiple coupon transaction in GBO

---

## Page 6

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 13

3 System Features
3.1 The New Journey
Amalgamated Trade for Gamification coupons

3.1.1 Explaining scenarios
Figma: n/a
JIRA: https://psplit.atlassian.net/browse/GAMI-1452 - GBO error report email
PC case: n/a

Overview:
What is Amalgamated trade:
 Today-
1. BUY $100 worth of ABC stock
2. BUY $50 worth of ABC stock
3. BUY $200 worth of ABC stock
 End of today-
System Amalgamates to $350 worth of ABC stock (3 trades place, 1 trade settlement)
Conditions for auto-amalgamate:
1. The trades must be done on the same trading day.
2. The trades must be of the same stock.
3. The trades must be of the same action. (A buy action can be amalgamated with another buy
action regardless of the trading mode)
4. The trade is done through the same account.
5. The payment mode must be the same. (cash or CPF)
6. The settlement currency must be the same. (USD or SGD or HKD or AUD or MYR or JPY)

Amalgamated Trade with Coupon Current behaviour:

 Today-
1. Activate S$10 Stock coupon 1, activate S$10 stock coupon 2, activate S$10 stock coupon 3
2. BUY $100 worth of ABC stock
3. BUY $50 worth of ABC stock
4. BUY $200 worth of ABC stock
 End of today-
• System Amalgamates to $350 worth of ABC stock (3 trades place, 1 trade settlement)

---

## Page 7

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 13

• Coupon status ->
o Stock coupon 1 - redeemed and rebated,
o Stock coupon 2 - redeemed and rebated,
o Stock coupon 3 - redeemed and rebated
• Client gets $30 rebates
• Coupons are sent in real time
• Coupons are sent individually
• Batch process is at the end of the day SGtime – 7.40pm

Description
Acceptance Criteria to do:
Amalgamated trade with coupon (WHAT WE WANT):
 Today-
1. Activate S$10 Stock coupon 1, activate S$10 stock coupon 2, activate S$10 stock coupon 3
2. BUY $100 worth of ABC stock
3. BUY $50 worth of ABC stock
4. BUY $200 worth of ABC stock
 End of today-
• System Amalgamates to $350 worth of ABC stock (3 trades place, 1 trade settlement)
• Coupon status ->
o Stock coupon 1 - redeemed and rebated
o Stock coupon 2 - activated status only but no redeem
o Stock coupon 3 - activated status only but no redeem
• ONLY stock coupon 1 redeemed. (because only 1 trade settlement)
• Client gets only $10 rebates
• If no amalgamation , individual coupon is processed as per normal.
• End of day Batch job SGT 7.40pm
• Batch job other markets ???

Note:
• As long as it is a amalgamated trade, it can be in any currency
• US market no amalgamation but trades can be settled in USD
• "1 coupon for 1 settled trade" is business rule
• Amalgamated trade must be with the same counter
• The first coupon will be used based on date and time of the first coupon
• Product Coupon Only (cash coupon not available)

---

## Page 8

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 13

• Coupon is configured by Market-level
• Coupon is judged by First In First Out FIFO
• Coupon is configured by Market-level
• Coupons are sent in real time
• Coupons are sent individually
• Apply only once per counter

GBO Error report email when transaction fails : https://psplit.atlassian.net/browse/GAMI-1452
•

3.1.2 P3 - Changes
Figma: n/a
Jira: n/a
PC Case: n/a
Overview: n/a

Steps UI/UX Description
1 n/a
Changes to P3 side:
Create a scheduler job run every 7PM to combine all PROCCESING
records (00AM to 07PM) rebate amount into 1 request of
PostTransaction API for each user
• Current:
o Data is sent in Real Time
o Send Post Transfer API: target account and amount
• New journey: User scheduler for once-a-day batch processing
• Coupon is configured by Market-level
Note: Any transaction after 7pm will be processed the next day.
• How to send the data over?
• Coupons are grouped by
o Market
o Counter
o Campaign
o How to differentiate the groups

---

## Page 9

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 13

<Illustration>

INK - HERE

---

## Page 10

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 13

UI Controls:
UI Control
/ Purpose Defaults / Remarks

---

## Page 11

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 13

4 Interface Requirements

Not requiremed. All work is back end – GBO and API

NOTE: There is a general misconception that interface requirements refer to user
interface design instead of cross system interfaces like API’s>

5 Non-Functional Requirements

N/A
<This section describes the non -functional requirements related to activities such as
security, audit and system housekeeping. >

5.1 Performance

<System Name> is expected to have:

Fast Loading of pages – each page is expected to complete loading no more than 3
seconds.  During the loading period, P3 must provide animated loading image to inform
users that page is still loading.

Pages that has grid or table and expected to have huge amount of data to be loaded,
lazy loading or pagination must be applied.

For exporting of data where loading time may expect to hear more than 3 seconds,
website must show a progress bar to provide meaningful info on how much percentage
of data has been downloaded.

Scalable – to meet the 10x demand, P3 must remain stable and fast regardless whether
number of simultaneous users grow by 10 times.  Scalability is all about handling
growth. Web App, APIs and database architecture must be in line with this concept.

5.2 Operational Requirements

<System Name> is expected to have:

High-availability – system must remain online 24/7 .  Hardware and software are
expected to fail due to unforeseen circumstances, but applying HA concept by having

---

## Page 12

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 11 of 13

multiple instance of the application will help reduce or avoid the possibility of downtime
due to run-time errors.

5.3 Security/Control Requirements

N/A

<System Name> is expected to have:

Secured – system is exposed to the internet therefore <System Name> , APIs and
databases must be well -protected against different security threats that exploit
vulnerabilities in an application's code

5.4 Service Requirements

<This section describes the Service delivery requirements of the system, including
archiving, backup & Recovery and BCP etc. List down the reports, which required the
tape backup. >

5.5 User Training Requirements

<Any user training required for this project?>

6 Assumptions and Limitations

<List down all the assumptions and Limitations for this project.>

7 Reference
Use below as reference:

1. Phillip Connect Case:

2. Mock-up Layout and Design:

8 Acceptance Form
Project Name: <Project Name>

---

## Page 13

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 12 of 13

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
