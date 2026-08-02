# URS P3 Stock Trade ticket   Lite mode
Source: `URS_P3_Stock Trade ticket - Lite mode.pdf` (13 pages)
Extracted: 2026-06-09

---

## Page 1

PHILLIP SECURITIES PTE LTD

User Requirement Specification
Implement Lite Mode of Trade Ticket

Front-End ITSR
POEMS Mobile 3 (M3)

For: Phillip Securities Pte Ltd Project Ref: Refer ITSR above
Author: Thuy Dao (P3 Business Analyst) Doc Ref:
  Version:
Date: 15 May 2026 Classification: Requirement
T o  :

C c :

---

## Page 2

1.1.1 Table of Contents

1.1.1 Table of Contents ...................................................................................................................................... 1
Document Revision History ................................................................................................................................. 2
2 INTRODUCTION ................................................................................................................................... 3
2.1 PURPOSE OF DOCUMENT .................................................................................................................................... 4
2.2 DOCUMENT CONVENTIONS ................................................................................................................................ 4
2.3 INTENDED AUDIENCE AND READING SUGGESTIONS .......................................................................................... 4
3 PROBLEM/PURPOSE STATEMENT ................................................................................................... 4
3.1 BACKGROUND / PROBLEM STATEMENT ............................................................................................................. 5
3.2 PURPOSE / OBJECTIVE ........................................................................................................................................ 5
3.3 PROJECT SCOPE ................................................................................................................................................. 5
4 SYSTEM FEATURES ........................................................................................................................... 5
4.1 IMPLEMENT LITE MODE FOR TRADE TICKET ...................................................................................................... 5
4.1.1 Basic rules ................................................................................................................................................. 5
4.1.2 SG Market ................................................................................................................................................. 6
4.1.3 US Market ................................................................................................................................................. 6
4.1.4 HK Market ................................................................................................................................................. 7
4.1.5 Other Markets ........................................................................................................................................... 8
4.2 SWITCH MODE IN TRADE TICKET ....................................................................................................................... 9
4.3 SAVE PREFERRED CLIENT’S SETTING ............................................................................................................... 10
4.4 MEASURE THE USAGE OF LITE MODE ............................................................................................................... 11
5 NON FUNCTIONAL REQUIREMENTS .............................................................................................. 12
5.1 PERFORMANCE................................................................................................................................................. 12
5.2 OPERATIONAL REQUIREMENTS ........................................................................................................................ 12
5.3 SECURITY/CONTROL REQUIREMENTS .............................................................................................................. 12
5.4 SERVICE REQUIREMENTS ................................................................................................................................. 12
5.5 USER TRAINING REQUIREMENTS ..................................................................................................................... 12
6 ASSUMPTIONS AND LIMITATIONS ................................................................................................. 12
7 REFERENCE ...................................................................................................................................... 12
8 APPENDIX .......................................................................................................................................... 12
9 ACCEPTANCE FORM ........................................................................................................................ 12

---

## Page 3

Document Revision History
Document Title:

Version Revised by Effective Date Summary of Change Reason for change
1.0 Thuy Dao (P3) 15 May 2026 New Creation Initial creation.

---

## Page 4

2 Introduction
2.1 Purpose of Document
This document records the requirements, both functional and non -functional, of the product to
be developed. It serves as a contract between the customer/user and the developers. It is also an
essential input to activities in analysis, design and testing.
2.2 Document Conventions
The following font colours shall have the corresponding meanings:
• Blue  - Reference to an external document or file
• Red  -  Important/critical point
• Green  - Unconfirmed or undetermined point
• Highlight  - New or changed point from previous document version
2.3 Intended Audience and Reading Suggestions
This document provides a reference for the project team members. It is meant for, but not limited
to:
• Project Steering Committee
• Project Sponsor
• Quality Assurance Engineers
• Business Analysts
• System Owners
• Users
• Functional Managers with employees assigned to project teams
• and IT development team.

Reader Group Sections
Project Steering Committee Problem\Purpose Statement
Project Sponsor Problem\Purpose Statement
Quality Assurance Engineers System Features, Interface Requirements, Non -functional
Requirements
Business Analysts  System Features, Interface Requirements, Non -functional
Requirements
System Owners  System Features
Users  System Features
Functional Managers  System Features
IT Development Team System Features, Interface Requirements, Non -functional
Requirements

