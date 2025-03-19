
import os
import subprocess

SRA_LIST_FILE = "test_sra.txt"
OUTPUT_DIR = "sra_test_downloads"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(SRA_LIST_FILE, "r") as file:
    for i, sra_id in enumerate(file):
        if i >= 2:  # Limit to first two SRAs
            break
        sra_id = sra_id.strip()
        print(f"Processing {sra_id}...")

        # Download SRA
        subprocess.run(["prefetch", sra_id, "-O", OUTPUT_DIR])

        # Convert to FASTQ
        subprocess.run(["fasterq-dump", "--split-files", "--outdir", OUTPUT_DIR, os.path.join(OUTPUT_DIR, sra_id)])

     
        fastq_1 = f"{OUTPUT_DIR}/{sra_id}_1.fastq"
        fastq_2 = f"{OUTPUT_DIR}/{sra_id}_2.fastq"
        if os.path.exists(fastq_1) and os.path.exists(fastq_2):
            print(f"FASTQ files generated successfully for {sra_id}.")
        else:
            print(f"Error: FASTQ files missing for {sra_id}!")
            break  
       
        os.remove(fastq_1)
        os.remove(fastq_2)

        print(f"Finished processing {sra_id}.")

print("Test complete!")
