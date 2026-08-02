# ITSR 369004 SMART Portfolio Phase 2
Source: `ITSR 369004 SMART Portfolio Phase 2.pdf` (25 pages)
Extracted: 2026-06-09

---

## Page 1

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 25

PHILLIP SECURITIES PTE LTD

Smart Portfolio Revamp Phase 2

User Requirement Specifications

For: Esther Project Ref: ITSR 351811
Author: Steven Li Doc Ref: URS
Proj Mgr: <Name> Version: 1.0
Date:  Classification: <New/Major
Enhancement/Minor
Enhancement>
To :                          Cc:

---

## Page 2

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 25

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
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 25

Document Revision History

Document Title: ITSR 000000 <Project Title> URS

Version Revised
by
Effective
Date
Summary of Change Reason for
change
1.0 Steven 28/05/2026 First draft New

---

## Page 4

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 25

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
Esther Tian Head, Transformation Customer
Journey

Amanda Huang Manager, UTOps
Wong Kwek Yong Co-CIO, ISD

1.5 Glossary
No Term Meaning
1
2
3
4
5

---

## Page 5

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 25

2 Problem/Purpose Statement
2.1 Background
Currently Managed account need to update PMIP form to start Regular Saving Plan
(RSP) model.

2.2 Problem
However, currently such process are still using paper submission

2.3 Purpose
To allow users to submit PMIP form from front end platform.
2.4 Project Scope
This project includes:
• Upgrade on the PMIP form: validation + upgrade to CQB4
• P3 E-Giro Journey
This project does not include:
• Upgrading PM journey
2.5 User Classes and Characteristics
The following table describes the user roles, which will use the system
User Class Activities

3 System Features
3.1 PMIP Enhancement
The purpose of PMIP form is to use this as the backend of the RSP module for
Smartportfolio.
To achieve this, we will move PMIP form into CQB4
This form should be able to be used by different systems that require to fill in the PMIP.
Here are the fields from the form:
Field Name Type Mandatory Description

---

## Page 6

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 25

Account
Number
Text input Yes The client's unique account
identifier.
Validation: Ensures that this is
unique in CQB PMIP form – To
prevent double entry.
Account Holder
Name
Text input Yes Full name of the account holder.
Should auto-populate upon valid
Account Number entry.

FA Code
(Alt/AE Code)
Text input Yes Financial Adviser code
associated with the account.

Special Code Text input No Account type code – for other
services
Read from CIS
Fund Source Dropdown Yes Source of funds for the
investment. Default value: Cash.
Possible values to include (e.g.,
Cash, SRS, CPFOA, CPFSA).

Collection
Amount
Numeric input Yes The recurring investment amount
(in SGD or applicable currency).
Must accept decimal values up to
2 decimal places.

Front End Load
% (Only for
WRAP)
Numeric input Conditional Applicable only when the plan is
under a WRAP account. Accepts
percentage values.

Frequency Radio button Yes The investment collection
frequency. Options: Monthly
(default selected) or Quarterly.

Status Dropdown Yes The status of the PMIP record.
Default value: Active. Possible
values: Active, Inactive

Status is depending on CIS
GIRO status
1. Active
2. Pend Giro – no active
pending Giro link
3. Terminated

Internal
Transfer
Dropdown No Account number under this NRIC
Field: Account number
Data: Get from CIS
Inclusion: Ledger account only
Exclude: SRS/ CPF fund source
Cash account only
Remarks Text area (multi-
line)
No Free-text field for additional
notes. Default placeholder text:

---

## Page 7

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 25

"default text".

To remove this field, not needed.

Form UI experience.
Journey from FA/ PM filling up the form themselves
1. Open form through form cabinet. - GWM approval flow or CQB
2. Fill in Acc number
3. Show the form with this account number.
a. If it is new, create a new entry.
b. If it is a current form, provide edit function to update the form.
4. Need to get client approval? - through which system?
3.2 P3 RSP Journey for SMART Portfolio
There are 3 journeys identified:
No User Journey
1 As a subscriber with no deposit
I want to start my investment and RSP today
So that I can start my investing journey

2 As a subscriber with deposit
I want to add on RSP service
So that I can dollar cost average my investment

