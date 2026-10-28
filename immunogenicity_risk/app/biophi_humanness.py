import sys
import pandas as pd


def calculate_humanness_scores(excel_path):
    """
    Read antibody peptide data from the specified Excel file
    and calculate multi-dimensional Humanness Scores based on OAS 9-mer frequencies.
    """
    try:
        # Load heavy and light chain worksheets
        heavy_df = pd.read_excel(excel_path, sheet_name='okt3_heavy')
        light_df = pd.read_excel(excel_path, sheet_name='okt3_light')
    except Exception as e:
        print(f"Error reading Excel file '{excel_path}': {e}")
        sys.exit(1)

    chains = {"Heavy Chain": heavy_df, "Light Chain": light_df}

    print("=" * 65)
    print(f"File Analyzed: {excel_path}")
    print("Antibody Humanness Score Summary")
    print("=" * 65)

    for chain_name, df in chains.items():
        # Drop missing values
        valid_df = df.dropna(subset=['Peptide Fraction OAS Subjects'])
        total_kmers = len(valid_df)

        if total_kmers == 0:
            print(f"\n🔹 {chain_name}: No valid 9-mer data found.")
            continue

        # Metric A: Mean 9-mer OAS peptide fraction
        mean_fraction = valid_df['Peptide Fraction OAS Subjects'].mean()

        # Metric B: Human-like 9-mer ratio (frequency >= 1%)
        human_like_count = (valid_df['Peptide Fraction OAS Subjects'] >= 0.01).sum()
        human_like_ratio = human_like_count / total_kmers

        # Metric C: Non-human / Low-frequency 9-mer count (frequency < 1%)
        non_human_count = (valid_df['Peptide Fraction OAS Subjects'] < 0.01).sum()

        print(f"\n🔹 {chain_name}:")
        print(f"  - Total valid 9-mers: {total_kmers}")
        print(f"  - Mean OAS Peptide Fraction Score: {mean_fraction:.4f} ({mean_fraction * 100:.2f}%)")
        print(
            f"  - Human-like 9-mer Ratio (>= 1% frequency): {human_like_ratio:.4f} ({human_like_count}/{total_kmers})")
        print(f"  - Non-human 9-mer Count (< 1% frequency): {non_human_count}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python calculate_humanness.py <excel_file_path>")
        print("Example: python calculate_humanness.py oasis_okt3.xlsx")
        sys.exit(1)

    excel_file = sys.argv[1]
    calculate_humanness_scores(excel_file)
