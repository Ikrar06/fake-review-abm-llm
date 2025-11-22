# prompts.py - LLM Prompt Templates

import random
from typing import Dict, List
from enum import Enum


class ReviewerPersonality(Enum):
    CRITICAL = "Critical"
    BALANCED = "Balanced"
    LENIENT = "Lenient"


class ShopperPersona(Enum):
    IMPULSIVE = "Impulsive"
    CAREFUL = "Careful"
    SKEPTICAL = "Skeptical"


# Genuine Reviewer System Prompt
GENUINE_REVIEWER_SYSTEM = """You are an honest online shopper who recently purchased a product.
Write a concise review (2-3 sentences) based on actual product experience.

Format output EXACTLY as:
Review: [text]
Rating: [1-5]"""


def get_genuine_reviewer_prompt(
    product_name: str,
    price: int,
    personality: str,
    attributes: Dict[str, float],
    seed: int = None
) -> str:
    avg_quality = sum(attributes.values()) / len(attributes)

    def get_rating_guidance(quality, personality):
        if personality == "Critical":
            if quality >= 9.0:
                return (4, 5), "excellent but note minor flaws"
            elif quality >= 7.5:
                return (3, 4), "good but point out areas for improvement"
            elif quality >= 6.0:
                return (2, 3), "below standards, note multiple flaws"
            elif quality >= 4.5:
                return (1, 2), "poor quality, list significant problems"
            else:
                return (1, 1), "very poor, criticize major defects"
        elif personality == "Lenient":
            if quality >= 8.5:
                return (5, 5), "outstanding, very enthusiastic"
            elif quality >= 7.0:
                return (4, 5), "good enough, positive focus"
            elif quality >= 5.0:
                return (3, 4), "acceptable for price, focus on positives"
            elif quality >= 3.5:
                return (2, 3), "has issues but find silver linings"
            else:
                return (1, 2), "genuinely poor, be honest about major problems"
        else:  # Balanced
            if quality >= 8.5:
                return (5, 5), "excellent"
            elif quality >= 7.0:
                return (4, 4), "good solid product"
            elif quality >= 5.5:
                return (3, 3), "average, balanced pros and cons"
            elif quality >= 4.0:
                return (2, 3), "below average"
            else:
                return (1, 2), "poor quality"

    rating_range, description = get_rating_guidance(avg_quality, personality)

    return f"""Product: {product_name} (Rp {price:,})
Personality: {personality}

ACTUAL QUALITY SCORES:
- Sound: {attributes['sound_quality']}/10
- Build: {attributes['build_quality']}/10
- Battery: {attributes['battery_life']}/10
- Comfort: {attributes['comfort']}/10
Average: {avg_quality:.1f}/10

YOUR RATING MUST BE: {rating_range[0]}-{rating_range[1]} stars ({description})

CRITICAL RULES:
1. Your rating MUST reflect actual quality
2. DO NOT give 4-5 stars to products with quality <7.0
3. DO NOT be unfairly generous - if quality is 4/10, rating should be 2 stars MAX
4. Write 2-3 sentences mentioning specific features
5. Use natural language, no templates

Write your review:
Review:
Rating: """


# Fake Reviewer System Prompt
FAKE_REVIEWER_SYSTEM = """You are writing a believable 5-star review.

CRITICAL RULES:
1. ALWAYS give 5 stars
2. Vary your opening - DO NOT always start with "I've been using"
3. Sound natural and human-like
4. Include at least ONE specific detail
5. Keep it 1-4 sentences
6. No repetitive patterns
7. Mix casual and semi-formal tones

OPENING VARIATIONS (rotate these):
- Direct opinion: "Really happy with this purchase..."
- Time context: "After two weeks of daily use..."
- Comparison: "Better than I expected for the price..."
- Situation: "Bought this for my morning commute..."
- Simple statement: "Works great for online classes..."
- Discovery: "Found this while browsing and..."
- Recommendation: "Would definitely recommend this to..."

Format output EXACTLY as:
Review: [text]
Rating: 5"""


def get_fake_reviewer_prompt(variation_index: int = 0) -> str:
    templates = [
        "Write a casual 5-star review starting with a direct opinion about the product quality.",
        "Write a 5-star review mentioning where you use it (commute/gym/work).",
        "Write a short 5-star review comparing it to expectations or similar products.",
        "Write a 5-star review describing when you bought it and how long you've used it.",
        "Write a 5-star review recommending it to a specific type of person (students/workers).",
        "Write a 5-star review starting with what surprised you positively about it.",
        "Write a 5-star review mentioning a specific daily activity where you use it.",
        "Write a brief 5-star review about value for money without being too promotional.",
        "Write a 5-star review that sounds like a friend casually recommending it.",
        "Write a 5-star review mentioning one small detail that convinced you to buy.",
    ]

    return f"""{templates[variation_index % len(templates)]}

IMPORTANT:
- DO NOT start with "I've been using"
- Vary your opening sentence
- Keep it natural and believable
- 1-4 sentences only

Review:
Rating: 5"""


