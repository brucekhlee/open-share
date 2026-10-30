import sys
import pandas as pd


def count_non_human_peptides(excel_path, threshold=0.01):
    """
    Read antibody peptide data from all worksheets in the specified Excel file,
    and calculate/sum the number of non-human 9-mer peptide segments
    whose OAS occurrence frequency is below the specified threshold.
    """
    try:
        xls = pd.ExcelFile(excel_path)
        sheet_names = xls.sheet_names
    except Exception as e:
        print(f"Error reading Excel file '{excel_path}': {e}")
        sys.exit(1)

    print("=" * 65)
    print(f"File Analyzed: {excel_path}")
    print(f"Antibody Immunogenicity Hotspots (Non-human / Low-frequency Peptides)")
    print(f"OAS Frequency Threshold: < {threshold * 100}% (including zero-hit segments)")
    print("=" * 65)

    for sheet_name in sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet_name)
        except Exception as e:
            print(f"Error reading worksheet '{sheet_name}': {e}")
            continue

        # Check required columns
        if 'Peptide Seq' not in df.columns or 'Peptide Fraction OAS Subjects' not in df.columns:
            print(f"\n🔹 Chain / Sheet: {sheet_name} (Skipped: missing required columns)")
            continue

        # Drop missing values
        valid_df = df.dropna(subset=['Peptide Seq', 'Peptide Fraction OAS Subjects'])
        total_kmers = len(valid_df)

        # Condition 1: Segments with 0 frequency (completely absent in OAS database)
        zero_hits = (valid_df['Peptide Fraction OAS Subjects'] == 0).sum()

        # Condition 2: Segments with frequency below the threshold (e.g., < 1%)
        low_freq = (valid_df['Peptide Fraction OAS Subjects'] < threshold).sum()

        print(f"\n🔹 Chain / Sheet: {sheet_name}")
        print(f"  - Total valid 9-mers: {total_kmers}")
        print(f"  - Segments with 0 OAS occurrence frequency: {zero_hits}")
        print(f"  - Total segments with frequency < {threshold * 100}% (Non-human count): {low_freq}")

        # List a few high-risk hotspot examples (frequency = 0) with their region and Kabat positions
        risk_peptides = valid_df[valid_df['Peptide Fraction OAS Subjects'] == 0]
        if not risk_peptides.empty:
            print(f"  - High-risk hotspot examples (Top 3):")
            for idx, row in risk_peptides.head(3).iterrows():
                kabat = row.get('Kabat', 'N/A')
                region = row.get('Region', 'N/A')
                print(f"    * [Kabat: {kabat}, Region: {region}] Sequence: {row['Peptide Seq']}")
        else:
            print(f"  - High-risk hotspot examples: None (0 zero-hit segments found)")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <excel_file_path> [threshold]")
        print("Example: python script_name.py oasis_controls.xlsx 0.01")
        sys.exit(1)

    excel_file = sys.argv[1]
    threshold_val = float(sys.argv[2]) if len(sys.argv) >= 3 else 0.01

    count_non_human_peptides(excel_file, threshold=threshold_val)
