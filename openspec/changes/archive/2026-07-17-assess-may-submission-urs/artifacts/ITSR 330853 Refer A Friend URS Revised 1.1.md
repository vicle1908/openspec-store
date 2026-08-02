# ITSR 330853 Refer A Friend URS Revised 1.1
Source: `ITSR 330853 Refer A Friend URS Revised 1.1.pdf` (73 pages)
Extracted: 2026-06-09

---

## Page 1

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 73

PHILLIP SECURITIES PTE LTD

Refer a Friend

User Requirement Specifications

For:
Phillip Securities Pte Ltd Project Ref:
Author: Nghia Doc Ref:
Proj Mgr: Nghia Version: 1.1
Date:  Classification:
T o  :                           C c :

---

## Page 2

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 73
Document Revision History .................................................................................................................................. 2
1 INTRODUCTION ................................................................................................................................................ 3
1.1 PURPOSE OF DOCUMENT ...................................................................................................................................... 4
1.2 DOCUMENT CONVENTIONS .................................................................................................................................. 4
1.3 INTENDED AUDIENCE AND READING SUGGESTIONS ............................................................................................ 4
1.4 COMMITTEE ......................................................................................................................................................... 4
1.5 GLOSSARY............................................................................................................................................................ 4
2 PROBLEM/PURPOSE STATEMENT .............................................................................................................. 5
2.1 BACKGROUND..................................................................................................................................................... 6
2.2 PROBLEM ............................................................................................................................................................ 6
2.3 PURPOSE ............................................................................................................................................................. 6
2.4 PROJECT SCOPE .................................................................................................................................................. 6
2.5 USER CLASSES AND CHARACTERISTICS .............................................................................................................. 6
3. REFER A FRIEND FLOW ..................................................................................................................................... 7
3.1. OVERALL FLOW ................................................................................................................................................... 7
A. Holder account having P3 installed................................................................................................................. 7
B. Potential User to become holder account who is new to P3: .......................................................................... 8
3.2. DIAGRAM FLOW. ................................................................................................................................................. 9
A. CREATING A REFERRAL CAMPAIGN (TO-BE) ....................................................................................................... 9
B. REFERRER PARTICIPATING IN REFER-A-FRIEND CURRENT ACTIVE CAMPAIGN (TO-BE) ..................................... 11
C. REFEREE (FRIEND) PARTICIPATING IN REFER-A-FRIEND PROGRAM TO GET REWARD (TO-BE) .......................... 12
D. REFERRER MONITORS INVITEES AND GETTING REWARD (TO-BE) ....................................................................... 15
E. EXPIRING A PREVIOUS REFERRAL CAMPAIGN (TO-BE) ....................................................................................... 15
4.SYSTEM FEATURES / EPICS & USER STORIES ........................................................................................... 19
4.1 USER STORIES THAT ARE DONE ........................................................................................................................ 19
 ...................................................................................................................................................................................... 19
FUN-1548 - MoEngage Card Campaign: Use deepLink to Navigate to Refer a Friend Screen with Promotion
Code from kvPairs .............................................................................................................................................. 19
Fun-1268 [Referrer] Referral link message changes ......................................................................................... 21
Fun-1235 [Referrer] Referrer's view - Promotion Carrousel ............................................................................ 24
Fun-1184 [RAF] Enable/Disable RAF ............................................................................................................... 27
Fun-1168 [Referee] Invitation to open account ................................................................................................. 28
Fun-1132 [Referrer] Generate the referral link ................................................................................................ 30
Fun-1131 [Referrer] Invites list history and rewards ........................................................................................ 32
Fun-1104 - [Referrer] on Me tab - How Referer approach the Referer Friend promotion .............................. 37
4.2 CHANGE REQUEST FOR RAF PROJECT ............................................................................................................... 40
User Story A- [Change Request] Block ineligible clients from generating referral link & show in-app prompt
 ............................................................................................................................................................................ 40
User Story B- [Referrer] [Change request] Invites list history and rewards .................................................... 43
AC6: .................................................................................................................................................................... 49
User Story C- [Change Request] RAF - Update Frontend Logic to Call Referral API on "Invite a Friend"
Button Click ........................................................................................................................................................ 53
User Story D - [Change Request] 'My Invites' Page - Display Referee Campaign Step Progress .................... 53
User Story E- [Change Request] 'My Invites' Page - Display Issued Coupons with Status Under Each Referral
 ............................................................................................................................................................................ 53
User Story F- [Change Request] Reward attribution flow - Push notification when reward is credited to
user’s reward inventory ...................................................................................................................................... 53
User Story G - [Change Request] Implement RAF Tooltips on "My Invites" and "Refer A Friend" Pages ...... 53
4.3 NON-FUNCTIONAL REQUIREMENTS ................................................................................................................... 53
4.4 PERFORMANCE ................................................................................................................................................... 53
4.5 OPERATIONAL REQUIREMENTS .......................................................................................................................... 53
4.6 SECURITY/CONTROL REQUIREMENTS ................................................................................................................ 53
4.7 SERVICE REQUIREMENTS ................................................................................................................................... 53
5. USER TRAINING REQUIREMENTS ................................................................................................................ 53
6. ASSUMPTIONS AND LIMITATIONS............................................................................................................... 53

---

## Page 3

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 73
7. REFERENCE ......................................................................................................................................................... 53
8. ACCEPTANCE FORM ......................................................................................................................................... 53
9. DISCLAIMER ........................................................................................................................................................ 53
10. DOCUMENT REVISION HISTORY ................................................................................................................ 53

---

## Page 4

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 73
Document Revision History

Document Title: ITSR 330853 Refer a Friend URS v1.2

Version Revised
by
Effective Date Summary of Change Reason for
change
1.0 Ronnie 13 Jan 2026 -  First version Requirement
drafted by Nghia
New
1.1 Ronnie 26 May 2026 1. CR of cases of friend getting
rewards.

Update based on
CR

---

