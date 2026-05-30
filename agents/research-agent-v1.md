# Research Agent v1.0 — Build Spec

**Status:** Ready to build  
**Stack:** Make.com + Claude API + Notion + Gmail  
**Goal:** Generate ≥1 postable content idea daily from 10 monitored creators  
**Notion DB:** https://www.notion.so/e73d07009bff459ba33a3f6eeea57a9f  
**Data Source ID:** `collection://f7ad3b1c-ed0f-47a1-ae07-865790119a31`

---

## 1. Creators

### Tier 1 — Attention Engineering
| Creator | Monitor On | Focus |
|---|---|---|
| Kane Kallaway | Instagram, TikTok | Identity hooks, social dynamics, "Study why..." format |
| Dan Koe | X, YouTube | Hook structure, identity framing |
| Alex Hormozi | Instagram, YouTube | Hook opens, pattern interrupts |
| Codie Sanchez | X, YouTube | Opportunity framing, wealth narratives |
| Justin Welsh | LinkedIn, X | Idea packaging, solopreneur positioning |

### Tier 2 — Viral Psychology
| Creator | Monitor On | Focus |
|---|---|---|
| Chris Williamson | X, YouTube | Social observations, modern psychology |
| Naval Ravikant | X | Leverage, wealth, status ideas |
| Ryan Holiday | X | Concise observations, reframing |

### Tier 3 — Opportunity & Future
| Creator | Monitor On | Focus |
|---|---|---|
| Shaan Puri | X, YouTube | Opportunity spotting, business narratives |
| Sam Parr | X | Trend detection, internet business models |

---

## 2. Scrape Schedule

```
Daily:   6:00 AM IST — last 24h posts, virality threshold 6.0+
Weekly:  Sunday 7:00 AM IST — last 7 days, threshold 5.0+ (catch slow burners)
```

Platforms via Make.com native integrations:
- **X/Twitter** — Make.com Twitter module (user timeline)
- **YouTube** — RSS feed per channel (`youtube.com/feeds/videos.xml?channel_id=...`)
- **LinkedIn** — RSS via Feedle or Phantombuster
- **Instagram/TikTok** — Manual review until reliable API available (flag for Apify upgrade)

---

## 3. Claude Extraction Prompt

### System Prompt

```
You are the Research Agent for LaunchPlan.dev — an Opportunity Detection System.

Your job: extract viral signal from content, not summarize it.

You are looking for hooks, formats, and emotional triggers that could be 
adapted for a founder/builder audience on LaunchPlan.dev.

LaunchPlan context: startup discovery, validation, and builder ecosystem. 
ICP: founders, indie hackers, developers, aspiring entrepreneurs.
```

### User Prompt (per post batch)

```
Analyze the following posts from [CREATOR] on [PLATFORM].

For each post with viral potential, extract:

HOOK: [exact opening line or core concept, verbatim]
FORMAT: [Numbered List / Prediction / Self-Diagnosis / Observation / Story / Question / Contrarian / Other]
EMOTIONAL TRIGGER: [Opportunity Anxiety / Identity Gap / Status / Fear of Obsolescence / Confidence / Curiosity / Other]
AUDIENCE: [who this speaks to]
CORE BELIEF: [the underlying worldview being activated — 1 sentence]
COMMENT DRIVER: [what makes people argue or respond]
SAVE DRIVER: [what makes people bookmark — utility, identity, future reference]
SHARE DRIVER: [what makes people send this to others]
LAUNCHPLAN ANGLE: [how this exact hook could work for founders building on LaunchPlan — be specific]
VIRALITY SCORE: [0.0–10.0 using: 40% shares, 25% saves, 15% comments, 10% view-to-follow, 10% reach]

Only extract posts scoring 6.0+.
Skip tutorials, "how to use [tool]" content, and personal updates.
Flag any hook using: fear of obsolescence, opportunity anxiety, identity gap, status comparison.

Output as JSON array.
```

### Output Schema

