import os

SRA_LIST_FILE = "/home/2025/sbhagi/L.mulieris_L.jensenii_Project/sb_test"
OUTPUT_DIR = "sra_test_downloads"
LOG_FILE = "processed_sra.log"
SYLPH_DB_PATH = "/home/2025/sbhagi/L.mulieris_L.jensenii_Project/sylph_db/database.syldb" ### CHANGE THIS TO YOUR PATH WHEN RUNNING

#loads the processed SRA in a log file
processed_sra = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as log:
        processed_sra = set(log.read().splitlines())

with open(SRA_LIST_FILE,"r") as file:
    sra_list = file.read()
    sra_list = sra_list.splitlines()

SRA_LIST_LENGTH = len(sra_list)

sra_list_temp = []
for sra in sra_list:
    sra_list_temp.append(sra.strip())

sra_list = sra_list_temp

print(f"SRA List: {sra_list}", flush=True)
print(f"Processed SRA: {processed_sra}", flush=True)

flag = False

while True:
    sra_id = None  # Make sure sra_id is always initialized at the start of the loop
    
    # Read processing.log if it exists
    processing = set()
    if os.path.exists("processing.log"):
        with open("processing.log", "r") as file:
            processing = set(file.read().splitlines())

    # Iterate through the SRA list and find the first unprocessed ID
    for sra_id_temp in sra_list:
        if sra_id_temp not in processed_sra and sra_id_temp not in processing:
            sra_id = sra_id_temp
            break  # Stop at the first unprocessed ID

    if sra_id is None:
        # If no new SRA ID found, exit the loop
        print("All SRA IDs have been processed.", flush=True)
        break

    print(f"Processing {sra_id}...", flush=True)

    # Continue with your existing processing logic
    with open("processing.log", 'a') as file:
        file.write(f"{sra_id}\n")

    # Creating directory for SRA
    sra_dir = os.path.join(OUTPUT_DIR, sra_id)
    os.makedirs(sra_dir, exist_ok=True)

    # Download the SRA
    os.system(f"prefetch {sra_id} -O {sra_dir}")

    # Convert to FASTQ
    print(f"Running fasterq-dump on {sra_id}!", flush=True)
    os.system(f"fasterq-dump --split-files --outdir {sra_dir} {os.path.join(sra_dir, sra_id)}")

    # Fastq file paths
    fastq_1 = f"{sra_dir}/{sra_id}_1.fastq"
    fastq_2 = f"{sra_dir}/{sra_id}_2.fastq"

    # Debugging file existence
    if os.path.exists(fastq_1) and os.path.exists(fastq_2):
        print(f"FASTQ files generated successfully for {sra_id}!", flush=True)
    else:
        print(f"Error: FASTQ files missing for {sra_id}!", flush=True)
        break

    # Run sylph for ANI
    os.system(f"sylph sketch -c 75 -1 {fastq_1} -2 {fastq_2} -d {sra_dir}")
    os.system(f"sylph profile --min-number-kmers 3 >> results.tsv {SYLPH_DB_PATH} {fastq_1 + '.paired.sylsp'}")

    # Log successful processing
    with open(LOG_FILE, "a") as log:
        log.write(sra_id + "\n")
        processed_sra.add(sra_id)
    
    # Remove from processing.log
    with open("processing.log", "r") as f:
        lines = f.readlines()
    with open("processing.log", "w") as f:
        for line in lines:
            if line.strip("\n") != sra_id:
                f.write(line)

    # Clean up (remove SRA files)
    os.system(f"rm -r {sra_dir}")

    print(f"Finished processing {sra_id} and removed directory.", flush=True)

    # If all SRA IDs processed, break
    if len(processed_sra) >= SRA_LIST_LENGTH:
        print(f"All {SRA_LIST_LENGTH} SRA IDs have been processed.", flush=True)
        break

print("Test complete!", flush=True)