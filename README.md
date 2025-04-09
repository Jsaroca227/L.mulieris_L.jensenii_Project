**Are _Lactobacillus mulieris_ and _Lactobacillus jensenii_ present in the gastrointestinal (GI) tract?**

**Introduction:**

Both _L.mulleris_ and _L.jensenii_ are dominant members of the female urogenital microbiome. _L.mulleris_ is a recently recognized species, however, they share identical 16S rRNA sequences. This project aims to assess whether these species are also present in the gastrointestinal tract. The interest of these species in the GI tract is important as _L.jensenii_ helps the body digest food and absorb nutrients. 

**Dependencies:**
- argparse
- sys
- os
- NCBI Datasets
- Sylph

**Getting Started:**

1. Clone the dictionary using git clone

```
git clone https://github.com/Jsaroca227/L.mulieris_L.jensenii_Project.git
```

2. Download conda, if not installed already using wget

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```
   
3. Download Sylph, if not installed already using conda

```
conda install -c conda-forge -c bioconda sylph
```

Sylph Toolkit: https://sylph-docs.github.io/sylph-cookbook/
- For more information on Sylph


**NCBI links to Reference Genomes:**

NCBI link for _L.jensenii_: https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_001936235.1/

NCBI link for _L. mulieris_: https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_042997415.1/

  Instructions to download the reference genome:
  1. Copy and paste the command from the "Dataset" tab of the NCBI link
  2. Unzip the dataset: unzip.ncbi_dataset
  3. Create directories to differentiate databases; e.g.
     - "Jensenii_db"
     - "Mulieris_db"

**Code and Test Data:**
- Test data can be found in  L.mulieris_L.jensenii_Project/sample_dataset.txt
- code can be found at L.mulieris_L.jensenii_Project/sylph_sb.py

**Overwiew of Wrapper:**

- Arguments: 2 command line arguments needed, -i accept file list and -p reference genome database path

- Initialization: checks for processed SRAs and reads the list of SRA IDs from input file

- Iterates through SRA IDs for processing: skips already processed SRAs, creates a new directory for each SRA

- Download and convert SRA to FASTQ: utilize prefetch to download the SRA file and using fasterq-dump to convert the SRA file to FASTQ format

- Sylph and ANI Profiling: uses sylph sketch to generate sketches from the FASTQ files and runs sylph query to compare sketch against the reference database
Output of ANI score to results.tsv

- Log Processing: updates processed_sra.log with completed SRA ID and removes SRA directory to free up space

- Repetition: continue processing until all SRA IDs in the list are completed 

 <img width="664" alt="Screenshot 2025-04-06 at 4 52 47 PM" src="https://github.com/user-attachments/assets/606f1057-6a8b-425f-9177-0e399687685a" />


**Overview of Output Files:**
1. **Processed_sra.log**: lists the SRA ID that has been processed and completed from the file
2. **Proccesing.log**: lists the SRA ID that is currently being processed in real time
3. **Result.tsv**: lists the SRA ID with the corresponding Sylph, ANI results

