import os

SRA_LIST_FILE = "test_sra.txt"
OUTPUT_DIR = "sra_test_downloads"

os.system(f"rm -r {OUTPUT_DIR}")

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(SRA_LIST_FILE, "r") as file:
    for i, sra_id in enumerate(file):
        if i >= 5:
            break
        sra_id = sra_id.strip()
        print(f"Processing {sra_id}...")

        #downloads the SRA
        os.system(f"prefetch {sra_id} -O {OUTPUT_DIR}")

        #convert it to a fastq file
        os.system(f"fasterq-dump --split-files --outdir {OUTPUT_DIR} {os.path.join(OUTPUT_DIR, sra_id)}")
     
        #file paths for the paired end fastq output files
        fastq_1 = f"{OUTPUT_DIR}/{sra_id}_1.fastq"
        fastq_2 = f"{OUTPUT_DIR}/{sra_id}_2.fastq"

        #statements for debugging purposes
        if os.path.exists(fastq_1) and os.path.exists(fastq_2):
            print(f"FASTQ files generated successfully for {sra_id}.")
        else:
            print(f"Error: FASTQ files missing for {sra_id}!")
            break  
        
        #removes the fastq files
        #os.system(f'rm {fastq_1}')

        #os.system(f'rm {fastq_2}')

        #statements for debugging
        print(f"Finished processing {sra_id}.")

print("Test complete!")

### TEST COMMENT 1