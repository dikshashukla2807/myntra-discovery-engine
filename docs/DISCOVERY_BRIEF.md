# Myntra Discovery Engine — complete walkthrough

**Who this is for.** Anyone who cannot open the live dashboard but still needs the same story the UI tells: the business metric, the six starting hypotheses, the public-source dataset, what the tests returned, the ranked opportunity landscape, and the interview handoff.

**What this is not.** A solution brief. The engine stops at **opportunity + evidence + research gap**. It does not recommend a feature. Monetary incentives are out of scope even when price shows up in comments.

**Dataset this document describes.** Public-source mode (`data/processed/`). Banner in the UI: *Public user-generated content collected from source platforms. Not independently verified as genuine.* Demo / sample data lives separately in `data/processed_demo/` and is never mixed into these counts.

**End state of the work.** `READY FOR PRIMARY RESEARCH` — 5–6 interviews, not a shipped product decision.

How to run the app locally: see the root `README.md`.

---

## How the five screens fit together

The sidebar label is **NextLeap · Growth / Myntra Discovery Engine**. Copy under the title:

> Business metric → hypotheses → public evidence → candidate opportunities → primary research.

Footer: *Stops at opportunity + evidence + research gap. Does not recommend a feature.*

| Screen | Route | What you see |
| --- | --- | --- |
| Overview | `/` | Metric, funnel, source counts, hypothesis status, coverage note, top 5 candidate opportunities |
| Hypothesis Testing | `/hypotheses` and `/hypotheses/[id]` | Six starting guesses, status badges, comparison table, supporting + counter quotes |
| Evidence Explorer | `/evidence` | Original public text, extraction fields, source URL, filters |
| Opportunity Landscape | `/opportunities` and `/opportunities/[id]` | All 11 ranked areas, 1–5 scores, workarounds, research gap |
| Research Handoff | `/research` | Interview plan for the selected opportunity |

Associations in every table are **co-occurrence**, not causation. Frequency (how often a pattern appears) is not the same as purchase association (how often the same comments also talk about postponing, abandoning, or buying something else).

---

## 1. Overview (`/`)

### Business metric

**Eyebrow:** Business metric

**Title:** Why don’t wishlisted items convert within 30 days?

**Description on screen:** Growth wants more users to buy at least one wishlisted item within 30 days — without monetary incentives. We started with six hypotheses, tested them on public comments, and still look for emerging themes. This engine does not pick a solution.

### Dataset switch

Two buttons: **Public-source dataset** (this document) and **Demo / sample data**. Demo observations use `demo://` URLs and must not be presented as public research.

### Funnel (public-source)

| Step | Count |
| --- | ---: |
| Collected | 7,793 |
| Duplicates / low-value removed | 1,886 |
| Irrelevant removed | 1,199 |
| Relevant | 4,708 |
| Purchase-related | 1,244 |
| Wishlist-related | 29 |

Removal breakdown inside the 1,886 low-value bucket: duplicate 1,158 · low information 659 · empty 61 · promotional 5 · spam 3. Separate from that, 1,199 comments were tagged irrelevant.

**Coverage note (shown on Overview):** Explicit wishlist/save language is rare in app-store reviews. That is a coverage gap, not a finding that users do not wishlist.

Wishlist-related = 29 of 4,708 relevant comments. Do not read this as “users don’t wishlist.” Public reviews almost never describe save/wishlist behavior in those words.

### Source counts (collected)

| Source | Collected | Relevant after cleaning |
| --- | ---: | ---: |
| Google Play (`com.myntra.android`) | 5,500 | 2,928 |
| Reddit | 1,394 | 1,157 |
| App Store (optional collector) | 899 | 623 |
| YouTube | **0** | 0 |
| **Total** | **7,793** | **4,708** |

YouTube is 0 because no API key / public export was used. Missing records are not fabricated.

Valid observations after empty/spam/duplicate filters (before relevance): 5,907.

Disclaimer on the page: *Public user-generated content collected from source platforms. Not independently verified as genuine.*

### Initial hypotheses tested (status counts)

| Status | Count |
| --- | ---: |
| Tested | 6 |
| Supported | 3 |
| Weakly supported | 0 |
| Contradicted | 2 |
| Insufficient evidence | 1 |

On-screen note: Status is calculated from classified comments. A common keyword (for example “price”) is not enough to support a hypothesis. **3,366** relevant comments did not support any of the six starting hypotheses. Those unexplained comments are still clustered as **emerging** opportunities.

### Top candidate opportunities (Overview cards)

The Overview list is the top of the landscape, not the full table. Each card shows rank, origin (emerging vs hypothesis id), title, frequency, % of relevant, and purchase association.

| Rank | ID | Origin | Title | Freq | % relevant | Purchase assoc. |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | opp-03 | Emerging | Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with product information. | 655 | 13.91 | 44.58 |
| 2 | opp-h6 | H6 | Some users hesitate to purchase because they lack sufficient confidence or information about the product. | 1,276 | 27.10 | 53.75 |
| 3 | opp-06 | Emerging | Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with return concern. | 1,052 | 22.34 | 24.14 |
| 4 | opp-05 | Emerging | Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with size. | 289 | 6.14 | 37.72 |
| 5 | opp-00 | Emerging | Return and exchange friction shows up in the decision, not only after a package arrives. | 611 | 12.98 | 17.51 |