## Page 5

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 73
1 Introduction
1.1 Purpose of Document
This URS records the functional and non -functional requirements for the Paper Trading
capability. It serves as a contract between stakeholders and delivery teams, and input to
analysis, design, and testing.

1.2 Document Conventions
The following font colors shall have the corresponding meanings.
Format Convention
Blue Reference to an external document or file
Red Important/critical point
Green Unconfirmed or undetermined point
Purple New or changed points from previous document version
%Variable% Application Variables
1.3 Intended Audience and Reading Suggestions
Product, Marketing, Trading Systems/IT, Middle Office, Compliance/Market Data,
and supporting functions. System Owners of impacted systems should confirm
functional features.
1.4 Committee
The following committee will need to provide their approval for this project to
commence.
Name Position Signature Date
 Project Champion BU
 System Owner
 HOD
 Director

1.5 Glossary
No Term Meaning
1 P3 Poems mobile 3.0
2 RFA Refer A Friend

3 RU Registered User(No live trading account yet)
4 Holder Account Existing holder account

---

## Page 6

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 73
5 RU become
Holder account

---

## Page 7

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 73
2 Problem/Purpose Statement
2.1 Background
• Customer can get rewards by becoming advocates of P3 and attracting new users. User
generated vs. salesmen generated growth of userbase
2.2 Problem
• Not having much user registering on P3 and not much RU to open account trading to become
Account Holders.
2.3 Purpose
• As a(n) Business user, I want to have the refer-a-friend-to-open accounts feature in P3. So
that this will encourage/help our existing users to refer their friends/family members using P3.
• Increase account opening, funding, trading (by requiring these activities as part of conditions to
qualify for rewards)
2.4 Project Scope
In Scope - This project will include:
+ For Poems Mobile 3 only.
+ Only implement defined URS change requests

Ronnie p3 figmas – Figma

Out Scope - this project does not include:
+ Implementing for others: M2, P2 Web.
+ Avatar invitees (treated as nice-to-have only)
+ Real-time auto-trigger from deposit system
+ Shutdown decision of P2

2.5 User Classes and Characteristics
The following table describes the user roles, which will use the system

User Class Activities
POEMS Marketing Managing the POEMS platform
Existing Holder Account Can refer friends to P3 usage to get rewards
Referee Referee join, then to become new holder
account

Referrers Eligible account type to invite their friend to P3
then get rewards.
TR Trading representative

---

## Page 8

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 73
FA Finance Advisor

3. Refer A Friend Flow
3.1. Overall flow
A. Holder account having P3 installed.

---

## Page 9

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 73

---

## Page 10

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 73
B. Potential User to become holder account who is new to P3:

3.2. Diagram flow.
a. Creating A Referral Campaign (TO-BE)

---

## Page 11

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 73

---

## Page 12

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 73

b. Referrer participating in Refer-A-Friend current active campaign (TO-BE)

---

## Page 13

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 73

c. Referee (Friend) participating in Refer-A-Friend Program to get reward (TO-BE)

---

## Page 14

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 73

Note Edge Use Cases:
       1.Friend click RAF link and install P3 and Sign up RU then Open Account

---

## Page 15

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 73

       2.Friend click RAF link and install P3 and Sign-up RU but did not open account immediately and does it some other time.

        3.Friend is existing RU and use client referral link before opening an account.

       4. Friend is existing RU and use other client Referal link right before submitting an Open trading account.

---

## Page 16

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 73

d. Referrer monitors invitees and getting reward (TO-BE)

---

## Page 17

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 73

e. Expiring a previous Referral Campaign (TO-BE)

---

## Page 18

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 73

---

## Page 19

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 73

---

## Page 20

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 0 of 73

4.System Features / Epics & User Stories
-Description:
1. As an account holder, I want a feature to allow me to refer P3 to Friend conveniently. And by
this I can refer my friend, sign up RU, open trading account then get some rewards with each
referral done.
2. Always to apply latest Referral program from web P2 access through P3 for this project:
www.poems.com.sg
4.1 User Stories that are DONE

FUN-1548 - MoEngage Card Campaign: Use deepLink to Navigate to Refer a
Friend Screen with Promotion Code from kvPairs

Description:
Background
Currently, MoEngage Cards support multiple CTA types such as deepLink and richLanding. We
aim to enhance the campaign experience by enabling navigation to the Refer a Friend screen
using the deepLink CTA type.
The deep link https://tdt-asia.onelink.me/raq7/029h0i3n will be registered and configured via
AppsFlyer.
This deep link includes the following params:
• screen_name = referafriendscreen
• url = the web URL to be loaded in a WebView screen
Additionally, the promotion code will be dynamically passed through MoEngage kvPairs
(key-value payload) within the campaign.
This approach ensures flexibility for marketers to configure and update campaigns without
requiring an app release.

---

## Page 21

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 1 of 73

Objective
Allow users to navigate to the Refer a Friend screen when tapping a MoEngage card that
includes:
• ctaAction.type = deepLink
• ctaAction.value = app://refer-a-friend
Also display a promotion code (for example, promoCode: MOE2025) on the screen if provided
via kvPairs.
Acceptance Criteria
Scenario 1: Navigate to Refer a Friend screen via deepLink using AppsFlyer
Given the MoEngage card has a ctaAction with type = deepLink
And the value is app://refer-a-friend
When the user taps the card
Then the app should validate the URL
And navigate to the Refer a Friend screen using AppsFlyer’s openUrl method
Scenario 2: Show promotion code configured from MoEngage kvPairs
Given the MoEngage card includes a kvPairs object with a promo code, for example,
promoCode = MOE2025
When the user reaches the Refer a Friend screen
Then the screen should extract the value of promoCode
And display it appropriately in the UI
If promoCode is missing or empty, show a default message or hide the promo code section
Scenario 3: Invalid or unsupported deepLink
Given the ctaAction.value is not a registered or valid deep link
When the user taps the card
Then the app should not crash
Show an invalid deep link screen
And log a warning message for developers or QA

---

