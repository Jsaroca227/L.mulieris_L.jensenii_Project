import os

SRA_LIST_FILE = "test_sra.txt"
OUTPUT_DIR = "sra_test_downloads"
LOG_FILE = "processed_sra.log"
REFERENCE_GENOMES = ["L_mulieris.fasta", "L_jensenii.fasta"]  

# loads the processed SRAs
processed_sra = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as log:
        processed_sra.update(log.read().splitlines())

with open(SRA_LIST_FILE, "r") as file:
    for sra_id in file:
        sra_id = sra_id.strip()
        if sra_id in processed_sra:
            continue  # makes sure to check if it has been processed, if process then skips

        print(f"\nprocessing {sra_id}...")

        # creates directory for the current running SRA
        sra_dir = os.path.join(OUTPUT_DIR, sra_id)
        os.makedirs(sra_dir, exist_ok=True)

        # downloads SRA data
        print("downloading...")
        os.system(f"prefetch {sra_id} -O {sra_dir}")
        
        # converts to a FASTQ file
        print("converting to FASTQ...")
        os.system(f"fasterq-dump --split-files --outdir {sra_dir} {os.path.join(sra_dir, sra_id)}")

        # checks the FASTQ file
        fastq_1 = f"{sra_dir}/{sra_id}_1.fastq"
        fastq_2 = f"{sra_dir}/{sra_id}_2.fastq"
        if not (os.path.exists(fastq_1) and os.path.exists(fastq_2)):
            print(f"errror: FASTQ files missing for {sra_id}!")
            continue

        # runs sylph for each reference genome
        print("running sylph analysis...")
        for ref in REFERENCE_GENOMES:
            ref_path = f"reference_genomes/{ref}"
            if not os.path.exists(ref_path):
                print(f"Warning: Missing {ref} reference genome!")
                continue
            
            # creates an output folder for current analysis
            output_dir = f"{sra_dir}/sylph_{ref.split('.')[0]}"
            os.makedirs(output_dir, exist_ok=True)

            # runs sylph 
            cmd = f"sylph analyze -1 {fastq_1} -2 {fastq_2} -r {ref_path} -o {output_dir} --ani -t 2"
            os.system(cmd)

        # logs results
        with open(LOG_FILE, "a") as log:
            log.write(sra_id + "\n")
        
        # removes the sra just processed
        print("removing ...")
        os.system(f"rm -r {sra_dir}")
        
        # checks if all are processed
        if len(processed_sra) + 1 >= 482:  # +1 for current SRA
            print("\nall 482 SRA IDs processed!")
            break

print("\nsylph ran successfully!")