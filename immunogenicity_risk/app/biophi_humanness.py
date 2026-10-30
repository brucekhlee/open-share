import sys
import pandas as pd


def calculate_humanness_scores(excel_path):
    """
    Read antibody peptide data from all worksheets in the specified Excel file
    and calculate multi-dimensional Humanness Scores based on OAS 9-mer frequencies.
    """
    try:
        xls = pd.ExcelFile(excel_path)
        sheet_names = xls.sheet_names
    except Exception as e:
        print(f"Error reading Excel file '{excel_path}': {e}")
        sys.exit(1)

    print("=" * 65)
    print(f"File Analyzed: {excel_path}")
    print("Antibody Humanness Score Summary")
    print("=" * 65)

    for sheet_name in sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
        except Exception as e:
            print(f"\n🔹 Chain / Sheet: {sheet_name} (Error reading worksheet: {e})")
            continue

        # Check required columns
        if 'Peptide Fraction OAS Subjects' not in df.columns:
            print(f"\n🔹 Chain / Sheet: {sheet_name} (Skipped: missing required columns)")
            continue

        # Drop missing values
        valid_df = df.dropna(subset=['Peptide Fraction OAS Subjects'])
        total_kmers = len(valid_df)

        if total_kmers == 0:
            print(f"\n🔹 Chain / Sheet: {sheet_name}: No valid 9-mer data found.")
            continue

        # Metric A: Mean 9-mer OAS peptide fraction
        mean_fraction = valid_df['Peptide Fraction OAS Subjects'].mean()

        # Metric B: Human-like 9-mer ratio (frequency >= 1%)
        human_like_count = (valid_df['Peptide Fraction OAS Subjects'] >= 0.01).sum()
        human_like_ratio = human_like_count / total_kmers

        # Metric C: Non-human / Low-frequency 9-mer count (frequency < 1%)
        non_human_count = (valid_df['Peptide Fraction OAS Subjects'] < 0.01).sum()

        print(f"\n🔹 Chain / Sheet: {sheet_name}")
        print(f"  - Total valid 9-mers: {total_kmers}")
        print(f"  - Mean OAS Peptide Fraction Score: {mean_fraction:.4f} ({mean_fraction * 100:.2f}%)")
        print(
            f"  - Human-like 9-mer Ratio (>= 1% frequency): {human_like_ratio:.4f} ({human_like_count}/{total_kmers})")
        print(f"  - Non-human 9-mer Count (< 1% frequency): {non_human_count}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python calculate_humanness.py <excel_file_path>")
        print("Example: python calculate_humanness.py oasis_okt3.xlsx")
        sys.exit(1)

    excel_file = sys.argv[1]
    calculate_humanness_scores(excel_file)