## Page 22

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 2 of 73
Scenario 4: No regression in other CTA types
Given other campaigns still use ctaAction.type = deepLink or richLanding
When the user taps those cards
Then the app should continue handling them using the existing logic without regression
Caveat
All screens and flows that follow the Refer a Friend screen remain unchanged.
• We are only changing how TRCode and referralCode are retrieved. you can refer this one
https://psplit.atlassian.net/browse/FUN-1543
• From the Refer a Friend screen, the app will call an API to fetch the required data (TRCode and
referralCode) to generate the deep link used for sharing the invitation with friends.
Please refer to the related tickets for more details
https://psplit.atlassian.net/browse/FUN-1131
https://psplit.atlassian.net/browse/FUN-1104
For testing purposes, you can use this campaign to test the feature.

Fun-1268 [Referrer] Referral link message changes

Description:
Requirements:

---

## Page 23

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 3 of 73
 1. Extending from Ac#3 https://psplit.atlassian.net/browse/FUN-1132 message need to be
changed as below.
' Open your Welcome Gift from POEMS when you sign up for Cash Plus Account and fund with
us! Check out the perks you can enjoy:
   Zero US Commission
      Free SGX Enhanced Market Depth
    Free Live Prices on popular markets
      Free Attractive US Shares
So what are you waiting for? Sign up now at *insert Referral Link '
1. *insert Referral Link* will be the same link we did before in
https://psplit.atlassian.net/browse/FUN-1132 , no changes to the link only the message will be
changed.
2. Below message will be changed and preview is not required. #updated 8th Jan

---

## Page 24

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 4 of 73

3. Translation as below:
English Simplified Chinese Traditional Chinese Japanese

---

## Page 25

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 5 of 73
Open your Welcome
Gift from POEMS
when you sign up for
Cash Plus Account
and fund with us!
Check out the perks
you can enjoy:

 0️⃣ Zero US
Commission
 📊 Free SGX
Enhanced Market
Depth
 📈 Free Live Prices
on popular markets
 🆓 Free Attractive
US Shares

 So what are you
waiting for? Sign up
now at *insert
Referral Link*
开设 Cash Plus 账户并存入资
金，即可领取 POEMS 的欢迎
礼包！
 以下是您可以享受的优惠：

 0️⃣ 零 美股佣金
 📊 免费使用 SGX 增强型市场
深度工具
 📈 免费订阅热门市场的实时
价格
 🆓 免费美股

 您还在等什么呢？
 立即注册*insert Referral Link*
開設 Cash Plus 帳戶並存入
資金，即可領取 POEMS 的
歡迎禮包！
 以下是您可以享受的優惠
：

 0️⃣ 零 美股佣金
 📊 免費使用 SGX 增強型
市場深度工具
 📈 免費訂閱熱門市場的
即時價格
 🆓 免費美股

 您還在等什麼呢 ？
 立即註冊 *insert Referral
Link*
Cash Plus アカウ
ントを開設し、
資金を入金する
と、POEMS のウ
ェルカムギフト
をお受け取りい
ただけます！
 以下の特典をご
利用いただけま
す：

 0️⃣ ゼロ 米国株
手数料
 📊 無料 SGX 拡
張市場深度
 📈 無料 人気市
場のリアルタイ
ム価格
 🆓 魅力的な米
国株を無料でプ
レゼント

 何を待っていま
すか?今すぐ登録
 *insert Referral
Link*

Fun-1235 [Referrer] Referrer's view - Promotion Carrousel
User Story:
As a Account Holder
I want to  views of the promotions available
so that  aware and take the promotion
Description:
Acceptance Criteria:
1. Check the content <Top 5 promotions> <existing API to retrieve from P2 Web>
2. Scroll to the right for more Promotions banner, maximum/top 5 promotions
3. Able to scroll back to left
4. Refer a friend should be the first item to be displayed, and followed by other promotion
campaigns.

---

## Page 26

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 6 of 73
5. Click on the promotion banner, open the promotion content
i. Verify the opened promotion content match with the promotion banner content and it should
open in-app browser to the specific URL, similar to promotions tab in home page →
https://psplit.atlassian.net/browse/PP3-230

ii. Click on '<' → it will navigate to me tab
1. For testers to take note.
a. Upon pressing it should be navigating to the RAF page.

---

## Page 27

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 7 of 73

b. Upon scrolling to 2nd carrousel promotion and tapping on the link it should open up the
related promotion link

---

## Page 28

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 8 of 73

Fun-1184 [RAF] Enable/Disable RAF
User Story:
As a Product Manager/Dev Team
I want to  enable/disable the feature in Prod env
so that I could be able to enable/disable based on the feature readiness
Description:
Refers to creating API control to turn On/Off for RAF module
Acceptance Criteria:
1. Create API control to turn On/Off for RAF module
2. The RAF will be hidden in Me tab if it’s off.

---

## Page 29

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 9 of 73
3. Upon turning off, the RAF carrousel → https://psplit.atlassian.net/browse/FUN-1104 won’t be
displayed.
4. If user click on invitation list upon the RAF is disable, user will receive error →
https://psplit.atlassian.net/browse/FUN-1168 in 2.D
Fun-1168 [Referee] Invitation to open account
User Story:
As a new user
I want to  view referral link from referrer
so that  I can download and open account from the link
Description:
Refers to referee screen upon receiving the link from referrer.
Acceptance Criteria:
1. Upon pressing on get started below action will happen for different users:
a. user never installed p3 app
i. Upon receiving invitation and URL link from referrer as in Figure 1, user will be
redirected to web browser to the page as in Figure 2 webpage →
https://www.poems.com.sg/referral-program/
ii. After installing P3, displays the Promo ad landing page for the first time. For
details, refer to AC1 ticket https://psplit.atlassian.net/browse/FUN-920.
iii. After user login or signup successfully, the Promo Ad landing page will be
displayed again, For details see the AC2, ticket
https://psplit.atlassian.net/browse/FUN-920.
iv. If the RAF ID is not valid, after user install P3, display the Promo ad landing page
only 1 time only. For display details, refer to AC 3a , ticket
https://psplit.atlassian.net/browse/FUN-920. After user login or signup
successfully, no Promo ad landing page displayed any more, user will work with
app with the current App working folow.
b. user already installed p3 app and not login → Refer to
https://psplit.atlassian.net/browse/FUN-921 Scenario 2
i. Deeplink takes the user to the Promo ad landing page, For details display, see
AC1 ticket https://psplit.atlassian.net/browse/FUN-920.
ii. After user logs in or signs up successfully, show the Promo ad landing page
again, For details see AC2, ticket https://psplit.atlassian.net/browse/FUN-920.
iii. If the PromoID is not valid, after user install P3, display the Promo ad landing
page only 1 time only. For display details, refer to AC 3a , ticket
https://psplit.atlassian.net/browse/FUN-920. After user login or signup
successfully, no Promo ad landing page displayed any more, user will work with
app with the current App working folow.
c. *user already installed app and already login as RU*→ Refer to
https://psplit.atlassian.net/browse/FUN-921 Scenario 3