Full 11-row landscape is in section 4.

---

## 2. Hypothesis Testing (`/hypotheses`)

**Page title:** Hypothesis Testing

**Description:** Six starting guesses about wishlist → 30-day conversion. They are not findings. Status is calculated from classified public comments. The engine is allowed to reject them.

Each card shows: id · priority, status badge, statement, support / counter / purchase association / confidence, and whether it was promoted to a **candidate opportunity**. Supported is not automatic promotion — the candidate gate also looks at purchase-related support.

### The six starting statements (guesses, not findings)

| ID | Name | Statement |
| --- | --- | --- |
| H1 | Wishlist as Bookmarking | Some users wishlist products primarily as a bookmarking mechanism rather than because they have strong purchase intent. |
| H2 | Budget / Timing | Some users want a wishlisted product but postpone purchasing because they do not want to spend money at that moment or their priorities change. |
| H3 | Future Occasion | Some users wishlist products for a future occasion such as a festival, event, vacation, wedding, or other planned use. |
| H4 | Cross-Platform Comparison | Some users wishlist an item on Myntra but later find the same or a similar item elsewhere and purchase it from another platform. |
| H5 | Availability / Size / Color | Some users intend to purchase a wishlisted product later but lose the opportunity because the product, size, or color becomes unavailable. |
| H6 | Product Uncertainty | Some users hesitate to purchase because they lack sufficient confidence or information about the product. |

Classification rules that matter:

- Mentioning **price** is not automatically H2 (budget/timing).
- Naming **Amazon / Flipkart** is not automatically H4 (switching and buying elsewhere).
- Each observation is tagged supporting / counter / unclear / neutral for each hypothesis.

### Comparison table (as on screen)

Note under the table: *Frequency is not importance. Purchase association is how often supporting comments also show postponement, abandonment, or buying elsewhere.*

| Hypothesis | Evidence | Support | Counter evidence | Purchase association | Confidence | Priority | Status | Candidate? |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | --- |
| H3 Future Occasion | Moderate | 20 | 0 | 45.0% | medium | 1 | Supported | yes |
| H6 Product Uncertainty | Strong | 1,276 | 0 | 33.15% | high | 2 | Supported | yes |
| H5 Availability / Size / Color | Strong | 94 | 4 | 31.91% | high | 3 | Supported | yes |
| H2 Budget / Timing | Counter-weighted | 1 | 68 | 100.0%* | medium | 4 | **Contradicted** | no |
| H4 Cross-Platform Comparison | Counter-weighted | 4 | 12 | 50.0% | medium | 5 | **Contradicted** | no |
| H1 Wishlist as Bookmarking | Insufficient | 2 | 2 | 50.0% | low | 6 | **Insufficient evidence** | no |

\*H2’s 100% purchase association is 1 of 1 supporting comments. Do not treat that as a strong conversion signal — the hypothesis is contradicted because counter-evidence (68) dwarfs support (1).

### Detail pages (`/hypotheses/H1` … `/hypotheses/H6`)

Each detail page shows supporting count, counter count, purchase association (with “N supporting comments observed alongside postponement / abandonment / alternative purchase”), unclear count, “What the counts say,” research gap, and side-by-side original quotes with source URLs.

#### H3 — Future Occasion — **supported** (candidate)

- Support 20 · counter 0 · unclear 183 · comments that touched this hypothesis 203
- Support is 0.42% of all 4,708 relevant comments
- Purchase-related support: 9 (association 45.0%)
- Support outcomes: postponed 6 · purchased 4 · abandoned 3 · unknown 5 · still considering 2
- Sources of supporting comments: Google Play 4 · App Store 4 · Reddit 12
- Segments that show up: occasion-driven, research-heavy, comparison-heavy, price-sensitive, brand-loyal shoppers
- Workarounds observed: asking friends/family, waiting, checking another ecommerce platform, Google, Reddit
- **What the counts say:** 20 observations support Future Occasion and 0 go against it (20 is 0.4% of relevant comments). 9 supporting comments are observed alongside postponement, abandonment, or alternative purchase (association 45.0%). That is co-occurrence, not causation.
- **Research gap:** Public comments cannot tell us whether Future Occasion is the primary reason a wishlisted item fails to convert within 30 days, who it hits hardest, or whether it happens before or after saving.

Example supporting comments (original text, truncated):

> Very disappointed with Myntra delivery service. I placed an order on May 15 with expected delivery on May 17, but it keeps getting delayed and now shows May 23. I ordered for my trip and now my plans are ruined. This is not the first time — earlier also my birthday order got delayed.
>
> — `go-5ff3fdfcc0558633` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=fd10bfd7-1a73-40e7-b917-5769698cfc3a)

