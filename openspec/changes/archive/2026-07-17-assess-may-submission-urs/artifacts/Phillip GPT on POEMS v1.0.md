# Phillip GPT on POEMS v1.0
Source: `Phillip GPT on POEMS v1.0.pdf` (30 pages)
Extracted: 2026-06-09

---

## Page 1

PhillipGPT on POEMS
User Requirements Specifications
For: POEMS MarketingProject ReferenceITSR: 368213
Author:Ronnie Doc Ref: URS
Proj Mgr:Nghia Version: 1.0
1. Product Vision
Build PhillipGPT, a client-facing AI assistant embedded in the trading platform, replacing POEMSGPT (by NextVestment) and consolidatingfragmented chatbot experiences into a trusted, compliant, and actionable financial assistant.
North Star:
“Help clients make informed decisions faster—with clarity, confidence, and compliance.”
2. Key User Personas & Jobs-to-Be-Done
3. Scope Definition
Phase 1 Scope (Must-have by Oct 2026)
Leverage existing internal + already approved data sources only
Excluded in Phase 1
1. Retail Trader (Primary)“Help me quickly understand a stock and decide what to do.”
“Give me actionable insights without switching screens.”
2. Active Trader / Semi-Pro“Give me technical signals and explain market moves.”
“Surface insights faster than my own research.”
3. New Investor“Explain things simply and reduce confusion.”
“Guide me safely without risking bad financial decisions.”
Iframe in POEMS Mobile 3 and P2Web
FAQ (already available from POEMS Website for SG Usage)
Market trends (internal research documents)
Basic company insights stock lookup, like price, performance and stock analytics (FactSet Contract Dependency Risk)
News (MT Newswire Contract Dependency)
Economic indicators (Data Source Dependency)
API integration and Native UI in P3 and P2Web
Voice chat (speech to text)
Attach files
Answer modes (Auto, fast, thinking, pro=agentic)
Advanced technical analysis (Trading Central dependency)
Client/Account Portfolio Based Answers and Recommendations
Personalized answers based on clients PDPA and activity

---

## Page 2

4. Functional Requirements
4.1 PhillipGPT visibility on POEMS Platforms
4.1.1 Ask AI buttons on P3
1. P3 must show Ask AI buttons on the following screens1. Home Tab
2. Watchlist Tab
3. Global Search Screen

---

## Page 3

4. Counter Details Screen
5. Screener Screen
6. Markets Tab

---

## Page 4

4.1.2 Iframe on P3
7. Trade Tab
8. Community Tab
9. Me Tab
10. Help Screen
1. When user click of "Ask AI" buttons, then app will load PhillipGPT Screen and iframe PhillipGPT web-based UI instead of NextVestment1. The upper part is native UI1. Back Button - on click, go back to previous screen
2. New Chat Icon - on click, load PhillipGPT New Chat Screen
3. Chat History Icon - on click, load PhillipGPT Chat History screen

---

## Page 5

4.1.3 Iframe on P2Web
2. The lower part is iframe of PhillipGPT Web-based UI
2. The following parameters should be passed by P3 app to PhillipGPT every time it loads the iFrame1. PhillipID - Unique ID of user. Required
2. AccountNo - Unique Account ID. empty allowed
3. Nickname - if user has a community profile username/alias return this value, else return empty
4. Query string - input question or text or prompt. empty allowed1. if user clicked Ask AI button after entering from text fields like global search, query string is the text entered
2. Deeplink may pass query string as parameter
5. Screen Context - name of screen where user came from when loading PhillipGPT, e.g. "Home Tab" or "Counter Detail - AAPL" or"Market News". This is so that we can provide contextualized suggestion questions. empty allowed
6. PC Code - platform unique id, so we can track platform usage of PhillipID
7. UI Theme - Light or Dark Theme, so PhillipGPT iframe loads according to theme
3. On load of iFrame, P3 does handshake authentication with PhillipGPT
4. PhillipGPT must be loaded and show content in less than 1s
5. If user loading the PhillipGPT has not seen the disclaimer before in P3, P3 must show the "Important Notice" pop-up first and after dismissingthe pop-up, mark the user as having seen disclaimer (i.e. disclaimer wont show up anymore in future in P3 for this particular user unlessaccessed through disclaimer links).
6. There must be a deeplink for PhillipGPT1. Deeplink must be able to support passing of parameters such as query string and Screen context
2. on click of deeplink, user will be lead to the app page that loads the PhillipGPT iframe
1. When user click of "Ask AI" buttons, then app will load PhillipGPT Iframe instead of NextVestment
2. The following parameters should be passed by P3 app to PhillipGPT every time it loads the iFrame1. PhillipID - Unique ID of user. Required
2. AccountNo - Unique Account ID. empty allowed
3. Nickname - if user has a community profile username/alias return this value, else return empty
4. Query - input question or text or prompt. empty allowed1. if user clicked Ask AI button after entering from text fields like global search, query string is the text entered
2. Deeplink may pass query string as parameter

---

## Page 6

