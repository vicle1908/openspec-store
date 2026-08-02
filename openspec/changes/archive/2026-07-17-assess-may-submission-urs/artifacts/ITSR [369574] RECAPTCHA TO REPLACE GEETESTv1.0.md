# ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0
Source: `ITSR [369574] RECAPTCHA TO REPLACE GEETESTv1.0.pdf` (17 pages)
Extracted: 2026-06-09

---

## Page 1

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 17

PHILLIP SECURITIES PTE LTD

GOOGLE RECAPTCHA TO REPLACE GEETEST

User Requirement Specifications

For: Google ReCAPTCHA to
Replace Geetest
Project Ref: ITSR 369574
Author: Ronnie/Kavitha  Doc Ref: URS
Proj Mgr: Kavitha Version: 1.0
Date:  Classification: <New Enhancement>
T o :                           Cc :

---

## Page 2

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 17

Table Of Contents

1.1. Document Revision History ............................................................................................................................ 2
2. INTRODUCTION ........................................................................................................................................................ 3
2.1. Purpose of Document ..................................................................................................................................... 3
2.2. Document Conventions................................................................................................................................... 3
2.3. Intended Audience and Reading Suggestions ................................................................................................. 3
2.4. Committee ....................................................................................................................................................... 3
2.5. Glossary.......................................................................................................................................................... 3
3. PROBLEM/PURPOSE STATEMENT .................................................................................................................... 3
3.1. Background .................................................................................................................................................... 3
3.2. Problem .......................................................................................................................................................... 4
3.3. Purpose ........................................................................................................................................................... 4
3.4. Project Scope .................................................................................................................................................. 5
3.5. User Classes and Characteristics .................................................................................................................. 5
4. USER REQUIREMENTS .......................................................................................................................................... 5
4.1. Phase 1 – RU Only ......................................................................................................................................... 5
4.1.1. User Story A1 – Replace GeeTest for RU only .............................................................................................. 6
4.1.2. User Story A2 - Enable/disable CAPTCHA enforcement .............................................................................. 9
4.1.3. User Story A3 – Other Front-End Control Mechanisms .............................................................................. 10
4.2. Phase 2 – Include Account Holders [AH] and build Admin Portal functionality for CEU assistance........ 10
4.2.1. User Story B1 – Replace GeeTest for AH only ............................................................................................ 10
4.2.2. User Story C1 – Changes on the admin portal ............................................................................................ 12
5. INTERFACE REQUIREMENTS ............................................................................................................................ 13
6. NON-FUNCTIONAL REQUIREMENTS (OPTIONAL) ...................................................................................... 13
6.1. Security ......................................................................................................................................................... 13
6.2. Performance ................................................................................................................................................. 13
Security/Control Requirements ................................................................................................................................... 13
6.3. Service Requirements ................................................................................................................................... 14
6.4. User Training Requirements<Optional>..................................................................................................... 14
7. ASSUMPTIONS AND LIMITATIONS................................................................................................................... 14
8. REFERENCE ............................................................................................................................................................ 14
DISCLAIMER ..................................................................................................................................................................... 15

---

## Page 3

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 17

1.1. Document Revision History

Document Title: ITSR [ 369574] <Google ReCAPTCHA to Replace Geetest>

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
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 17

2. Introduction
2.1. Purpose of Document

The overall purpose of the solution is to implement a robust fraud detection and prevention
mechanism across authentication and OTP workflows. Replace GeeTest with Google
invisible reCAPTCHA and SMS Defender Prevent non-human or suspicious activities
before OTP generation. Enable configurable security controls without system redeployment

2.2. Document Conventions
The following font colors shall have corresponding meanings.
Format Convention
Blue Reference to an external document or file
Red Important/critical point
Green Unconfirmed or undetermined point
Purple New or changed points from previous document version
%Variable% Application Variables

2.3. Intended Audience and Reading Suggestions
This document is for various channel and product departments to document the requirement for
Google reCAPTCHA implementation .  System Owners of POEMS and Wealth  are also required to
read the document for them to confirm functional features that will be available for the system.

2.4. Committee
The following committee will need to provide their approval for this project to commence.
Name Position Signature Date
 System Owner
 HOD
 Director

2.5. Glossary

No Term Meaning
1
2
3
4
5

3. Problem/Purpose Statement
3.1.  Background
The current system uses GeeTest but faces security vulnerabilities and SMS OTP abuse by bots,
leading to increased costs and risk of service disruption for legitimate users. To address this, the