> I'm a college student (21F) nd I have a small family function coming up in 3-4 days. I want a very elegant decent simple yet party worthy suit/kurta… I've been scrounging through online websites but haven't found.
>
> — `re-067a1bd241f25412` · Reddit · [source](https://www.reddit.com/r/bangalore/comments/16xcnx1/ethnic_reccos_from_myntra/)

> Wedding next week! HELP!! … my tailor messed up the blouse… I have bought the blouse from Myntra (soch blouse), but i think it’s not matching.
>
> — `re-0fb5a0ea5eef6623` · Reddit · [source](https://www.reddit.com/r/IndianFashionAddicts/comments/1grsl8l/wedding_next_week_help/)

H3 is **supported but small**. Festival-sale language in Play reviews is sometimes classified as occasion; the stronger behavioral stories (trip, wedding, family function) are mostly Reddit. That is why evidence is labeled Moderate, not Strong.

#### H6 — Product Uncertainty — **supported** (candidate)

- Support 1,276 · counter 0 · unclear 1,847 · comments that touched this hypothesis 3,123
- Support is 27.1% of relevant comments
- Purchase-related support: 423 (association 33.15%)
- Support outcomes: still considering 519 · unknown 323 · postponed 129 · abandoned 292 · purchased 11 · purchased alternative 2
- Sources: Google Play 445 · App Store 197 · Reddit 634
- **Which uncertainty (shown as badges on the H6 detail page):** comparison · returns · quality · size · fit · product information · material/fabric · reviews
- Workarounds: checking another ecommerce platform, asking friends/family, waiting, comparing alternatives, visiting an offline store
- **What the counts say:** 1,276 observations support Product Uncertainty and 0 go against it. 423 supporting comments are observed alongside postponement, abandonment, or alternative purchase (association 33.15%). That is co-occurrence, not causation.
- **Research gap:** Public comments cannot tell us whether Product Uncertainty is the primary reason a wishlisted item fails to convert within 30 days, who it hits hardest, or whether it happens before or after saving.

Example supporting comment:

> earlier myntra used to be up to the mark with quality but from quite some time quality control sharply degraded… dirt all over the clothes… Myntra, Are you guys even aware what you r selling? used products? returned items? Nykaa and Amazon is much better now a days. Now I feel reluctant to open package ,don't even want to buy on myntra.
>
> — `go-3c0793e5084c1c3e` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=33cf7e53-7886-4765-924a-86b7ef909549)

H6 is the largest *supported* starting hypothesis. It is still not “the problem.” Interviews have to name *which* uncertainty actually stalls a saved item.

#### H5 — Availability / Size / Color — **supported** (candidate)

- Support 94 · counter 4 · unclear 0 · comments that touched this hypothesis 98
- Support is 2.0% of relevant comments
- Purchase-related support: 30 (association 31.91%)
- Support outcomes: unknown 53 · abandoned 22 · postponed 8 · purchased 4 · still considering 7
- Sources: Google Play 51 · App Store 24 · Reddit 19
- **What the counts say:** 94 observations support Availability / Size / Color and 4 go against it (94 is 2.0% of relevant comments). 30 supporting comments are observed alongside postponement, abandonment, or alternative purchase (association 31.91%). That is co-occurrence, not causation.

Example supporting:

> good experience, sometimes delivery not available.
>
> — `go-c2d68d18ca4983e5` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=10ccc4bd-f2d5-4735-9d28-53ae8caf853f)

Example counter (stock came back, but the user did not get the original deal — still not a clean “I waited and it vanished” story):

> i ordered few perfumes in sale and Myntra cancelled the order. when I contacted customer support they told it's not in stock… now the perfume is back in stock but it's price is increased by multiple times
>
> — `go-80a0f3c6cd518361` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=79b791da-c8b1-4bea-a640-7b34cfab24d2)

#### H2 — Budget / Timing — **contradicted** (not a candidate)

- Support 1 · counter 68 · unclear 3 · comments that touched this hypothesis 72
- Support is 0.02% of relevant comments; counter is 1.44%
- **What the counts say:** Counter-evidence (68) outweighs supporting comments (1) for Budget / Timing. Treat the starting hypothesis as challenged, not confirmed.
- Affected segments: *Insufficient evidence.*
- Caution encoded in the hypothesis bank: a price mention is not a budget constraint.

The single supporting comment is a Reddit post about a ₹500 T-shirt budget and whether to buy local vs online (`re-4d9897ba3d2802a9`). Most “price” comments are people who *did* buy and called the price reasonable, or who are complaining about quality-for-price after purchase — that is counter to “I want it but I won’t spend now.”

Example counter:

> i have been using this app and ordered products and the quality of the product is unbelievable and also in reasonable price
>
> — `go-b7f2089edde7b16e` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=f57c0489-0cb2-4226-b4ee-c3c0171ad0da)

#### H4 — Cross-Platform Comparison — **contradicted** (not a candidate)

