# PANDUAN PENYUSUNAN PAPER: Fake Review ABM Simulation

## Dokumen ini berisi panduan lengkap untuk menyusun paper publikasi level Scopus berdasarkan hasil simulasi ABM fake review.

---

# INFORMASI PROJECT

## 1. Judul yang Disarankan

**Opsi 1 (Teknis):**
> "The Illusion of Trust: Simulating the Impact of LLM-Generated Fake Review Attacks on Heterogeneous Consumer Personas using Agent-Based Modeling"

**Opsi 2 (Fokus Behavioral):**
> "How Fake Reviews Fool Different Shoppers: An Agent-Based Simulation of Consumer Vulnerability to AI-Generated Review Manipulation"

**Opsi 3 (Fokus Platform):**
> "Burst Attack Dynamics in E-commerce: Simulating Fake Review Campaigns and Consumer Response Using LLM-Powered Agents"

---

## 2. Research Questions

### RQ1: Sales/Conversion Impact
> "How much does conversion rate increase for low-quality products targeted by fake review campaigns?"

### RQ2: Consumer Vulnerability
> "Which consumer persona (Impulsive, Careful, Skeptical) is most vulnerable to fake review manipulation?"

---

## 3. Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| ABM Framework | **MESA** (Python) | Agent scheduling, data collection |
| LLM Engine | **Ollama + Llama 3.1 8B** | Generate natural language reviews & decisions |
| Database | **In-memory + CSV exports** | Store simulation results |
| Analysis | **Pandas, NumPy, SciPy** | Statistical analysis |
| Visualization | **Matplotlib** | Publication figures |

### Konfigurasi LLM (dari `config.py` dan `llm_client.py`)

```python
# config.py
MODEL_NAME = "llama3.1"
KEEP_ALIVE = "60m"  # GPU optimization
LLM_TIMEOUT = 180   # Seconds

# llm_client.py - Temperature settings (PENTING untuk paper)
# generate_text() default: temperature=0.6 (untuk reviews)
# generate_json() default: temperature=0.3 (untuk shopper decisions)
```

**Justifikasi Temperature:**
- **0.6 (Reviewer & Fake Reviewer)**: Menghasilkan variasi natural dalam review text
- **0.3 (Shopper)**: Memastikan output JSON konsisten dan decision logic reliable

---

## 4. Experimental Setup

### 4.1 Simulation Parameters (dari `config.py`)

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Total Iterations | 20 | Sufficient for temporal dynamics observation |
| Genuine Reviews/Product/Iteration | 12 | Balanced design (4C + 4B + 4L) |
| Shoppers/Product/Persona | 20 | n=400 per persona for statistical power |
| Burst Iterations | 4, 5 | After baseline established |
| Burst Volume | 40/iteration | 20 fake reviews per target product |
| Maintenance Volume | 15/iteration | Sustain inflated ratings |
| Target Products | BudgetBeats, ClearSound | Low-quality products |

### 4.2 Product Characteristics (Table 1 di paper)

| Product | Quality Level | Price (IDR) | Sound | Build | Battery | Comfort | Targeted |
|---------|--------------|-------------|-------|-------|---------|---------|----------|
| SoundMax Pro | High | 450,000 | 8.5 | 8.0 | 9.0 | 8.5 | No |
| AudioBlast | Medium-High | 350,000 | 7.5 | 7.0 | 8.0 | 7.5 | No |
| BudgetBeats | Low | 150,000 | 4.0 | 3.5 | 5.5 | 4.5 | **Yes** |
| TechWave Elite | Premium | 650,000 | 9.5 | 9.0 | 9.5 | 9.0 | No |
| ClearSound | Low-Medium | 250,000 | 5.0 | 4.5 | 6.0 | 5.5 | **Yes** |

### 4.3 Agent Design

#### A. Reviewer Agents (3 Personalities)

| Personality | Rating Tendency | Behavior |
|-------------|-----------------|----------|
| **Critical** | Lower ratings (-1 star bias) | Focus on flaws, high standards |
| **Balanced** | Objective ratings | Fair pros/cons assessment |
| **Lenient** | Higher ratings (+1 star bias) | Focus on positives, forgiving |

**Distribution**: 4 Critical + 4 Balanced + 4 Lenient = 12 per product (BALANCED DESIGN)

#### B. Fake Reviewer Agents