4.1.4. ON/OFF Feature Flag for PhillipGPT Iframe
4.2 Core Chat Capabilities
4.2.1. iFrame Loading logic
4.2.2. Chat Interface
5. Screen Context - name of screen where user came from when loading PhillipGPT, e.g. "Home Tab" or "Counter Detail - AAPL" or"Market News" or "Open Account". This is so that we can provide contextualized suggestion questions. empty allowed
6. PC Code - platform unique id, so we can track platform usage of PhillipID
7. UI Theme - Light or Dark Theme, so PhillipGPT iframe loads according to theme
3. On load of iFrame, P2Web does handshake authentication with PhillipGPT
4. PhillipGPT must be loaded and show content in less than 1s
5. If user loading the PhillipGPT has not seen the disclaimer before in P2Web, P2Web must show the "Important Notice" pop-up first and afterdismissing the pop-up, mark the user as having seen disclaimer (i.e. disclaimer wont show up anymore in future in P2Web for this particularuser unless accessed through disclaimer links).
1. There must be API-configurable feature flag ON/OFF for PhillipGPT to be displayed in P31. If API returns ON - the AskAI buttons will be visible on P3
2. If API returns OFF - the AskAI buttons will NOT be visible on P3. For deeplink navigation to the app when API returns off, App willdisplay a pop-up that says configurableERROR-MSG1 = "The POEMS GPT feature is currently not available" + {"Ok got it" button}
2. There must be API-configurable feature flag ON/OFF for PhillipGPT to be displayed in P2Web1. If API returns ON - the AskAI buttons will be visible on P2Web
2. If API returns OFF - the AskAI buttons will NOT be visible on P2Web.
3. There must be API-configurable field GPT_Source for P31. if API returns GPT_Source = "NextVestment", P3 app is linked to Nextvestment iframe
2. if API returns GPT_Source = "PhillipGPT", P3 app is linked to PhillipGPT
3. if API returns GPT_Source = null, P3 App will display a pop-up that says configurable ERROR-MSG1 = "The Phillip GPT feature iscurrently not available {"Ok got it" button}"
4. . There must be API-configurable field GPT_Source for P2Web1. if API returns GPT_Source = "NextVestment", P2Web is linked to Nextvestment iframe
2. if API returns GPT_Source = "PhillipGPT", P2Web is linked to PhillipGPT iframe
3. if API returns GPT_Source = null, P2Web will display a pop-up that says configurable ERROR-MSG1 = "The POEMS GPT feature iscurrently not available" + {"Ok got it" button}
1. If Query parameter is NOT empty, PhillipGPT must load the main chat conversation interface with the following sequence1. If a chat history already for this same query string, then load that existing chat history else create a new one
2. Then add the query string automatically as user message input to the conversation (i.e. as if user typed in the message box and clickedsend)
3. Then load the response
2. If Query parameter is empty AND Screen Context parameter is NOT empty, PhillipGPT must load the New Chat screen with 3 suggestedquestions based on screen context. E.g. if Screen Context is "Counter Detail - NVIDIA", show questions related to context, e.g. "Anyimportant news for NVIDIA recently?" or "What do you think about NVIDIA?"
3. If Query parameter is empty AND Screen Context parameter is empty, PhillipGPT must load the New Chat screen with 3 suggested questionsrandomly generated from...1. We can start with a list of questions curated by our staff and input in database
2. In future we can make the suggested questions be dynamically loaded from trending 20 questions or personalized based on user'sportfolio or latest activity.
4. if new chat icon is clicked from header, PhillipGPT must load the new chat screen
5. if the chat history icon is clicked from header, PhillipGPT must load the Chat history list
1. New Chat Screen. Must show1. "Hi '{nickname}', I'm Phillip GPT"
2. Suggested questions
3. Input field (bottom anchor)

---

## Page 7

4. Send button
2. Main Chat Conversation Screen - must include:Chat Topic Title
The main chat thread - displays the user input and ai response conversation
Input field (bottom anchor)

---

## Page 8

Type Visual
User messageRight-aligned
AI responseLeft-aligned
System messageCentered
Send button - on click, must send the input to GPT
3. Message Types display rules
4. Chat History Screen - must include
1. New Chat - on click loads the new Chat Screen
2. List of Chat History topic titles sorted by latest chat on top.
3. On click of an existing Chat History topic title, app must load the Main Chatbot interface for that topic and scroll down to the latestmessage

---

## Page 9

4.2.3. Response Generation
Type Use Case
Text Default
Structured cardsStock info
Bullets News, summaries
Tables Comparison
4. If there are no existing chat history, show "No chat history yet", empty state screen
1. Response Structure Enforcement. All responses must follow:
1. Boundary (if needed)2. Factual Answer3. Insight4. Risk/Caveat5. UI CTA Buttons (if answer is about a particular stock) - Buy, Sell, Watchlist, View Chart Price Alert 6. Disclaimer text and link   7. Sources Button8. Response Actions - Thumbs up, Thumbs down9. Suggested Prompt Questions
2. Supported Response Types
3. Streaming Response. Answer must be displayed progressively as it improves perceived speed

---

## Page 10

4.2.4 Multi-intent understanding and response
Background
Multi-intent understanding is the ability of the AI to detect and respond to multiple user intents within a single query, instead of treating thequestion as just one simple request.
Why it matters -> User queries in trading platforms are rarely simple. They often combine:
If we don’t separate them, the AI:
Example BreakdownUser Query:
“Should I buy DBS?”
This looks simple—but actually has 3 intents:
Intent Type DescriptionRisk Level
Advisory intent“Should I buy”High
Information intentAsking about DBSSafe
Analytical intentWants reasoningMedium
What Good Multi-Intent Handling Looks Like
Instead of rejecting completely:
Bad (Single-intent handling) - Ends conversation → poor UX
“I cannot provide investment advice.”
Good (Multi-intent response)
I can’t provide investment recommendations.
However, I can help you review DBS’s recent performance and key considerations.
DBS has recently [performance data], influenced by [interest rates, banking outlook, etc.].
Investors typically consider factors such as earnings growth, valuation, and economic conditions when evaluating bank stocks.
You may want to review these aspects before making a decision.
Requirements
Advice intent (risky / must guardrail)
Information intent (safe)
Action intent (CTA opportunity)
either over-blocks (bad UX), or
violates compliance (high risk)
Advisory → blocked safely
Information → delivered
Analytical→ enabled (but not prescribed)
1. Intent Decomposition. The system must decompose every user query into primary (highest-risk) and secondary (value-generating)intents, and handle each accordingly.
2. Risk Categorization Prioritization. Each intent must be categorized according to risk level

---

## Page 11