- Support 4 · counter 12 · **unclear 1,020** · comments that touched this hypothesis 1,036
- Support 0.08% · counter 0.25% of relevant
- Purchase-related support: 2 (association 50.0% of the 4 supporting comments)
- **What the counts say:** Counter-evidence (12) outweighs supporting comments (4). Treat the starting hypothesis as challenged, not confirmed.
- The 1,020 unclear comments are the important number: people *name* another platform without describing a switch-and-buy. Naming Amazon ≠ H4.

Example supporting (price comparison that ends in buying the cheaper listing):

> Honestly, your best bet is checking Myntra for brands like Levi's or Roadster, and Flipkart for U.S. Polo Assn. I also recommend using a price comparison tool to check if the exact same pair is cheaper on Amazon vs Myntra before checking out - saved me a good amount on my last purchase.
>
> — `re-d559337afc232d64` · Reddit · [source](https://www.reddit.com/r/IndianFashionAddicts/comments/1vx1n5s/any_websites_to_buy_good_jorts/p5wznf8/)

Example counter (staying on Myntra):

> I have rarely returned the products bcoz of quality issues bought from Myntra...I usually get all the brands I look for on this site...
>
> — `go-cd749123fda36295` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=9e60c847-6699-4f27-a76f-f9943d8fef44)

#### H1 — Wishlist as Bookmarking — **insufficient evidence** (not a candidate)

- Support 2 · counter 2 · unclear 25 · comments that touched this hypothesis 29
- Those 29 are essentially the entire wishlist-language slice of the corpus
- **What the counts say:** Wishlist as Bookmarking was tested on 4,708 relevant observations. 2 supported it and 2 contradicted it — not enough classified evidence to judge. Explicit wishlist/save language is rare in app reviews; that is a coverage gap, not proof that bookmarking is absent.
- **Research gap:** Public UGC does not contain enough behavioral evidence to accept or reject Wishlist as Bookmarking. Interviews are required if this remains a suspected conversion path.
- Confidence: low. Segments: *Insufficient evidence.*

Example supporting (thin — the comment is almost only the words themselves):

> exploring wishlist, wishlisted , bookmark
>
> — `go-a9cf32113d55254c` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=d540e989-045a-409e-8f8e-3e2559b4fa6c)

This hypothesis cannot be closed from public reviews. It is the main reason the engine is **ready for interviews**, not ready to declare a wishlist-intent problem.

---

## 3. Evidence Explorer (`/evidence`)

**Title:** Evidence Explorer

**Description:** Original public text, extraction, theme, and source URL. Quotes are never fabricated.

Every row is a relevant observation. The UI shows:

- Source badge (google_play / reddit / app_store / youtube)
- Public-source vs DEMO / SAMPLE DATA
- Date, `observation_id`
- **Original text** (`text_original` is never overwritten)
- Extraction: why considered · after consideration (purchase outcome) · barrier · workaround · uncertainty · theme
- Link: **Open original source**

### Filters

| Filter | Options |
| --- | --- |
| Search | Original text |
| Source | All · Google Play · Reddit · YouTube · App Store |
| User intent | consideration, wishlist/save, comparison, purchase intent, post-purchase, postponed, abandoned, return/exchange |
| Purchase outcome | purchased, postponed, abandoned, purchased alternative, still considering, unknown |
| Barrier | fit, size, quality uncertainty, price, reviews/trust, comparison, product information, return concern |
| Hypothesis | H1–H6 |
| Stance | supporting, counter, unclear, neutral / not about this hypothesis |
| Theme | free-text |

Pagination: 25 per page. Empty state: *No matching comments. Clear filters, or switch dataset on Overview if you expected demo samples.*

Hypothesis detail pages deep-link here, e.g. `/evidence?hypothesis=H6&stance=supporting`.

You cannot dump all 4,708 comments in this markdown file. Use Evidence Explorer (or `data/processed/relevant_observations.jsonl`) when you need the full list. Observation ids in this brief are enough to look them up.

---

## 4. Opportunity Landscape (`/opportunities`)

**Title:** Opportunity Landscape

**Description:** Candidate areas only — not features to build. Purchase association is how often postponed, abandoned, or alternative-purchase language shows up in the same cluster. That is not causation.

Origin badges:

- **Emerging opportunity** — clustered from comments that the six Hs did not explain (or from mixed themes)
- **H3 / H5 / H6** — promoted from a *supported* starting hypothesis that also cleared the purchase-association candidate gate

H1, H2, and H4 were **not** promoted.

### Scoring (1–5 per dimension)

Composite is a weighted average (max 5):

| Dimension | Weight |
| --- | ---: |
| Evidence strength | 0.20 |
| Frequency | 0.15 |
| Purchase association (postponed / abandoned / bought alternative only — not “still considering”) | 0.25 |
| User severity | 0.15 |
| Workaround intensity | 0.15 |
| Segment relevance | 0.10 |

Each opportunity detail page explains why that rank beat the next (`why_ranked_higher`). Scoring notes on every detail page: *Frequency is how often the pattern appears; purchase association is how often it is observed alongside postponed / abandoned / purchased-alternative language. Those are not the same thing, and neither is causation.*

### Full ranked table (all 11 rows)

This is the landscape table plus the 1–5 score breakdown from each detail page.