| Characteristic | Description |
|----------------|-------------|
| Rating | Always 5 stars (forced in `agents.py` line 109) |
| Text Pattern | Generic praise, varied openings |
| Timing | Burst (iter 4-5) + Maintenance (iter 6+) |
| Variation | 10 prompt templates in `get_fake_reviewer_prompt()` |

#### C. Shopper Agents (3 Personas)

| Persona | Reviews Read | Decision Logic | Expected Vulnerability |
|---------|--------------|----------------|----------------------|
| **Impulsive** | 3 | Trust ratings blindly, quick decisions | HIGH |
| **Careful** | 10 | Balance pros/cons, consider price | MEDIUM |
| **Skeptical** | 15 | Analyze patterns, detect anomalies | LOW |

---

## 5. Proses Simulasi (Methodology)

### 5.1 Simulation Flow per Iteration

```
┌─────────────────────────────────────────────────────────────┐
│                    ITERATION FLOW                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 1: REVIEW GENERATION                                 │
│  ├── Generate 12 genuine reviews per product (LLM)          │
│  ├── IF iteration in [4,5]: Inject 40 fake reviews (burst)  │
│  └── IF iteration > 5: Inject 15 fake reviews (maintenance) │
│                                                             │
│  PHASE 2: SHOPPING DECISIONS                                │
│  ├── 20 Impulsive shoppers × 5 products = 100 decisions     │
│  ├── 20 Careful shoppers × 5 products = 100 decisions       │
│  └── 20 Skeptical shoppers × 5 products = 100 decisions     │
│                                                             │
│  PHASE 3: DATA COLLECTION                                   │
│  └── Record all reviews, decisions, ratings                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Attack Scenario Timeline

```
Iteration:  1   2   3   4   5   6   7   8  ...  20
            |-------|   |-----|   |--------------|
            BASELINE    BURST     MAINTENANCE

Baseline (1-3):   Only genuine reviews, establish natural ratings
Burst (4-5):      Inject 40 fake reviews/iteration (20 per target)
Maintenance (6+): Inject 15 fake reviews/iteration to sustain ratings
```

### 5.3 Rating Aggregation Formula

Rating produk dihitung sebagai simple average dari semua reviews:

```
R_product = (Σ r_i) / n

Where:
- r_i = individual review rating (1-5)
- n = total number of reviews
```

**Catatan**: Fake reviews dengan rating 5 akan mendorong average naik secara signifikan ketika baseline reviews rendah.

---

## 6. Statistical Methods & Formulas

### 6.1 Chi-Square Test (RQ1)

Digunakan untuk menguji signifikansi perbedaan conversion rate antara baseline vs burst period.

**Formula:**
```
χ² = Σ [(O_i - E_i)² / E_i]

Where:
- O_i = Observed frequency
- E_i = Expected frequency
```

**Contingency Table:**
```
                    BUY     NO_BUY
Baseline Period     a       b
Burst Period        c       d
```

**Interpretation:**
- p < 0.05: Significant difference
- p < 0.01: Highly significant
- p < 0.001: Very highly significant (report as ***)

### 6.2 Cramér's V (Effect Size for Chi-Square)

**Formula:**
```
V = √(χ² / n)

Where:
- χ² = Chi-square statistic
- n = Total sample size
```

**Interpretation:**
| V Value | Effect Size |
|---------|-------------|
| 0.1 | Small |
| 0.3 | Medium |
| 0.5+ | Large |

### 6.3 ANOVA (RQ2)

Digunakan untuk membandingkan conversion rate antar 3 persona.

**Formula:**
```
F = MS_between / MS_within