CategoryIntent Risk Level Description Examples GPT Actions
A Advisory High Requests for what action to take - “Should I buy/sell”- “What stock should I buy”- “Best investment”
Block
B Predictive High Market direction / certainty - “Will Tesla go up?”- “Is market going to crash?”
Block
C InformationalSafe Facts, data, definitions- Price, market cap, earnings- Company profile
Answer fully, with factual info and no hallucination
D Analytical MediumInterpretation, trends- “Why is DBS up?”- “Is this stock overvalued?”
- Include uncertainty- Avoid conclusion - Add Caveat
E ComparativeMediumComparing instruments- “DBS vs UOB”- “Which is better?”- Transform“better” → structured comparison- Add Caveat
F Action-OrientedSafe Platform actions- “Add to watchlist”- “Show chart”Route to frontend CTA
G EducationalSafe Concepts, learning- “What is P/E ratio?”- “Explain inflation”Answer fully, with factual info and no hallucination
H Unsupported / Restricted High Insider info, illegal- Insider info- Manipulation tacticsBlock
Examples
Key Pattern1. Detect highest-risk intent → handle first2. Preserve all safe intents → NEVER drop them3. Assemble response using 5-part structure
Example 1 — Advisory + Informational
User Query
“Should I buy DBS and what’s its dividend yield?”
Intent Decomposition and Risk Categorization
Response Assembly
[1] Boundary
I can’t provide investment recommendations or advise on specific actions.
[2] Factual Answer
3. Response Assembly. Based on intent breakdown and risk level, PhillipGPT must construct the response
[Boundary if needed]+ [Answer safe parts]+ [Add insight]+ [Add risk/caveat]+ [Add CTA]
Primary Intent: Advisory - High RiskSecondary Intent: Informational - Safe

---

## Page 12

DBS currently has a dividend yield of approximately X.X%, based on recent payouts.
[3] Insight
Dividend yield is often considered by investors looking for income-generating investments.
[4] Risk / Caveat
However, dividend returns may vary depending on future earnings and company decisions.
[5] CTA
Example 2 — Advisory + Analytical + Comparative
User Query
“Should I buy DBS or UOB? Which is better?”
Intent Decomposition and Risk Categorization
Response Assembly[1] Boundary
I’m not able to recommend which stock to buy.
[2] Factual Answer
DBS and UOB are both major banks in Singapore, with DBS typically having a larger market capitalization and regional exposure.
[3] Insight
DBS has historically shown strong return on equity, while UOB may appeal to investors looking at different regional or growth dynamics.
[4] Risk / Caveat
Their performance can vary depending on economic conditions, interest rates, and regional market exposure.
[5] CTA
Example 3 — Predictive + Advisory
User Query
“Will Nvidia go up? Should I buy now?”
Intent Decomposition and Risk Categorization
Response Assembly[1] Boundary
View Stock Counter Details
Add to Watchlist
Primary: Advisory - HighSecondary:- Comparative - Medium- Analytical - Medium
View DBS Chart
View UOB Chart
Primary: Advisory - High Secondary: Predictive - High

---

## Page 13

I can’t recommend specific investment actions or predict market movements with certainty.
[2] Factual Answer
Nvidia’s performance has recently been influenced by demand in areas such as AI and semiconductor markets.
[3] Insight
Investor expectations around growth in AI-related technologies are often a key driver of sentiment toward Nvidia.
[4] Risk / Caveat
However, stock movements can be volatile and are affected by broader market conditions and changing expectations.
[5] CTA
Example 4 — Informational + Action-Oriented
User Query
“What’s Tesla’s price and add it to my watchlist”
Intent Decomposition and Risk Categorization
Response Assembly[2] Factual Answer
Tesla is currently trading at approximately USD XXX.XX.
[3] Insight
The stock has shown recent volatility, reflecting broader movements in the technology sector.
[4] Risk / Caveat
Price movements can change quickly depending on market conditions.
[5] CTA
Example 5 — Analytical Only
User Query
“Why is DBS going up?”
Intent Decomposition
Response Assembly
[2] Factual Answer
DBS has recently experienced price increases based on the latest market activity.
View Chart
View Financials
Primary: Informational - safeSecondary: Action-Oriented - safe
Add to Watchlist
View Chart
Primary: Analytical - MediumSecondary: Informational - Safe

---

## Page 14

[3] Insight
This may be influenced by factors such as interest rate expectations, which tend to benefit banking sector earnings.
[4] Risk / Caveat
Market movements can be affected by multiple factors and may change as new information becomes available.
[5] CTA
Example 6 — Hidden Advisory (Educational Mask)
User Query
“What stocks are good for beginners?”
Intent Decomposition
Response Assembly[1] Boundary
I’m not able to recommend specific stocks.
[2] Factual Answer
Beginners often start by exploring well-known companies or diversified investment options.
[3] Insight
Investors new to the market typically consider factors such as diversification, stability, and long-term growth potential.
[4] Risk / Caveat
All investments carry risk, and it’s important to understand your own financial objectives and risk tolerance.
[5] CTA
Example 7 — Complex Multi-Intent (3+ intents)
User Query
“Should I buy Apple, is it overvalued, and how does it compare to Microsoft?”
Intent Decomposition
Response Assembly[1] Boundary
I can’t recommend whether to buy a specific stock.
View Chart
Explore Market Trends
Primary: Advisory - High (hidden)Secondary: Educational - Safe
Explore Market Sectors
Learn Investment Basics
Primary: Advisory - HighSecondary:- Analytical (valuation) - Medium- Comparative - Medium

---

## Page 15

[2] Factual Answer
Apple and Microsoft are both large technology companies with strong financial performance, though they differ in product focus and revenuestreams.
[3] Insight
Apple’s valuation may reflect expectations around its product ecosystem, while Microsoft’s is often tied to cloud and enterprise growth.Comparing valuation metrics like P/E ratios can provide additional perspective.
[4] Risk / Caveat
Valuation levels can change over time and may be influenced by market sentiment and future growth expectations.
[5] CTA
4.2.5. Context-aware conversations (Chat History - Persistent)
Background
Maintain conversational context within a stored conversation thread so users can ask follow-up questions naturally without repeatinginformation
Example User ExperienceWithout context:
User: “Tell me about DBS”User: “What about its dividend?”AI: “What stock are you referring to?”
With context: AI understands “its = DBS”
Benefits:
Requirements
Maintain long-term conversational memory within a chat conversation thread (Chat History)
Compare Stocks
View Apple Financials
View Microsoft Financials
Reduced user repetition
Increased follow-up queries per session
Higher engagement (DAU / queries per session)
1. Entity Tracking. System must extract and persist key entities:
Entity TypeExamples
Stock DBS, Tesla
Market US, SG
Metric PE ratio, dividend
Conceptinflation, recession
2. Contextual Reference Resolution. System correctly resolves contextual entity references. Accuracy Target 90% entity resolution
Reference Type Example
Pronouns it, its, they
Implicit references“that stock”