---

## Page 30

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 10 of 73
i. Display the Promotion landing page after the user clicks on the deep link. For
details, refer to AC2, ticket https://psplit.atlassian.net/browse/FUN-920
ii. If the PromoID is not valid, after user install P3, display the Promo ad landing
page only 1 time only. For display details, refer to AC 3b , ticket
https://psplit.atlassian.net/browse/FUN-920.
d. If promotionID is invalid, user never installed p3 app or user already installed p3 app
and not login, below screen will be displayed.
i. Fixed title: POEMS Mobile 3
ii. The back button will take the user to the Main Splash page.
iii. LOGIN and SIGNUP buttons are always displayed and handled by the Mobile
side. click on LOGIN, P3 takes User to Login page. clicks on SIGNUP button, P3
takes user to the SIGNUP page.
e. user already install app and already login and already have trading account → Refer to
https://psplit.atlassian.net/browse/FUN-920 AC#3.2
i. User already stay in App and current in Page X, display screen
ii. Fixed title: POEMS Mobile 3
iii. The back button will take the user to the page X
1. If user is active it will bring back user to the page user was visiting.
2. If user is inactive it will bring user to homepage
iv. Page content shown as Figma provided
2. There will be a log for ac #1 and the information should cover for both referee and referral
3. https://psplit.atlassian.net/browse/FUN-1131- To test complete flow from referral to referee
this ticket need to be checked,
4. Once referee open account then referral code will be saved from API wrapper.
5. Corporate account users won't be able to use the function.
Figure 1 Figure 2 Figure 3

Figure 4 Figure 5

---

## Page 31

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 11 of 73

Fun-1132 [Referrer] Generate the referral link
User Story:
As a referrer
I want to  generate referral link
so that  I can share with other person to open new account
Description:
Refers to generating URL to pass to friends/family so that they can open account.
Acceptance Criteria:
1. Upon pressing on 'invite a friend' button from → https://psplit.atlassian.net/browse/FUN-1104,
there will be a URL generated as below format from appflyer.
https://www.poems.com.sg/open-an-account/?referral=yNZW8?TR=123 - deeplink generated
from Appflyer + referal code (Poem web) + TR code (P3 database)
• To be clarified
1. The refer a friend share link will have element as below.
a. Share via - will be dependent on OS (This would be similar to sharing the URL in
community tab ‘share via’ - it will display a popup section showing users the respective
additional options for sharing for IOS/Android.) #updated on 6/11
i. iOS - https://medium.com/@worachote/a-guide-to-post-sharing-with-
uiactivityviewcontroller-1fd3455a1c2f
ii. Android - https://developer.android.com/training/sharing/send
b. Sharing to other platforms.
i. Copy link - Upon copy there will be toast message ‘Link copied’ displayed
#updated on 6/11
ii. Whatsapp - Copy the URL and open whatsapp ‘Send to’ to send the URL as in
figure 3
iii. Telegram- Copy the URL and open telegram ‘select chat’ to send the URL

---

## Page 32

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 12 of 73
iv. Facebook - Copy the URL and either send to 'news feed' or ‘your groups’ in
facebook.
v. Depending on user device and app it should be displayed in the tab. #updated
on 6/11
2. Once send the referal link, user will receive message below as in Figure 4 and icon will be based
on promotion that we are running.
a. -Check out the POEMS Mobile 3 App for amazing investment opportunities -
Customizable based on promotion (Will be from API)-
Use my link to get started: https://app.poems.com.sg/open-an-
account/?referral=yNZW8?TR=123
3. Please refer to https://psplit.atlassian.net/browse/FUN-1268 for the message changes.
#updated on 19/12
Scenario:
Figure 1 Figure 2 -updated on 6/11 Figure 3

<Expectation below will be
OS specific hence will be
different behavior from iOS
and Android> Below is just
an example
Android

IoS

---

## Page 33

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 13 of 73

Figure 4

Fun-1131 [Referrer] Invites list history and rewards
User Story:
As a referrer
I want to view my invitation list
so that  I can track my reward info.
Description:
Refers to invitation list where the campaigns are dynamic and can be change or added in the list.
Applicable only for account holder. This page can’t be seen by registered user.
Acceptance Criteria:
Figure Logic
Figure 1 - Updated the image on 5/11 1. My Invites screen displayed as figure 1
2. Friend’s name: Display the full real name
of the referee. If a friend uses the
referer’s referral friend link to open an

---

## Page 34

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 14 of 73