3 As a subscriber of smart portfolio
I want to amend my RSP amount
So that I can dollar cost average with the amount that I want

3.3 Journey 1
As a subscriber with no deposit
I want to start my investment and RSP today
So that I can start my investing journey

Acceptance Criteria
- AC1 Clients can choose to deposit lumpsum or recurring
- AC2 Clients can set up recurring order amount if it is above the min investment amount
- AC3 Clients can choose when to start their investment
- AC4 Clients automatically taken to deposit flow to start this month’s investment
- AC5 Clients can only choose “Today” when they have no deposit done.
- AC6 Clients automatically taken to recurring flow right after deposit flow is successful
- AC7 Clients can choose either to set up recurring via eGiro or Internal transfer
- AC8 Clients can see bank account connected to eGiro

  New Functions

---

## Page 8

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 25

1 Starting point is after account and Smart
portfolio is set up.

Functions:
Button - “Manage”
(will be covered in next section)

Button - “Deposit Funds”
Clicking in will open the deposit
module for Smart Portfolio

2 Deposit Fund Page

New:
There will be 2 tabs:
1. Lumpsum
2. Recurring

No change for the lumpsum.
This is the same as existing module

3 Recurring Order Validation:
If no active RSP with this account,
bring to this page. Else, bring to
amendment of RSP page covered in
journey 3.

New Function:
Title: “Deposit Details”

---

## Page 9

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 25

Fields:
1. “Investment Amount (SGD)” -
Numeric (Separated by
comma example X,XXX.XX)
a. Validate with min
investment amount
2. Text description: “Min
Investment: SGD <Min
investment amount>
a. Min investment amount
from CQB form for
Smart Portfolio
3. “Frequency”: “Monthly
a. Just text
4. “When do you want to start” -2
options will be shown:
a. Today
b. Next Month

If account value is zero, only enable
“Today”

“Note”: Text as per figma

Button: Next
Validation:
If user choose Today, bring user to
deposit lumpsum amount first.
If user choose next month, bring user
to Giro Page

4 Lumpsum Deposit Flow Follow existing flow

---

## Page 10

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 25

5 Upon completion of Lumpsum flow:
Straight away bring in the Recurring flow

Pop up from bottom drawer
Style as per current P3 design
system

Title: Let’s set up your Recurring
Method
Options: These are buttons, texts on
it:
1. eGiro: Auto debit via eGiro
from your bank account
monthly
2. Internal Transfer: Transfer
funds from your other trading
account

Clicking this will bring to the confirm
Recurring Deposit page

6 Confirmation Page Show confirmation data
Button:
Text: “Button”
Function: Call Central eGiro form

---

## Page 11

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 25

7 Confirmation Page

Follow as per figma
Button: Bring back to portfolio details
page
8 Portfolio Details page with Recurring order
set up
Add a new field if:
RSP is successfully set up:
Data can take from RSP CQB form
(PMIP form above)

---

## Page 12

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 11 of 25

3.4 Journey 2
As a subscriber with deposit
I want to add on RSP service
So that I can dollar cost average my investment

Note: The journey is the same as per journey 1, however, we will select “start next month” as
the option.

Acceptance Criteria
- AC1 Clients can choose to deposit lumpsum or recurring
- AC2 Clients can set up recurring order amount if it is above the min investment amount
- AC3 Clients can choose when to start their investment
- AC4 Clients choosing start investment next month
- AC5 Clients automatically taken to recurring flow
- AC6 Clients can choose either to set up recurring via eGiro or Internal transfer
- AC7 Clients can see bank account connected to eGiro

  New Functions
1 Starting point is after account and Smart
portfolio is set up.

Functions:
Button - “Manage”
(will be covered in next section)

Button - “Deposit Funds”
Clicking in will open the deposit
module for Smart Portfolio

---

## Page 13

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 12 of 25

2 Deposit Fund Page

New:
There will be 2 tabs:
3. Lumpsum
4. Recurring

No change for the lumpsum.
This is the same as existing module

3 Recurring Order Validation:
If no active RSP with this account,
bring to this page. Else, bring to
amendment of RSP page covered in
journey 3.

New Function:
Title: “Deposit Details”
Fields:

---

## Page 14

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 13 of 25