```json
[
  {
    "date": "YYYY-MM-DD",
    "creator": "",
    "platform": "",
    "hook": "",
    "format": "",
    "emotional_trigger": "",
    "audience": "",
    "core_belief": "",
    "comment_driver": "",
    "save_driver": "",
    "share_driver": "",
    "launchplan_angle": "",
    "virality_score": 0.0
  }
]
```

---

## 4. Notion Schema

**Database name:** `OUTLIER CONTENT VAULT`

| Property | Type | Options |
|---|---|---|
| Hook | Title | — |
| Date | Date | — |
| Creator | Select | Kane Kallaway, Dan Koe, Alex Hormozi, Codie Sanchez, Justin Welsh, Chris Williamson, Naval Ravikant, Ryan Holiday, Shaan Puri, Sam Parr |
| Platform | Select | X, Instagram, YouTube, LinkedIn, TikTok |
| Format | Select | Numbered List, Prediction, Self-Diagnosis, Observation, Story, Question, Contrarian |
| Emotional Trigger | Select | Opportunity Anxiety, Identity Gap, Status, Fear of Obsolescence, Confidence, Curiosity |
| Audience | Multi-select | Founders, Students, Young Professionals, Creators, Developers |
| Core Belief | Text | — |
| Comment Driver | Text | — |
| Save Driver | Text | — |
| Share Driver | Text | — |
| LaunchPlan Angle | Text | — |
| Virality Score | Number | 0–10 |
| Posted? | Checkbox | — |
| Results | Text | — |

**Views to create:**
- `Daily Brief` — filter: Date = today, sort: Virality Score desc
- `Not Posted` — filter: Posted? = false, sort: Virality Score desc
- `By Trigger` — group by Emotional Trigger
- `By Format` — group by Format

---

## 5. Gmail Digest Format

**Subject:** `Research Brief — [Day, Date] | Top Hook: [highest-scoring hook]`

**Body:**

```
RESEARCH BRIEF — [DATE]

━━━━━━━━━━━━━━━━━━━━━━━
TOP 3 HOOKS TODAY
━━━━━━━━━━━━━━━━━━━━━━━

1. [Hook] — [Creator] ([Score])
   Trigger: [Emotional Trigger]
   LaunchPlan Angle: [Angle]

2. [Hook] — [Creator] ([Score])
   Trigger: [Emotional Trigger]
   LaunchPlan Angle: [Angle]

3. [Hook] — [Creator] ([Score])
   Trigger: [Emotional Trigger]
   LaunchPlan Angle: [Angle]

━━━━━━━━━━━━━━━━━━━━━━━
TOP 3 EMERGING NARRATIVES
━━━━━━━━━━━━━━━━━━━━━━━

1. [Narrative] — seen in [N] posts this week
2. [Narrative] — seen in [N] posts this week
3. [Narrative] — seen in [N] posts this week

━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED REEL TODAY
━━━━━━━━━━━━━━━━━━━━━━━

Hook: [exact hook]
Format: [format]
Why today: [1 sentence]

━━━━━━━━━━━━━━━━━━━━━━━
Full vault: [Notion link]
━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Make.com Workflow

```
Trigger: Schedule (6:00 AM IST daily)
    ↓
Module 1: Fetch posts — X/Twitter module × 5 accounts
    ↓
Module 2: Fetch posts — YouTube RSS × 5 channels
    ↓
Module 3: Aggregate + filter (remove posts < 6h old, remove duplicates)
    ↓
Module 4: Claude API — extraction prompt (batch per creator)
    ↓
Module 5: Parse JSON response
    ↓
Module 6: Notion — create record in OUTLIER CONTENT VAULT
    ↓
Module 7: Aggregate top 3 by Virality Score
    ↓
Module 8: Claude API — compile digest email
    ↓
Module 9: Gmail — send to yashvardhan@specflowai.com
```

---

## Success Metric

> Did the brief generate at least 1 content idea I actually want to post today?

Track daily. If answer is No for 7 consecutive days — the agent is failing. Debug extraction prompt or swap creator list.

---

## Phase 2 Trigger

When vault has 90+ entries AND ≥30 `Posted? = true` with Results filled:
→ Build Distribution Intelligence Agent reading from this vault.
