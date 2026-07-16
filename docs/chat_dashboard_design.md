# Enterprise Chat Dashboard — Design Document

## 1. Overview

This document describes the design of an Enterprise Chat Dashboard, a two-tiered interface consisting of a **Dashboard** view for end users interacting with an AI assistant, and an **Admin View** for administrators who need to monitor system health, usage, and cost. The system is intended for organizations deploying a retrieval-augmented generation (RAG) style AI assistant across teams, where users upload documents, chat with an AI grounded in those documents, and where administrators need visibility into how the system is being used, how well it is performing, and how much it costs to run.

The design balances three competing needs: a clean, low-friction chat experience for end users; rich observability for administrators; and a data architecture that supports both without duplicating effort. Every screen described below is grounded in a specific user goal, and each section explains not just *what* is shown but *why* it is shown and *how* it should behave under real usage conditions (large document sets, many concurrent users, degraded retrieval, cost overruns, and so on).

## 2. Goals and Non-Goals

### 2.1 Goals

* Provide a fast, trustworthy chat experience where users can ask questions and receive answers grounded in uploaded or connected knowledge sources.
* Make the provenance of every AI answer inspectable — users should always be able to see which documents or passages informed a response.
* Give users a durable record of their work: past conversations, past uploads, and saved threads should be easy to find again.
* Give administrators the operational visibility needed to run the system responsibly: who is using it, how well retrieval is performing, how many tokens are being consumed, and what it costs.
* Support incremental rollout — the dashboard should work sensibly for a five-person pilot team and scale to a few thousand daily active users without a redesign.

### 2.2 Non-Goals

* This document does not specify the underlying retrieval or embedding pipeline in detail; it assumes a RAG backend exists and focuses on how its outputs and metrics are surfaced.
* This document does not cover authentication/SSO implementation specifics beyond permission boundaries relevant to UI design.
* This is not a visual style guide; component-level visual design (colors, exact spacing) is left to the design system team, though structural and interaction patterns are specified.

## 3. Personas

| Persona | Description | Primary Needs |
|---|---|---|
| **End User (Analyst/Contributor)** | Uses the assistant daily to answer questions from internal documents (policies, reports, contracts, wikis). | Fast answers, trustworthy citations, ability to revisit past chats, ability to upload new material. |
| **Power User (Team Lead)** | Uses the assistant heavily and also curates source material for their team. | All end-user needs, plus visibility into what has been uploaded and how well it's being retrieved. |
| **Administrator (IT/Ops)** | Responsible for system uptime, access control, and performance. | Active session visibility, retrieval health, error rates. |
| **Administrator (Finance/Procurement)** | Responsible for budget and vendor cost. | Token usage trends, cost breakdowns, forecasting, anomaly alerts. |
| **Compliance/Security Reviewer** | Periodically audits usage. | Query logs, feedback logs, access to who queried what and when. |

Designing for five personas across two views means the navigation must clearly separate "things I do" (chat, upload, save) from "things I monitor" (sessions, metrics, cost), while still letting power users move fluidly between them if their role permits.

## 4. Information Architecture

The application is organized into two top-level surfaces, selectable via a persistent left-hand navigation rail. Which surface a user lands on by default is determined by role: end users land on **Dashboard → AI Chat**; administrators land on **Admin View → Active Sessions**, though admins can always switch back to the standard Dashboard to use the assistant themselves.

```
Enterprise Chat App
├── Dashboard (all users)
│   ├── AI Chat
│   ├── Upload History
│   ├── Sources Panel
│   ├── Conversation History
│   ├── Analytics (personal)
│   ├── Feedback
│   └── Saved Conversations
└── Admin View (admin role only)
    ├── Active Sessions
    ├── Query Analytics
    ├── Retrieval Metrics
    ├── Token Usage
    └── Cost Dashboard
```

The navigation rail is collapsible to a compact icon-only mode for users who spend most of their time in the chat pane and want maximum width for reading answers and source excerpts.