---

## Page 5

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 17

system will implement Google invisible reCAPTCHA and SMS Defender to provide bots detection,
improve security, reduce OTP abuse, and ensure reliable service availability.

3.2. Problem

1. Bad actors abusing our SMS OTP leads to wastage of SMS OTP costs
2. Abuse of SMS OTP can potentially stop our SMS OTP service for other legitimate users if we
reach our spending limit for SMS OTP.  Some login/signup functionality will not be available if
that happens
3. GeeTest has some vulnerability that IT GWM team raised. It’s a security loophole that needs to
be addressed

Current Preventive Measures (as of 26 May 2026):

Front-end controlled mechanisms
1. GeeTest blocks bots/suspicious actors on login

2. On OTP input screens, there’s a 60s resend countdown timer before user can request for new
OTP – to prevent user to ask OTP multiple times rapidly

API controlled mechanisms
1. Device, Mobile, IP blocking (10 fail SMS OTP attempts on M2, M3)
2. Daily SMS limit for single device ID (total of 50 on M3)
3. Daily SMS limit for phone number (total of 50 on M3)
4. Daily SMS limit for PhillipID (total of 50 on M3)
5. Daily SMS limit for system level (total of 1000 on M2, online pwd, dormant account alert) - M3
doesn't limit (disabled but can be configured)
6. Country code on API and AWS (M2, M3, online pwd, dormant acct alert) - Blocking certain
codes
7. IP range checking (disabled due to POEMS event concern)

---

## Page 6

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 17

8. Mobile number range checking (disabled due to POEMS event concern)

See PC case link for more details -
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/cases#/detail/292
84

3.3. Purpose
The purpose of this document is to define the user requirements for implementing Google
reCAPTCHA and SMS Defender to replace the existing GeeTest solution.
It aims to:
• Address security vulnerabilities in the current GeeTest implementation
• Prevent fraudulent and bot-driven abuse of SMS OTP services
• Reduce unnecessary SMS OTP costs caused by malicious activity
• Ensure system stability and availability of OTP services for legitimate users

3.4. Project Scope

This project includes:

Phase 1 scope – Must be delivered by August or September (so that we have ample time to assess
reCAPTCHA performance in Production environment)
a) Replace GeeTest with Google reCAPTCHA and SMS Defender for Registered Users only
b) Other front-end changes

Phase 2 scope – Must be delivered by end of October 2026  (so that we can choose not to renew
contract with GeeTest whereby the renewal will be in November)
a) Replace GeeTest with Google reCAPTCHA and SMS Defender for Account Holders only
b) Admin Portal Changes

3.5. User Classes and Characteristics
The following table describes the user roles, which will use the system
User Class Activities
Registered Users (RU)

Non-account holders or general users
Use onboarding and authentication features
Characteristics:
  - May register via mobile/email
 -   Perform OTP-based verification
 -   Vulnerable to bot impersonation

Needs:
-Seamless and invisible CAPTCHA experience
-Secure OTP delivery
Account Holders Users who have done KYC and successfully opened a
POEMS account

---

## Page 7

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 17

4. User Requirements

4.1. Phase 1 – RU Only

---

## Page 8

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 17

Description

Replacement of GeeTest with Google reCAPTCHA and SMS Defender to enable multi-layer fraud
detection and secure OTP processes across user flows.

Reference:
Google Invisible reCAPTCHA- Invisible reCAPTCHA  |  Google for Developers
SMS Defender - Detect and prevent SMS fraud  |  Google Cloud Fraud Defense  |  Google Cloud
Documentation

Epic A – ReCAPTCHA Protection for RU Flows

4.1.1. User Story A1 – Replace GeeTest for RU only
As a system owner, I want the system to detect fraud/suspicious bot activity for RU using Google
reCAPTCHA instead of GeeTest, so that we can effectively block the bad actors.

---

## Page 9

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 17

Acceptance Criteria
AC1.  When an RU does any of the below activity, BEFORE asking the SMS OTP or Email
OTP, the system will no longer use GeeTest and must validate the activity on 2 layers with the
Google invisible reCAPTCHA and the SMS Defender (for SMS OTP only)