5. “Investment Amount (SGD)” -
Numeric (Separated by
comma example X,XXX.XX)
a. Validate with min
investment amount
6. Text description: “Min
Investment: SGD <Min
investment amount>
a. Min investment amount
from CQB form for
Smart Portfolio
7. “Frequency”: “Monthly
a. Just text
8. “When do you want to start” -2
options will be shown:
a. Today
b. Next Month

“Note”: Text as per figma

Button: Next
Validation:
If user choose Today, bring user to
deposit lumpsum amount first.
If user choose next month, bring user
to Giro Page

4 No Lumpsum deposit method
Move to Lumpsum flow right away

5 Recurring flow Pop up from bottom drawer
Style as per current P3 design
system

Title: Let’s  set up your Recurring
Method
Options: These are buttons, texts on
it:
3. eGiro: Auto debit via eGiro
from your bank account
monthly
4. Internal Transfer: Transfer
funds from your other trading
account

---

## Page 15

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 14 of 25

Clicking this will bring to the confirm
Recurring Deposit page

6 Confirmation Page

Show confirmation data
Button:
Text: “Button”
Function: Call Central eGiro form
7 Confirmation Page Follow as per figma
Button: Bring back to portfolio details
page

---

## Page 16

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 15 of 25

8 Portfolio Details page with Recurring order
set up

Add a new field if:
RSP is successfully set up:
Data can take from RSP CQB form
(PMIP form above)

3.5 Journey 3
As a subscriber of smart portfolio
I want to amend my RSP amount
So that I can dollar cost average with the amount that I want

Acceptance Criteria
- AC1 Clients can manage their recurring flow by clicking Deposit Funds > Recurring
- AC2 Clients can manage their recurring flow by clicking  Manage > Amend Regular
Savings Plan

---

## Page 17

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 16 of 25

- AC3 Clients can update GIRO Linkage by clicking Manage > Update Giro Linkage
- AC4 Clients can amend their recurring amount by editing the recurring amount
- AC5 Clients will be notified when recurring amount is changed successfully
- AC6 Clients can choose to suspend their recurring orders by clicking suspend
- AC7 Client will receive notification on portfolio detail page that will say: Your Regular
Savings Plan was suspended on 05 Dec 2026. Tap Manage to resume.

Acceptance Criteria for Internal transfer
- AC1 Clients can amend deposit method
- AC2 Clients can choose which account they want to transfer the internal transfer from
- AC3 Client will know which account is being used for internal transfer in the portfolio
details

  New Functions
1 Starting point is after account and Smart
portfolio is set up.

Functions:
Button - “Manage”
Clicking it will open a pop up shown
in point 2a

Button - “Deposit Funds”
Clicking in will open the deposit
module for Smart Portfolio

Amendments of Giro can use 2a or
2b to access.

2 a Options is RSP is active Pop up drawer
Options that will be shown ONLY if
RSP is active:
1. Amend Regular Saving Plan
2. Update Giro Linkage

Amend Regular saving plan will be
written in this section

Update Giro Linkage, need to follow
the flow from Central UI form: eGiro.

---

## Page 18

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 17 of 25

2 b Deposit Fund Page

New:
There will be 2 tabs:
1. Lumpsum
2. Recurring

No change for the lumpsum.
This is the same as existing module

Clicking recurring when there is an
active RSP status, will lead you to
amendment of RSP flow

3 Amend Recurring Amount Title: Manage Recurring Order
Button:
1. Suspend
2. Amend

---

## Page 19

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 18 of 25

3 a Suspend

Pop up will be shown
Title: Stop Regular Saving Plan
Text: This will stop all future
scheduled investments. You can
restart the plan anytime.

Buttons:
1. Suspend (in grey)
2. Keep Plan (in orange)

Clicking Suspend will update our
PMIP form to inactive status.
Bring user back to Portfolio detail
page.

Keep Plan will bring client back to
Manage Recurring Order page.

3 b Edit Recurring Title: Edit Recurring
Fields:
1. “Investment Amount (SGD)” -
Numeric (Separated by
comma example X,XXX.XX)
a. Validate with min
investment amount
2. Text description: “Min
Investment: SGD <Min
investment amount>

---

## Page 20

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 19 of 25

Internal transfer option

