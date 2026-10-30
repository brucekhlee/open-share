#!/bin/bash

# Define the root directory path
export DIR_immunogenicity_risk=$PWD

# Create and switch to the test execution directory
mkdir -p ex_trastuzumab
cd ex_trastuzumab

# Create FASTA input file containing heavy (Trastuzumab_Heavy) and light (Trastuzumab_Light) chains
cat << 'EOF' > trastuzumab.fa
>Trastuzumab_Heavy
EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS
>Trastuzumab_Light
DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK
EOF

# 1. Run BioPhi OASis evaluation on control antibodies
biophi oasis trastuzumab.fa \
  --oasis-db $DIR_immunogenicity_risk/db/OASis_9mers_v1.db \
  --output trastuzumab_oasis.xlsx

# 2. Parse global humanness metrics across all chains
python $DIR_immunogenicity_risk/app/biophi_humanness.py trastuzumab_oasis.xlsx | tee trastuzumab_biophi_humanness.log

# 3. Count non-human 9-mer hotspots across all chains
python $DIR_immunogenicity_risk/app/biophi_counts.py trastuzumab_oasis.xlsx | tee trastuzumab_biophi_counts.log

# 4. Query IEDB MHC-II API for T-cell epitope prediction
python $DIR_immunogenicity_risk/app/iedb_mhcii.py trastuzumab.fa | tee trastuzumab_iedb_mhcii.log