Functionality  Validate with
Google ReCAPTCHA
Validate with SMS
Defender
a) Login by Mobile + Verification Code
(SMS OTP)
Yes Yes
b) Signup by Mobile > SMS OTP  Yes Yes
c) Me Tab > Settings > Change Mobile
> SMS OTP
Yes Yes
d) Signup by Email > Email OTP Yes No
e) Me Tab > Settings > Change Email >
Email OTP
Yes  No
f) Forgot Password > Email OTP  Yes  No
g) Forgot Password > Mobile Method >
SMS OTP (RU Only) -> verify if exist
for AH also?
Yes Yescha
h) Me Tab > Settings > Activate Login
by Email>Email OTP
Yes No
i) Me Tab > Settings > Activate Login
by Mobile>SMS OTP
Yes Yes

AC2. When an RU does any of the below functions, on the Enter OTP Screen, for every click
of Resend Code, the system will no longer use GeeTest and must validate the activity on 2 layers
with the Google invisible reCAPTCHA and the SMS Defender (for SMS OTP only)

Functionality  Validate with
Google ReCAPTCHA
Validate with SMS
Defender
a) Login by Mobile + Verification Code
(SMS OTP)
b)
Yes  Yes
c) Signup by Mobile > SMS OTP

Yes  Yes

---

## Page 10

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 17

d) Me Tab > Settings > Change Mobile
> SMS OTP

Yes  Yes
e) Signup by Email > Email OTP

Yes

No
f) Me Tab > Settings > Change Email >
Email OTP

Yes

No
g) Forgot Password > Email OTP

Yes

No
h) Forgot Password > Mobile Method >
SMS OTP (RU Only) -> verify if exist
for AH also?

Yes  Yes
i) Activate Login by Email>Email OTP Yes No
j) Activate Login by Mobile>SMS OTP Yes Yes

Validation Rules

Condition  Status for reCAPTCHA
If reCAPTCHA score is below the configured threshold  FAIL
If the reCAPTCHA score is higher or equal to the
configured threshold
PASS

Condition  Status for SMS Defender
If the SMS Defender risk score is higher than the
configured risk threshold
FAIL
If SMS Defender risk score is lower or equal to the
configured risk threshold
PASS

AC3. For Email OTP, if reCAPTCHA Status is FAIL, the OTP is not sent and a pop-up with an OK
button and configurable error message “ERRORMSG-FAIL” is shown to the user and all the details
of the activity and assessments are logged in system.
AC4. For Email OTP, if reCAPTCHA status is PASS, then email OTP is sent as per normal.
AC5. For SMS OTP items, if reCAPTCHA status is FAIL or the SMS Defender status is FAIL, the
OTP is not sent and a pop-up with an OK button and configurable error message “ERRORMSG-
FAIL” is shown to the user and all the details of the activity and assessments are logged in system.

---

## Page 11

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 17

AC6. For SMS OTP items, if reCAPTCHA status is PASS and the SMS Defender status is PASS,
then the SMS OTP is sent as per normal
AC7. If the response from SDK is any other error that is not the ones mentioned to AC3 or AC5, the
OTP is not sent and a pop-up with an OK button and configurable error message “ERRORMSG-
OTHERS” is shown to the user and all the details of the activity is logged in system.

4.1.2. User Story A2 - Enable/disable CAPTCHA enforcement
As a system owner, I want to enable/disable CAPTCHA enforcement and adjust thresholds
without redeploying code
Acceptance Criteria.
AC1. Backend must allow toggling invisible reCAPTCHA validation (on/off). If OFF, A1-AC3,
 A1-AC4, will no longer block sending of OTP, no showing of error message, but the details of the
activity and assessments is still logged.

AC2. Backend must allow toggling SMS Defender validation (on/off). If OFF, A1-AC4, will no longer
block sending of OTP, no showing of error message, but the details of the activity and assessments
is still logged.

AC3. Invisible ReCAPTCHA Threshold score value must be editable via configuration API. (Initial
value 0.2)

AC4. SMS Defender Risk Threshold score value must be editable via configuration API. (initial
value 0.7)

AC5. Error messages text must be editable via configuration API database.

ERRORMSG-FAIL  “Your request can’t be completed at the moment. Please try again
later or contact support at <support contact number>”
ERRORMSG-OTHERS  “We couldn’t verify this request right now. Try again later or
contact customer support at <support contact number>”

AC6. Changes take effect without system restart.

AC7. Logs must capture email, phone number, country, reCAPTCHA score, SMS Defender risk
score, and reasons, IP, deviceID, OS, Model, datetime stamps

AC8. GeeTest can be configured ON/OFF in API to be concurrent with Google reCAPTCHA/SMS
Defender.