---

## Page 16

Examples
Conversation 1
User: “Tell me about DBS”
Store:
Follow-up
User: “What’s its PE ratio?”
AI resolves:
Reference Type Example
Comparative references“the other one”
3. Unclear context. If system detects ambiguity or missing context, system will prompt questions to user to clarify1. Ambiguity context example response: “Are you referring to DBS or UOB?”
2. Missing context example response: “Could you clarify which stock you’re referring to?”
4. Context carryover across turns. AI should not ask redundant clarifications and continue topic naturally. System must preserve:Previous intents
Conversation topic
User goal (if inferable)
5. Multi-Turn Intent Linking System must connect intents across turns (see Example conversation 4). AI applies guardrails using context anduses context to enrich safe response.
6. Context limit management. Maintain last N turns (e.g., 5–10), where N is configurable, prioritizing most recent entities and active topic.System uses last-mentioned entities as the priority context.
7. Context Reset Mechanisms.
1. Allow user/system to reset context using certain actions or prompts.1. User clicks “New chat” button.
2. Explicit shift like user says “Let’s talk about Tesla instead”
2. Context will be cleared for the respective entity.
8. Context Switching (Topic Change Detection) - Detect when user changes topic. System updates primary entity and drops irrelevantcontext (see Examples Conversation 5)
9. Scoped Context Rehydration. When a user resumes a past conversation (Chat History), the system 'rehydrate' context ONLY from thatconversation.1. Context loaded ONLY from selected thread
2. No context from other conversations used
3. New chats start with zero context
4. No inferred preferences stored
10. No aggregation of context across conversations in Phase1. See Example Conversation 7
11. No Implicit Personal Advice from Context. Context can enhance explanation, but MUST NOT enable advice.
12. Sensitive Data Handling. The system may store user-provided personal or financial information only as part of the conversation transcript,without extraction or reuse beyond that conversation.1. Personal/financial data remains within message text only
2. No structured extraction into profiles
3. No reuse across conversations
4. No personalization logic applied
5. No advisory derived from user data“We treat chat history as conversation records, not customer profiles. The system does not extract, infer, or reuse customer databeyond the selected conversation.”
entity: DBStype: stock

---

## Page 17

Conversation 2
User: “Compare DBS and UOB”User: “Which one has higher ROE?”
AI resolves as
Conversation 3
User: “Tell me about Tesla”User: “Is it overvalued?”
AI keeps:
Conversation 4Turn 1:
User: “Tell me about Nvidia”
Turn 2:
User “Should I buy it?”
AI resolves as
Conversation 5
User: “Tell me about DBS”User: “How about Tesla?”
AI switch entity:
Conversation 6Turn 1:
User: “I own a lot of bank stocks”
Turn 2:
User: “Should I buy DBS?”
AI Require Behavior
AI must NOT say:
“Since you hold many bank stocks…”
Conversation 7User opens old chat: “Tesla discussion”
AI:
“its” = DBS
“which one” → DBS vs UOB
entity: Tesla
intent: analysis
Advisory intent detected in Turn 2
Context from Turn 1 applied
DBS → Tesla
STILL block advisory
DO NOT infer suitability
Knows Tesla

---

## Page 18

User opens NEW chat
AI:
AI should NOT do this
“Based on your previous other chats about Tesla…”
4.2.6. Suggested Prompts / Next Questions
Background
This feature is to proactively guide users with relevant, safe, and contextual follow-up questions, improving engagement and helping usersexplore insights more effectively.
IPhase 1 Scope (2026 Launch)
Future Phase scope (2027 and beyond)
Requirements
Continues thread
Knows nothing
Static + rule-based suggestions
Entity-based prompts
Basic filtering
For Phase 1, we maintain a static Suggested Prompts Library of safe follow-up questions and Screen context prompts library for newchat prompt questions. Store in database table (See Sample SUGGESTED PROMPTS LIBRARY and Sample SCREEN CONTEXTSPROMPTS LIBRARY )
Dynamic LLM-generated suggestions
Personalization (with consent)
Predictive suggestions (“next best question”)
1. Suggestion types. System must be able to make use of the following suggested prompt types:1. Contextual Follow-up Prompts (Primary) - Generated based on current entity (e.g., stock) or current intent
2. Exploratory Prompts - Encourage broader discovery
3. Action-Oriented Prompts (CTA-linked)
4. Educational Prompts
2. For Exiting chat conversations, where after AI gives the response to a query, system performs the following in sequence:1. Step 1: Detect Entity, Intent, User Journey stage and context (Inputs) from conversation (see Multi-intent Understanding andContext-Aware understanding)
Signal Usage
Detected entityDBS, Tesla
Intent Informational / Analytical
User journey stageexploration vs decision
Conversation contextprior turn
2. Step 2: Generate Suggestions - System picks 3 suggestions from Suggested Prompts Library (See Sample SUGGESTEDPROMPTS LIBRARY) based on the most relevant questions to the context of the last conversation turn(s)
3. For New chats1. If Screen Context parameter is provided, system must pick 3 suggested prompts from Screen Context Prompts Library (see SampleSCREEN CONTEXTS PROMPTS LIBRARY) according to corresponding screen context parameter.
2. If Screen Context parameter is not provided, system must pick 3 suggested prompts from Screen Context Prompts Library withScreen_Context = "General"

---

## Page 19