---

## Page 5

3 Problem/Purpose Statement
3.1 Background / Problem Statement
o Complex UI for Less Experienced Users: The current POEMS Mobile 3 (M3) Stock Trade Ticket
presents a high volume of advanced market data fields (such as Volume, Buy Volume, Sell
Volume, and Unit Share prices) and advanced conditional order types by default. While
necessary for professional traders, this dense interface can overwhelm retail, new, or less-
experienced users who only require basic trading capabilities.
o Friction from Secondary Settings: Secondary trading fields (e.g., specific Payment Modes,
Settlement Currencies, or Session and Validity rules) are constantly visible. This clutter creates
unnecessary friction, making the interface less intuitive for the majority of everyday retail
investors.
o Lack of Interface Personalization: Currently, users lack the flexibility to choose a simplified user
interface (UI) layout that aligns with their personal trading expertise, preventing a tailored and
seamless user experience.
3.2 Purpose / Objective
o Introduce a Simplified "Lite Mode": Implement a streamlined "Lite Mode" variant of the Trade
Ticket across all supported markets (including SG, US, HK, and future expansions) specifically
optimized for retail and less experienced investors.
o Reduce Cognitive Load: Declutter the trading interface by removing intensive data points (like
Counter Search and Vol/Bvol/Svol) and condensing advanced secondary configuration fields
under a collapsible "More Settings" menu.
o Restrict Order Types Safely: Limit available choices in Lite Mode to basic execution types—such
as only Limit Orders for SG and other markets, and Limit & Market Orders for US and HK
markets—while maintaining an easy, intuitive pivot path to "Pro Mode" if a user attempts to
select complex conditional orders.
o Enhance User Retention via Settings Persistence: Automatically save and persist the user's
preferred layout choice (Lite vs. Pro mode, as well as the expand/collapse state of "More
Settings") directly on their device to eliminate repetitive setup actions during future app
sessions.
o Enable Data-Driven Optimization: Establish telemetry logging via GA4 and Appsflyer during the
order review phase to track exact order volume trends between Lite and Pro modes, allowing
product management to prioritize future feature development for the majority user base.
3.3 Project Scope
• In the scope:
o Trade of Stocks (EQ & ETF)
o All existing markets & other markets which be deployed in the future.
• This project focuses purely on UI rearrangement without altering any downstream order validation,
back-end account validation, Field behaviors/validation or review screen behaviors .... only focus on
user experience (UX), UI layout flexibility, and data tracking.
4 System Features
4.1 Implement lite mode for Trade Ticket

---

## Page 6

4.1.1 Basic rules
• Lite mode is applicable for Limit Order (LO) and Market Order (MO) only. Other
advanced/conditional order types are available in Pro mode.
• Position important information such as Quantity, Price, and Amount in the main section. Other
information is in a collapsible section “More settings”.
4.1.2 SG Market

Scope of Change Pro mode Lite mode
- Remove Counter Search
- Remove Vol/ Bvol/ Svol
- Remove Unit Share
prices
- Remove Force Key

- Secondary fields (Order
Type, Payment Mode,
Settlement Currency,
Validity) that are not
used by majority of the
new/ less experienced
users are placed under
‘More Settings’.
- The section collapsed
by default if cannot find
the preferred setting
saved in the device.

- Only Limit for Lite
Mode.
- To trade other
conditional orders,
need to switch to Pro
Mode

4.1.3 US Market
Scope of Change Pro mode Lite mode

---

## Page 7

- Only display the current
session prices
- Remove Counter Search
- Remove Vol/ Bvol/ Svol

- Secondary fields (Order
Type, Session,
Settlement Currency,
Validity) that are not
used by majority of the
new/ less experienced
users are placed under
‘More Settings’.
- The section collapsed
by default if cannot find
the preferred setting
saved in the device.

- Only Limit & Market
Order for Lite Mode.
- To trade other
conditional orders,
need to switch to Pro
Mode

4.1.4 HK Market
Scope of Change Pro mode Lite mode

---

## Page 8

- Remove Counter Search
- Remove Vol/ Bvol/ Svol

- Secondary fields (Order
Type, Settlement
Currency, Validity) that
are not used by
majority of the new/
less experienced users
are placed under ‘More
Settings’.
- The section collapsed
by default if cannot find
the preferred setting
saved in the device.

- Only Limit & Market
Order for Lite Mode.
- To trade other
conditional orders,
need to switch to Pro
Mode.

4.1.5 Other Markets

Scope of Change Pro mode Lite mode
- Remove Counter Search
- Remove Vol/ Bvol/ Svol

---

## Page 9

- Secondary fields (Order
Type, Settlement
Currency, Validity) that
are not used by
majority of the new/
less experienced users
are placed under ‘More
Settings’.
- The section collapsed
by default if cannot find
the preferred setting
saved in the device.

- Only Limit for Lite
Mode.

The details matrix: Trade ticket - Lite mode.xlsx

---

## Page 10

4.2 Switch mode in Trade Ticket
User Story:
As a(n) Product manager
I want to allow client to switch the mode of Trade ticket: Lite or Pro
so that client can select the UI they feel familiar and useful.
Acceptance Criteria:
1. From Trade ticket screen of Stock, there is a selection that allows clients to switch
between Pro mode and Lite Mode. Upon selection, system loads the respective mode
of Trade ticket.

2. For markets which support conditional order (SG, US, HK currently), client able to
switch from Lite mode to Pro mode by tapping “Switch to Pro Mode” from the
bottom sheet of Order Type, which is prompted when tap on Order Type dropbox in
UI of Trade ticket of stock.

---

## Page 11

3. Upon Switching mode, clear all entered fields to reset to default value.
4.3 Save preferred client’s setting
User Story:
As a(n) Product manager
I want to save client’s setting for Trade ticket for the next visit
so that client no need to do any additional action to view their preferred UI.
Acceptance Criteria:
1. Client’s settings for Trade ticket referring
a. Pro mode or Lite mode
b. Collapse/Expand status of “More Settings” section

---

## Page 12

2. Client’s settings should be saved in the device. Refer the table below for detail
scenario.
3. Pro mode is the default mode for all clients on first use or when no saved preference
exists.
Scenario Behavior
Change device Reset to default Pro mode
Uninstall & reinstall Reset to default Pro mode
Clear cache Reset to default Pro mode
Switch account in app (me tab) Keep previous client’s selection
Logout login with different account Keep previous client’s selection
Logout login with same account Keep previous client’s selection
SSTO Keep previous client’s selection
Kill app and open again Keep previous client’s selection
Upgrade app version Keep previous client’s selection
4.4 Measure the usage of Lite mode
User Story:
As a(n) Product manager
I want to count how many orders are placed in each mode.
so that I may concentrate more on getting better for the majority in the future.
Acceptance Criteria:
1. Log GA4 and Appsflyer upon tapping Review Order on Trade ticket of Stock
a. Client is using Lite Mode, log as Trade_Stock_Lite_mode
b. Client is using Pro Mode, log as Trade_Stock_Pro_mode

5 Non Functional Requirements
5.1 Performance
Screen loading time should each be 1 second and below
5.2 Operational Requirements
Data should be available real-time, 24/7

---

## Page 13

5.3 Security/Control Requirements
NA
5.4 Service Requirements
NA
5.5 User Training Requirements
NA
6 Assumptions and Limitations
- The change is about UI rearrangement only, no change in field behavior, field validation,
account validation, order validation/notice, page header/footer behavior, scrolling behavior ....
as mentioned in Trade ticket revamp - phase 1:
URS_Trade_Ticket_Revamp_Mobile_v1.3.docx
- No change for the “Review order” screen.
7 Reference
- Detail matrix: Trade ticket - Lite mode.xlsx
- Figma: Trade / Counter Details - Stocks – Figma
- URS of Trade ticket revamp: URS_Trade_Ticket_Revamp_Mobile_v1.3.docx
8 Appendix
         NA
9 Acceptance Form

Project Name : Implement Lite mode of Trade ticket
Document Name URS
Company Name : Phillip Securities Pte Ltd
Requested By* : Ravelo Ronnie Joy Dela Cruz
Designation : Lead Product Manager
Requested By Signature/Date :
Requirement Documented & Designed By: Thuy Dao
Designation : Business Analyst (P3 BA)
Approved By (System Owner): Ravelo Ronnie Joy De La Cruz
Designation : Lead Product Manager
