# Fake Review ABM Simulation

Agent-Based Modeling (ABM) simulation untuk meneliti dampak fake reviews terhadap keputusan pembelian di e-commerce menggunakan Large Language Models (LLM).

**OPTIMAL SETUP**: 7,550 agents, 20 iterations.

## Research Questions

- **RQ1**: How much does conversion rate increase for low-quality products targeted by fake review campaigns?
- **RQ2**: Which consumer type is most vulnerable to fake reviews? (Impulsive vs Careful vs Skeptical)

## Key Features

- **Publication-Grade**: Statistical tests (Chi-Square, ANOVA), effect sizes, confidence intervals
- **Optimal Design**: Balanced experimental design with n=400 per persona
- **LLM-Powered Agents**: Natural language reviews and purchase decisions via Llama 3.1 8B
- **Realistic Attack Scenario**: 100+ fake review burst attacks with maintenance mode
- **Comprehensive Analysis**: Automated RQ1/RQ2 analysis with visualizations

## Technology Stack

- **Python 3.9+**
- **Ollama** - LLM Engine (Llama 3.1 8B)
- **SQLAlchemy** - Database ORM
- **Pandas, Matplotlib, Seaborn, SciPy** - Data analysis & statistical testing

## Project Structure

```
fake_review_sim/
├── src/                      # Source code
│   ├── config.py            # OPTIMAL configuration (20 iter, 12 reviews/product, 20 shoppers)
│   ├── database.py          # SQLAlchemy models
│   ├── llm_client.py        # Ollama wrapper (GPU optimized)
│   ├── prompts.py           # LLM prompt templates (English-only)
│   ├── products.py          # Product manager
│   ├── agents.py            # Reviewer & Shopper agents
│   └── engine.py            # Simulation orchestrator 
├── data/                     # Database & analysis outputs
├── analysis/                 # Analysis scripts
│   ├── comprehensive_analysis.py  # RQ1 & RQ2 analysis
│   └── visualize_results.py       # Simple visualization
├── main.py                   # Entry point
└── requirements.txt          # Dependencies
```

## Installation

### 1. Install Ollama

Download from: https://ollama.com/download

```powershell
# Verify installation
ollama --version
```

### 2. Download LLM Model

```powershell
ollama pull llama3.1:8b
```

### 3. Setup Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Start Ollama Service

Ollama should auto-start on Windows. Verify it's running:

```powershell
ollama list
```

You should see `llama3.1:8b` in the list.

### 2. Run Simulation (OVERNIGHT RECOMMENDED)

```powershell
# Delete old database for fresh run
del data\simulation.db

# Run simulation (4-6 hours)
python main.py
```

**Expected Runtime**: 4-6 hours (overnight run recommended)
- Total LLM calls: ~7,540
- Genuine reviews: 1,200 (60 per iteration × 20 iterations)
- Fake reviews: 340 (burst + maintenance)
- Shopper decisions: 6,000 (300 per iteration × 20 iterations)

### 3. Analyze Results

```powershell
python analysis\comprehensive_analysis.py
```

**Outputs**:
- `data/rq1_comprehensive_analysis.png` - RQ1: Conversion rate impact (4 subplots)
- `data/rq2_comprehensive_analysis.png` - RQ2: Persona vulnerability (4 subplots)
- `data/analysis_report.txt` - Statistical test results & summary

**Simple visualization** (optional):
```powershell
python analysis\visualize_results.py
```

## Simulation Configuration (OPTIMAL SETUP)

From `src/config.py`:

```python
# Iterations - Extended for temporal dynamics
TOTAL_ITERATIONS = 20  # Increased from 10

# Genuine reviews - BALANCED DESIGN
GENUINE_REVIEWS_PER_PRODUCT = 12  # 4 Critical + 4 Balanced + 4 Lenient
# Total per iteration: 5 products × 12 = 60 reviews

# Fake review campaign - REALISTIC ATTACK
BURST_ITERATIONS = [4, 5]  # Strategic timing
BURST_VOLUME = {4: 100, 5: 100}  # 100 fakes per burst (50 per target)
MAINTENANCE_VOLUME = 10  # 5 per target, iterations 6-20

# Shoppers - HIGH STATISTICAL POWER
SHOPPERS_PER_PRODUCT_PER_PERSONA = 20  # n=400 per persona total
# Total per iteration: 5 products × 3 personas × 20 = 300 shoppers

# Reading behavior
REVIEWS_READ = {
    "Impulsive": 3,    # Quick decisions
    "Careful": 10,     # Moderate analysis
    "Skeptical": 15    # Deep pattern detection
}
```