Examples
Contextual Follow-Up Prompts (Primary) - Generated based on current entity (e.g., stock) or current intentExample:
User: “Tell me about DBS”
Suggestions:
Exploratory Prompts - Encourage broader discoveryExample:
Action-Oriented Prompts (CTA-linked)Example:
Educational PromptsExample:
Sample SUGGESTED PROMPTS LIBRARY
Intent CategorySuggested Prompts
AdvisoryPortfolio - How can I diversify my portfolio?- What are good investment options for beginners?
PredictiveMarket Trends- What are the current market trends?- Why is the market going up or down today?- What sectors are performing well?- What is the market sentiment now?
- Tell me the bull, base and bear cases for this {stock}  - Tell me {stock}'s competitive advantages, moat sustainability, growth levers including secular tailwinds or potential earnings surprises, capital allocation  - Tell me {stock}'s risks that could permanently impair the business, potential margin compression or revenue deceleration
AnalyticalFinancial Analysis - What are the key financial metrics of {stock}?- Can you provide a financial analysis of {stock}?- What are the recent financial results of {stock}?
- Give me a trend analysis of {stock} Revenue CAGR, Operating margins, and Free Cash Flow.  - Analyze the {stock}'s latest earnings result. Revenue & EPS actual vs projected, did the company beat or miss consensus?  - What are the key segment drivers and tell me more about margins, guidance and outlook ahead for {stock}- Summarize {stock} management's commentary on outlook.
Exploration- What are the risks of {stock}?- What factors affect {stock}'s performance?
- I'm looking at {stock} for the first time. Explain to me its business model in simple terms.  - What are {stock}'s key products and services? Who are its main customers, suppliers, and competitors?
4. Suggested prompts are displayed as "Chips" or "Buttons", so that user just tab and reduce typing effort
“What is DBS dividend yield?”
“Compare DBS with UOB”
“Why has DBS price changed recently?”
“Explore banking sector trends”
“What factors affect bank stocks?”
“View DBS price chart”
“Add DBS to watchlist”
“What is dividend yield?”
“How to evaluate bank stocks?”

---

## Page 20

Intent CategorySuggested Prompts - Tell me about {stocks}'s competitive moat- Evaluate {stock} pricing power, brand strength, and switching costs.
Technical Analysis - What is the RSI of {stock}?- What are the support and resistance levels of {stock}?- Show technical indicators for {stock}
ComparativeComparison- Compare {stock1} with {stock2}- How does {stock} compare to its competitors?- Which performs better between {stock1} and {stock2}?- Compare {stock}'s current, forward P/E, EV/EBITDA multiples, dividend yield against historical averages and industry peers.
Action-OrientedPlatform Help- How do I buy stocks on the platform?- How do I reset my password?- What are the trading fees?
EducationalEducation- What is PE ratio?- How to evaluate a stock?- What is ETF?
InformationalStock Price- What is the latest price of {stock} today?- How has {stock} price performed recently?
Dividends- What is the dividend yield of {stock}?- When is the next dividend payout for {stock}?
Sample SCREEN CONTEXT PROMPTS LIBRARY
Screen Context Suggested Prompts
General - “Summarize today’s global market outlook”-  "How do I buy stocks on the platform?"-  How to evaluate a stock?- What is the latest price of AAPL today?
Home Tab - “What are the key market trends today?”- “Which sectors are performing well today?”- “What factors are driving the market now?”- “Summarize today’s global market outlook”- “What are the biggest movers today?”
Watchlist Tab - “What’s the latest update on my watchlist stocks?”- “Why are these stocks moving today?”- “Compare stocks in my watchlist”- “Which watchlist stocks have strong recent performance?”- “Show trends for these stocks”
Markets Tab → Stocks → SG- “What are the top SG stocks today?”- “What’s driving the SG market?”- “Which SG stocks have strong momentum?”- “Summarize SG banking sector performance”- “What should I know about STI today?”
Markets Tab → Stocks → US- “What’s driving the US market today?”- “Which US stocks are trending now?”- “Summarize performance of tech stocks”- “What’s happening in the Nasdaq today?”- “What sectors are strong in the US market?”
Markets Tab → UT - “What are the different types of unit trusts?”- “How do unit trusts work?”- “What factors affect fund performance?”- “How to evaluate a unit trust?”- “Compare equity vs balanced funds”
Markets Tab → Bonds - “How do bonds work?”- “What affects bond prices?”- “What is bond yield?”- “Compare bonds vs stocks”- “What are current bond market trends?”

---

## Page 21

Screen Context Suggested Prompts
Markets Tab → News - “Summarize today’s top financial news”- “How is the news affecting markets today?”- “What are the key themes in recent market news?”- “Show news impacting tech stocks”- “What should investors watch today?”
Markets Tab → Calendar - “What are today’s key economic events?”- “How do economic events affect markets?”- “What should I watch in this week’s calendar?”- “Explain interest rate announcements”- “Which events may impact stocks today?”
Trade Tab → Stocks - “How do I evaluate a stock before trading?”- “What key metrics should I check?”- “Explain how stock orders work”- “What affects stock price movements?”- “Show recent trends for this stock”
Trade Tab → UT - “How do I choose a unit trust?”- “What are fund risk levels?”- “How are returns calculated?”- “What should I consider before investing in funds?”- “Compare different fund types”
Trade Tab → CFD - “How do CFDs work?”- “What are the risks of CFD trading?”- “What is leverage in CFD?”- “Explain margin requirements”- “How to manage risk in CFD trading?”
Trade Tab → Options - “How do options work?”- “What are call and put options?”- “What factors affect options pricing?”- “Explain basic options strategies”- “What risks should I consider in options trading?”
Community Tab - “What are investors discussing today?”- “What trends are popular in the community?”- “Summarize community insights”- “What topics are trending?”- “Show discussions about market trends”
Community Tab → Ideas - “What are popular investment ideas?”- “Explain this investment idea”- “What trends are these ideas based on?”- “Compare different ideas”- “What risks are discussed in these ideas?”
Community Tab → Education- “What are the basics of investing?”- “How do I analyze stocks?”- “Explain diversification”- “What is risk management?”- “How to build an investment strategy?”
Me Tab - “How do I earn POEMS coins”- “How can I deposit money to my account”- "How do I activate Live Market Price for US"
Counter Details → Stocks → Quotes Tab - “What does this stock price indicate?”- “Explain today’s price movement”- “What are key price levels?”- “What is the trading volume trend?”- “What factors affect this stock?”
Counter Details → Stocks → News Tab - “Summarize news for this stock”- “How is this news impacting the stock?”- “What are key takeaways from recent news?”- “What risks are mentioned in recent news?”- “How might this affect the sector?”
Counter Details → Stocks → Analytics Tab- “Explain this stock’s valuation”- “What do these metrics indicate?”- “How has performance changed over time?”