| Rank | ID | Origin | Opportunity | Freq | % rel. | Purch. assoc. | Postponed | Abandoned | Evidence | Composite | Confidence |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | opp-03 | Emerging | Delivery reliability in the same comments as buying hesitation. Also product information. | 655 | 13.91 | 44.58 | 6.56 | 38.02 | 5 | **4.70** | high |
| 2 | opp-h6 | H6 Product Uncertainty | Lack of confidence / information about the product. | 1,276 | 27.10 | 53.75 | 6.25 | 47.50 | 3 | 4.45 | high |
| 3 | opp-06 | Emerging | Delivery reliability + return concern. | 1,052 | 22.34 | 24.14 | 2.57 | 21.58 | 5 | 4.35 | high |
| 4 | opp-05 | Emerging | Delivery reliability + size. | 289 | 6.14 | 37.72 | 17.99 | 19.72 | 5 | 4.30 | high |
| 5 | opp-00 | Emerging | Return/exchange friction in the decision, not only after a package arrives. | 611 | 12.98 | 17.51 | 7.04 | 10.47 | 5 | 4.20 | high |
| 6 | opp-h5 | H5 Availability | Size / color / product becomes unavailable before they buy. | 94 | 2.00 | 30.00 | 7.50 | 22.50 | 5 | 4.15 | high |
| 7 | opp-h3 | H3 Future Occasion | Saved for a festival, event, vacation, wedding, or other planned use. | 20 | 0.42 | 45.00 | 30.00 | 15.00 | 3 | 4.00 | medium |
| 8 | opp-02 | Emerging | Keep multiple options in play and delay while comparing products or platforms. | 974 | 20.69 | **2.98** | 1.23 | 1.54 | 5 | 3.85 | high |
| 9 | opp-04 | Emerging | Cannot tell from the listing whether quality will match the price. Also price. | 536 | 11.38 | **0.19** | 0.00 | 0.19 | 5 | 3.55 | high |
| 10 | opp-01 | Emerging | Delivery reliability + quality uncertainty. | 480 | 10.20 | **0.83** | 0.42 | 0.42 | 5 | 3.55 | high |
| 11 | opp-07 | Emerging | Quality vs price, also observed with return concern. | 111 | 2.36 | **0.90** | 0.00 | 0.90 | 5 | 3.20 | high |

**Read ranks 8–11 carefully.** Comparison (opp-02) is *frequent* (974 comments, 20.69% of relevant) but almost never sits next to postponed/abandoned language (purchase assoc. 2.98). Quality/price clusters (opp-04, opp-01, opp-07) are loud in reviews and **weak** on the conversion co-occurrence the metric cares about. Frequency ≠ importance for 30-day wishlist purchase.

Alternative-purchase association is 0.0 on every emerging cluster except opp-02 (2 comments). Users rarely write “I bought this on another site instead” in this corpus.

### Score cards (1–5)

| ID | Evidence | Frequency | Purchase assoc. | Severity | Workaround | Segment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| opp-03 | 5 | 3 | 5 | 5 | 5 | 5 |
| opp-h6 | 3 | 4 | 5 | 5 | 5 | 5 |
| opp-06 | 5 | 4 | 3 | 5 | 5 | 5 |
| opp-05 | 5 | 2 | 4 | 5 | 5 | 5 |
| opp-00 | 5 | 3 | 3 | 5 | 5 | 5 |
| opp-h5 | 5 | 1 | 4 | 5 | 5 | 5 |
| opp-h3 | 3 | 1 | 5 | 5 | 5 | 5 |
| opp-02 | 5 | 4 | 1 | 5 | 5 | 5 |
| opp-04 | 5 | 2 | 1 | 5 | 5 | 5 |
| opp-01 | 5 | 2 | 1 | 5 | 5 | 5 |
| opp-07 | 5 | 1 | 1 | 5 | 5 | 3 |

Why #1 beats #2: weighted score 0.25 higher. Biggest gap: **evidence strength 5/5 vs 3/5**. opp-h6 has more raw support (1,276) but weaker evidence-strength scoring than the delivery + product-information cluster.

### Opportunity detail pages (`/opportunities/[id]`)

Every detail page uses the same pattern:

1. **What we observed** (`what_we_know`)
2. Frequency · purchase association (with postponed / abandoned / alt split) · evidence 1–5 · confidence
3. **Why did this rank here?** plus the six 1–5 scores
4. **Segments** and **workarounds**
5. **Supporting evidence** (original text + outcome + barriers + source URL)
6. **Counter evidence** — *Comments that contradict the dominant barrier, or purchased without it. Prevents confirmation bias.*
7. **Research gap** and a link to Research Handoff

Shared unknowns on every opportunity (from `data/processed/gaps.json`):

- Does this actually cause users to postpone after wishlisting, or is it only mentioned in the same comments?
- Is it concentrated in a segment, category (apparel vs footwear), or price band?
- Does it occur before saving, at the moment of saving, or in the days after?
- How severe is it relative to other open questions?
- What workaround do users prefer, and does it resolve the uncertainty?
- Would resolving this change purchase intent within 30 days, or would another barrier remain?