• If GeeTest is ON,  system will show and do validation for GeeTest AND at the same time
validate with ReCAPTCHA/SMS Defender.
• If GeeTest is OFF, the system will show and do NOT validation for GeeTest AND at the
same time validate with ReCAPTCHA/SMS Defender.

---

## Page 12

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 11 of 17

4.1.3. User Story A3 – Other Front-End Control Mechanisms

As a system owner, I want the app behavior around OTP request to be modified so that we can
effectively block the bad actors.

AC1. On the SMS OTP input screen, if the user (RU or AH) taps the Back button, the resend
cooldown timer continues running in the background. When the user returns to the SMS OTP input
screen immediately, the timer goes on as if user never left, and there’s no auto resend of new OTP,
until user requests again.

AC2. On the Email OTP input screen, if the user (RU or AH) taps the Back button, the resend
cooldown timer continues running in the background. When the user returns to the Email OTP input
screen immediately, the timer goes on as if user never left, and there’s no auto resend of new OTP,
until user requests again.

AC3. Current Resend Cooldown Timer is 60s, but the SMS notification we send to client says valid
for 2 minutes. The cooldown timer on the app must be changed to 120s

4.2. Phase 2 – Include Account Holders [AH] and build Admin Portal
functionality for CEU assistance

Epic B – ReCAPTCHA Protection for Account Holder Flows

4.2.1. User Story B1 – Replace GeeTest for AH only

As a system owner, I want the system to detect fraud/suspicious bot activity for AH using Google
reCAPTCHA instead of GeeTest, so that we can effectively block the bad actors.

Acceptance Criteria:

AC1. When an AH does any of the below activity, BEFORE asking the SMS OTP or Email OTP,
the system will no longer use GeeTest and must validate the activity on 2 layers with the Google
invisible reCAPTCHA and the SMS Defender (for SMS OTP only)

Functionality Validate with
Google
ReCAPTCHA
Validate with SMS
Defender
a) Login by Mobile + Verification Code
(SMS OTP)
Yes  Yes

---

## Page 13

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 12 of 17

b) Me Tab > Settings > Change Mobile
> SMS OTP
Yes  Yes
c) Me Tab > Settings > Change Email > Email
OTP
Yes

No
d) Forgot Password > Email OTP   Yes

No
e) Forgot Password > Mobile Method > SMS
OTP (RU Only) -
Yes  Yes
f) Enable 2FA > SMS OTP  Yes  Yes
g) Activate Login by Email > Email OTP  Yes  No
h) Activate Login by Mobile > SMS OTP  Yes  Yes

Functionality Validate with
Google ReCAPTCHA
Validate with SMS
Defender
a) Login by Mobile + Verification Code
(SMS OTP)
Yes  Yes
b) Me Tab > Settings > Change Mobile
> SMS OTP
Yes  Yes
c) Me Tab > Settings > Change Email >
Email OTP
Yes   No
d) Forgot Password > Email OTP   Yes

No
e) Forgot Password > Mobile Method >
SMS OTP (RU Only) -
Yes  Yes
f) Enable 2FA > SMS OTP  Yes  Yes
g) Activate Login by Email > Email OTP  Yes  No
h) Activate Login by Mobile > SMS OTP  Yes  Yes

Validation Rules

Condition Status for reCAPTCHA
If reCAPTCHA score is below the configured threshold  FAIL
If the reCAPTCHA score is higher or equal to the
configured threshold
PASS

Condition  Status for SMS Defender

---

## Page 14

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 13 of 17

If the SMS Defender risk score is higher than the
configured risk threshold
FAIL
If SMS Defender risk score is lower or equal to the
configured risk threshold
PASS

AC3. For Email OTP, if reCAPTCHA Status is FAIL, the OTP is not sent and a pop-up with an OK
button and configurable error message ERRORMSG-FAIL is shown to the user, and all the details
of the activity and assessments are logged in system.

AC4. For Email OTP, if reCAPTCHA status is PASS, then email OTP is sent as per normal.

AC5. For SMS OTP items, if reCAPTCHA status is FAIL or the SMS Defender status is FAIL, the
OTP is not sent and a pop-up with an OK button and configurable error message ERRORMSG-
FAIL is shown to the user and all the details of the activity and assessments are logged in system.

AC6. For SMS OTP items, if reCAPTCHA status is PASS and the SMS Defender status is PASS,
then the SMS OTP is sent as per normal

AC7: If the user (whether AH or RU) has failed on 1st and 2nd attempt, on the 3rd
and subsequent attempts on below login attempts:
• Login by Account
• Login by Email
• Login by Mobile + Password