A role check gates the Admin View entirely: users without the `admin` or `viewer-analytics` role never see the Admin View entry in navigation, rather than seeing it disabled. This avoids leaking the existence of usage data to users who shouldn't see it, which is itself a mild but real information-disclosure concern in enterprise contexts.

## 5. Dashboard (End-User View)

The Dashboard is the default workspace. It is built around a three-pane layout on desktop: a left navigation/history rail, a center chat pane, and a right-hand contextual panel that changes depending on what's being discussed (typically the Sources Panel). On narrower viewports, the right pane collapses into a slide-over drawer triggered by a "Sources" button in the chat header.

### 5.1 AI Chat

This is the primary screen and the one most users will spend the majority of their time in.

**Layout**: A scrolling message thread with the newest message at the bottom, a persistent input box pinned to the bottom of the viewport, and a header showing the current conversation's title (auto-generated from the first message, editable by the user) along with quick actions: New Chat, Save, Share, Export.

**Message composition**: The input box supports multi-line text, drag-and-drop file attachment (which routes into Upload History), and an optional "source scope" selector that lets the user restrict the assistant's retrieval to a specific folder, document set, or connected data source (e.g., "Search only: Q3 Contracts"). This scope selector matters a great deal in enterprise settings, because unscoped search across an entire organizational corpus often produces noisier, less trustworthy answers than a deliberately scoped one.

**Assistant responses**: Each AI response is rendered with:
* The generated answer text, formatted (markdown, tables, code blocks as needed).
* Inline citation markers (e.g., superscript numbers or highlighted spans) that map to specific source passages.
* A confidence or grounding indicator — a simple three-state badge (Well-Grounded / Partially Grounded / Low Confidence) computed from retrieval score thresholds, so users develop calibrated trust rather than uniform trust in every answer.
* A row of message-level actions: copy, regenerate, thumbs up/down (feeding Feedback), "show sources" (opens Sources Panel scoped to this specific message), and "flag for review" for compliance-sensitive answers.

**Streaming behavior**: Responses stream token-by-token with a visible "Retrieving sources…" state shown before generation begins, so users understand that a retrieval step is happening rather than assuming the system is idle or stuck.

**Empty state**: When a user starts a new chat, the center pane shows a short set of suggested prompts drawn from popular queries in their team (if telemetry permits) or from a static onboarding list, plus a one-line reminder of which sources are currently in scope.

**Error and degraded states**: If retrieval fails, times out, or returns zero relevant passages, the assistant should say so plainly rather than silently generating an ungrounded answer. A visible banner — "No relevant sources found; answering from general knowledge" — followed by the answer, or a stronger stop-and-ask pattern if the organization has configured strict grounding-only mode.

### 5.2 Upload History

A dedicated screen listing every file the current user (or their team, depending on visibility settings) has uploaded to the system, whether uploaded directly into a chat or added proactively as a source.

**Table columns**: File name, type, size, upload date, uploaded by, processing status (Queued / Indexing / Ready / Failed), and the number of chunks or pages indexed. A search box and filters (by date range, file type, status, uploader) sit above the table.

**Row actions**: Preview, download original, re-index (useful if a document was updated), remove from index, and "view usage" — a shortcut that shows which conversations have cited this document, which is a natural bridge into the Sources Panel.

**Failed uploads**: Files that fail processing (unsupported format, OCR failure, size limit exceeded) are shown with a clear reason and a retry action, rather than silently disappearing. This is a common failure point in RAG systems — content silently failing to index and users never realizing why the assistant "doesn't know" about a document they uploaded — so surfacing failure states explicitly is a design priority, not an afterthought.

**Bulk upload**: A drag-and-drop zone supports multi-file and folder upload, with a progress list showing per-file status as processing proceeds asynchronously in the background.

### 5.3 Sources Panel

The Sources Panel is the trust layer of the entire product. It appears as the right-hand contextual pane during chat and can also be opened as a standalone full-page view for deeper inspection.