## Agent Types

### Reviewers

**Genuine Reviewers** (3 personalities, perfectly balanced):
- **Critical** - High standards, focuses on flaws (4 per product per iteration)
- **Balanced** - Fair and objective (4 per product per iteration)
- **Lenient** - Optimistic and forgiving (4 per product per iteration)

**Fake Reviewers**:
- Generic English praise ("Amazing!", "Perfect!", "Great value!")
- No specific product details
- Always 5 stars
- Varied prompts to avoid identical reviews

### Shoppers

**3 Personas** (20 shoppers each per product per iteration):

- **Impulsive**
  - Reads only 3 reviews
  - Decides based on average rating
  - Trusts high ratings

- **Careful**
  - Reads 10 reviews
  - Balances pros and cons
  - Looks for specific details

- **Skeptical**
  - Reads 15 reviews
  - **Detects burst attacks** via [Iter:X] tags
  - Red flags: Many 5-stars + Same iteration + Generic text

## Database Schema

### Products Table
```sql
- id, name, price
- base_quality (High/Medium/Low)
- sound_quality, build_quality, battery_life, comfort (0-10 scale)
- current_rating, review_count (updated dynamically)
```

### Reviews Table
```sql
- id, product_id, agent_type, agent_personality
- rating (1-5), text (LLM-generated)
- is_fake (boolean), iteration (timestamp)
```

### Transactions Table
```sql
- id, product_id, buyer_persona
- decision (BUY/NO_BUY), reasoning (LLM-generated)
- reviews_read, fake_in_sample, iteration
```

## Expected Results

### RQ1: Fake Review Impact

**Baseline (Iterations 1-3)**:
- BudgetBeats (Low quality): ~15-25% conversion rate
- ClearSound Basic (Low-Med): ~20-30% conversion rate

**Burst Attack (Iterations 4-5)**:
- BudgetBeats: **~60-80% conversion rate** (+250-400% increase)
- ClearSound Basic: **~65-85% conversion rate** (+200-350% increase)

**Statistical Significance**: Chi-Square test, p < 0.001 (highly significant)

### RQ2: Persona Vulnerability

**Vulnerability Ranking** (expected):
1. **Impulsive**: +40-60% increase (MOST vulnerable)
2. **Careful**: +20-35% increase
3. **Skeptical**: +5-15% increase (LEAST vulnerable)

**ANOVA**: Significant differences across personas (p < 0.01)

## Performance Optimizations

1. **GPU Keep-Alive**: Model stays in VRAM for 60 minutes
2. **No N+1 Queries**: Direct Review object access
3. **Balanced Design**: Eliminates sampling bias
4. **Progress Bars**: Real-time monitoring with tqdm

## Viewing Database

### Option 1: DB Browser for SQLite
Download: https://sqlitebrowser.org/

### Option 2: Python
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/simulation.db")
products = pd.read_sql_query("SELECT * FROM products", conn)
reviews = pd.read_sql_query("SELECT * FROM reviews", conn)
transactions = pd.read_sql_query("SELECT * FROM transactions", conn)
print(products)
```

## Troubleshooting

### Ollama Not Responding
```powershell
# Check if running
ollama list

# Restart Ollama (if needed)
# Close Ollama app and restart it
```

### Slow Simulation
- **GPU usage**: Check with `nvidia-smi` or Task Manager
- **Normal speed**: ~2-3 seconds per LLM call
- **If slower**: Check Ollama logs, ensure llama3.1:8b is loaded

### ModuleNotFoundError
```powershell
# Make sure venv is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Locked
```powershell
# Close any DB browser applications
# Delete database and re-run
del data\simulation.db
python main.py
```


## License

Educational/Research use only.

## Citation

If you use this work in your research, please cite:

```
@software{fake_review_abm_2025,
  author = {Ikrar},
  title = {Fake Review ABM Simulation: LLM-Powered Agent-Based Modeling},
  year = {2025},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/yourusername/fake_review_sim}}
}
```

## Author

Ikrar - 2025


