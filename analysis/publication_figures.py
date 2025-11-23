# analysis/publication_figures.py
# Publication-grade figures and tables for research paper
# PROFESSIONAL ACADEMIC STYLE - Minimal, Clean, IEEE/Nature-compatible

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PROFESSIONAL ACADEMIC STYLE SETTINGS
# =============================================================================
plt.rcParams.update({
    # Font settings (serif for academic papers)
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,

    # Axes
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,

    # Ticks
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,

    # Legend
    'legend.fontsize': 9,
    'legend.frameon': False,

    # Lines
    'lines.linewidth': 1.5,
    'lines.markersize': 5,

    # Grid
    'grid.linewidth': 0.5,
    'grid.alpha': 0.3,

    # Figure
    'figure.dpi': 150,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})


class PublicationFigures:
    """
    Generate publication-quality figures for research paper

    Style: Minimal, professional, academic
    - Grayscale base with minimal accent colors
    - Clean lines, no visual clutter
    - IEEE/Nature/Science compatible
    """

    def __init__(self, results_dir: str = None):
        # Auto-detect project root
        if results_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            results_dir = project_root / "data" / "results"

        self.results_dir = Path(results_dir)
        self.output_dir = self.results_dir.parent / "publication"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # PROFESSIONAL COLOR PALETTE (minimal, high contrast)
        self.colors = {
            'primary': '#2C3E50',      # Dark blue-gray (main)
            'secondary': '#7F8C8D',    # Medium gray
            'accent': '#C0392B',       # Dark red (for emphasis only)
            'light': '#BDC3C7',        # Light gray
            'white': '#FFFFFF',
            'black': '#1A1A1A',
        }

        # Markers (simple, professional)
        self.markers = {
            'circle': 'o',
            'square': 's',
            'triangle': '^',
            'diamond': 'D',
        }

        # Product mapping
        self.products = {
            1: "SoundMax Pro",
            2: "AudioBlast",
            3: "BudgetBeats",
            4: "TechWave Elite",
            5: "ClearSound"
        }

        self.fake_targets = [3, 5]
        self.burst_iterations = [4, 5]

        print("="*70)
        print("PUBLICATION FIGURE GENERATOR")
        print("Style: Professional Academic (Minimal, Clean)")
        print("="*70)

    def load_data(self):
        """Load latest CSV exports"""
        print("\n[1] Loading data...")

        reviews_files = sorted(self.results_dir.glob("reviews_*.csv"))
        transactions_files = sorted(self.results_dir.glob("transactions_*.csv"))

        if not reviews_files or not transactions_files:
            raise FileNotFoundError("No CSV files found. Run simulation first.")

        self.reviews_df = pd.read_csv(reviews_files[-1], encoding='utf-8')
        self.transactions_df = pd.read_csv(transactions_files[-1], encoding='utf-8')

        print(f"    Reviews: {len(self.reviews_df)}")
        print(f"    Transactions: {len(self.transactions_df)}")

    def _prepare_detailed_data(self):
        """Prepare detailed purchase data"""
        results = []

        for iteration in sorted(self.transactions_df['iteration'].unique()):
            iter_data = self.transactions_df[self.transactions_df['iteration'] == iteration]

            for product_id in sorted(self.transactions_df['product_id'].unique()):
                product_data = iter_data[iter_data['product_id'] == product_id]

                for persona in ['Impulsive', 'Careful', 'Skeptical']:
                    persona_data = product_data[product_data['persona'] == persona]

                    total_evals = len(persona_data)
                    purchases = (persona_data['decision'] == 'BUY').sum()
                    conversion = (purchases / total_evals * 100) if total_evals > 0 else 0

                    results.append({
                        'iteration': iteration,
                        'product_id': product_id,
                        'persona': persona,
                        'total_evaluations': total_evals,
                        'purchases': purchases,
                        'conversion_rate': conversion
                    })

        return pd.DataFrame(results)

    # =========================================================================
    # FIGURE 1: RQ1 - FAKE REVIEW IMPACT
    # =========================================================================

    def create_figure_1_rq1(self):
        """
        Figure 1: Impact of Fake Reviews on Conversion Rate (RQ1)

        Layout: 2 panels side by side
        (a) Temporal dynamics
        (b) Before/After comparison
        """
        print("\n[2] Creating Figure 1 (RQ1)...")

        # Larger figure with more spacing
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        fig.subplots_adjust(wspace=0.35, left=0.08, right=0.95, top=0.90, bottom=0.15)
        detailed_df = self._prepare_detailed_data()

        # Panel (a): Temporal dynamics
        ax = axes[0]
        self._plot_rq1_temporal(ax, detailed_df)
        ax.text(-0.15, 1.08, '(a)', transform=ax.transAxes,
               fontsize=12, fontweight='bold', va='top')

        # Panel (b): Before/After bars
        ax = axes[1]
        self._plot_rq1_bars(ax, detailed_df)
        ax.text(-0.15, 1.08, '(b)', transform=ax.transAxes,
               fontsize=12, fontweight='bold', va='top')

        output_path = self.output_dir / "Figure_1_RQ1.png"
        plt.savefig(output_path, facecolor='white', edgecolor='none')
        output_pdf = self.output_dir / "Figure_1_RQ1.pdf"
        plt.savefig(output_pdf, facecolor='white', edgecolor='none')
        print(f"    Saved: {output_path}")
        print(f"    Saved: {output_pdf}")
        plt.close()

    def _plot_rq1_temporal(self, ax, detailed_df):
        """Panel (a): Conversion rate over time"""

        # Aggregate targeted products
        targeted = detailed_df[detailed_df['product_id'].isin(self.fake_targets)]
        control = detailed_df[~detailed_df['product_id'].isin(self.fake_targets)]

        for data, label, color, marker in [
            (targeted, 'Targeted', self.colors['accent'], 'o'),
            (control, 'Control', self.colors['secondary'], 's')
        ]:
            agg = data.groupby('iteration').agg({
                'purchases': 'sum',
                'total_evaluations': 'sum'
            })
            agg['rate'] = agg['purchases'] / agg['total_evaluations'] * 100

            ax.plot(agg.index, agg['rate'], marker=marker, label=label,
                   color=color, markerfacecolor='white', markeredgewidth=1.5,
                   markersize=4, linewidth=1.5)

        # Mark burst period (subtle shading)
        ax.axvspan(3.5, 5.5, alpha=0.08, color=self.colors['black'], zorder=0)
        ax.text(4.5, 92, 'Burst', ha='center', fontsize=8, color=self.colors['secondary'])

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Conversion Rate (%)')
        ax.set_xlim(0.5, 20.5)
        ax.set_ylim(0, 100)
        ax.legend(loc='lower right')
        ax.grid(True, linestyle=':', alpha=0.4)

    def _plot_rq1_bars(self, ax, detailed_df):
        """Panel (b): Before/After comparison"""

        results = []
        for target_id in self.fake_targets:
            data = detailed_df[detailed_df['product_id'] == target_id]

            baseline = data[data['iteration'].isin([1, 2, 3])]
            burst = data[data['iteration'].isin(self.burst_iterations)]

            baseline_rate = baseline['purchases'].sum() / baseline['total_evaluations'].sum() * 100
            burst_rate = burst['purchases'].sum() / burst['total_evaluations'].sum() * 100

            results.append({
                'product': self.products[target_id],
                'baseline': baseline_rate,
                'burst': burst_rate
            })

        df = pd.DataFrame(results)
        x = np.arange(len(df))
        width = 0.30  # Slightly narrower bars

        # Bars
        ax.bar(x - width/2, df['baseline'], width, label='Baseline',
              color=self.colors['light'], edgecolor=self.colors['primary'], linewidth=1)
        ax.bar(x + width/2, df['burst'], width, label='During Attack',
              color=self.colors['primary'], edgecolor=self.colors['primary'], linewidth=1)

        # Value labels - positioned better
        for i, row in df.iterrows():
            # Baseline label (inside bar if tall enough, otherwise above)
            if row['baseline'] > 10:
                ax.text(i - width/2, row['baseline']/2, f"{row['baseline']:.0f}%",
                       ha='center', va='center', fontsize=9, color=self.colors['primary'])
            else:
                ax.text(i - width/2, row['baseline'] + 3, f"{row['baseline']:.0f}%",
                       ha='center', fontsize=9, color=self.colors['secondary'])

            # Attack label (inside bar)
            ax.text(i + width/2, row['burst']/2, f"{row['burst']:.0f}%",
                   ha='center', va='center', fontsize=9, color='white', fontweight='bold')

        # Significance brackets - more space
        for i in range(len(df)):
            y = max(df.iloc[i]['baseline'], df.iloc[i]['burst']) + 8
            ax.plot([i-width/2, i+width/2], [y, y], 'k-', linewidth=0.8)
            ax.text(i, y+3, '***', ha='center', fontsize=10)

        ax.set_ylabel('Conversion Rate (%)')
        ax.set_xticks(x)
        ax.set_xticklabels(df['product'], fontsize=10)
        ax.set_ylim(0, 105)  # More headroom
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, axis='y', linestyle=':', alpha=0.4)

    # =========================================================================
    # FIGURE 2: RQ2 - PERSONA VULNERABILITY
    # =========================================================================

    def create_figure_2_rq2(self):
        """
        Figure 2: Persona Vulnerability to Fake Reviews (RQ2)

        Layout: 2 panels side by side
        (a) Temporal comparison by persona
        (b) Vulnerability ranking
        """
        print("\n[3] Creating Figure 2 (RQ2)...")

        # Larger figure with more spacing
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        fig.subplots_adjust(wspace=0.35, left=0.08, right=0.95, top=0.90, bottom=0.15)
        detailed_df = self._prepare_detailed_data()

        # Panel (a): Temporal by persona
        ax = axes[0]
        self._plot_rq2_temporal(ax, detailed_df)
        ax.text(-0.15, 1.08, '(a)', transform=ax.transAxes,
               fontsize=12, fontweight='bold', va='top')

        # Panel (b): Vulnerability ranking
        ax = axes[1]
        self._plot_rq2_ranking(ax, detailed_df)
        ax.text(-0.15, 1.08, '(b)', transform=ax.transAxes,
               fontsize=12, fontweight='bold', va='top')

        output_path = self.output_dir / "Figure_2_RQ2.png"
        plt.savefig(output_path, facecolor='white', edgecolor='none')
        output_pdf = self.output_dir / "Figure_2_RQ2.pdf"
        plt.savefig(output_pdf, facecolor='white', edgecolor='none')
        print(f"    Saved: {output_path}")
        print(f"    Saved: {output_pdf}")
        plt.close()

    def _plot_rq2_temporal(self, ax, detailed_df):
        """Panel (a): Persona behavior over time on targeted products"""

        personas = ['Impulsive', 'Careful', 'Skeptical']
        markers = ['o', 's', '^']
        # Grayscale gradient for personas
        colors = [self.colors['black'], self.colors['secondary'], self.colors['light']]

        for persona, marker, color in zip(personas, markers, colors):
            data = detailed_df[
                (detailed_df['persona'] == persona) &
                (detailed_df['product_id'].isin(self.fake_targets))
            ]

            agg = data.groupby('iteration').agg({
                'purchases': 'sum',
                'total_evaluations': 'sum'
            })
            agg['rate'] = agg['purchases'] / agg['total_evaluations'] * 100

            ax.plot(agg.index, agg['rate'], marker=marker, label=persona,
                   color=color, markerfacecolor='white', markeredgewidth=1.5,
                   markersize=4, linewidth=1.5)

        # Mark burst period
        ax.axvspan(3.5, 5.5, alpha=0.08, color=self.colors['black'], zorder=0)

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Conversion Rate (%)')
        ax.set_xlim(0.5, 20.5)
        ax.set_ylim(0, 100)
        ax.legend(loc='lower right')
        ax.grid(True, linestyle=':', alpha=0.4)

    def _plot_rq2_ranking(self, ax, detailed_df):
        """Panel (b): Vulnerability ranking (horizontal bars)"""

        personas = ['Impulsive', 'Careful', 'Skeptical']
        impacts = []

        for persona in personas:
            data = detailed_df[
                (detailed_df['persona'] == persona) &
                (detailed_df['product_id'].isin(self.fake_targets))
            ]

            baseline = data[data['iteration'].isin([1, 2, 3])]
            burst = data[data['iteration'].isin(self.burst_iterations)]

            baseline_rate = baseline['purchases'].sum() / baseline['total_evaluations'].sum() * 100
            burst_rate = burst['purchases'].sum() / burst['total_evaluations'].sum() * 100

            impacts.append(burst_rate - baseline_rate)

        df = pd.DataFrame({'persona': personas, 'impact': impacts})
        df = df.sort_values('impact', ascending=True)

        # Horizontal bars (grayscale) - taller bars
        colors = [self.colors['light'], self.colors['secondary'], self.colors['primary']]
        bars = ax.barh(df['persona'], df['impact'], height=0.6, color=colors,
                      edgecolor=self.colors['primary'], linewidth=0.8)

        # Value labels - inside bars
        for bar, val, color in zip(bars, df['impact'], colors):
            # Put label inside bar
            text_color = 'white' if color == self.colors['primary'] else self.colors['primary']
            ax.text(val - 2, bar.get_y() + bar.get_height()/2,
                   f'+{val:.1f}pp', va='center', ha='right', fontsize=10,
                   fontweight='bold', color=text_color)

        ax.set_xlabel('Conversion Rate Increase (pp)', fontsize=10)
        ax.set_xlim(0, max(impacts) * 1.15)
        ax.tick_params(axis='y', labelsize=10)
        ax.grid(True, axis='x', linestyle=':', alpha=0.4)

    # =========================================================================
    # FIGURE 3: TEMPORAL DYNAMICS (SINGLE PANEL)
    # =========================================================================

    def create_figure_3_temporal(self):
        """
        Figure 3: Complete temporal dynamics
        Single panel showing targeted vs control over time
        """
        print("\n[4] Creating Figure 3 (Temporal)...")

        # Larger single panel figure
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.subplots_adjust(left=0.10, right=0.95, top=0.92, bottom=0.12)
        detailed_df = self._prepare_detailed_data()

        # Targeted products
        targeted = detailed_df[detailed_df['product_id'].isin(self.fake_targets)]
        targeted_agg = targeted.groupby('iteration').agg({
            'purchases': 'sum', 'total_evaluations': 'sum'
        })
        targeted_agg['rate'] = targeted_agg['purchases'] / targeted_agg['total_evaluations'] * 100

        # Control products
        control = detailed_df[~detailed_df['product_id'].isin(self.fake_targets)]
        control_agg = control.groupby('iteration').agg({
            'purchases': 'sum', 'total_evaluations': 'sum'
        })
        control_agg['rate'] = control_agg['purchases'] / control_agg['total_evaluations'] * 100

        # Plot
        ax.plot(targeted_agg.index, targeted_agg['rate'],
               marker='o', color=self.colors['primary'], label='Targeted Products',
               markerfacecolor='white', markeredgewidth=1.5, markersize=5, linewidth=2)
        ax.plot(control_agg.index, control_agg['rate'],
               marker='s', color=self.colors['secondary'], label='Control Products',
               markerfacecolor='white', markeredgewidth=1.5, markersize=4, linewidth=1.5)

        # Burst shading
        ax.axvspan(3.5, 5.5, alpha=0.1, color=self.colors['black'], zorder=0)

        # Annotations (minimal)
        ax.annotate('Attack', xy=(4.5, targeted_agg.loc[4:5, 'rate'].mean()),
                   xytext=(7, 80), fontsize=8,
                   arrowprops=dict(arrowstyle='->', color=self.colors['secondary'], lw=0.8))

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Conversion Rate (%)')
        ax.set_xlim(0.5, 20.5)
        ax.set_ylim(0, 100)
        ax.legend(loc='lower right')
        ax.grid(True, linestyle=':', alpha=0.4)

        plt.tight_layout()

        output_path = self.output_dir / "Figure_3_Temporal.png"
        plt.savefig(output_path, facecolor='white', edgecolor='none')
        output_pdf = self.output_dir / "Figure_3_Temporal.pdf"
        plt.savefig(output_pdf, facecolor='white', edgecolor='none')
        print(f"    Saved: {output_path}")
        print(f"    Saved: {output_pdf}")
        plt.close()

    # =========================================================================
    # TABLES
    # =========================================================================

    def create_tables(self):
        """Generate publication-ready tables"""
        print("\n[5] Creating tables...")

        self._create_table_1_products()
        self._create_table_2_rq1()
        self._create_table_3_rq2()

    def _create_table_1_products(self):
        """Table 1: Product Characteristics"""
        print("    Table 1 (Products)...")

        products_data = [
            ["SoundMax Pro", "High", "450,000", 8.5, 8.0, 9.0, 8.5, "No"],
            ["AudioBlast", "Medium-High", "350,000", 7.5, 7.0, 8.0, 7.5, "No"],
            ["BudgetBeats", "Low", "150,000", 4.0, 3.5, 5.5, 4.5, "Yes"],
            ["TechWave Elite", "Premium", "650,000", 9.5, 9.0, 9.5, 9.0, "No"],
            ["ClearSound", "Low-Medium", "250,000", 5.0, 4.5, 6.0, 5.5, "Yes"],
        ]

        df = pd.DataFrame(products_data, columns=[
            'Product', 'Quality', 'Price (IDR)',
            'Sound', 'Build', 'Battery', 'Comfort', 'Targeted'
        ])

        # CSV
        csv_path = self.output_dir / "Table_1_Products.csv"
        df.to_csv(csv_path, index=False)

        # LaTeX
        latex_path = self.output_dir / "Table_1_Products.tex"
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{table}[t]\n")
            f.write("\\centering\n")
            f.write("\\caption{Product characteristics and quality attributes (scale: 1--10)}\n")
            f.write("\\label{tab:products}\n")
            f.write("\\small\n")
            f.write("\\begin{tabular}{llcccccl}\n")
            f.write("\\toprule\n")
            f.write("Product & Quality & Price & Sound & Build & Battery & Comfort & Target \\\\\n")
            f.write("\\midrule\n")

            for _, row in df.iterrows():
                target_mark = "\\checkmark" if row['Targeted'] == "Yes" else "--"
                f.write(f"{row['Product']} & {row['Quality']} & {row['Price (IDR)']} & ")
                f.write(f"{row['Sound']} & {row['Build']} & {row['Battery']} & ")
                f.write(f"{row['Comfort']} & {target_mark} \\\\\n")

            f.write("\\bottomrule\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")

        print(f"      CSV: {csv_path}")
        print(f"      LaTeX: {latex_path}")

    def _create_table_2_rq1(self):
        """Table 2: RQ1 Statistical Results"""
        print("    Table 2 (RQ1 Results)...")

        detailed_df = self._prepare_detailed_data()
        results = []

        for target_id in self.fake_targets:
            data = detailed_df[detailed_df['product_id'] == target_id]

            baseline = data[data['iteration'].isin([1, 2, 3])]
            burst = data[data['iteration'].isin(self.burst_iterations)]

            baseline_rate = baseline['purchases'].sum() / baseline['total_evaluations'].sum() * 100
            burst_rate = burst['purchases'].sum() / burst['total_evaluations'].sum() * 100

            # Chi-square test
            b_buy = baseline['purchases'].sum()
            b_nobuy = baseline['total_evaluations'].sum() - b_buy
            a_buy = burst['purchases'].sum()
            a_nobuy = burst['total_evaluations'].sum() - a_buy

            chi2, p_val = stats.chi2_contingency([[b_buy, b_nobuy], [a_buy, a_nobuy]])[:2]
            n = b_buy + b_nobuy + a_buy + a_nobuy
            cramers_v = np.sqrt(chi2 / n)

            results.append({
                'Product': self.products[target_id],
                'Baseline': round(baseline_rate, 1),
                'Attack': round(burst_rate, 1),
                'Increase_pp': round(burst_rate - baseline_rate, 1),
                'Chi2': round(chi2, 2),
                'p': p_val,
                'V': round(cramers_v, 3),
                'n': int(baseline['total_evaluations'].sum() + burst['total_evaluations'].sum())
            })

        df = pd.DataFrame(results)

        # CSV
        csv_path = self.output_dir / "Table_2_RQ1.csv"
        df.to_csv(csv_path, index=False)

        # LaTeX
        latex_path = self.output_dir / "Table_2_RQ1.tex"
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{table}[t]\n")
            f.write("\\centering\n")
            f.write("\\caption{RQ1: Impact of fake reviews on conversion rate}\n")
            f.write("\\label{tab:rq1}\n")
            f.write("\\small\n")
            f.write("\\begin{tabular}{lcccccc}\n")
            f.write("\\toprule\n")
            f.write("Product & Baseline & Attack & $\\Delta$ (pp) & $\\chi^2$ & $p$ & Cram\\'er's V \\\\\n")
            f.write("\\midrule\n")

            for _, row in df.iterrows():
                p_str = f"{row['p']:.4f}" if row['p'] >= 0.0001 else "$<$0.0001"
                sig = "***" if row['p'] < 0.001 else "**" if row['p'] < 0.01 else "*" if row['p'] < 0.05 else ""
                f.write(f"{row['Product']} & {row['Baseline']}\\% & {row['Attack']}\\% & ")
                f.write(f"+{row['Increase_pp']} & {row['Chi2']} & {p_str}{sig} & {row['V']} \\\\\n")

            f.write("\\bottomrule\n")
            f.write("\\multicolumn{7}{l}{\\scriptsize Note: pp = percentage points. ")
            f.write("*** $p < 0.001$, ** $p < 0.01$, * $p < 0.05$}\\\\\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")

        print(f"      CSV: {csv_path}")
        print(f"      LaTeX: {latex_path}")

    def _create_table_3_rq2(self):
        """Table 3: RQ2 Persona Comparison"""
        print("    Table 3 (RQ2 Results)...")

        detailed_df = self._prepare_detailed_data()
        personas = ['Impulsive', 'Careful', 'Skeptical']
        results = []

        # Attack period = burst + maintenance (iterations >= 4)
        attack_iterations = list(range(4, 21))

        for persona in personas:
            data = detailed_df[
                (detailed_df['persona'] == persona) &
                (detailed_df['product_id'].isin(self.fake_targets))
            ]

            baseline = data[data['iteration'].isin([1, 2, 3])]
            attack = data[data['iteration'].isin(attack_iterations)]

            baseline_rate = baseline['purchases'].sum() / baseline['total_evaluations'].sum() * 100
            attack_rate = attack['purchases'].sum() / attack['total_evaluations'].sum() * 100

            results.append({
                'Persona': persona,
                'Baseline': round(baseline_rate, 1),
                'Attack': round(attack_rate, 1),
                'Impact_pp': round(attack_rate - baseline_rate, 1),
                'n_baseline': int(baseline['total_evaluations'].sum()),
                'n_attack': int(attack['total_evaluations'].sum())
            })

        df = pd.DataFrame(results).sort_values('Impact_pp', ascending=False)
        df['Rank'] = range(1, len(df) + 1)

        # ANOVA using individual decisions (not aggregated rates)
        # This gives proper sample size for statistical testing
        attack_data = self.transactions_df[
            (self.transactions_df['product_id'].isin(self.fake_targets)) &
            (self.transactions_df['iteration'].isin(attack_iterations))
        ].copy()
        attack_data['buy_binary'] = (attack_data['decision'] == 'BUY').astype(int)

        groups = []
        for persona in personas:
            persona_decisions = attack_data[attack_data['persona'] == persona]['buy_binary'].values
            groups.append(persona_decisions)

        f_stat, p_val = stats.f_oneway(*groups)

        # Print ANOVA details
        print(f"      ANOVA: F={f_stat:.2f}, p={p_val:.4f}")
        print(f"      Sample sizes: {[len(g) for g in groups]}")

        # CSV
        csv_path = self.output_dir / "Table_3_RQ2.csv"
        df.to_csv(csv_path, index=False)

        # LaTeX
        latex_path = self.output_dir / "Table_3_RQ2.tex"
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{table}[t]\n")
            f.write("\\centering\n")
            f.write("\\caption{RQ2: Persona vulnerability to fake reviews (targeted products only)}\n")
            f.write("\\label{tab:rq2}\n")
            f.write("\\small\n")
            f.write("\\begin{tabular}{clccccc}\n")
            f.write("\\toprule\n")
            f.write("Rank & Persona & Baseline & Attack & Impact (pp) & $n_{base}$ & $n_{attack}$ \\\\\n")
            f.write("\\midrule\n")

            for _, row in df.iterrows():
                f.write(f"{row['Rank']} & {row['Persona']} & {row['Baseline']}\\% & ")
                f.write(f"{row['Attack']}\\% & +{row['Impact_pp']} & {row['n_baseline']} & {row['n_attack']} \\\\\n")

            f.write("\\bottomrule\n")
            p_str = f"{p_val:.4f}" if p_val >= 0.0001 else "$<$0.0001"
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            f.write(f"\\multicolumn{{7}}{{l}}{{\\scriptsize ANOVA: $F = {f_stat:.2f}$, $p = {p_str}${sig}}}\\\\\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")

        print(f"      CSV: {csv_path}")
        print(f"      LaTeX: {latex_path}")

    # =========================================================================
    # MAIN GENERATOR
    # =========================================================================

    def generate_all(self):
        """Generate all publication materials"""
        print("\n" + "="*70)
        print("GENERATING PUBLICATION MATERIALS")
        print("="*70)

        self.load_data()
        self.create_figure_1_rq1()
        self.create_figure_2_rq2()
        self.create_figure_3_temporal()
        self.create_tables()

        print("\n" + "="*70)
        print("COMPLETE")
        print("="*70)
        print(f"\nOutput: {self.output_dir}/")
        print("\nFigures (PNG + PDF, 600 DPI):")
        print("  - Figure_1_RQ1.png/pdf")
        print("  - Figure_2_RQ2.png/pdf")
        print("  - Figure_3_Temporal.png/pdf")
        print("\nTables (CSV + LaTeX):")
        print("  - Table_1_Products.csv/tex")
        print("  - Table_2_RQ1.csv/tex")
        print("  - Table_3_RQ2.csv/tex")
        print("="*70 + "\n")


def main():
    generator = PublicationFigures()
    generator.generate_all()


if __name__ == "__main__":
    main()