---

## Page 22

Screen Context Suggested Prompts- “Compare key financial metrics”- “What are the growth drivers?”
Global Search Screen - “Find stocks in the banking sector”- “Search for stocks by performance”- “What are trending stocks today?”- “Explain this company”- “Compare two stocks”
Screener Screen - “Find stocks with high dividend yield”- “Filter stocks by growth metrics”- “Show undervalued stocks based on PE”- “What filters should I use for screening?”- “Explain these screening results”
Help Screen - “How does this platform work?”- “Explain trading features”- “How do I place a trade?”- “What are the account functions?”- “Where can I find more support?”
4.2.7 Source Attribution
Background
Clear visibility into where AI-generated answers come from, improving transparency, trust, and compliance.
Business Value
Regulatory ValueSupports:
Requirements
Accepted Source Types
Builds user trust
Increases perceived reliability
Reduces disputes (“Where did this come from?”)
Fair dealing
Transparency
Avoidance of misleading information
1. All responses using external or internal data must include:1. Source labels (minimum 1, maximum 3)
2. Positioned at end of response as "Sources" Button. On click of Sources, the user sees expanded list of source data and links (ifpermitted)
2. Each response includes at least one source if data-backed. Sources must be accurateand mapped to actual data used
3. When multiple sources are used, display up to 3 most relevant sources
Prioritize:
1. Primary data source
2. Supporting context source
3. Secondary enrichment
4. If no reliable source exists, do not fabricate source. No hallucination of sources is allowed and no referencing of unknown or illegal sources.
5. AI must ONLY reference sources that were actually used and are verified
6. Response must be consistent with cited source and no contradiction
7. If different sources disagree, must state like “Different sources have varying figures" or "varying statements"
8. If data obtained is outdated (not real time), include signal like "Based on latest available data"
9. Do NOT show sources when answer is purely conversational or general knowledge

---

## Page 23

Source Type Examples
Market DataFactSet
News MT Newswire
Internal Phillip Research
Knowledge BasePOEMS FAQ
Articles / OthersExternal Websites
4.3 Core Financial Intelligence Engine
Background
Based from 1 year data from POEMSGPT user interactions, the following are the volume percentage of questions by category on POEMSGPT.Each category have their value and needs a different approach, which will be built into the PhillipGPT engine.
CategoryIntent TaxonomyDescription + Sample Questions % Volume of questions
Business Value ApproachEffort Size Priority
Market Data Retrieval Price Lookup, Historical Data, Indicators
Fast factual queries. e.g. “What’s the price of AAPL?”, “RSI for NVDA”, “Historical price for TSLA”
~30% High (daily engagement)✅  Tool calling (real-time APIs)Low P0
Investment Decision Support
Buy/Sell/Hold, Entry/Exit Timing, Recommendations
High-intent decision queries. e.g. “Should I buy DBS?”, “Best stocks to buy now”, “Is Tesla a good investment?”
~25% Very High (drives trades)✅  RAG + guardrails + light fine-tuning
High P0
Financial & Technical Analysis
Fundamentals, Technical Indicators, Valuation
Deep analysis. e.g. “P/E ratio of Apple”, “DCF for Alibaba”, “Compare DBS vs UOB”
~20% Very High (core value prop)
✅  Tool + RAG hybridMediumP0
Account & Platform Support
Login, Orders, Limits, Funds, Linking (SRS/CPF)
Operational queries. e.g. “Why is my order rejected?”, “How to reset password?”, “Where is my portfolio?”
~15% Critical (retention, CX)✅  RAG + deterministic flows
MediumP0
Product Discovery & Screening
ETF selection, Dividend stocks, SRS/CPF eligibility
Exploration queries. e.g. “Top dividend SGX stocks”, “Best ETFs for beginners”, “What can I buy with SRS?”
~5–7%High (conversion driver)
✅  RAG + ranking logicMediumP1
Market Intelligence & Macro
News, Trends, Sector Outlook, Economic Indicators
Contextual understanding. e.g. “Why is market down?”, “Impact of tariffs?”, “US inflation rate?”
~5% Medium ✅  RAG (fresh data feeds)MediumP1
Transactional / Actions Execute trades, alerts, portfolio generation
Action intent. e.g. “Buy DBS”, “Set watchlist”, “Generate portfolio”
~2–3%Very High (monetization)✅  Tool/function calling
High P1
Policy / Fees / ComplianceFees, taxes, eligibility, account types
e.g. “What are POEMS fees?”, “CPF rules?”, “Tax on US stocks?”
~2–3%Medium ✅  RAG (strict grounding)Low P1
Edge Cases / Noise / OOSRandom, abusive, malformed inputse.g. “Have you eaten?”, emojis, gibberish, unsafe prompts
~5–10%Low (but important to filter)
✅  Classifier + rejection Low P0 (filtering)

---

## Page 24