Claim type for all of them: **HYPOTHESIS**. Suggested interview count in the gap file: 5.

---

### Rank 1 — opp-03 — emerging — composite 4.7

**Title:** Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with product information.

**Description:** Users describing abandoned, return/exchange repeatedly surface delivery, return concern, product information. Some still complete a purchase; others postpone, abandon, or keep considering. This is an observed pattern in public comments, not a proven cause of 30-day wishlist conversion.

**What we observed:** 655 relevant observations (13.91%) grouped here. Observed alongside postponed=43, abandoned=249, purchased alternative=0. These are co-occurrences, not causes.

**Segments:** research-heavy shoppers, price-sensitive shoppers, comparison-heavy shoppers

**Workarounds:** checking another ecommerce platform, waiting, asking friends/family, comparing alternatives

**Research gap:** Public comments mention ‘delivery, return concern, product information’ in this cluster. We do not know whether it actually prevents 30-day wishlist conversion, for whom it is strongest, or whether it happens before or after saving an item.

**Why #1 vs #2:** Ranked #1 vs #2 because the weighted score is 0.25 higher (max 5). Biggest gap: evidence strength (5/5 vs 3/5).

Example supporting:

> Very disappointing experience with Myntra. I ordered two shirts worth around ₹2,000, but when the package arrived, there was only ONE shirt inside. I immediately raised a complaint… after their so-called “investigation,” they simply said everything was fine from their end. So I paid for two shirts and received one… Think twice before ordering.
>
> — `go-97cd12fa9edd3eac` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=2a93e713-125e-4933-bfbb-7da3051ef71d)

Example counter (purchased / satisfied — the cluster is not universal):

> whatever i have ordered it was worthy and satisfying .
>
> — `go-f04931c3c61776cb` · Google Play · [source](https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=5e0b7c77-0386-4c78-9044-b596f3e0f443)

8 counter comments are stored against this cluster. Confirmation bias is the failure mode if you only read delivery complaints.

---

### Rank 2 — opp-h6 — H6 — composite 4.45

**Title:** Some users hesitate to purchase because they lack sufficient confidence or information about the product.

**What we observed:** Same as the H6 hypothesis write-up (1,276 support / 0 counter / 33.15% purchase association on the *hypothesis* object). The opportunity object’s purchase-association field is 53.75 with postponement 6.25 and abandonment 47.5 — that is the cluster-level mix used in ranking, still co-occurrence.

**Segments:** research-heavy, comparison-heavy, fit-conscious shoppers

**Workarounds:** asking friends/family, checking another ecommerce platform, comparing alternatives, waiting, adding alternatives to wishlist

**Why #2 vs #3:** Weighted score 0.10 higher. Biggest gap: purchase association (5/5 vs 3/5).

No counter-evidence ids on this opportunity object.

---

### Rank 3 — opp-06 — emerging — composite 4.35

**Title:** Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with return concern.

**What we observed:** 1,052 relevant observations (22.34%). Observed alongside postponed=27, abandoned=227, purchased alternative=0.

**Themes in the gap text:** delivery, return concern, price.

**Segments:** price-sensitive, research-heavy, brand-loyal shoppers

**Workarounds:** asking friends/family, checking another ecommerce platform, waiting, comparing alternatives

**Why #3 vs #4:** Weighted score 0.05 higher. Biggest gap: frequency (4/5 vs 2/5).

This cluster is *larger* than opp-03 (1,052 vs 655) but weaker on purchase association (24.14 vs 44.58), so it ranks lower. Again: frequency ≠ conversion link.

---

### Rank 4 — opp-05 — emerging — composite 4.30

**Title:** Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with size.

**What we observed:** 289 relevant observations (6.14%). Observed alongside postponed=52, abandoned=57, purchased alternative=0.

Highest postponement association in the emerging set (17.99).

**Segments:** research-heavy, fit-conscious, price-sensitive shoppers

**Workarounds:** waiting, checking another ecommerce platform, asking friends/family, Instagram

**Why #4 vs #5:** Weighted score 0.10 higher. Biggest gap: purchase association (4/5 vs 3/5).

---

### Rank 5 — opp-00 — emerging — composite 4.20

**Title:** Return and exchange friction shows up in the decision, not only after a package arrives.

**What we observed:** 611 relevant observations (12.98%). Observed alongside postponed=43, abandoned=64, purchased alternative=0.

**Gap themes:** return concern, delivery, quality uncertainty, size.

**Segments:** fit-conscious, research-heavy, brand-loyal shoppers

**Workarounds:** waiting, checking another ecommerce platform, asking friends/family, checking measurements manually

**Why #5 vs #6:** Weighted score 0.05 higher. Biggest gap: frequency (3/5 vs 1/5).

---

### Rank 6 — opp-h5 — H5 — composite 4.15

**Title:** Some users intend to purchase a wishlisted product later but lose the opportunity because the product, size, or color becomes unavailable.

