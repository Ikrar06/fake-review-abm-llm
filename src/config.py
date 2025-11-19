# Configuration file for fake review simulation
# OPTIMAL SETUP FOR PUBLICATION-GRADE RESEARCH

# ============================================================
# LLM SETTINGS
# ============================================================
MODEL_NAME = "llama3.1"
LLM_TIMEOUT = 180  # Increased to 180 seconds for stability
KEEP_ALIVE = "60m"  # Keep model in VRAM for 60 minutes (extended for long runs)

# ============================================================
# OPTIMAL SIMULATION PARAMETERS
# ============================================================

# Iterations - Extended for temporal dynamics observation
TOTAL_ITERATIONS = 20  # Increased from 10 for long-term effect analysis

# Genuine reviews (per product per iteration)
# BALANCED DESIGN: Each product gets exactly 12 reviews (4C + 4B + 4L)
GENUINE_REVIEWS_PER_PRODUCT = 12  # 4 Critical + 4 Balanced + 4 Lenient
# Total genuine per iteration: 5 products × 12 = 60 reviews

# Product IDs for fake campaign targets
FAKE_CAMPAIGN_TARGETS = [3, 5]  # BudgetBeats (Low) & ClearSound Basic (Low-Medium)

# Fake Review Strategy - REALISTIC ATTACK SCENARIO
BURST_ITERATIONS = [4, 5]  # Strategic burst timing (after baseline established)
BURST_VOLUME = {4: 100, 5: 100}  # 100 fakes per burst (50 per target) - realistic attack
MAINTENANCE_VOLUME = 10  # 5 per target per iteration, iterations 6-20 (sustained attack)

# Shoppers - HIGH STATISTICAL POWER
# BALANCED DESIGN: Each product viewed by equal number of each persona
SHOPPERS_PER_PRODUCT_PER_PERSONA = 20  # Increased from 4 for statistical robustness
# Total shoppers per iteration: 5 products × 3 personas × 20 = 300 shoppers

# Database
DB_PATH = "data/simulation.db"

# Review Reading Behavior (by persona)
REVIEWS_READ = {
    "Impulsive": 3,    # Reads few reviews, decides quickly based on rating
    "Careful": 10,     # Reads moderate amount, looks for specific details (increased from 7)
    "Skeptical": 15    # Reads many reviews, analyzes patterns deeply (increased from 12)
}

# ============================================================
# EXPECTED OUTCOMES
# ============================================================
# Total LLM calls: ~7,540
# - Genuine: 60 × 20 = 1,200
# - Fake: 200 + 140 = 340
# - Shoppers: 300 × 20 = 6,000
#
# Runtime: 4-6 hours (overnight run recommended)
# Statistical power: n=400 per persona (high confidence)
# Margin of error: ±4.9% at 95% confidence
# ============================================================