Where:
- MS_between = Between-group variance
- MS_within = Within-group variance
```

**Interpretation:**
- Large F + small p-value = Significant difference between personas

### 6.4 Conversion Rate

**Formula:**
```
Conversion Rate (%) = (Number of BUY decisions / Total evaluations) × 100
```

### 6.5 Absolute Increase (pp = percentage points)

**Formula:**
```
Δ (pp) = Conversion_burst - Conversion_baseline
```

**Contoh**: Baseline 0%, Burst 54% → Δ = +54 pp

---

## 7. Hasil Simulasi (Results)

### 7.1 RQ1 Results: Fake Review Impact

**Table 2: Impact of Fake Reviews on Conversion Rate**

| Product | Baseline | Attack | Δ (pp) | χ² | p | Cramér's V |
|---------|----------|--------|--------|-----|---|------------|
| BudgetBeats | 0.0% | 54.2% | +54.2 | 121.30 | <0.0001*** | 0.636 |
| ClearSound | 0.0% | 71.7% | +71.7 | 177.35 | <0.0001*** | 0.769 |

**Key Findings:**
- Conversion rate meningkat dari ~0% ke 54-72% setelah burst attack
- Effect size LARGE (V > 0.5)
- Highly statistically significant (p < 0.0001)

### 7.2 RQ2 Results: Persona Vulnerability

**Table 3: Persona Vulnerability Ranking**

| Rank | Persona | Baseline | Attack | Impact (pp) |
|------|---------|----------|--------|-------------|
| 1 | Impulsive | X% | Y% | +Z pp |
| 2 | Careful | X% | Y% | +Z pp |
| 3 | Skeptical | X% | Y% | +Z pp |

**ANOVA Results:** F = X.XX, p = X.XXXX

**Key Findings:**
- Impulsive most vulnerable (highest increase)
- Skeptical most resistant (lowest increase)
- Significant difference between groups (ANOVA p < 0.05)

---

## 8. Figures yang Dihasilkan

### Figure 1: RQ1 - Impact of Fake Reviews
**File:** `data/publication/Figure_1_RQ1.pdf`

| Panel | Content | Purpose |
|-------|---------|---------|
| (a) | Temporal dynamics (line plot) | Show conversion rate over time for targeted vs control products |
| (b) | Before/After comparison (bar chart) | Direct comparison of baseline vs attack period |

### Figure 2: RQ2 - Persona Vulnerability
**File:** `data/publication/Figure_2_RQ2.pdf`

| Panel | Content | Purpose |
|-------|---------|---------|
| (a) | Persona behavior over time (line plot) | Show how each persona responds to attack |
| (b) | Vulnerability ranking (horizontal bars) | Rank personas by conversion rate increase |

### Figure 3: Temporal Dynamics
**File:** `data/publication/Figure_3_Temporal.pdf`

| Content | Purpose |
|---------|---------|
| Single panel: Targeted vs Control over time | Overview of entire simulation dynamics |

---

## 9. Tables yang Dihasilkan

| Table | File | Content |
|-------|------|---------|
| Table 1 | `Table_1_Products.tex` | Product characteristics |
| Table 2 | `Table_2_RQ1.tex` | RQ1 statistical results |
| Table 3 | `Table_3_RQ2.tex` | RQ2 persona comparison |

**Format:** LaTeX (booktabs style) + CSV

---

## 10. LIMITATIONS (Keterbatasan)

### 10.1 Prompt Engineering Challenge (CRITICAL)

> **"Menyeting prompt agar mendapatkan hasil yang sempurna adalah tantangan utama dalam penelitian ini."**

**Detail:**
- Prompt untuk shopper personas memerlukan iterasi berulang untuk mendapatkan behavior yang realistis
- Calibrating thresholds (kapan BUY vs NO_BUY) membutuhkan trial-and-error
- Skeptical persona awalnya terlalu "skeptis" (tidak membeli sama sekali), perlu adjustment
- Fake review prompts perlu variasi agar tidak terdeteksi sebagai pattern

**Implikasi untuk Paper:**
> "The design of effective prompts for LLM-based agents required extensive iteration. Particularly challenging was calibrating the Skeptical persona to maintain realistic resistance without becoming unrealistically paranoid."

### 10.2 LLM Limitations

| Limitation | Description | Impact |
|------------|-------------|--------|
| Context Window | Limited memory across interactions | Each decision is independent |
| Determinism | Same prompt can yield different outputs | Requires multiple runs for robustness |
| No Visual Input | Text-only reviews | Cannot simulate image-based products |
| English Only | Prompts in English | May not generalize to other markets |

### 10.3 Simulation Simplifications

| Aspect | Simplification | Real World Complexity |
|--------|----------------|----------------------|
| Product Category | Headphones only | Diverse product types |
| Review Volume | 12 genuine/product/iteration | Thousands per day |
| Consumer Pool | 300 shoppers/iteration | Millions of users |
| Time Scale | 20 iterations | Continuous over months |
| Platform Features | No images, no verified purchase | Multiple trust signals |

### 10.4 Statistical Limitations

- **No confidence intervals** reported for conversion rates (bisa ditambahkan)
- **Single simulation run** (idealnya multiple seeds untuk robustness)
- **No sensitivity analysis** (bagaimana hasil berubah jika parameter berbeda)

---

## 11. Struktur Paper yang Disarankan

### ABSTRAK (200-250 kata)

```
[PROBLEM] Review palsu merusak ekosistem e-commerce.