a. Min investment amount
from CQB form for
Smart Portfolio
3. “Frequency”: “Monthly
a. Just text
4. Deposit Method: Dropdown
with 2 options
a. eGiro
b. Internal Transfer
5. Note: Follow the figma

If internal transfer is chosen:
A new dropdown box appear
Show: Account number s under this
NRIC

Field: Account number
Data: Get from CIS
Inclusion: Ledger account only
Exclude: SRS/ CPF
Cash account only

Button: Done
Function: Will amend the PMIP form
for the amount.

4 Successful update Upon successful amendment
Show Recurring page once more

Show the new invested amount

Pop up to notify clients will be shown
too.
Text: RSP amend successfully

---

## Page 21

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 20 of 25

3.6 Portfolio Details Logic
This is sharing of Portfolio Details Logic on what to show. The above journey will show
different scenarios but all should follow this logic.

---

## Page 22

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 21 of 25

Condition/ Validation Impact
If eGiro has been created
and active
Show:

Source: PMIP form
Retrieve:
1. Status
2. Date
If eGiro has been created
and inactive/ suspend
Show:
AND

Source: PMIP form
Retrieve:
1. Status
2. Date
If Internal Transfer is chosen
as source for recurring
Show:

Source: PMIP form
Retrieve:
1. Status
2. Date
If Internal Transfer is chosen
as source for recurring and
status is inactive/ suspend

Show:
AND
Source: PMIP form
Retrieve:
1. Status
2. Date

---

## Page 23

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 22 of 25

If no recurring Order is
created
Show:

Check if Acc is in the PMIP
form. If not found, means no
recurring is created.

Generic flow:
1. After form is submitted, PMIP form is submitted with these additional info as it is
SMART portfolio
a. FEL = 0
b. Form status: Pending
2. Upon form approval – CIS is updated instantaneously.
a. PMIP form status should be updated when CIS is updated. (T + Now or T + 0)

Interface Requirements

<This section describes the interface with other systems. To listdown any new
requirements for inter -system data exchange for this project. Draw the data flow
diagram.

NOTE: There is a general misconception that interface requirements refer to user
interface design instead of cross system interfaces like API’s>

4 Non-Functional Requirements

All CQB4 forms must be usable with internet. This is to cater for the contractual portfolio
managers (CPM) who might be using this withdrawal form.

4.1 Performance

Fast Loading of pages – each page is expected to complete loading no more than 3
seconds.  During the loading period, website must provide animated loading image to
inform users that page is still loading.

---

## Page 24

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 23 of 25

Pages that has grid or table and expected to have huge amount of data to be loaded,
lazy loading or pagination must be applied.

For exporting of data where loading time may expect to hear more than 3 seconds,
website must show a progress bar to provide meaningful info on how much percentage
of data has been downloaded.

Scalable – to meet the 10x demand, website must remain stable and fast regardless
whether number of simultaneous users grow by 10 times.  Scalability is all about
handling growth. Web App, APIs and database architecture must be in line with this
concept.

4.2 Operational Requirements

High-availability – system must remain online 24/7 .  Hardware and software are
expected to fail due to unforeseen circumstances, but applying HA concept by having
multiple instance of the application will help reduce or avoid the possibility of downtime
due to run-time errors.

4.3 Security/Control Requirements
Secured – system is exposed to the internet therefore <System Name> , APIs and
databases must be well -protected against different security threats that exploit
vulnerabilities in an application's code

4.4 Service Requirements

<This section describes the Service delivery requirements of the system, including
archiving, backup & Recovery and BCP etc. List down the reports, which required the
tape backup. >

4.5 User Training Requirements

<Any user training required for this project?>

5 Assumptions and Limitations

<List down all the assumptions and Limitations for this project.>

---

## Page 25

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 24 of 25

6 Reference
Use below as reference:

1. Phillip Connect Case:

2. Mock-up Layout and Design:

7 Acceptance Form
Project Name: <Project Name>
Document Name ITSR 000000 <Project Name> URS
Company Name: Phillip Securities Pte Ltd
Name of Management:
Requested By:
Requested By Signature/Date:
Approved By (System Owner):
Designation :

8 Disclaimer
<If the project has been submitted by business users, the affected business department
is willing to accept the risks involved in skipping section 4 & 5 in the document.>