**What we observed:** Same as H5 (94 support / 4 counter / 31.91% hypothesis purchase association). Opportunity-level purchase association 30.0 (postponed 7.5 · abandoned 22.5).

**Segments:** research-heavy, fit-conscious, price-sensitive shoppers

**Workarounds:** asking friends/family, checking another ecommerce platform, waiting, comparing alternatives, checking brand website

**Why #6 vs #7:** Weighted score 0.15 higher. Biggest gap: evidence strength (5/5 vs 3/5).

---

### Rank 7 — opp-h3 — H3 — composite 4.00

**Title:** Some users wishlist products for a future occasion such as a festival, event, vacation, wedding, or other planned use.

**What we observed:** Same as H3 (20 support / 0 counter / 45.0% purchase association). Small n, high association, medium confidence.

**Segments:** occasion-driven, research-heavy, comparison-heavy shoppers

**Workarounds:** asking friends/family, waiting, checking another ecommerce platform, Google, Reddit

**Why #7 vs #8:** Weighted score 0.15 higher. Biggest gap: purchase association (5/5 vs 1/5).

This is the example of “rare but tightly linked to delay language” versus opp-02 “common but barely linked.”

---

### Rank 8 — opp-02 — emerging — composite 3.85

**Title:** Users keep multiple options in play and delay buying while they compare products or platforms.

**What we observed:** 974 relevant observations (20.69%). Observed alongside postponed=12, abandoned=15, purchased alternative=2.

Purchase association **2.98** despite being one of the largest clusters. The comparison conversation in public UGC is mostly “still considering,” which is **excluded** from purchase association by design.

**Gap themes:** comparison, fit, price, quality uncertainty.

**Segments:** research-heavy, comparison-heavy, fit-conscious shoppers

**Workarounds:** checking another ecommerce platform, asking friends/family, visiting an offline store, comparing alternatives

**Why #8 vs #9:** Weighted score 0.30 higher. Biggest gap: frequency (4/5 vs 2/5).

---

### Rank 9 — opp-04 — emerging — composite 3.55

**Title:** Users cannot tell from the listing whether quality will match the price they would pay. Also observed with price.

**What we observed:** 536 relevant observations (11.38%). Observed alongside postponed=0, abandoned=1, purchased alternative=0.

Purchase association **0.19**. High-volume quality/price talk after purchase is not a 30-day wishlist-conversion signal in this corpus.

**Why #9 vs #10:** 0.00 composite edge; individual 1–5 scores are close, so treat the order as comparison, not a large gap.

---

### Rank 10 — opp-01 — emerging — composite 3.55

**Title:** Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with quality uncertainty.

**What we observed:** 480 relevant observations (10.2%). Observed alongside postponed=2, abandoned=2, purchased alternative=0.

Purchase association **0.83**. Same family of delivery language as opp-03, but this slice barely co-occurs with postpone/abandon. That is why it is rank 10, not rank 1.

**Why #10 vs #11:** Weighted score 0.35 higher. Biggest gap: segment relevance (5/5 vs 3/5).

---

### Rank 11 — opp-07 — emerging — composite 3.20

**Title:** Users cannot tell from the listing whether quality will match the price they would pay. Also observed with return concern.

**What we observed:** 111 relevant observations (2.36%). Observed alongside postponed=0, abandoned=1, purchased alternative=0.

**Segment:** price-sensitive shoppers only (segment relevance 3/5).

**Why last:** Lowest of the discovered opportunities on the six 1–5 scores.

---

## 5. Research Handoff (`/research`)

**Title:** Research handoff

**Description:** Public data can surface a candidate opportunity. It cannot prove the final user problem. This page ends at ready for primary research — not a final solution.

The dropdown defaults to rank #1 (**opp-03**). You can switch to any of the 11 opportunities; the default plan below is the one stored in `data/processed/interview_plan.json`.

### Selected opportunity (default)

Delivery reliability is mentioned in the same comments as buying hesitation. Also observed with product information.

**Target segment:** research-heavy shoppers

### What we know

655 relevant observations (13.91%) grouped here. Observed alongside postponed=43, abandoned=249, purchased alternative=0. These are co-occurrences, not causes.

### What we don’t know

Public comments mention ‘delivery, return concern, product information’ in this cluster. We do not know whether it actually prevents 30-day wishlist conversion, for whom it is strongest, or whether it happens before or after saving an item.

### Research hypothesis

If this barrier is a true decision blocker for high-intent / high-wishlist users, we should hear it unprompted in stories of products they wanted but did not buy. This remains a hypothesis until interviews.

**Research objective (one-liner on the card):** Understand what actually happens between expressing interest (save/wishlist) and buying or not buying, for this opportunity area — without validating a solution.

### What we should ask users (research objectives)

These are labeled on screen as research objectives, not feature-validation questions.

1. What actually happened between saving/wishlisting and deciding not to buy?
2. Was this barrier the main reason, or one of several?
3. Who else was involved, and what information was still missing?
4. When in the 30 days after saving did the decision stall?

### Interview questions (12, past-behavior)

