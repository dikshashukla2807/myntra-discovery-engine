from __future__ import annotations

import re
from typing import Iterable

# Keyword evidence is used only as a fallback when no LLM is configured.
# Matches never overwrite original text and never invent quotes.


def _rx(*parts: str) -> re.Pattern[str]:
    return re.compile("|".join(parts), re.I)


WISHLIST_EXPLICIT = _rx(
    r"\bwish\s*lists?\b",
    r"\bwishlist(ed|ing)?\b",
    r"\badded to (my )?wish\b",
)
SAVED_EXPLICIT = _rx(r"\bsaved for later\b", r"\bsave(d)? it\b", r"\bsaved items?\b")
SHORTLIST = _rx(r"\bshortlist(ed|ing)?\b", r"\bfew options\b", r"\bnarrowed (it )?down\b")
CART_CONSIDER = _rx(r"\b(add(ed)? to (cart|bag)|in (my )?(cart|bag))\b")

POSTPONE = _rx(
    r"\blater\b",
    r"\bwait(ing)? for\b",
    r"\bnot now\b",
    r"\bnext (month|sale|payday)\b",
    r"\bwill (buy|order) later\b",
    r"\bholding off\b",
    r"\bpostpon",
    r"\bsale (is|are) coming\b",
)
ABANDON = _rx(
    r"\bdidn'?t buy\b",
    r"\bdid not buy\b",
    r"\bnever bought\b",
    r"\bnot buying\b",
    r"\bcancel(led|ed)?\b",
    r"\bremoved from\b",
    r"\bwaste of time\b",
    r"\buninstalled after\b",
)
PURCHASED = _rx(r"\bbought\b", r"\bpurchased\b", r"\bordered\b", r"\bplaced (an )?order\b")
PURCHASE_INTENT = _rx(r"\bgoing to buy\b", r"\bwill buy\b", r"\bplanning to (buy|order)\b", r"\bwant to buy\b")
COMPARISON = _rx(r"\bcompar(e|ed|ing)\b", r"\bvs\.?\b", r"\balternative\b", r"\bbetter than\b", r"\bajio\b", r"\bamazon\b", r"\bmeesho\b", r"\bnykaa\b")
RETURNS = _rx(r"\breturn(s|ed|ing)?\b", r"\bexchange(d|s)?\b", r"\brefund\b")
FIT = _rx(r"\bfit(s|ted|ting)?\b", r"\btoo (tight|loose|small|big)\b", r"\bdoesn'?t fit\b")
SIZE = _rx(r"\bsize(s|d|ing)?\b", r"\bsize chart\b", r"\bsizing\b", r"\bxx?l\b", r"\bmeasurements?\b")
QUALITY = _rx(r"\bquality\b", r"\bcheap (look|feel|quality)\b", r"\bflimsy\b", r"\bstitch(ing)?\b", r"\bfade[ds]?\b")
FABRIC = _rx(r"\bfabric\b", r"\bmaterial\b", r"\btexture\b", r"\bsee through\b", r"\btransparent\b", r"\bfeel\b")
APPEARANCE = _rx(r"\bnothing like (the )?photo\b", r"\bdifferent (from|than) (the )?picture\b", r"\bcolour differ", r"\bcolor differ", r"\blooks different\b")
PRICE = _rx(r"\bprice\b", r"\bexpensive\b", r"\bcostly\b", r"\boverpriced\b", r"\bdiscount\b", r"\bsale\b", r"\bmrp\b", r"\bcheap\b")
REVIEWS = _rx(r"\breviews?\b", r"\brating\b", r"\bfake review\b", r"\bphotos? from (buyers|customers)\b")
INFO = _rx(r"\bsize chart\b", r"\bdescription\b", r"\bdetails?\b", r"\binformation\b", r"\bspecs?\b", r"\bhow (it )?looks\b")
SOCIAL = _rx(r"\bfriend(s)?\b", r"\binfluencer\b", r"\binstagram\b", r"\breel(s)?\b", r"\binstagram\b")
OCCASION = _rx(r"\bwedding\b", r"\bparty\b", r"\boffice\b", r"\bfestival\b", r"\boccasion\b", r"\bevent\b")
AVAIL = _rx(r"\bout of stock\b", r"\bnot available\b", r"\bsold out\b", r"\bunavailable\b")
DELIVERY = _rx(r"\bdeliver(y|ed|ing)\b", r"\bshipping\b", r"\blate\b", r"\bdelay")
EXTERNAL = _rx(
    r"\byoutube\b",
    r"\bgoogle(d| search)?\b",
    r"\binstagram\b",
    r"\breddit\b",
    r"\boffline\b",
    r"\bstore visit\b",
    r"\bbrand website\b",
    r"\bchecked on amazon\b",
)
DECISION = _rx(r"\bdecid(e|ed|ing)\b", r"\bconfused\b", r"\btoo many options\b", r"\boverwhelmed\b", r"\bnot sure\b", r"\bunsure\b")
CONSIDER = _rx(r"\bconsider(ing|ed)?\b", r"\bthinking (of|about) buy", r"\bmight buy\b", r"\blooking (at|for)\b")
BROWSE = _rx(r"\bbrows(e|ing)\b", r"\bscroll(ing)?\b", r"\bjust looking\b")
INSPIRATION = _rx(r"\binspir(e|ation|ed)\b", r"\bideas?\b", r"\bstyle\b")
NEED = _rx(r"\bneed(ed)?\b", r"\breplace\b", r"\bwardrobe\b")
BRAND = _rx(r"\bbrand\b", r"\boriginal\b", r"\bauthentic\b", r"\bfake product\b")
TREND = _rx(r"\btrend(y|ing)?\b", r"\bviral\b")
DESIGN = _rx(r"\bdesign\b", r"\bprint\b", r"\bcolour\b", r"\bcolor\b", r"\blook(s|ed|ing)? nice\b", r"\bpretty\b")
URGENCY = _rx(r"\bno hurry\b", r"\bnot urgent\b", r"\bwhenever\b", r"\bmaybe later\b")
OVERLOAD = _rx(r"\btoo many\b", r"\bso many options\b", r"\boverwhelmed\b", r"\bcan'?t decide\b")
TIMING = _rx(r"\bpayday\b", r"\bnext month\b", r"\bwait for sale\b", r"\bend of season\b")
COMPETING = _rx(r"\bbought (from|on) (amazon|ajio|meesho|nykaa|flipkart)\b", r"\bbetter on\b")