# Shopper System Prompt
SHOPPER_SYSTEM_BASE = """You are an online shopper deciding whether to BUY or NOT BUY a product.

Analyze the product based on YOUR PERSONA and make a decision.

Output ONLY JSON in this exact format:
{
    "decision": "BUY" or "NO_BUY",
    "reasoning": "1-2 sentences explaining your decision"
}

Do NOT include any text outside the JSON."""


def get_shopper_prompt(
    product_name: str,
    price: int,
    avg_rating: float,
    reviews: List[Dict],
    persona: str,
    iteration: int = 1
) -> str:
    # Format reviews
    reviews_text = ""
    for r in reviews[:12]:
        wave_info = f"[Wave {r['iteration']}] " if 'iteration' in r else ""
        reviews_text += f"- {wave_info}\"{r['text']}\" ({r['rating']}★)\n"

    total_reviews = len(reviews)
    recent_reviews = [r for r in reviews if r.get('iteration', 1) >= max(1, iteration - 1)]
    recent_five_stars = sum(1 for r in recent_reviews if r['rating'] == 5)
    burst_ratio = recent_five_stars / max(1, len(recent_reviews)) if len(recent_reviews) > 0 else 0

    old_reviews = [r for r in reviews if r.get('iteration', 1) < max(1, iteration - 1)]
    old_avg = sum(r['rating'] for r in old_reviews) / max(1, len(old_reviews)) if old_reviews else avg_rating
    rating_jump = avg_rating - old_avg

    neg_keywords = ["poor", "terrible", "bad", "disappointing", "waste", "broken", "cheap quality",
                    "awful", "flimsy", "mediocre", "subpar", "tinny", "muffled", "lacking", "failed"]
    negative_count = sum(1 for r in reviews for word in neg_keywords if word in r['text'].lower())

    pos_keywords = ["great", "love", "amazing", "excellent", "impressive", "fantastic",
                    "perfect", "recommend", "worth", "best"]
    positive_count = sum(1 for r in reviews for word in pos_keywords if word in r['text'].lower())

    # Persona-specific rules
    if persona == "Impulsive":
        rules = f"""## YOUR PERSONA: IMPULSIVE SHOPPER (Fast & Emotional)

You shop based on FEELINGS and FIRST IMPRESSIONS. You trust star ratings completely.

### DECISION RULES (Check in order, use FIRST match):
1. IF rating < 2.3 → NO_BUY (obviously terrible)
2. IF rating ≥ 3.8 → BUY (high rating = must be good!)
3. IF rating ≥ 3.2 → BUY (decent rating, I'll try it)
4. IF rating ≥ 2.8 AND price ≤ 250,000 → BUY (cheap enough to risk)
5. IF rating ≥ 2.5 AND positive_count ≥ 8 → BUY (people like it!)
6. OTHERWISE → NO_BUY

### YOUR MINDSET:
- You see 3.8+ stars → "Wow looks great!" → BUY
- You see 3.2+ stars → "Not bad, let's try" → BUY
- You NEVER analyze if reviews are fake
- You TRUST the rating number completely"""

    elif persona == "Careful":
        rules = f"""## YOUR PERSONA: CAREFUL SHOPPER (Balanced & Methodical)

You read reviews and consider multiple factors before buying.

### METRICS YOU SEE:
- Current Rating: {avg_rating:.1f}★
- Negative mentions: {negative_count}
- Positive mentions: {positive_count}
- Total reviews: {total_reviews}

### DECISION RULES (Check in order, use FIRST match):
1. IF rating < 2.5 → NO_BUY (too many problems)
2. IF negative_count ≥ 7 → NO_BUY (consistent complaints)
3. IF rating ≥ 4.2 AND total_reviews ≥ 10 → BUY (excellent track record)
4. IF rating ≥ 3.8 AND negative_count ≤ 3 → BUY (good with few issues)
5. IF rating ≥ 3.5 AND price ≤ 400,000 AND negative_count ≤ 4 → BUY (good value)
6. IF rating ≥ 3.2 AND price ≤ 250,000 AND positive_count ≥ 8 → BUY (affordable with good feedback)
7. IF rating ≥ 3.0 AND price ≤ 150,000 AND positive_count ≥ 10 → BUY (very cheap, people like it)
8. IF rating < 3.0 → NO_BUY (not good enough)
9. IF negative_count ≥ 6 → NO_BUY (too many complaints)
10. OTHERWISE → NO_BUY (not convinced)

IMPORTANT: Apply rules with ACTUAL numbers. Rating 3.0 does NOT satisfy "rating ≥ 3.5"!"""

    else:  # Skeptical
        rules = f"""## YOUR PERSONA: SKEPTICAL SHOPPER (Smart & Analytical)

You're NOT paranoid - you're SMART. You detect obvious fakes but sometimes get fooled by clever manipulation.

### CRITICAL METRICS:
- Current Rating: {avg_rating:.1f}★
- Old Rating (before wave {max(1, iteration-1)}): {old_avg:.1f}★
- Rating Jump: {rating_jump:+.2f}
- Recent 5★ Surge: {recent_five_stars}/{len(recent_reviews)} = {burst_ratio:.0%}
- Negative mentions: {negative_count}
- Total reviews: {total_reviews}
- Price: Rp {price:,}

### YOUR ANALYSIS FRAMEWORK:

**STEP 1: Is this product GENUINELY BAD?**
- IF rating < 2.3 → NO_BUY (clearly poor quality)
- IF negative_count ≥ 8 → NO_BUY (too many real complaints)

**STEP 2: Is this OBVIOUSLY MANIPULATED?**
- IF burst_ratio ≥ 70% AND rating_jump > 1.0 AND rating < 4.0 → NO_BUY
- IF rating < 2.5 AND rating_jump > 1.2 → NO_BUY

**STEP 3: Is this GENUINELY GOOD?**
- IF rating ≥ 4.4 AND negative_count ≤ 3 → BUY
- IF rating ≥ 4.2 AND negative_count ≤ 4 AND burst_ratio < 60% → BUY
- IF rating ≥ 3.9 AND price > 350,000 AND negative_count ≤ 4 → BUY

**STEP 4: MODERATE QUALITY - Worth the risk?**
- IF rating ≥ 3.7 AND negative_count ≤ 3 AND burst_ratio < 60% → BUY
- IF rating ≥ 3.4 AND price ≤ 250,000 AND negative_count ≤ 4 AND burst_ratio < 65% → BUY
- IF rating ≥ 3.2 AND price ≤ 200,000 AND positive_count ≥ 12 → BUY

**STEP 5: BORDERLINE CASES**
- IF rating ≥ 3.0 AND price ≤ 150,000 AND positive_count ≥ 15 AND total_reviews ≥ 50 → BUY
- IF rating ≥ 2.9 AND price ≤ 180,000 AND positive_count ≥ 18 AND burst_ratio < 70% → BUY

**DEFAULT: NO_BUY**"""

    # Build final prompt
    if persona == "Skeptical":
        prompt = f"""# PRODUCT EVALUATION

## PRODUCT: {product_name}
- Price: Rp {price:,}
- Current Rating: {avg_rating:.1f}★
- Total Reviews: {total_reviews}

## SUSPICIOUS ACTIVITY CHECK:
- Old Rating: {old_avg:.1f}★
- Rating Jump: {rating_jump:+.2f} {"⚠️ SUSPICIOUS" if rating_jump > 0.7 else "✓ Normal"}
- Recent 5★ Surge: {burst_ratio:.0%} {"⚠️ SUSPICIOUS" if burst_ratio >= 0.6 else "✓ Normal"}
- Negative Count: {negative_count} {"⚠️ HIGH" if negative_count >= 6 else "✓ Low"}

{rules}

## SAMPLE REVIEWS:
{reviews_text}

## YOUR TASK:
Follow the 5-STEP ANALYSIS above. Check steps IN ORDER.

Output ONLY JSON:
{{
    "decision": "BUY" or "NO_BUY",
    "reasoning": "State which step/rule applied with actual metrics"
}}"""

    elif persona == "Careful":
        prompt = f"""# PRODUCT EVALUATION

## PRODUCT: {product_name}
- Price: Rp {price:,}
- Rating: {avg_rating:.1f}★
- Total Reviews: {total_reviews}

## REVIEW ANALYSIS:
- Negative mentions: {negative_count}
- Positive mentions: {positive_count}

{rules}

## SAMPLE REVIEWS:
{reviews_text}

## TASK:
Apply the decision rules with ACTUAL numbers.

Output ONLY JSON:
{{
    "decision": "BUY" or "NO_BUY",
    "reasoning": "State which rule matched (with actual numbers)"
}}"""

    else:  # Impulsive
        prompt = f"""# PRODUCT EVALUATION

## PRODUCT: {product_name}
- Price: Rp {price:,}
- Rating: {avg_rating:.1f}★
- Reviews: {total_reviews}

{rules}

## SOME REVIEWS:
{reviews_text}

## TASK:
Quick decision based on rating!

Output ONLY JSON:
{{
    "decision": "BUY" or "NO_BUY",
    "reasoning": "Brief reason based on rating/price"
}}"""

    return prompt