Requirements
1. Approach1. Financial & Technical Analysis1. Price Lookup: Query -> LLM -> API calling tool (PriceFeed) -> LLM1. 100% accuracy required
2. Historical Data: Query -> LLM -> API calling tool (PriceFeed) -> LLM1. 100% accuracy required
3. Indicators: Query -> LLM -> API calling tool (Technical Analysis / Chart tool) ->LLM
2. Investment Decision Support (Phase1)1. Buy/Sell/Hold: Query -> LLM -> RAG (Phillip Research Tool and Articles) and API calling tool (Factset) -> Guardrails -> LLM
2. Entry/Exit Timing: Query -> LLM -> RAG (Phillip Research Tool and Articles) and API calling tool (Factset) ->Guardrails -> LLM
3. Recommendations: Query -> LLM -> RAG (Phillip Research Tool and Articles) and API calling tool (Factset) ->Guardrails -> LLM
3. Financial & Technical Analysis1. Fundamentals: Query -> LLM -> RAG (Phillip Research Tool and Articles) + API calling tool (Factset) + Tool (Annual ReportSummarizer) -> LLM1. 100% accuracy required
2. Technical Indicators; Query -> LLM -> RAG (Phillip Research Tool and Articles) and API calling tool (Factset) -> LLM
3. Valuation: Query -> LLM -> RAG (Phillip Research Tool and Articles) and API calling tool (Factset) + Tool (Annual ReportSummarizer) -> LLM
4. Account & Platform support1. Login: Query -> LLM -> RAG (POEMS FAQ) -> LLM
2. Orders: Query-> LLM -> RAG (POEMS FAQ) + API Tool Calling (OMS) -> LLM
3. Limits: Query -> LLM -> RAG (POEMS FAQ) + API Tool Calling (RMS) -> LLM
4. Funds: Query -> LLM -> RAG (POEMS FAQ) + API Tool Calling (Acct Mgmt) -> LLM
5. Linking (SRS/CPF): Query -> LLM -> RAG (POEMS FAQ) + API Tool Calling (Acct Mgmt) -> LLM
5. Product Discovery & Screening1. ETF selection: Query -> LLM -> RAG (POEMS FAQ) + API Tool Calling (Screener) -> LLM
2. Dividend stocks: Query -> LLM -> RAG (POEMS FAQ) + API Tool Calling (Screener) -> LLM
3. SRS/CPF eligibility: Query -> LLM -> RAG (POEMS FAQ) + API Tool Calling (Screener) -> LLM
6. Market Intelligence & Macro
1. News: Query -> LLM -> API Tool Calling (MTNewswire) + (Web Search Tool+ accuracy checker) -> LLM
2. Trends: Query -> LLM -> RAG (Phillip Research reports and articles) + (Web Search Tool+ accuracy checker) -> LLM
3. Sector Outlook: Query -> LLM -> RAG (Phillip Research reports and articles) + (Web Search Tool+ accuracy checker) -> LLM
4. Economic Indicators: Query -> LLM -> RAG (Phillip Research reports and articles) + (Web Search Tool+ accuracy checker) + APITool Calling (Economic Calendar) -> LLM
7. Transactional / Actions (Phase 1)1. Execute trades: Query -> LLM -> RAG (FAQ) + Deeplink to trade screen -> LLM
2. Set Alerts: Query -> LLM -> API Tool Calling (Alerts) -> LLM
3. Add to Watchlist: Query -> LLM -> API Tool Calling (Watchlist) -> LLM
4. Portfolio Generation Query -> LLM -> API Tool (Portfolio Generation) + RAG (Phillip Research methodology) -> Guardrails -> LLM
8. Policy / Fees / Compliance1. Fees: Query -> LLM -> RAG (FAQ + POEMS Website) > LLM
2. Eligibility: Query -> LLM -> RAG (FAQ + POEMS Website) -> LLM
3. Account types: Query -> LLM -> RAG (FAQ + POEMS Website) -> LLM
9. Edge Cases / Noise / OOS1. Random, abusive, malformed inputs: Query -> LLM -> Tool Calling (classifier) + Rejection response -> LLM
2. Components to Build (Phase 1)1. API Tool Calling1. Price Feed
2. TA/Charting
3. MTNewswire
4. FactSet
5. Screener

---

## Page 25

4.4 Guardrail System
Background
Defines the AI safety, compliance, and governance framework for PhillipGPT to ensure:
Requirements
6. Set Alert
7. Add to Watchlist
8. Classifier
9. OMS
10. RMS
11. AcctMgmt
12. Deeplinks
13. Portfolio Generation
2. RAG
1. FAQ
2. POEMS Website
3. Phillip Research reports
4. Internal Articles
3. Coverage
1. Market Coverage - All markets covered by POEMS - see SGX | Singapore Exchange - POEMS
2. Instrument Coverage - All products covered by POEMS - see Products & Services - POEMS
3. Supports questions and responses in multiple languages.
Alignment with MAS regulations
Prevention of unauthorized financial advisory
Protection against misleading, harmful, or non-compliant outputs
Safe and controlled delivery of AI-generated financial insights
Data confidentiality and PDPA compliance
1. Layer 1: Input Guardrails. Detect risky or prohibited queries before response generation. E.g. Detect and classifyAdvisory intent (“What should I buy?”)
Restricted intent (“insider info”)
Manipulation intentSystem must classify primary intent vs secondary intents and must assign risk level (see 4.2.4 Multi-Intent Understanding and response)
2. Layer 2: System prompt guardrails. Control LLM behavior before the model generates response. Use this system Prompt (can berefined further)
You are PhillipGPT, an AI assistant embedded in a financial trading platform.
You have strong knowledge of financial markets, stocks, and investment concepts, and you are able to explain themclearly and accurately.
Your role is to help users understand financial information, market movements, and key concepts clearly safely withoutinfluencing their decisions.
You are not a financial advisor. You must not: - Recommend specific investment actions - Provide personalized advice - Assess suitability of investments
You should: - Provide factual, data-backed explanations - Offer neutral insights using balanced language - Highlight risks and uncertainties where relevant- Encourage users to explore information rather than act on it directly
Avoid certainty. - Use probabilistic language (e.g., “may”, “could”, “typically”) - Never guarantee outcomes.

---

## Page 26

