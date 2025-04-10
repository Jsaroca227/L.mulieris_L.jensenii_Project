import os
import sys
import argparse

# function to parse command line arguments
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

# retrieve command line arguments
arguments = check_arg(sys.argv[1:])
SRA_LIST_FILE = arguments.sra_file
SYLPH_DB_PATH = arguments.path_db
THREADS = arguments.threads
OUTPUT_DIR = "sra_downloads"
LOG_FILE = "processed_sra.log"

# loads the processed SRAs
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
# Looping through SRAs
while True:
    for sra_id_temp in sra_list:
        processing = []
        # binning SRAs that have already been processed
        if os.path.exists("processing.log"):
            with open("processing.log","r") as file:
                processing = file.read()
                processing = processing.splitlines()
        if (sra_id_temp in processed_sra) or (sra_id_temp in processing):
            continue # skips the SRA IDs that have already been processed
        else:
            sra_id = sra_id_temp
        if set(sra_list) == processed_sra:
            flag = True
    # if all SRAs have been processed break the loop
    if flag:
        break

    print(f"Processing {sra_id}...", flush = True)
    # begin processing SRA, write SRA to log files
    with open("results.tsv","a") as file:
        file.write(sra_id + "\n")
    with open("processing.log",'a') as file:
        file.write(f"{sra_id}\n")

    # creates the directory inside of the loop in order to store all things related to the SRA there
    sra_dir = os.path.join(OUTPUT_DIR, sra_id)
    os.makedirs(sra_dir, exist_ok=True)

    # downloads the SRA
    os.system(f"prefetch {sra_id} -O {sra_dir}")

    # run fasterq-dump
    print(f"Running fasterq-dump on {sra_id}!", flush = True)
    if os.path.exists(os.path.join(sra_dir, sra_id)):
        os.system(f"fasterq-dump --threads {THREADS} --split-files --outdir {sra_dir} {os.path.join(sra_dir, sra_id)}")
    elif os.path.exists(os.path.join(sra_dir, sra_id, sra_id + '.sralite')):
        os.system(f"fasterq-dump --threads {THREADS} --split-files --outdir {sra_dir} {os.path.join(sra_dir, sra_id, sra_id + '.sralite')}")
    else:
        print(f"SRA failed to download.")
        break
    
    # define path of the fastq files
    fastq_1 = f"{sra_dir}/{sra_id}_1.fastq"
    fastq_2 = f"{sra_dir}/{sra_id}_2.fastq"

    single_fastq = f"{sra_dir}/{sra_id}.fastq"

    # statments for debugging purposes, now supports sralite files
    if os.path.exists(fastq_1) and os.path.exists(fastq_2):
        print(f"Paired end FASTQ files generated successfully for {sra_id}!", flush = True)
        # process fastq with sylph
        os.system(f"sylph sketch -t {THREADS} -c 45 -1 {fastq_1} -2 {fastq_2} -d {sra_dir}")
        os.system(f"sylph profile -u --read-seq-id 99 -t {THREADS} --min-number-kmers 2 >> results.tsv {SYLPH_DB_PATH} {fastq_1}.paired.sylsp")
    elif os.path.exists(single_fastq):
        print(f"Single end FASTQ files generated successfully for {sra_id}!", flush = True)
        # process fastq with sylph
        os.system(f"sylph sketch -t {THREADS} -c 45 {single_fastq} -d {sra_dir}")
        os.system(f"sylph profile -u --read-seq-id 99 -t {THREADS} --min-number-kmers 2 >> results.tsv {SYLPH_DB_PATH} {single_fastq}.sylsp")
    else:
        print(f"FASTQ files not successfully generated for {sra_id}")
        break

    # log sylph results
    with open(LOG_FILE, "a") as log:
        log.write(sra_id + "\n")
        processed_sra.add(sra_id)
    
    with open("processing.log", "r") as f:
        lines = f.readlines()
    with open("processing.log", "w") as f:
        for line in lines:
            if line.strip("\n") != sra_id:
                f.write(line)

    # remove SRA for free data purposes
    os.system(f"rm -r {sra_dir}")

    print(f"Finished processing {sra_id} and removed directory.\n", flush = True)

    # checks if all SRAs have been processed
    if len(processed_sra) >= SRA_LIST_LENGTH:
        print(f"All {SRA_LIST_LENGTH} SRA IDs have been processed.", flush = True)
        break

print("Test complete!", flush = True)