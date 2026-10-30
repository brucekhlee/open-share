#!/bin/bash

# Define the root directory path
export DIR_immunogenicity_risk=$PWD

# Create and switch to the test execution directory
mkdir -p ex_pembrolizumab
cd ex_pembrolizumab

# Create FASTA input file containing heavy (Pembrolizumab_Heavy) and light (Pembrolizumab_Light) chains
cat << 'EOF' > pembrolizumab.fa
>Pembrolizumab_Heavy
QVQLVQSGVEVKKPGASVKVSCKASGYTFTNYYMYWVRQAPGQGLEWMGGINPSNGGTNFNEKFKNRVTLTTDSSTTTAYMELKSLQFDDTAVYYCARRDYRFDMGFDYWGQGTTVTVSS
>Pembrolizumab_Light
EIVLTQSPATLSLSPGERATLSCRASKGVSTSGYSYLHWYQQKPGQAPRLLIYLASYLESGVPARFSGSGSGTDFTLTISSLEPEDFAVYYCQHSRDLPLTFGGGTKVEIK
EOF

# 1. Run BioPhi OASis evaluation on control antibodies
biophi oasis pembrolizumab.fa \
  --oasis-db $DIR_immunogenicity_risk/db/OASis_9mers_v1.db \
  --output pembrolizumab_oasis.xlsx

# 2. Parse global humanness metrics across all chains
python $DIR_immunogenicity_risk/app/biophi_humanness.py pembrolizumab_oasis.xlsx | tee pembrolizumab_biophi_humanness.log

# 3. Count non-human 9-mer hotspots across all chains
python $DIR_immunogenicity_risk/app/biophi_counts.py pembrolizumab_oasis.xlsx | tee pembrolizumab_biophi_counts.log

# 4. Query IEDB MHC-II API for T-cell epitope prediction
python $DIR_immunogenicity_risk/app/iedb_mhcii.py pembrolizumab.fa | tee pembrolizumab_iedb_mhcii.log