**Per-message view**: When a user clicks "show sources" on an assistant message, the panel lists every retrieved passage that contributed to the answer, ranked by relevance score. Each entry shows the source document name, the specific page or section, a highlighted excerpt showing the exact text that was used, and a relevance score displayed as a simple bar or percentage.

**Passage-to-claim mapping**: Where feasible, hovering over a citation marker in the answer text highlights the corresponding passage in the Sources Panel, and vice versa — clicking a source excerpt highlights the sentence(s) in the answer it supports. This bidirectional linking is what lets a user actually audit a claim rather than just trust a citation exists.

**Standalone Sources browser**: Independent of any single chat, users can browse all indexed sources, filter by document set, and see aggregate stats per document (how often it's been retrieved, how often it's been rated helpful when cited, last updated date). This helps power users understand which of their team's documents are actually pulling weight in the assistant's answers and which are effectively invisible to retrieval (a strong signal that a document needs better formatting, chunking, or metadata).

### 5.4 Conversation History

A chronological, searchable list of all past conversations belonging to the user (and, for shared team workspaces, conversations shared with the team).

**Layout**: A left-hand list (title, snippet of last message, timestamp, source-scope tag) with the selected conversation rendered in the main pane in read-only or resumable mode. Users can resume any past conversation directly, continuing the thread with full context intact.

**Organization**: Conversations can be grouped by date (Today, Yesterday, Previous 7 Days, Previous 30 Days, Older), and optionally by project or source-scope tag if the organization uses that feature. A search bar supports full-text search across conversation content, not just titles, since users very often remember a fact from an answer but not the conversation title.

**Retention and deletion**: Users can delete individual conversations or bulk-delete by date range, respecting whatever data retention policy the organization has configured (e.g., an admin-set maximum retention period, after which conversations auto-expire regardless of user action).

### 5.5 Analytics (Personal)

A lightweight, personal-scope analytics view distinct from the admin-facing Query Analytics. This answers "how have I been using the assistant" rather than "how is the whole org using it."

**Contents**:
* Total conversations and messages over time (simple line chart, selectable time range).
* Most frequently referenced source documents.
* Personal feedback given (thumbs up/down ratio over time).
* Time saved estimate (if the organization has configured a baseline assumption, e.g., "estimated X hours saved this month" — clearly labeled as an estimate, not a hard metric).

This section is optional and can be hidden entirely by admin configuration for organizations that prefer not to expose usage self-tracking to end users, but where present it tends to build user trust and adoption by making value visible.

### 5.6 Feedback

A dedicated space where thumbs-up/thumbs-down ratings and free-text feedback given throughout the chat experience are collected, viewable, and — importantly — actionable by the user who gave them.

**List view**: All feedback the user has submitted, with the associated question, answer, rating, and any comment, sorted by date. Users can edit or retract feedback.

**Submission flow**: A thumbs-down triggers an optional short follow-up ("What went wrong?" with quick-select tags: Incorrect, Missing context, Wrong sources, Off-topic, Other) plus a free-text field. Thumbs-up can optionally prompt "What made this helpful?" for positive signal but should never be forced — friction on positive feedback tends to suppress it entirely.

**Why this matters structurally**: Feedback collected here feeds directly into the Admin View's Query Analytics, and over time into retrieval tuning and prompt iteration. The design principle here is that feedback should be nearly zero-friction to give and easy to review later, since feedback volume drops sharply with every added step.

### 5.7 Saved Conversations

Distinct from ordinary Conversation History, Saved Conversations is a curated, user-maintained collection of threads worth keeping for reference — the difference between a browser's full history and its bookmarks.

**Behavior**: Any conversation can be "saved" via a star/pin action from the chat header or from the Conversation History list. Saved conversations appear in their own tab, optionally organized into user-created folders or tags (e.g., "Onboarding answers," "Legal precedents").

**Sharing**: Saved conversations can be shared with specific teammates or made visible to a whole team/workspace, turning a personal save into a small internal knowledge base of vetted Q&A pairs. This is a particularly high-value feature in enterprise deployments, since it lets good answers compound in value across an organization rather than being reproduced or re-asked repeatedly.

