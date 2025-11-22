# config.py - Simulation Configuration

# LLM Settings
MODEL_NAME = "llama3.1"
LLM_TIMEOUT = 180
KEEP_ALIVE = "60m"

# Simulation Parameters
TOTAL_ITERATIONS = 20

# Reviews per product per iteration (4 Critical + 4 Balanced + 4 Lenient)
GENUINE_REVIEWS_PER_PRODUCT = 12

# Token Limits
REVIEWER_MAX_TOKENS = 300
SHOPPER_MAX_TOKENS = 250

# Temperature Settings
REVIEWER_TEMPERATURE = 0.6
SHOPPER_TEMPERATURE = 0.3
FAKE_REVIEWER_TEMPERATURE = 0.7

# Fake Campaign Targets (BudgetBeats & ClearSound Basic)
FAKE_CAMPAIGN_TARGETS = [3, 5]

# Fake Review Attack Strategy
BURST_ITERATIONS = [4, 5]
BURST_VOLUME = {4: 40, 5: 40}
MAINTENANCE_VOLUME = 15

# Shoppers per product per persona
SHOPPERS_PER_PRODUCT_PER_PERSONA = 20

# Database
DB_PATH = "data/simulation.db"

# Review Reading Behavior
REVIEWS_READ = {
    "Impulsive": 3,
    "Careful": 10,
    "Skeptical": 15
}
