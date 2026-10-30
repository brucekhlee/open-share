import sys
import urllib.parse
import urllib.request
import pandas as pd

io = __import__('io')


def parse_fasta(filepath):
    """
    Parse a FASTA file and return a dictionary of {sequence_name: sequence}.
    """
    sequences = {}
    current_name = None
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    current_name = line[1:]
                    sequences[current_name] = ""
                elif current_name and line:
                    sequences[current_name] += line
    except Exception as e:
        print(f"Error reading FASTA file '{filepath}': {e}")
        sys.exit(1)
    return sequences


def query_iedb_mhcii(sequence_text, allele="HLA-DRB1*01:01", method="recommended"):
    """
    Query IEDB MHC Class II prediction API using Python's urllib
    and print the equivalent curl command.
    """
    url = "https://tools-cluster-interface.iedb.org/tools_api/mhcii/"

    post_data = {
        'method': method,
        'sequence_text': sequence_text,
        'allele': allele
    }

    # Construct and print the equivalent curl command for transparency
    encoded_data = urllib.parse.urlencode(post_data)
    curl_command = f"curl --data \"{encoded_data}\" {url}"
    print("\n--- Equivalent cURL Command ---")
    print(curl_command)
    print("-" * 70)

    data = urllib.parse.urlencode(post_data).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error querying IEDB API: {e}")
        return None


def analyze_fasta_and_predict(fasta_path, allele="HLA-DRB1*01:01", rank_cutoff=2.0):
    """
    Read FASTA file, format sequences, print curl command,
    submit to IEDB MHC-II API, and map seq_num back to FASTA names.
    """
    sequences = parse_fasta(fasta_path)
    seq_name_mapping = {i + 1: name for i, name in enumerate(sequences.keys())}

    print("=" * 70)
    print(f"FASTA File Analyzed: {fasta_path}")
    print(f"Target Allele: {allele}")
    print(f"Rank Cutoff: < {rank_cutoff}% (Strong Binders / Hotspots)")
    print("=" * 70)

    # Reconstruct FASTA format string to submit multiple sequences at once
    fasta_formatted_text = ""
    for name, seq in sequences.items():
        fasta_formatted_text += f">{name}\n{seq}\n"
        print(f"🔹 Loaded Chain: {name} (Length: {len(seq)} aa)")

    print("\nQuerying IEDB MHC-II API...")
    api_output = query_iedb_mhcii(sequence_text=fasta_formatted_text, allele=allele, method="recommended")

    if not api_output:
        print("Failed to get response from IEDB API.")
        return

    # Parse the TSV response from IEDB API using pandas
    try:
        df = pd.read_csv(io.StringIO(api_output), sep='\t')
    except Exception as e:
        print(f"Error parsing API response: {e}")
        print("Raw response preview:")
        print(api_output[:500])
        return

    print("\n" + "=" * 70)
    print("Prediction Results & High-Risk Hotspot Filtering")
    print("=" * 70)

    if 'rank' in df.columns:
        high_risk_df = df[df['rank'] < rank_cutoff]

        print(f"Total peptides evaluated: {len(df)}")
        print(f"Total high-risk hotspots found (Rank < {rank_cutoff}%): {len(high_risk_df)}")

        if len(high_risk_df) > 0:
            print("\nDetailed High-Risk Hotspots:")
            for idx, row in high_risk_df.iterrows():
                numeric_id = row.get('seq_num', 1)
                # Map numeric seq_num back to original FASTA header name
                chain_name = seq_name_mapping.get(numeric_id, f"Chain_{numeric_id}")

                peptide = row.get('peptide', 'N/A')
                core = row.get('core_peptide', 'N/A')
                rank_val = row.get('rank', 'N/A')
                allele_name = row.get('allele', 'N/A')

                print(
                    f"  * [Chain: {chain_name} | Allele: {allele_name}] Peptide: {peptide} (Core: {core}) | Rank: {rank_val}%")
        else:
            print(f"  * No hotspots found below rank {rank_cutoff}%.")
    else:
        print("Warning: 'rank' column not found in IEDB response.")
        print(df.head())

    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_fasta.py <fasta_file_path> [allele] [rank_cutoff]")
        print("Example: python predict_fasta.py okt3.fa HLA-DRB1*01:01 2.0")
        sys.exit(1)

    fasta_file = sys.argv[1]
    target_allele = sys.argv[2] if len(sys.argv) >= 3 else "HLA-DRB1*01:01"
    cutoff_val = float(sys.argv[3]) if len(sys.argv) >= 4 else 2.0

    analyze_fasta_and_predict(fasta_file, allele=target_allele, rank_cutoff=cutoff_val)