account, when the open account form is
submitted successfully, the referer will
see his/her friend in this list.
a. Back button, take user to the
previous screen
b. My Invites: fixed texts from API
c. Active referral campaign will list
out all the successful invited
friends of the user in the current
activated referral campaign.
<Date (Format DD MMM YYYY)
and 0/30 will be shown>
#Updated on 18/11
i. The image of user will be
as below.
d. According to the tier achieved,
the result will be displayed for
the referral
i. For this campaign
achieved tier <1,2,3> will
be standardize total
received $20 for each
tier
ii. There will be different
total received or
unlimited tier for
different campaigns
e. If user achieved a tier then
achieved <Tier 1> will be
displayed #to be removed 25/10
f. In progress will be shown after 1
task (Open account) completed
g. Upon completion user can view
the total received
h. By clicking on arrow 'v' to
expand, user will be able to view
either in progress or completed -
the achieved tier <1,2,3> with
the amoun-t #changed on 18/11
i. Once achieve tier 3, status will
be changed to completed
j. Expired referral campaigns
where we list out all the
successful invited friends of the

---

## Page 35

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 15 of 73
user of the previous referral
campaigns.
k. Total received: Display total
rewards that user earned total in
money for all the campaigns
including the expired campaign
Figure 2

1. Once referral has received the reward
there will be a notification pushed as
Figure 2.
However the message will be as below
#updated on 21/11:

Header: Congrats! One of your referee
has reached a milestone!
Body: Tap here to view your reward
Figure 3

1. Upon pressing on the push notification as
in figure 2 user would be able to view the
banner as in Figure 3. (Need to change
this, different banner for different tier)
a. User can press 'x' button to close
it, upon closing the banner user
will be directed to the same page
that user is in before. #updated
on 25/10
b. Upon clicking on ‘See invites list’,
user will be directed to the
invites page as in figure 1 and the
status will be changed to the
progress according to referee
progress. #updated on 25/10
Figure 5 1. User can view the reward deposited in
the transaction history page.

---

## Page 36

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 16 of 73

Figure 6 <This would be an example of the
campaigns and how the process in Figure 1>