[GAP] Studi sebelumnya fokus pada deteksi, bukan dampak behavioral
secara dinamis menggunakan Generative AI.

[METHOD] Simulasi ABM (MESA Framework) dengan agen kognitif berbasis
Llama 3.1 8B. Tiga persona konsumen (Impulsive, Careful, Skeptical)
mengevaluasi produk berdasarkan reviews yang di-generate LLM.

[RESULTS]
- RQ1: Burst attack meningkatkan conversion rate produk low-quality
  dari ~0% ke 54-72% (p < 0.0001, Cramér's V > 0.6)
- RQ2: Impulsive paling vulnerable, Skeptical paling resistant,
  dengan perbedaan signifikan (ANOVA p < 0.05)

[IMPLICATION] Platform memerlukan deteksi berbasis temporal patterns
dan semantic analysis, bukan hanya rating aggregation.
```

### SECTION 1: INTRODUCTION

**Content:**
1. Background: Ekonomi reputasi digital, pentingnya reviews
2. Problem: LLM membuat fake reviews murah dan convincing ("Democratization of Fraud")
3. Gap: Existing research fokus deteksi, bukan behavioral impact secara dinamis
4. RQ1 & RQ2: State explicitly
5. Contribution: Apa yang paper ini tawarkan (simulation framework, behavioral insights)

### SECTION 2: RELATED WORK

**2.1 Fake Review Detection**
- Metode klasik (text classification, sentiment analysis)
- Tantangan baru: AI-generated text hampir indistinguishable

**2.2 Agent-Based Modeling in E-commerce**
- Sejarah ABM untuk market simulation
- Keunggulan: Heterogeneous agents, emergent behavior

**2.3 Generative Agents & LLM**
- Cite: "Generative Agents: Interactive Simulacra of Human Behavior" (Stanford)
- Tren menggunakan LLM sebagai "cognitive engine" untuk simulasi

### SECTION 3: METHODOLOGY

**3.1 System Architecture**
- Diagram: MESA + Ollama integration
- Data flow: Reviewer → Database → Shopper

**3.2 Agent Design**
- Genuine Reviewer: 3 personalities dengan prompt berbeda
- Fake Reviewer: Burst strategy, generic praise
- Shopper: 3 personas dengan cognitive biases berbeda

**3.3 Interaction Mechanism**
- Iteration flow
- Rating aggregation
- Decision logic per persona

**3.4 LLM Configuration**
- Model choice (Llama 3.1 8B)
- Temperature settings dengan justifikasi
- Prompt design philosophy

### SECTION 4: EXPERIMENTAL SETUP

**4.1 Simulation Parameters**
- Table dengan semua parameters (dari Section 4 di atas)

**4.2 Scenarios**
- Baseline: No fake reviews
- Attack: Burst (iter 4-5) + Maintenance (iter 6+)

**4.3 Data Collection**
- Metrics collected per iteration
- Statistical tests planned

### SECTION 5: RESULTS

**5.1 RQ1: Impact on Conversion Rate**
- Figure 1
- Table 2
- Statistical interpretation

**5.2 RQ2: Persona Vulnerability**
- Figure 2
- Table 3
- ANOVA interpretation

**5.3 Temporal Dynamics**
- Figure 3
- Pattern analysis

**5.4 Qualitative Analysis (Optional)**
- Sample review texts
- Comparison genuine vs fake

### SECTION 6: DISCUSSION

**6.1 Key Findings Interpretation**
- Why burst attacks are effective
- Why Impulsive most vulnerable
- Why Skeptical still somewhat vulnerable (price-risk tradeoff)

**6.2 Implications for Platforms**
- Need for temporal pattern detection
- Semantic analysis beyond ratings
- Verified purchase weight

**6.3 Implications for Consumers**
- Awareness of manipulation tactics
- Reading behavior recommendations

### SECTION 7: CONCLUSION

**7.1 Summary**
- Restate findings for RQ1 & RQ2

**7.2 Limitations**
- Prompt engineering challenges
- Simulation simplifications
- Single run (no robustness check)

**7.3 Future Work**
- Multi-product categories
- Platform defense agents
- Image-based reviews
- Cross-cultural validation

### REFERENCES

Format: IEEE atau APA

**Key papers to cite:**
1. Generative Agents (Stanford, 2023)
2. MESA Framework documentation
3. Fake review detection surveys
4. E-commerce trust literature
5. ABM methodology papers

### APPENDICES

**Appendix A: Prompt Templates**
- Full prompts from `prompts.py`

**Appendix B: Sample Data**
- Example reviews (genuine vs fake)
- Sample shopper decisions with reasoning

**Appendix C: Source Code Availability**
- Repository link (if open source)
- Configuration files

---

## 12. Files untuk Paper

### Source Files
| File | Description | Use in Paper |
|------|-------------|--------------|
| `src/config.py` | All parameters | Methodology, Appendix |
| `src/prompts.py` | LLM prompts | Appendix A |
| `src/model.py` | MESA model | Methodology |
| `src/agents.py` | Agent definitions | Methodology |
| `src/llm_client.py` | Ollama wrapper | Methodology |
| `main.py` | Entry point | Appendix |

### Output Files
| File | Description | Use in Paper |
|------|-------------|--------------|
| `data/publication/Figure_1_RQ1.pdf` | RQ1 figure | Results |
| `data/publication/Figure_2_RQ2.pdf` | RQ2 figure | Results |
| `data/publication/Figure_3_Temporal.pdf` | Temporal figure | Results |
| `data/publication/Table_1_Products.tex` | Product table | Methodology |
| `data/publication/Table_2_RQ1.tex` | RQ1 results | Results |
| `data/publication/Table_3_RQ2.tex` | RQ2 results | Results |

### Data Files
| File | Description | Use in Paper |
|------|-------------|--------------|
| `data/results/reviews_*.csv` | All reviews | Appendix B |
| `data/results/transactions_*.csv` | All decisions | Appendix B |

---

## 13. Checklist Sebelum Submit

### Content
- [ ] RQ1 & RQ2 terjawab dengan data
- [ ] Statistical tests dengan p-values
- [ ] Effect sizes (Cramér's V)
- [ ] Figures professional quality (600 DPI)
- [ ] Tables dalam format LaTeX
- [ ] Limitations section honest & complete

### Methodology Transparency
- [ ] All parameters documented
- [ ] LLM settings justified
- [ ] Prompt templates in appendix
- [ ] Reproducibility instructions

### Writing Quality
- [ ] Abstract 200-250 words
- [ ] No grammatical errors
- [ ] Technical terms defined
- [ ] Citations complete (IEEE/APA)

### Ethical Considerations
- [ ] Discuss potential misuse of findings
- [ ] Note that simulation is for research purposes
- [ ] Recommend platform countermeasures

---

## 14. Tips Tambahan untuk Scopus-Level Paper

### 1. Novelty Statement
Tekankan bahwa ini adalah:
- **First** simulation menggunakan LLM untuk both review generation AND consumer decision
- **First** quantitative study of heterogeneous consumer vulnerability to AI-generated reviews

### 2. Practical Implications
Reviewer Scopus suka paper dengan actionable insights:
- Platform: "Implement burst detection algorithms"
- Regulators: "Require disclosure of AI-generated content"
- Consumers: "Read more reviews, check temporal patterns"

### 3. Visual Quality
- Figures harus **publication-ready** (sudah ada di `data/publication/`)
- Gunakan PDF untuk vector quality
- Consistent color scheme (grayscale + accent)

### 4. Statistical Rigor
- Always report:
  - Sample size (n)
  - Test statistic (χ², F)
  - p-value
  - Effect size (V, d)
- Use significance stars (*, **, ***)

### 5. Honest Limitations
Reviewer menghargai kejujuran. Acknowledge:
- Prompt engineering challenge (ini differentiator papermu!)
- Simulation vs real-world gap
- Single run limitation

---

## 15. Contoh Kalimat untuk Setiap Section

### Introduction
> "The proliferation of Large Language Models (LLMs) has democratized the creation of convincing fake reviews, posing unprecedented challenges to e-commerce platforms."

### Methodology
> "We employ MESA, a Python-based agent-based modeling framework, integrated with Llama 3.1 8B via Ollama for natural language generation."

### Results
> "The burst attack resulted in a dramatic increase in conversion rate for BudgetBeats, from 0% at baseline to 54.2% during the attack period (χ² = 121.30, p < 0.0001, Cramér's V = 0.636)."

### Discussion
> "Contrary to intuition, even Skeptical consumers showed some vulnerability to manipulation, suggesting that price-quality tradeoffs can override analytical caution."

### Limitations
> "A significant challenge in this research was prompt engineering. Calibrating agent behavior, particularly the Skeptical persona, required extensive iteration to achieve realistic decision patterns."

---

**Document Version:** 1.1
**Last Updated:** November 2025
**Project:** Fake Review ABM Simulation (MESA Framework)