IRRELEVANT_APP_ONLY = _rx(
    r"\botp\b",
    r"\blogin\b",
    r"\bsign in\b",
    r"\bcrash(es|ing|ed)?\b",
    r"\bkeeps stopping\b",
    r"\bwhite screen\b",
    r"\bapp not opening\b",
    r"\bupdate (ruined|broke)\b",
    r"\bnotification spam\b",
    r"\btoo many notifications\b",
    r"\bplease fix the app\b",
)
PROMO = _rx(r"\buse (my )?code\b", r"\breferral\b", r"\bsubscribe to\b", r"\bcheck( out)? my (channel|store)\b")
SPAMMY = _rx(r"\bfree iphone\b", r"\bwhatsapp\b.*\bhttp", r"\bcrypto\b")

LOW_INFO_PHRASES = {
    "good",
    "nice",
    "ok",
    "okay",
    "super",
    "great",
    "love it",
    "best app",
    "worst app",
    "awesome",
    "bad",
    "very good",
    "very nice",
    "excellent",
    "thank you",
    "nice app",
    "good app",
    "poor",
    "worst",
    "fake",
    "cheaters",
}


def contains(pattern: re.Pattern[str], text: str) -> bool:
    return bool(pattern.search(text or ""))


def matched_span(pattern: re.Pattern[str], text: str, limit: int = 3) -> list[str]:
    spans = []
    for match in pattern.finditer(text or ""):
        start = max(0, match.start() - 40)
        end = min(len(text), match.end() + 40)
        snippet = (text[start:end] or "").strip()
        if snippet and snippet not in spans:
            spans.append(snippet)
        if len(spans) >= limit:
            break
    return spans


def any_match(patterns: Iterable[re.Pattern[str]], text: str) -> bool:
    return any(p.search(text or "") for p in patterns)
