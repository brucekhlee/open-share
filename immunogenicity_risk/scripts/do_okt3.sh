#!/bin/bash

# Define the root directory path
export DIR_immunogenicity_risk=$PWD

# Create and switch to the test execution directory
mkdir -p ex_okt3
cd ex_okt3

# Create FASTA input file containing heavy (okt3_heavy) and light (okt3_light) chains
cat << 'EOF' > okt3.fa
>okt3_heavy
QVQLQQSGAELARPGASVKLSCKASGYTFTRYTMHWVKQRPGQGLEWIGYINPSRGYTNYNQKFKDKATLTDKSSSTAYMQLSSLTSEDSAVYYCARYYDDHYCLDYWGQGTTLTVSS
>okt3_light
DIQMTQTTSSLSASLGDRVTISCRASQDIRNYLNWYQQKPDGTVKLLIYYTSRLHSGVPSRFSGSGSGTDYSLTISNLEQEDIATYFCQQGNTLPWTFGGGTKLEIK
EOF


# 1. Run BioPhi OASis evaluation on control antibodies
biophi oasis okt3.fa \
  --oasis-db $DIR_immunogenicity_risk/db/OASis_9mers_v1.db \
  --output okt3_oasis.xlsx

# 2. Parse global humanness metrics across all chains
python $DIR_immunogenicity_risk/app/biophi_humanness.py okt3_oasis.xlsx | tee okt3_biophi_humanness.log

# 3. Count non-human 9-mer hotspots across all chains
python $DIR_immunogenicity_risk/app/biophi_counts.py okt3_oasis.xlsx | tee okt3_biophi_counts.log

# 4. Query IEDB MHC-II API for T-cell epitope prediction
python $DIR_immunogenicity_risk/app/iedb_mhcii.py okt3.fa | tee okt3_iedb_mhcii.log