**Export**: Saved conversations can be exported as Markdown or PDF for use outside the tool (e.g., pasting into a wiki page or ticket).

## 6. Admin View

The Admin View is restricted to users with administrative or analytics-viewer roles. It is organized around five screens that map to the operational questions administrators actually ask: *who is using this right now, what are they asking, is retrieval working, how much are we consuming, and what does it cost.*

### 6.1 Active Sessions

A near-real-time view of who is currently using the system.

**Layout**: A table of active sessions — user, department/team (if available from identity provider), session start time, last activity timestamp, current conversation topic (if visible under the org's privacy settings), and connection status. A summary strip above the table shows concurrent session count, a rolling 24-hour active user count, and a simple sparkline of concurrency over the last few hours.

**Session detail**: Clicking a session opens a detail pane with recent activity (without necessarily exposing full message content, depending on the privacy tier the organization has configured — some orgs will want full transparency for compliance reasons, others will want metadata-only visibility to preserve employee trust). This privacy tier should be an explicit, documented admin setting rather than an implicit default, since it has real organizational and legal implications.

**Session controls**: Admins with sufficient privilege can force-terminate a session (e.g., for an offboarded employee whose access hasn't yet propagated) and can see rate-limit or quota status per user.

### 6.2 Query Analytics

This screen answers "what are people actually asking, and how well is the system serving them."

**Top-line metrics**: Total queries (with trend over selectable time window: 24h, 7d, 30d, custom), average queries per active user, average response latency, and overall thumbs-up/thumbs-down ratio pulled from the Feedback data described in section 5.6.

**Query volume over time**: A time-series chart, with the ability to break it down by team, source-scope, or query outcome (answered / no sources found / error).

**Top queries and topics**: A ranked list or word-cloud/topic-cluster view showing the most common query themes, generated via lightweight clustering of query embeddings. This helps admins spot recurring information needs — a strong early signal that a particular topic deserves a dedicated FAQ or a better-curated source document.

**Negative feedback drill-down**: A filtered table showing every low-rated response, with the query, answer, cited sources, and the user's free-text feedback tag. This is arguably the single most operationally useful table in the whole admin surface, since it's the fastest path to finding systematic failure patterns (a bad document, a stale policy, a misconfigured scope) rather than one-off issues.

**Failed / zero-result queries**: A dedicated list of queries where retrieval returned no relevant passages, since these represent knowledge gaps — questions people are asking that the current source corpus simply cannot answer, and thus a prioritized list for content teams to fill.

### 6.3 Retrieval Metrics

Where Query Analytics is about user-facing outcomes, Retrieval Metrics is about the health of the retrieval pipeline itself, aimed at whoever owns the RAG infrastructure.

**Core metrics**:
* **Retrieval precision proxy**: average relevance score of top-k retrieved chunks per query, trended over time.
* **Recall proxy / coverage**: percentage of queries where at least one retrieved chunk exceeds the relevance threshold.
* **Latency breakdown**: embedding time, vector search time, reranking time (if applicable), and generation time, shown as a stacked bar so bottlenecks are visually obvious.
* **Index health**: total documents indexed, total chunks, failed indexing jobs, average time from upload to searchable.
* **Source utilization**: which documents are retrieved most and least often (linking back to the Sources Panel's standalone browser from section 5.3), surfacing both over-relied-upon documents (a concentration risk if that document is ever wrong or stale) and never-retrieved documents (candidates for removal or re-chunking).

**Diagnostic tools**: A "test query" sandbox lets an admin run a query against the live index and see raw retrieval results with scores, independent of the chat/generation layer — useful for debugging why a particular question isn't finding the right document without needing to reproduce it through an actual chat session.

### 6.4 Token Usage

A consumption-focused view, primarily useful for capacity planning and for feeding the Cost Dashboard.

**Breakdown**: Input tokens vs. output tokens, trended daily/weekly/monthly, with the ability to segment by team, user, model (if multiple models are configured for different use cases), and source-scope.

**Per-user and per-team leaderboards**: A sortable table of top consumers, useful both for identifying heavy users worth talking to about efficient prompting and for spotting anomalous usage (e.g., a service account or integration consuming far more than expected, which is often the first sign of a misconfigured automation or an abuse case).

**Quota visibility**: If the organization has configured per-user or per-team token quotas, this screen shows current consumption against quota, with configurable alert thresholds (e.g., notify admin at 80% of monthly quota).

**Model mix**: If the platform routes queries across multiple models (e.g., a cheaper model for simple queries and a more capable model for complex ones), this screen shows the split, since model mix is often the single biggest lever on both cost and quality.

### 6.5 Cost Dashboard

The financial view, generally the one shared upward to finance or leadership stakeholders.

**Top-line**: Current month-to-date spend, projected end-of-month spend (based on trailing usage rate), and comparison to the previous month, displayed prominently at the top of the page.

**Cost breakdown**: A stacked chart breaking total cost into components — model inference cost (input/output tokens at current pricing), embedding/indexing cost, storage cost, and any third-party retrieval or reranking service cost, since enterprise RAG deployments frequently have non-trivial infrastructure cost beyond raw model tokens.

**Cost by team/department**: A table allocating cost across organizational units (via the same team/department metadata used in Active Sessions and Token Usage), supporting internal chargeback or showback models that many enterprises use to allocate shared-tool costs.

**Cost per outcome**: A more advanced but valuable metric — cost per "successful" query (grounded, positively rated) versus cost per "wasted" query (zero-result or negatively rated), giving a rough efficiency signal rather than just raw spend.

**Alerts and budgets**: Admins can set a monthly budget with configurable alert thresholds (e.g., 75%, 90%, 100% of budget), triggering email or in-app notifications to designated recipients. A hard-stop option (disabling further queries once budget is exhausted) should be available but off by default, since silently cutting off a production assistant is a significant operational decision that should require explicit admin opt-in rather than being a default safety net.

**Export**: All cost data should be exportable as CSV for finance teams to incorporate into their own reporting/forecasting tools, since very few finance teams will want to work directly inside the product dashboard.

## 7. Cross-Cutting Design Principles

A few principles recur across nearly every screen described above and are worth stating explicitly so future additions to the product stay consistent:

1. **Provenance over confidence**: The system should always prefer showing users *why* an answer looks the way it does (sources, scores, grounding badges) over simply asserting confidence. This is true in the Dashboard (Sources Panel) and in the Admin View (Retrieval Metrics), where raw scores are surfaced rather than hidden behind an opaque "quality" number.
2. **Failure states are first-class, not edge cases**: Failed uploads, zero-result queries, and degraded retrieval are treated as designed states with clear UI, not silent fallbacks. In an enterprise context, an assistant that fails silently is more dangerous than one that fails loudly, because silent failure erodes trust invisibly.
3. **Personal and organizational views are separate but linked**: A user's personal Analytics and an admin's Query Analytics pull from the same underlying event data but are scoped and framed differently, avoiding both an oversharing problem (individual users seeing org-wide data) and a duplicated-effort problem (two separate analytics pipelines).
4. **Everything expensive is visible before it's spent**: Token Usage and Cost Dashboard exist specifically so that cost is never a surprise; usage should be visible and trending well before a monthly bill arrives.
5. **Consistent scoping model**: The "source scope" concept introduced in AI Chat (section 5.1) is reused across Upload History, Sources Panel, Conversation History tagging, and several Admin View breakdowns, so the mental model of "which documents can this answer draw from" stays consistent everywhere rather than being redefined per screen.

## 8. Permissions Model (Summary)

| Role | Dashboard Access | Admin View Access | Notes |
|---|---|---|---|
| Standard User | Full | None | Default role. |
| Power User / Team Lead | Full, plus team-level Saved Conversations sharing | None, unless separately granted | Can manage team source collections. |
| Analytics Viewer | Full | Query Analytics, Retrieval Metrics, Token Usage (read-only) | No Active Sessions or Cost Dashboard access by default. |
| Admin | Full | Full | Can manage quotas, budgets, and session termination. |
| Compliance/Security | Full (own account) | Query Analytics, Active Sessions (metadata-tier), export tools | Access governed by org's configured privacy tier. |

## 9. Responsive and Accessibility Considerations

* The three-pane Dashboard layout collapses gracefully: on tablet widths the Sources Panel becomes a drawer; on mobile widths, navigation becomes a bottom tab bar and the chat pane becomes full-screen with sources reachable via a single tap.
* All charts in the Admin View include an accessible data-table fallback view, since charts alone are not sufficient for screen-reader users or for precise value inspection.
* Color is never the sole encoding for status (e.g., grounding badges use icon + text + color together, not color alone) to remain usable for colorblind users and to remain legible when screenshotted into a black-and-white report.
* Keyboard navigation is fully supported in the chat thread (message navigation, citation jump-to-source) given how heavily power users rely on keyboard-first workflows once familiar with a tool.

## 10. Success Metrics

To evaluate whether this design is working post-launch, the following metrics are recommended as an initial scorecard:

* **Adoption**: Weekly active users as a percentage of licensed seats; ratio of returning users to first-time users.
* **Trust and quality**: Thumbs-up ratio trend; percentage of queries with "Well-Grounded" badges; rate of "no sources found" responses over time (should trend down as source coverage improves).
* **Efficiency**: Average time-to-first-token and total response latency; percentage of sessions where the user finds an answer without needing to rephrase.
* **Operational health**: Failed upload rate; index freshness (time from upload to searchable); admin-reported incident count related to retrieval quality.
* **Cost discipline**: Variance between projected and actual monthly spend; percentage of teams operating within their token quota.

## 11. Phased Rollout Recommendation

Given the breadth of this design, a phased build is recommended rather than attempting all eleven screens simultaneously:

* **Phase 1 (Core Experience)**: AI Chat, Upload History, Sources Panel, Conversation History — the minimum viable loop of upload, ask, verify, revisit.
* **Phase 2 (Trust and Retention)**: Feedback, Saved Conversations, personal Analytics — features that increase trust and long-term stickiness once the core loop is validated.
* **Phase 3 (Operational Visibility)**: Active Sessions, Query Analytics, Retrieval Metrics — giving admins the tools to see what's happening and diagnose quality issues.
* **Phase 4 (Financial Governance)**: Token Usage, Cost Dashboard — once usage patterns are established and there's enough data history to make cost trends and budgets meaningful.

This ordering front-loads the features that directly deliver user value and defers the more operationally-focused screens until there is enough real usage data for them to be useful — an empty Cost Dashboard or Query Analytics screen at launch provides little value and can even undersell the product to stakeholders evaluating it early.

## 12. Open Questions

* Should Conversation History and Saved Conversations be merged into a single screen with a "saved" filter, or kept as fully separate top-level items? This document keeps them separate on the theory that "everything I've ever asked" and "things worth keeping" are different enough mental models to deserve separate homes, but this should be validated with user testing.
* What is the default privacy tier for Active Sessions (message-level visibility vs. metadata-only) for a typical enterprise customer, and should this be configurable per-workspace or fixed at the org level?
* Should personal Analytics be on by default or opt-in, given that some employees may find usage self-tracking uncomfortable even when framed positively?
* How should source-scope selections in AI Chat interact with team-level default scopes — should a user's manual selection always override a team default, or should some scopes be locked by policy for regulated content?

## 13. Summary

This design organizes an enterprise AI chat product into two clearly separated but data-linked surfaces: a Dashboard built around the core loop of asking, verifying, and revisiting AI-assisted answers, and an Admin View built around the operational questions of who is using the system, how well it's performing, and what it costs. The through-line connecting every screen is provenance — every answer traceable to a source, every metric traceable to an underlying event, and every cost traceable to a specific team or usage pattern — because in an enterprise setting, an assistant that cannot explain itself, however capable, will not earn the trust required for sustained adoption.