1. Tell me about the last fashion product you wanted to buy but didn't.
2. Walk me through how that product ended up saved, wishlisted, or sitting in your bag.
3. What made you save it in the first place?
4. What happened between saving it and deciding whether to buy?
5. What information were you still looking for?
6. Where did you go to find that information, if anywhere?
7. Did you look anywhere outside Myntra? If yes, what were you trying to learn?
8. If you compared it with something else, how did you compare?
9. What did you eventually do, and what made that the decision?
10. Tell me about a time you did buy something you had saved. What was different?
11. When you hesitate, what usually makes you wait versus drop it altogether?
12. Who, if anyone, do you involve before you buy clothes online?

### Interview notes (on screen)

- Ask for the last real episode, not hypotheticals.
- Follow the story: trigger → save → wait → research → decide.
- Do not pitch a feature. The engine stops at opportunity + evidence + research gap.
- End state: ready for primary research — not a final solution.

### End state (green card)

**READY FOR PRIMARY RESEARCH**

Public UGC can show that a pattern exists and whether it is observed alongside postponement or non-purchase. It cannot prove the final user problem, severity, or whether fixing it would change 30-day wishlist conversion. That takes 5–6 interviews.

---

## Behavioral segments (discovered, not assumed)

These numbers are of the 4,708 relevant observations. A comment can match more than one segment, so percentages do not sum to 100.

| Segment | Definition | n | % | Dominant barriers | Workarounds that show up |
| --- | --- | ---: | ---: | --- | --- |
| unclassified | No discovered behavioral signal | 2,404 | 51.06 | delivery, return concern, quality uncertainty, product information, reviews/trust | — |
| research-heavy shoppers | Looking things up, photos, measurements, leaving the app | 1,098 | 23.32 | comparison, delivery, return concern, quality uncertainty, price | other ecommerce, friends/family, waiting, offline store, comparing |
| fit-conscious shoppers | Fit or size as part of the decision | 747 | 15.87 | size, fit, return concern, delivery, quality uncertainty | other ecommerce, friends/family, measurements, offline store, waiting |
| price-sensitive shoppers | Price, value, discounts, waiting for sales | 698 | 14.83 | price, quality uncertainty, delivery, return concern, comparison | other ecommerce, friends/family, offline store, comparing, waiting |
| comparison-heavy shoppers | Comparing products or platforms | 670 | 14.23 | comparison, delivery, price, quality uncertainty, return concern | other ecommerce, friends/family, comparing, offline store, Instagram |
| brand-loyal shoppers | Brand, authenticity, originals | 398 | 8.45 | return concern, delivery, quality uncertainty, price, comparison | other ecommerce, friends/family, offline store, waiting, comparing |
| occasion-driven shoppers | Events, weddings, office, timed need | 154 | 3.27 | occasion, delivery, comparison, return concern, quality uncertainty | other ecommerce, friends/family, offline store, Instagram, waiting |
| exploratory browsers | Browsing, inspiration, just looking | 72 | 1.53 | quality uncertainty, delivery, material/fabric, price, size | friends/family, other ecommerce, offline store, comparing, Google |
| high-wishlist users | Explicit wishlist / saved-item language | **19** | **0.40** | size, reviews/trust, price, return concern, delivery | adding alternatives to wishlist, friends/family, comparing, waiting, measurements |

High-wishlist users (19) is the same coverage gap as the 29 wishlist-related funnel count — slightly different tagging, same conclusion: **you cannot research wishlist conversion from Play/App Store text alone.**

---

## How to read this without over-claiming

1. **H6 is common. H3 is rare but more tightly tied to delay language. H2 and H4 are contradicted. H1 cannot be tested here.**
2. **Delivery + missing product information (opp-03) is the top candidate** because evidence strength and purchase co-occurrence both score high — not because we proved it causes 30-day wishlist failure.
3. **Comparison noise (opp-02) is huge and weakly associated with postpone/abandon.** Do not promote it just because the cluster is large.
4. **Quality/price rants (opp-04, opp-01, opp-07) are frequent and almost unlinked to postponement in this corpus.**
5. **No feature follows from this document.** The next artifact is 5–6 past-behavior interviews using the handoff questions.
6. **Quotes above are real public comments** with `observation_id` and source URL. Classifier labels are imperfect (some H3 “occasion” hits are weak). Always open the original URL before treating a quote as decisive.

---

## Where the numbers live

| UI | File |
| --- | --- |
| Overview funnel, sources, top opportunities | `data/processed/overview.json` |
| Hypothesis cards + comparison | `data/processed/hypotheses.json`, `hypothesis_comparison.json` |
| Opportunity table + detail | `data/processed/opportunities.json` |
| Research handoff | `data/processed/interview_plan.json` |
| Gaps / unknowns | `data/processed/gaps.json` |
| Segments | `data/processed/segments.json` |
| Quality / removal reasons | `data/processed/quality_report.json` |
| Original comments | `data/processed/relevant_observations.jsonl` |

Re-running collection or the pipeline will change these counts. This brief matches the public-source snapshot that the dashboard was showing when the document was written.
