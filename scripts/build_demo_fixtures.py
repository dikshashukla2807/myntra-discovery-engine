#!/usr/bin/env python3
"""Labeled Demo / Sample Data. Not public-source research."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.pipeline.normalize import normalize_record  # noqa: E402
from backend.utils.io import utc_now, write_jsonl  # noqa: E402
from config import settings  # noqa: E402

SAMPLES = [
    ("google_play", "demo-gp-01", "Saved 4 kurtas to wishlist last month. Still haven't bought any because I can't tell if the size chart matches my body. I keep opening the listing and closing it.", 3, "wishlist fit"),
    ("google_play", "demo-gp-02", "I add things to bag and then wait for a better price even when I like the design. Not sure if I actually want them or I'm just collecting options.", 4, "postpone price"),
    ("google_play", "demo-gp-03", "Bought a dress after saving it for 2 weeks. Customer photos finally convinced me it wasn't as shiny as the studio shot.", 5, "purchased photos"),
    ("google_play", "demo-gp-04", "Quality looks different from pictures. I returned two tops. Now I hesitate to buy anything I wishlisted.", 2, "quality return"),
    ("google_play", "demo-gp-05", "Size XL in one brand is M in another. Wishlist is full of jeans I am afraid to order.", 2, "size"),
    ("google_play", "demo-gp-06", "App keeps crashing on checkout.", 1, "irrelevant crash"),
    ("google_play", "demo-gp-07", "Nice app", 5, "low info"),
    ("google_play", "demo-gp-08", "Compared the same sneakers on Amazon and Ajio after saving them here. Bought the pair that had more real photos, not the one I wishlisted first.", 4, "comparison alternative"),
    ("google_play", "demo-gp-09", "I search YouTube hauls for the exact product code before I buy anything from my wishlist. Fabric is impossible to judge.", 3, "youtube fabric"),
    ("google_play", "demo-gp-10", "OTP not coming. Can't login.", 1, "irrelevant otp"),
    ("google_play", "demo-gp-11", "Saved a saree for my cousin's wedding. Event is in 6 weeks so I'm waiting, not because I dislike it.", 4, "occasion postpone"),
    ("google_play", "demo-gp-12", "Too many similar dresses. I shortlisted 8 and then bought none. Overwhelmed.", 3, "overload abandon"),
    ("google_play", "demo-gp-13", "Reviews feel fake. All 5 stars with the same words. I won't purchase from wishlist until I see more customer photos.", 2, "reviews trust"),
    ("google_play", "demo-gp-14", "Asked my sister which colour to pick. Still considering the two I saved.", 4, "social considering"),
    ("google_play", "demo-gp-15", "Went to the brand store offline to check the fit of a jacket I had wishlisted. Then ordered online in my size.", 5, "offline purchased"),
    ("app_store", "demo-as-01", "I use wishlist as a bookmark for outfits I might wear later, not as a buy list.", 4, "bookmark"),
    ("app_store", "demo-as-02", "Delivery is so delayed that I cancelled two orders of wishlisted items.", 2, "delivery abandon"),
    ("app_store", "demo-as-03", "The size I saved went out of stock. By the time it returned I had bought something else.", 3, "availability alternative"),
    ("app_store", "demo-as-04", "Love browsing. Rarely checkout. Saved items sit there for months.", 4, "browse postpone"),
    ("app_store", "demo-as-05", "Measured myself and compared to the size chart. Still didn't buy because sleeve length wasn't listed.", 3, "info size"),
    ("app_store", "demo-as-06", "Bought immediately when I found a product I needed for office. No hesitation that time.", 5, "need purchased"),
    ("app_store", "demo-as-07", "Return pickup is painful in my area so I avoid buying clothes I'm unsure about, even if they're in wishlist.", 2, "return concern"),
    ("app_store", "demo-as-08", "Great", 5, "low info"),
    ("reddit", "demo-rd-01", "Anyone else add a ton of stuff to Myntra wishlist and then never buy it? I think I use it like Pinterest.", None, "bookmark intent"),
    ("reddit", "demo-rd-02", "I google the product name + review before buying. Myntra page isn't enough to know if the fabric pills.", None, "google quality"),
    ("reddit", "demo-rd-03", "Fit is all over the place. I check Reddit and Instagram customer pics. Still returned a kurta.", None, "fit external return"),
    ("reddit", "demo-rd-04", "I wait for the big sale even if I already decided I like it. Wishlist is my sale queue.", None, "timing price"),
    ("reddit", "demo-rd-05", "Bought from Nykaa Fashion instead because they had a video of the dress. Had it sitting in Myntra wishlist for 10 days.", None, "external alternative"),
    ("reddit", "demo-rd-06", "How do you decide between two similar jeans? I keep both saved and freeze.", None, "comparison overload"),
    ("reddit", "demo-rd-07", "I actually buy most of my wishlist within a week if I need it for travel. Depends on urgency.", None, "counter urgency purchased"),
    ("reddit", "demo-rd-08", "Checked the brand website for measurements after saving a shirt on Myntra. Then purchased.", None, "brand site purchased"),
    ("reddit", "demo-rd-09", "Unsure if it will look like the photos on a real body. That's why my cart/wishlist never converts.", None, "appearance postpone"),
    ("reddit", "demo-rd-10", "Not Myntra specific: I abandon fashion carts when I can't tell quality. Same on every app.", None, "quality abandon"),
    ("youtube", "demo-yt-01", "Came here from a haul video because the Myntra listing photos looked too edited. Still not buying until I see more real clips.", None, "youtube appearance"),
    ("youtube", "demo-yt-02", "Does this kurti run small? I have it wishlisted.", None, "size wishlist"),
    ("youtube", "demo-yt-03", "Thanks for showing the fabric close up. I ordered after 3 weeks of saving it.", None, "workaround purchased"),
    ("youtube", "demo-yt-04", "I compare prices on two apps after watching hauls. Wishlist is just a reminder.", None, "comparison bookmark"),
    ("youtube", "demo-yt-05", "Please do a try-on with measurements. Size charts don't tell drape.", None, "fit info"),
    ("youtube", "demo-yt-06", "I asked friends in the comments whether to buy. Still waiting.", None, "social postpone"),
    ("youtube", "demo-yt-07", "Returned mine. Colour was different. Don't trust the product page.", None, "appearance return"),
    ("google_play", "demo-gp-16", "I keep checking later hoping new reviews appear on the wishlisted heels.", 3, "waiting reviews"),
    ("google_play", "demo-gp-17", "Added alternatives to wishlist so I can decide after payday.", 4, "workaround timing"),
    ("google_play", "demo-gp-18", "Stitching came undone. Now I assume quality is risky and postpone even brands I like.", 1, "quality postpone"),
    ("google_play", "demo-gp-19", "For shoes I buy faster than ethnic wear. Fit is clearer from the size number.", 4, "segment footwear"),
    ("google_play", "demo-gp-20", "Use my code SAVE20 at checkout!!!", 5, "promo"),
    ("app_store", "demo-as-09", "Notifications are annoying.", 2, "irrelevant notif"),
    ("app_store", "demo-as-10", "Looked at Instagram reels of the same top I saved. Then decided it wasn't for my office.", 4, "instagram occasion abandon"),
    ("reddit", "demo-rd-11", "Do people really use Myntra wishlist as purchase intent? I treat it as a moodboard.", None, "intent question"),
    ("reddit", "demo-rd-12", "I purchased after the influencer showed a close-up of buttons. Information on the page was too thin.", None, "info purchased"),
]


def main() -> None:
    collected_at = utc_now()
    rows = []
    for source, sid, text, rating, tag in SAMPLES:
        url = f"demo://sample/{source}/{sid}"
        rows.append(
            normalize_record(
                source=source,
                source_id=sid,
                source_url=url,
                text=text,
                collected_at=collected_at,
                date="2026-01-15T00:00:00Z",
                rating=rating,
                title=f"DEMO SAMPLE: {tag}",
                metadata={"demo_tag": tag, "warning": "Demo / Sample Data — not a real review"},
                dataset_label="demo_sample",
            )
        )
    path = settings.FIXTURES_DIR / "demo_observations.jsonl"
    write_jsonl(path, rows)
    print(f"wrote {len(rows)} labeled demo observations to {path}")


if __name__ == "__main__":
    main()