a) The system will no longer use GeeTest and must validate the activity with the Google
invisible reCAPTCHA. Apply AC3 and AC4.
b) Failed attempts tracking is done on multiplatform level and account level (for AH),
and PhilipID level (for non-account holder RU).
c) Multiplatform level means if a user fails in P2web, it’s considered one failed attempt. then
same user then opens M2 app and did another failed attempt, it will be second attempt
d) Account level means we count failed attempts per accountno, i.e. if user failed 2 times on
account A then tried to login using his other account B for the first time, account B’s failed
attempt count must be 0,
e) PhillipID level means we count failed attempts per PhillipID. this applies to non-account
holder RUs. For account-holder RUs, tracking is on account level.
f) Must validate reCAPTCHA before validating password.

AC8.  If the app detects activity that is not humanly possible, e.g. 1second difference between 1st
attempt and 2nd attempt, the system will no longer use GeeTest and must validate the activity with
the Google invisible reCAPTCHA.

Epic C – Admin Portal

4.2.2. User Story C1 – Changes on the admin portal

As a CEU user, I want an Admin Portal page to view block reasons and unblock users.

---

## Page 15

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 14 of 17

Acceptance Criteria

AC1. Portal must support or cover POEMS and GWM/MyWealth Users.

AC2. For selected user record, portal must show latest log details done by user and reason for
blocking (i.e. reCAPTCHA fail score, SMS Defender fail score, other current blocking reasons like
country block, ip block, device block, multiple wrong attempts and which system).

AC3. For selected user, there must be a control where CEU can switch on/off to bypass blocking. If
bypass=ON, SMS OTP / Email OTP will not be blocked for this particular user, but logs are still
captured by the system.

AC4. Audit trail logs must be kept for admin portal activities done on AC4 and AC5.

5. Interface Requirements
6. Non-Functional Requirements (Optional)
6.1. Security
• Sensitive data (login, device info, logs) must be securely stored and transmitted

6.2.  Performance
a) Validation (reCAPTCHA + risk scoring) must occur in real time without noticeable delay to
users
b) System must handle high login and OTP request volumes efficiently

6.3. Security/Control Requirements

6.4. Service Requirements
a) The system shall provide real-time validation services for login, signup, and OTP-related
actions.
b) The system shall integrate with external security services (Google reCAPTCHA and SMS
Defender) to assess abnormal or suspicious activities.
c) The system shall ensure that OTP delivery services (SMS/Email) are only triggered upon
successful security validation.
d) The system shall support high availability of authentication and security services to avoid
login disruption.

---

## Page 16

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 15 of 17

6.5.  User Training Requirements<Optional>

7. Assumptions and Limitations

Assumptions
a) POEMS 3 has stable integration with Google reCAPTCHA and SMS Defender.
b) Users have active internet connectivity during login and OTP-related transactions.
c) Login, signup, and OTP flows follow existing POEMS 3 authentication architecture
d) Security thresholds and configurations will be managed by authorized system administrators.
e) Admin Portal users are properly trained and granted appropriate access rights.
Limitations
a) The solution relies on external third￼party services;
b) Abnormal login detection reduces risk but does not guarantee full prevention of all attack
scenarios.
c) Some legitimate users may be falsely flagged due to strict risk scoring threshold
d) Effectiveness is dependent on the accuracy of risk models provided by reCAPTCHA and
SMS Defender.
e) The scope covers authentication and OTP￼related activities only; post￼login behavior
monitoring is not included.

8. Reference
Use below as reference:

a) Phillip Connect Case:GOOGLE RECAPTCHA TO REPLACE GEETEST
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/ca
ses#/detail/29284
b) Mock-up Layout and Design: Sample:
c) Diagram: Recaptcha diagram.png

9. Acceptance Form
Project Name: Google ReCAPTCHA to Replace Geetest
Document Name ITSR 369574 < Google ReCAPTCHA to Replace
Geetest > URS
Company Name: Phillip Securities Pte Ltd
Name of Management: Securities Workgroup

---

## Page 17

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template                      ITSD/REF15/V1.4

_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 16 of 17

Requested By:
Requested By Signature/Date:
Approved By (System Owner): Shanti Tjiunardi / Tan Wee Kiat
Designation: System Owner

Disclaimer
<If the project has been submitted by business users, the affected business department is willing to
accept the risks involved in skipping section 4 & 5 in the document.>
