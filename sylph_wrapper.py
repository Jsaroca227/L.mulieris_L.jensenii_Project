##this code should contain the running of sylph

import os
import sys
import argparse

#function to parse command line arguments
def check_arg(args=None):
    parser = argparse.ArgumentParser(
    description="ADD TITLE OF SCRIPT HERE (shows on help -h)")

    parser.add_argument("-i", "--sra_file",
    help="input file",
    required=True)

    parser.add_argument("-p", "--path_db",
    help="input of reference genome path",
    required=True)

    parser.add_argument("-t", "--threads",
    help="number of threads to use",
    required=True)

    return parser.parse_args(args)

#retrieve command line arguments
arguments = check_arg(sys.argv[1:])
SRA_LIST_FILE = arguments.sra_file
SYLPH_DB_PATH = arguments.path_db
THREADS = arguments.threads
OUTPUT_DIR = "sra_downloads"
LOG_FILE = "processed_sra.log"

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

flag = False

while True:
    for sra_id_temp in sra_list:
        processing = []
        if os.path.exists("processing.log"):
            with open("processing.log","r") as file:
                processing = file.read()
                processing = processing.splitlines()
        if (sra_id_temp in processed_sra) or (sra_id_temp in processing):
            continue #skips the SRA IDs that have already been processed
        else:
            sra_id = sra_id_temp
        if set(sra_list) == processed_sra:
            flag = True

    if flag:
        break

    print(f"Processing {sra_id}...", flush = True)
    with open("results.tsv","a") as file:
        file.write(sra_id + "\n")
    with open("processing.log",'a') as file:
        file.write(f"{sra_id}\n")

    #creates the directory inside of the loop in order to store all things related to the SRA there
    sra_dir = os.path.join(OUTPUT_DIR, sra_id)
    os.makedirs(sra_dir, exist_ok=True)

    #downloads the SRA
    os.system(f"prefetch {sra_id} -O {sra_dir}")

    print(f"Running fasterq-dump on {sra_id}!", flush = True)
    #converts it to a fastqfile
    os.system(f"fasterq-dump --threads {THREADS} --split-files --outdir {sra_dir} {os.path.join(sra_dir, sra_id)}")
    
    #defines the path of the fastq file
    fastq_1 = f"{sra_dir}/{sra_id}_1.fastq"
    fastq_2 = f"{sra_dir}/{sra_id}_2.fastq"

    #statments for debugging purposes
    if os.path.exists(fastq_1) and os.path.exists(fastq_2):
        print(f"FASTQ files generated successfully for {sra_id}!", flush = True)
    else:
        print(f"Error: FASTQ files missing for {sra_id}, attempting .sralite!", flush = True)
        os.system(f"fasterq-dump --threads {THREADS} --split-files --outdir {sra_dir} {os.path.join(sra_dir, sra_id, sra_id + '.sralite')}")

    if os.path.exists(fastq_1) and os.path.exists(fastq_2):
        print(f"FASTQ files generated successfully for {sra_id}!", flush = True)
    else:
        print(f"Error: FASTQ files missing for {sra_id}!", flush = True)
        break

    #processes ANI with sylph
    os.system(f"sylph sketch -t {THREADS} -c 45 -1 {fastq_1} -2 {fastq_2} -d {sra_dir}")
    os.system(f"sylph profile -u --read-seq-id 99 -t {THREADS} --min-number-kmers 2 >> results.tsv {SYLPH_DB_PATH} {fastq_1}.paired.sylsp")


    #log the successful processing of sylph/ANI
    with open(LOG_FILE, "a") as log:
        log.write(sra_id + "\n")
        processed_sra.add(sra_id)
    
    with open("processing.log", "r") as f:
        lines = f.readlines()
    with open("processing.log", "w") as f:
        for line in lines:
            if line.strip("\n") != sra_id:
                f.write(line)

    #remove SRA for free data purposes
    os.system(f"rm -r {sra_dir}")

    print(f"Finished processing {sra_id} and removed directory.", flush = True)

    #checks if all 482 SRA has been processed, if not contine the loop
    if len(processed_sra) >= SRA_LIST_LENGTH:
        print(f"All {SRA_LIST_LENGTH} SRA IDs have been processed.", flush = True)
        break

print("Test complete!", flush = True)