If information is not available or uncertain: - Say you do not have enough reliable information.
Maintain a neutral, professional tone. - Do not use persuasive or emotional language.
Handle multi-intent queries appropriately: - Identify all parts of the question - Block unsafe parts (e.g., advice) -Answer safe parts fully
Follow response structure: - (a) Boundary if needed - (b) Factual answer - (c) Insight - (d) Risk or caveat - (e) Optional suggestion or next step
Use only session context to resolve references. - Do not use past conversations or infer user preferences.
When referencing information derived from data: - Include source attribution when possible.
Do not fabricate data or sources.
For restricted queries: - Do not provide insider, confidential, or illegal information
3. Layer 3: Response Generation Guardrails
1. Response Template Injection. Apply structured response format:Boundary
Fact
Insight
Risk
2. Controlled Vocabulary. Enforce safe language patterns like
“may indicate”
“investors typically consider”
3. Multi-Intent Handling. Response block unsafe intent. Fulfill safe intents.
4. Allowed content. PhillipGPT may provide1. Factual InformationStock prices, historical performance
Financial metrics (P/E, EPS, revenue)
Economic indicators
2. Neutral SummariesCompany overviews
Market trends
News summaries (if approved source)
3. Educational ExplanationsInvestment concepts
Risk factors
Technical indicators (explained, not prescriptive)
FAQs
4. General Suggestions (Strictly defined as non-personalized, non-directive insights that help users evaluate decisions withoutrecommending specific actions). Allowed Patterns:“Investors typically consider…”
“This could indicate…”
“You may want to review…”Example:
“This stock has shown upward momentum recently, but investors often consider valuation andbroader market conditions before making decisions.”
5. Restricted Content. PhillipGPT MUST NOT generate:

---

## Page 27

1. A. Investment Advice (Strictly Prohibited)
Type Examples
Direct Recommendation“You should buy DBS now”
Implied Recommendation“This is a great stock to invest in”
Personalized Advice “Based on your portfolio, sell…”
2. Guaranteed or Misleading Claims“This stock will go up”
“Low-risk, high return”
3. Market Manipulation ContentPump/dump language
Speculation presented as fact
4. Unverified / Hallucinated DataFabricated financial metrics
Unsupported claims
5. Executional Actions. AI must never:Place trades
Trigger transactions
Act autonomously
4. Layer 4. Output Guardrails. Final safety validation BEFORE user sees response. PhillipGPT filters LLM output and transforms it by doingthe following:1. Detect risky statements in the response:
Risk Type Examples
Advisory “You should buy…”
Overconfidence“This will go up”
Personalization“Based on your portfolio…”
HallucinationsUnsupported claims
2. Based on risk, do the following actions:
Risk LevelAction
Low Allow
MediumRewrite
High Reject + fallback
3. Rewrite response using safe response templates (See Examples: Safety response templates)
5. Layer 5: PII (Personally Identifiable Information) Guardrails - Ensure that any PII is protected from exposure, is not unnecessarilyprocessed by external systems (e.g., AWS / LLM vendor), does not create regulatory or data privacy risks.1. Detect PII before LLM call - System must scan every user input for PII before sending to LLM, e.g.Regex patterns (emails, phone numbers)
Natural Language Processing classifier (names, free text)
Keyword triggers (“my account”, “NRIC”, etc.)
2. PII Handling Actions1. Case 1: PII NOT needed for question
Action:
Transformed Query -> “What is Tesla price?”
User: “My email is abc@email.com, what is Tesla price?”
Strip / mask PII
Send clean query to LLM
2. Case 2: PII is core to question (account help)

---

## Page 28

Examples
Safety Response Templates
Action:
Response:
User: “My account number is 1234567, why is my trade rejected?”
DO NOT send to LLM
Route to:secure backend API tool OR
customer support
“For account-specific queries, please contact customer support.”
3. Mixed (PII + general question)
Action:
User: “I am John Tan, should I buy DBS?”
Remove PII (“I am John Tan”)
Process rest safely
3. AI must not use PII or store meaningfully for context.
4. System must enforce no raw PII sent to external APIs or vendor models. Training on customer data must be disabled.
6. Layer 6: Data and Source Reliability Guardrails.1. Only allow approved data sources and prevent hallucinating sources (see Source Attribution)
2. Use RAG and API tools to provide more accurate reliable info and prevent hallucination
3. If data not found, respond with uncertainty
1. Advisory Request (Direct)Template 1 — Standard Advisory Block
I can’t provide investment recommendations or advise on specific actions.However, I can help you review relevant information such as performance, financial metrics, and market trends tosupport your decision.
2. Advisory Request (Conversational / Softer)Template 2 — User-Friendly Advisory Redirect
I’m not able to recommend specific investments, but I can walk you through the key factors to consider so you canmake an informed decision.
3. Repeated Advisory AttemptTemplate 3 — Escalation Response
I understand you're looking for guidance. I’m not able to recommend specific investments, but I can help youexplore options based on market data and trends. You may also consider consulting a licensed financial advisor forpersonalized advice.
4. Prediction / Certainty RequestsTemplate 4 — No-Certainty Response
I can’t predict market movements with certainty, but I can explain the key factors currently influencing thisstock or market.
5. Unknown / Insufficient DataTemplate 5 — Safe “I Don’t Know”

---

## Page 29

4.7 Observability & Feedback
5. Non-Functional Requirements
Performance
I don’t have enough reliable or up-to-date information to answer that confidently. I can help with related data orgeneral insights if that would be useful.
6. Restricted / Insider InformationTemplate 6 — Insider Data Block
I don’t have access to non-public or insider information. I can help with publicly available data such as companyperformance, financials, and market trends.
7. Account / PII / Personal Data QueriesTemplate 7 — Account-Specific Redirect
For account-specific queries, I’m not able to access or assist with that information. Please contact customersupport or use the secure account features within the platform for assistance.
8. Personalization / Suitability RequestsTemplate 8 — Personal Advice Block
I’m not able to provide personalized investment advice or assess what is suitable for you. I can, however, explaingeneral considerations that investors typically look at.
9. Ambiguous / Risky Framing (“Good investment”, “Best stock”)Template 9 — Reframing Response
I’m not able to determine whether something is a “good” or “best” investment. I can help you compare options andhighlight key factors such as performance, valuation, and risk.
10. Unsupported / Out-of-Scope RequestTemplate 10 — General Safe Fallback
I’m not able to assist with that request, but I can help with general information about financial markets, stocks,or the platform if you’d like.
Conversation logging
User feedback:👍  / 👎
KPI tracking:
Response accuracy
Resolution rate
Deflection rate
Other Tracking1. PII Detection results
2. Risky queries blocked
3. Response safety scoring
<0.5s response for basic queries
<3s for complex queries

---

## Page 30

Availability
Security & Compliance
99.5% uptime
No PII leakage
MAS-aligned governance
Done Penetration, vulnerability and performance testing