<this would be the illustration from wrapper
and mambo side> The reward decision would
not be done from mambo API, it will be a
manual process as in ac#10
1. Based on Figure 6, each status will
change in [Ronnie(Referrer)] as in figure
1 once the Quest has been completed by
the referral [Navin(friend)]
a. In progress - The referral
[Navin(friend)] need to open
account
b. Achieved tier 1 - Opened
account, Funded 2000 and Trade
3 stocks
c. Achieved tier 2 - Funded 7000,
Traded 5 stocks
d. Completed - Funded 20000,
Traded 10 stocks
2. For each of the quest done there will be
a verb of the task parameter(metadata)
passed to Gamification wrapper API.
3. The metadata need to be passed from
wrapper to Mambo API (as in ac#6), for
example:
a. Sending of Account opening
approved to Mambo
b. Sending of Funded activity to
Mambo
c. Sending of first_traded activity to
Mambo
4. The last received link from Referrer will
receive the reward (For example if user A
passes the link to user B and user B
proceed to sign up but didn’t open

---

## Page 37

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 17 of 73

<This is the process for ac#10 and Figure 2
and to check in transaction history and RAF
invite history>

account and fund. After a while User C
passes the link to user B and user B
decides to open account and fund using
the link from user C then user C will get
the reward)
a. User A status - In Progress
b. User C status - Achieved Tier 1
5. Internal staff will get data exported from
tableau API to CSV and send to email list
via schedulded job from mambo that
client has funded the account. #Updated
on 22/11
a. CSV will consist Refferer Name,
Refferer Acct no, Refferee Name,
Refferee Acct No, Amount or
reward #Updated on 22/11
6. Refer to
1. for the complete logic from Wrapper side
and mambo.
Figure 7 - Updated the image on 6/11 1. If users invite list is empty then figure 7
will be displayed.
2. Upon pressing on ‘invite a friend’ button,
the behavior would be as in ac#2 in
https://psplit.atlassian.net/browse/FUN-
1132
3. The referral link that is shared will be
similar as in Ac#1 in
https://psplit.atlassian.net/browse/FUN-
1132

---

## Page 38

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 18 of 73

Fun-1104 - [Referrer] on Me tab - How Referer approach the Referer Friend
promotion
User Story:
As a Account holder
I want to refer a friend to open an account feature on Me Tab
so that
I can refer my friends/family members to do an activity
based on the promotion campaign

Refers to displaying refer a friend for AH, For RU it won’t be displayed.
Acceptance Criteria:
1. If a user is an AH whose account is approved, the Me tab will have the new “-REFER A FRIEND-”
“Promotion” section.#updated on 12th Nov
a. There will be a carrousel where user can view the banners, there will be a timer for 5
sec where the banner will move to the next banner.
b. The carrousel indicator numbers below will be returned based on the banners that are
being displayed. → Refer to this for carrousel
logichttps://psplit.atlassian.net/browse/FUN-1235
c. The image and the sub text will be returned from API.
d. Tap on any part of this section or the arrow icon, take user to the Refer-a-Friend
campaign detail page as in ac#2

---

## Page 39

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 19 of 73

2. Once user has been re-directed to refer a friend page below will be the actions :
a. Back button, take user to the Me Tab
b. Upon tapping on the 'Invites List' button, it will redirect user to the invites list history.
Refer to this https://psplit.atlassian.net/browse/FUN-1131
c. Refer a Friend content: Returned from API
d. INVITE A FRIEND: a fixed button handled by FE. Tap on this button, to show the unique
referral link of the current user. Refer to this https://psplit.atlassian.net/browse/FUN-
1132
i. A,B and D Will be native while C is returned from API and URL to use and user
can scroll to see the entire page→ https://www.poems.com.sg/referral-
program/ #updated on 22/10

---

## Page 40

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 20 of 73

1. Deeplink will be required for the page above.
2. On/Off API for this new section. → https://psplit.atlassian.net/browse/FUN-1184
3. Apply Multi-language for this section.
English Japanese Simplified Chinese
Traditional
Chinese
Refer A friend お友達を紹介する 推荐朋友 推薦朋友
Invites 招待 邀请 邀請
My Invites 私の招待 我的邀请 我的邀請
Total received 受取合計 收到总数 收到總數

---

## Page 41

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 21 of 73
4.2 Change Request for RAF Project
User Story A- [Change Request] Block ineligible clients from generating
referral link & show in-app prompt
Ticket: Fun-1627:
User Story:
As a user participating in Refer a Friend,
I want to see a specific ineligibility message based on my account type,
so that I can understand why I can't participate and what action I can take.
Description:
Before: Any holder accounts can join RAF program

After: some types of accounts is not eligible.
In the Refer a Friend campaign: TR, Staff, internal FAs, Cash Trading, Joint, Corporate account
holders are not eligible to be referrers.
When a user taps “INVITE A FRIEND” button, the app must first call the existing API, API
site only return the popup message only

---

## Page 42

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 22 of 73

The front end should evaluate to show the error message and block any ineligible user for
referring friends. The referral link should not be generated.
Acceptance Criteria:
AC 1 - API Integration
• AC 1.1: Tapping "Invite a Friend" triggers the updated API call.
• AC 1.2: The API response includes isTRStaff, isCashAccount, and
isJointOrCorporateAccount.
AC 2 - Ineligibility Handling
• AC 2.1: If any flag is true, do not generate or display the referral link.
• AC 2.2: Show one of the above messages based on the flag(s) returned.

---

## Page 43

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 23 of 73
• AC 2.3: Dismissing the modal returns the user to the Refer a Friend screen with no state
changes.
AC 3 - Eligible Users
• AC 3.1: If all flags are false, generate and display the referral link.
AC 4 - Error Handling
• AC 4.1: If the API fails or returns malformed data, show: "Something went wrong.
Please try again."
• AC 4.2: Do not generate a referral link on error.
• AC 4.3: Log an error event in analytics.
AC 5 - Message Mapping (based on flags) with content and design as below:
Flag(s) Set Message to Display
isTRStaff = true
"MAS-licensed individuals and staff are not eligible to participate in the
Referral Program"
isCashAccount = true
"The Referral Program is not available for Cash Trading Accounts. Please
switch to other eligible account types to join the program."
isJointOrCorporateAccount
= true
"The Referral Program is not available for Joint/ Corporate. Please switch
to other eligible account type to join the program”

---

## Page 44

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 24 of 73

AC6: In the popup message if user hit on hyperlink [other eligible account types], client will be
navigated to mobile web browser for FAQ page:
Referral Program Be our influencer with POEMS

AC7: Multi Languages (will add here)

User Story B- [Referrer] [Change request] Invites list history and rewards
Ticket: https://psplit.atlassian.net/browse/FUN-1350
AC 1: Change status label from “In Progress” to “Active”
Before

Status are : Status transition: Invite Sent > In Progress > Completed or Expired

After

---

## Page 45

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 25 of 73

Status transition:  Active > Completed or Expired
AC2: Change from “You received <total received value>” showing “Reward Earned” and can
expand/collapse all friend list as so many at the same time as expected
Before:

After:

AC3: Change from “Expired Referral Campaigns” to “Past Referral Campaigns”. This is where
we are listing out all the successful invited friends of the user of the previous referral campaigns
(from the past 2 years’ campaign will be displayed):
Before:

After:
It will be renamed to Past Referral Campaign, also get same behavior of expand/ collapse as

---

## Page 46

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 26 of 73
Active campaign section.

AC4: Change the Notification content when referal receives a reward
Before:

After:
Header: Congrats! Your referee has reached a milestone!
Body: Tap here for more info

---

## Page 47

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 27 of 73

AC5: Change “Congratulations banner” pop-up from
Before:

---

## Page 48

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 28 of 73

Content
- (X) close button on top right
- Congratulations
- You have just earned S$68 Cash Credit
- Gift image
- “One of your friends has completed in their POEMS trading account”
- Claim button
After:
Content
-  Close button to be tap on to close this pop up.
- Congratulations
- “One of your friends has completed in their POEMS trading account”
- “See Invites List” button – On click go to Invites List screen

---

## Page 49

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 29 of 73

+Click See Invite List will direct user to:

---

## Page 50

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 30 of 73

+Click Close to close up the popup.
Ronnie p3 figmas – Figma
AC6:
Before: Total Value Received is shown.

---

## Page 51

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 31 of 73

After:
Total Value Received row will be changed to Referrals Made:

---

## Page 52

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 32 of 73

+ Tap on Invite A Friend will navigate user to:

+Value will be total number of friends referred by the Referrer since the beginning -> returned
by API

AC7: Invite X/Y
Before: All users will be limited of up to 10 invites

---

## Page 53

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 33 of 73

After:
Most users are limited to 10 invites (configurable) - text says “Invite X/Y”

---

## Page 54

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 34 of 73

But some specific users can be configured to have unlimited number of invites, e.g.

---

## Page 55

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 35 of 73
KOLs/Influencers. For these users, the text should say “Invite X” only

To tag these KOL users, specify the userid (get from GFO Admin) as custom field in Missions in
Mambo

AC8: Multi Languages (will add here)

User Story C- [Change Request] RAF - Update Frontend Logic to Call Referral
API on "Invite a Friend" Button Click
Ticket: https://psplit.atlassian.net/browse/FUN-1543
User Story:
As an account holder,
I want the referral information to be retrieved when I click on the "Invite a Friend" button,
so that a unique referral deeplink can be generated seamlessly using AppsFlyer.
Description:
Before:
Currently, the referral API is triggered when the user clicks on a promotion carousel banner.

---

## Page 56

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 36 of 73

After:
This logic needs to be updated so that the API is only called when the user clicks the "Invite a
Friend" button.

---

## Page 57

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 37 of 73

The backend will return a trCode, referralCode which will be used to generate a unique
AppsFlyer referral deeplink.
Acceptance Criteria:
AC1 - Referral API is no longer triggered from the promotion carousel banner
AC2 - Referral API is triggered when "Invite a Friend" button is clicked
AC3 - Referral deeplink is correctly generated via AppsFlyer
AC4 - On click of Invite a Friend, send “invite_friend” verb activity to Mambo
AC5 - On click of Invite a Friend, send “invite_friend” event to MoEngage

---

## Page 58

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 38 of 73
User Story D - [Change Request] 'My Invites' Page - Display Referee Campaign
Step Progress
Ticket: [FUN-1634] [Change Request] 'My Invites' Page - Display Referee Campaign Step
Progress - PSPL Project Management
User Story:
As a user, I want to see the current step and remaining eligibility status for each eligible
referee in my invite list,
so that I can track their progress and understand who is still eligible to complete the
campaign.
Before: (logic to show data, refer: [FUN-1131] [Referrer] Invites list history and rewards -
PSPL Project Management)
1.My Invites screen displayed as below:

---

## Page 59

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 39 of 73

2.Friend’s name: Display the full real name of the referee. If a friend uses the referer’s referral
friend link to open an account, when the open account form is submitted successfully, the
referer will see his/her friend in this list.
a. Back button, take user to the previous screen
b. My Invites: fixed texts from API
c. Active referral campaign will list out all the successful invited friends of the user in
the current activated referral campaign. <Date (Format DD MMM YYYY) and 0/30 will
be shown> #Updated on 18/11
i. The image of user will be as below.
d. According to the tier achieved, the result will be displayed for the referral
i. For this campaign achieved tier <1,2,3> will be standardize total received $20
for each tier
ii. There will be different total received or unlimited tier for different campaigns

---

## Page 60

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 40 of 73
e. If user achieved a tier then achieved <Tier 1> will be displayed #to be removed
25/10
f. In progress will be shown after 1 task (Open account) completed
g. Upon completion user can view the total received
h. By clicking on arrow 'v' to expand, user will be able to view either in progress or
completed -the achieved tier <1,2,3> with the amoun-t #changed on 18/11
i. Once achieve tier 3, status will be changed to completed
j. Expired referral campaigns where we list out all the successful invited friends of the
user of the previous referral campaigns.
k. Total received: Display total rewards that user earned total in money for all the
campaigns including the expired campaign

After:

Ronnie p3 figmas – Figma
Background
Current Referral Campaign Terms & Conditions is
• Referees must meet all of the following basic criteria:
o B2B = NO
o Service Type = KC / CASH PLUS

---

## Page 61

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 41 of 73
o Client Type = INDIVIDUAL
o New to PSPL = YES
• Referees must do the following:
o Current campaign steps:
▪ Step 1: Open a KC / CASH PLUS account
▪ Step 2: Opt in to MMF within 14 days of account opening
▪ Step 3: Fund at least S$3,000 within 14 days of account opening and hold
for at least 30 days
o Only referees who meet the basic criteria and have successfully opened then
an eligible account will appear in the "My Invites" list.
o Up to 10 referee per campaign period per referrer is allowed.
Our acceptance criteria is based on above, so if Marketing plans to change the Refer a
Friend program conditions above, they will have to submit a change request.
Acceptance Criteria:
• AC1: Only referees who meet all basic criteria (B2B = NO, Service Type = KC/CASH
PLUS, Client Type = INDIVIDUAL, New to PSPL = YES) are eligible for display.
• AC2: Backend verifies if account opening status is successful, and only then includes
the eligible referee in the "My Invites" list. Pending Approval and Rejected should not
show in the “My Invites” list.
• AC3: Above each referee’s image, their current step details is shown in the campaign is
shown
o X of Y steps – e.g. "2 of 3 steps”
o Time left and action require - “14 days left to opt in to MMF".
o Colored Bars for steps progress – based on number of steps done.
▪ Colored bar – done steps
▪ Gray bar – not yet done steps

---

## Page 62

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 42 of 73

• AC4: Up to 10 referees (limit is configurable) are allowed per campaign period per
referrer. App must show “Invite <count of referees in invite list for active campaigns> /
<Limit>”. See Users Story B > AC7 additional scenario

• AC5: Marketing team can update campaign step criteria at the start of each campaign
period, and backend uses this updated logic for eligibility filtering. Example: if
marketing change the step 3 from “Fund 3000” to “Fund 1000”, the new eligibility
criteria should be followed.
• AC6: If a referee fails to complete a time-limited step before the deadline, the step shows
as expired, and no further rewards are tracked.

---

## Page 63

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 43 of 73

• AC7: If a referee completes all steps successfully (returned by referral_completed), a
‘Completed’ status should be shown. No Step Name should be shown next to ‘X of Y
steps’

• AC8: Past 2 years campaigns referees should show under “Past Referral Campaigns”
secion. Same data to be displayed like how it is displayed in Active Campaigns. Rewards
earned details section must be collapsed by default.

---

## Page 64

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 44 of 73

• AC9: Refer-A-Friend Invites List is based on PhillipID level and not account level.
o If referrer has more than one account, the same list and count are displayed even
if the referrer switches between different counts.

User Story E- [Change Request] 'My Invites' Page - Display Issued Coupons
with Status Under Each Referral
Ticket: [FUN-1632] [Change Request] 'My Invites' Page - Display Issued Coupons with Status
Under Each Referral - PSPL Project Management
User Story:
As a user,
I want to see the list of potential and issued coupons directly under each successful referral on
the My Invites page,
so that I can clearly track which specific rewards have been issued for each invitee.
Description:
Before:
Refer: [FUN-1131] [Referrer] Invites list history and rewards - PSPL Project Management

---

## Page 65

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 45 of 73
After:

Design:

Acceptance Criteria:
• AC1: Each invitee’s (referee) section shows a list of all eligible coupon rewards.
• AC2: Coupons issued via Mambo show a green check mark next to their name. If no
coupons have been issued for a referral, all coupon names are shown without green ticks.
• AC3: Each coupon name in the dropdown is a clickable link redirecting to its detail page
in the reward inventory (which can be found on Me Tab > Rewards > My Rewards
Inventory)
• AC4: Backend caches coupon names at the beginning of each campaign period.

---

## Page 66

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 46 of 73
User Story F- [Change Request] Reward attribution flow - Push notification
when reward is credited to user’s reward inventory
Ticket: [FUN-1624] [Change Request] Reward attribution flow - Push notification when reward
is credited to user’s reward inventory - PSPL Project Management
User Story:
As a referrer,
I want to receive a push notification when a stock coupon or cash coupon is added to my reward
inventory,
so that I am immediately informed of my earnings from the referral campaign.
Description:
Before:  Auto send coupon, cash credit coupon to user, refer logic on original ticket: Fun-1131 :
[FUN-1131] [Referrer] Invites list history and rewards - PSPL Project Management

After:
When a referee completes a milestone in the referral campaign, marketing staff will manually
credit the appropriate reward (stock coupon or cash coupon) to the user’s reward inventory via
the admin panel.
Once the reward is credited, the system must automatically send a push notification to inform
the user of their new reward.
Notification Mapping Table:
Reward Type
Amount
(example) Notification Text Example Trigger Event
Stock Coupon/cash
coupon Not Mentioned
Congrats! One of your referee has
reached a milestone!
Tap here to view your reward

Marketing staff credits
coupons to user inventory

Acceptance Criteria:

---

## Page 67

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 47 of 73
• AC 1 - Trigger Behavior
o When marketing staff credits a stock coupon to a user’s reward inventory, a push
notification is sent immediately.
o When marketing staff credits a cash coupon to a user’s reward inventory, a push
notification is sent immediately.
• AC 2 - Notification Content

+ Tap on Close to close up the popup
+ Tap SEE INVITE LIST to access invite list screen.

• AC 3 - Delivery & Linking
o Push notification is delivered to the user’s device within a reasonable time (≤ 1
minute after crediting).
o Tapping the notification opens the Rewards Inventory page in the app.
• AC 4 - Error Handling

---

## Page 68

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 48 of 73
o If push notification fails, the event is logged as an error with retry attempts
recorded.

User Story G - [Change Request] Implement RAF Tooltips on "My Invites"
and "Refer A Friend" Pages
Ticket: [FUN-1648] [Change Request] Implement RAF Tooltips on "My Invites" and "Refer A
Friend" Pages - PSPL Project Management
User Story:
As a user, I want to see tooltips that explain how the Refer A Friend campaign works, so that I
can understand the conditions required to earn referral rewards.
Description:
Before:
No tool tips shown.
After:
Design:
1.Tooltip Placement 1 – My Invites (top of page, next to “My Invites” header):

These Tool tips content will be responsed by API

---

## Page 69

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 49 of 73

2.Tooltip Placement 2 – Refer A Friend page (top of page)

---

## Page 70

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 50 of 73

The tooltips should use a consistent UI pattern (small “i” icon → hover/click → tooltip content
box).
Acceptance Criteria:
• AC1: Tooltip appears on the "My Invites" page when user taps the info icon
• AC2: Tooltip appears on the "Refer A Friend" landing page when user taps the info
icon
• AC3: Tooltip contains the following 3 bullet points:
o Share by clicking 'Invite A Friend'.
o You'll get a reward only if your friend opens an account and meets the campaign
criteria on time: Referral Program Be our influencer with POEMS
o If the criteria are not met on time, you will not qualify for rewards.
• AC4: Tooltip closes when the user taps outside of it or on a visible close icon

---

## Page 71

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 51 of 73
• AC5: Tooltip content is readable and accessible across all supported devices and screen
sizes
AC6: Multi Langguages:
+Tool tips content 1
+Tool tips content 2.
Figma link: Ronnie p3 figmas – Figma

4.3 Non-Functional Requirements
• Network and database connections / interactions must be approved by Information Security
Team
• In case of Mobile app unable to connect to CIS to retrieve the mobile number, display this
message:
“Service is currently unavailable. Please try again later.”

4.4 Performance
System is expected to have:
• Fast Loading of screen – each page is expected to complete loading no more than 1 seconds.
During the loading period, app/website must provide animated loading image to inform users
that page is still loading.

• Pages that has grid or table and expected to have huge amount of data to be loaded, lazy
loading or pagination must be applied.

•  Scalable – to meet the 10x demand, system must remain stable and fast regardless whether
number of simultaneous users grow by 10 times.  Scalability is all about handling growth. Web
App, APIs and database architecture must be in line with this concept.
4.5 Operational Requirements

• The APIs and all systems involved in this project must be operational 24x7.
• Each system involved in this project should maintain audit logs, including date, uniqueID and
transaction details
• Hardware and software are expected to fail due to unforeseen circumstances, but applying
HA concept by having multiple instance of the application will help reduce or avoid the
possibility of downtime due to run-time errors.
4.6 Security/Control Requirements

---

## Page 72

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 52 of 73
• IT Security must assess the structure and advise further requirements, e.g. penetration tests
and other authentications methods
• Secured – system is exposed to the internet therefore app, APIs and databases must be well-
protected against different security threats that exploit vulnerabilities in an application's code

4.7 Service Requirements
• Data must be archived according to existing archiving policies

5. User Training Requirements
6. Assumptions and Limitations

7. Reference
• Phillip Connect link:
https://phillipconnect.net/portal/g/:spaces:poems_mobile_3_0/poems_mobile_3_0/cases#/det
ail/25975
• Figma link:

8. Acceptance Form

Project Name: In-app referral
Document Name ITSR  Refer A Friend
Company Name: Phillip Securities Pte Ltd
Name of Management: Jeffrey Goh
Requested By*: Ronnie
Requested by Signature/Date:
Approved By (System Owner): Shanti Tjiunardi / Tan Wee Kiat
Designation: System Owner

9. Disclaimer
10. Document Revision History

Document Title: ITSR 000000 <Project Title> URS

---

## Page 73

Operations Manual-IT Singapore-Appendix35-User Requirement Specifications Template        ITSD/REF15/V1.1
_____________________________________________________________________________________________
  Phillip Securities Pte Ltd                                                                                                          Page 53 of 73
Version Revised
by
Effective
Date
Summary of Change Reason for
change
1.1 Ronnie
