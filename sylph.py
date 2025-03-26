import os

SRA_LIST_FILE = "test_sra.txt"
OUTPUT_DIR = "sra_test_downloads"
LOG_FILE = "processed_sra.log"

#loads the processed SRA in a log file
processed_sra = set()
if os.path.exists(LOG_FILE):
with open(LOG_FILE, "r") as log:
processed_sra.update(log.read().splitlines())

while True:
with open(SRA_LIST_FILE, "r") as file:
for sra_id in file:
sra_id = sra_id.strip()
if sra_id in processed_sra:
continue #skips the SRA IDs that have already been processed

print(f"Processing {sra_id}...")

#creates the directory inside of the loop in order to store all things related to the SRA there
sra_dir = os.path.join(OUTPUT_DIR, sra_id)
os.makedirs(sra_dir, exist_ok=True)

#downloads the SRA
os.system(f"prefetch {sra_id} -O {sra_dir}")

#converts it to a fastqfile
os.system(f"fasterq-dump --split-files --outdir {sra_dir} {os.path.join(sra_dir, sra_id)}")

#defines the path of the fastq file
fastq_1 = f"{sra_dir}/{sra_id}_1.fastq"
fastq_2 = f"{sra_dir}/{sra_id}_2.fastq"

#statments for debugging purposes
if os.path.exists(fastq_1) and os.path.exists(fastq_2):
print(f"FASTQ files generated successfully for {sra_id}.")
else:
print(f"Error: FASTQ files missing for {sra_id}!")
break

#processes ANI with sylph
os.system(f"sylph compare -q {fastq_1} -r reference_genomes/*.fastq > {sra_dir}/{sra_id}_ani.txt")

#log the successful processing of sylph/ANI
with open(LOG_FILE, "a") as log:
log.write(sra_id + "\n")
processed_sra.add(sra_id)

#remove SRA for free data purposes
os.system(f"rm -r {sra_dir}")

print(f"Finished processing {sra_id} and removed directory.")

#checks if all 482 SRA has been processed, if not contine the loop
if len(processed_sra) >= 482:
print("All 482 SRA IDs have been processed. Exiting.")
break

print("Test complete!")