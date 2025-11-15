"""
Optional: Install matplotlib for visualizations
pip install matplotlib pandas

This script creates basic visualizations of the synthetic data.
"""

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import argparse
    from pathlib import Path
except ImportError:
    print("Error: This script requires matplotlib and pandas")
    print("Install with: pip install matplotlib pandas")
    exit(1)


def load_data(filepath: str) -> pd.DataFrame:
    """Load CSV data into pandas DataFrame."""
    return pd.read_csv(filepath)


def plot_discount_conversion(df: pd.DataFrame, output_dir: str):
    """Plot conversion rate vs discount percentage."""
    # Create bins
    df['discount_bin'] = pd.cut(df['discount_pct'], 
                                 bins=[0, 10, 20, 30, 40, 50],
                                 labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%'])
    
    # Calculate conversion by bin
    conv_by_discount = df.groupby('discount_bin')['sold'].agg(['mean', 'count'])
    conv_by_discount['mean'] *= 100  # Convert to percentage
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(conv_by_discount)), conv_by_discount['mean'], 
                   color='steelblue', alpha=0.8)
    plt.xlabel('Discount Range', fontsize=12)
    plt.ylabel('Conversion Rate (%)', fontsize=12)
    plt.title('Conversion Rate by Discount Percentage', fontsize=14, fontweight='bold')
    plt.xticks(range(len(conv_by_discount)), conv_by_discount.index)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/discount_conversion.png', dpi=150)
    print(f"✓ Saved: {output_dir}/discount_conversion.png")


def plot_category_performance(df: pd.DataFrame, output_dir: str):
    """Plot conversion and revenue by category."""
    cat_stats = df.groupby('category').agg({
        'sold': ['mean', 'sum'],
        'revenue': 'sum'
    })
    cat_stats.columns = ['conversion', 'sales_count', 'revenue']
    cat_stats['conversion'] *= 100
    cat_stats = cat_stats.sort_values('conversion', ascending=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Conversion rate
    ax1.barh(range(len(cat_stats)), cat_stats['conversion'], color='coral', alpha=0.8)
    ax1.set_yticks(range(len(cat_stats)))
    ax1.set_yticklabels(cat_stats.index)
    ax1.set_xlabel('Conversion Rate (%)', fontsize=11)
    ax1.set_title('Conversion Rate by Category', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(cat_stats['conversion']):
        ax1.text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=9)
    
    # Revenue
    ax2.barh(range(len(cat_stats)), cat_stats['revenue'], color='mediumseagreen', alpha=0.8)
    ax2.set_yticks(range(len(cat_stats)))
    ax2.set_yticklabels(cat_stats.index)
    ax2.set_xlabel('Revenue ($)', fontsize=11)
    ax2.set_title('Revenue by Category', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(cat_stats['revenue']):
        ax2.text(v + 200, i, f'${v:,.0f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/category_performance.png', dpi=150)
    print(f"✓ Saved: {output_dir}/category_performance.png")


def plot_expiry_urgency(df: pd.DataFrame, output_dir: str):
    """Plot conversion by days to expiry."""
    # Create bins
    bins = [0, 3, 7, 14, 30, 999]
    labels = ['1-3 days', '4-7 days', '8-14 days', '15-30 days', '30+ days']
    df['expiry_bin'] = pd.cut(df['days_to_expiry'], bins=bins, labels=labels)
    
    expiry_stats = df.groupby('expiry_bin').agg({
        'sold': 'mean',
        'discount_pct': 'mean'
    })
    expiry_stats['sold'] *= 100
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    x = range(len(expiry_stats))
    ax1.bar(x, expiry_stats['sold'], color='steelblue', alpha=0.7, label='Conversion Rate')
    ax1.set_xlabel('Days to Expiry', fontsize=12)
    ax1.set_ylabel('Conversion Rate (%)', fontsize=12, color='steelblue')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=15)
    ax1.tick_params(axis='y', labelcolor='steelblue')
    ax1.grid(axis='y', alpha=0.3)
    
    # Overlay average discount
    ax2 = ax1.twinx()
    ax2.plot(x, expiry_stats['discount_pct'], 'o-', color='coral', 
             linewidth=2, markersize=8, label='Avg Discount')
    ax2.set_ylabel('Average Discount (%)', fontsize=12, color='coral')
    ax2.tick_params(axis='y', labelcolor='coral')
    
    plt.title('Conversion Rate and Discount by Days to Expiry', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/expiry_urgency.png', dpi=150)
    print(f"✓ Saved: {output_dir}/expiry_urgency.png")


def plot_day_of_week(df: pd.DataFrame, output_dir: str):
    """Plot conversion by day of week."""
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dow_stats = df.groupby('day_of_week')['sold'].mean() * 100
    
    plt.figure(figsize=(10, 6))
    colors = ['lightcoral' if i < 5 else 'lightgreen' for i in range(7)]
    bars = plt.bar(range(7), dow_stats, color=colors, alpha=0.8)
    plt.xlabel('Day of Week', fontsize=12)
    plt.ylabel('Conversion Rate (%)', fontsize=12)
    plt.title('Conversion Rate by Day of Week', fontsize=14, fontweight='bold')
    plt.xticks(range(7), days)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='lightcoral', alpha=0.8, label='Weekday'),
                      Patch(facecolor='lightgreen', alpha=0.8, label='Weekend')]
    plt.legend(handles=legend_elements, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/day_of_week.png', dpi=150)
    print(f"✓ Saved: {output_dir}/day_of_week.png")


def plot_correlation_heatmap(df: pd.DataFrame, output_dir: str):
    """Plot correlation heatmap of numeric features."""
    # Select numeric columns
    numeric_cols = ['base_price', 'discount_pct', 'days_to_expiry', 
                   'inventory_level', 'day_of_week', 'is_weekend',
                   'sold', 'units_sold']
    
    corr_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    plt.imshow(corr_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(label='Correlation Coefficient')
    
    # Add labels
    plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45, ha='right')
    plt.yticks(range(len(numeric_cols)), numeric_cols)
    
    # Add correlation values
    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            text = plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha='center', va='center', 
                          color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black',
                          fontsize=9)
    
    plt.title('Feature Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/correlation_heatmap.png', dpi=150)
    print(f"✓ Saved: {output_dir}/correlation_heatmap.png")


def main():
    parser = argparse.ArgumentParser(
        description="Create visualizations from synthetic purchase data"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input CSV file path"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/visualizations",
        help="Output directory for plots (default: data/visualizations)"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"\nLoading data from {args.input}...")
    df = load_data(args.input)
    print(f"✓ Loaded {len(df):,} records\n")
    
    print("Generating visualizations...")
    plot_discount_conversion(df, args.output_dir)
    plot_category_performance(df, args.output_dir)
    plot_expiry_urgency(df, args.output_dir)
    plot_day_of_week(df, args.output_dir)
    plot_correlation_heatmap(df, args.output_dir)
    
    print(f"\n✓ All visualizations saved to {args.output_dir}/")
    print("\nGenerated plots:")
    print("  1. discount_conversion.png - Conversion rate by discount range")
    print("  2. category_performance.png - Category conversion and revenue")
    print("  3. expiry_urgency.png - Urgency effect by days to expiry")
    print("  4. day_of_week.png - Weekly conversion patterns")
    print("  5. correlation_heatmap.png - Feature correlations")


if __name__ == "__main__":
    main()
