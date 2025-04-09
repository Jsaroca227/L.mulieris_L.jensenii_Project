import os
import sys
from datetime import datetime
import argparse

SRA_LIST_FILE = "/home/2025/sbhagi/L.mulieris_L.jensenii_Project/sb_test"
OUTPUT_DIR = "/home/2025/sbhagi/L.mulieris_L.jensenii_Project/sra_downloads"
SYLPH_DB = "/home/2025/sbhagi/L.mulieris_L.jensenii_Project/sylph_db/database.syldb"
RESULTS_FILE = "/home/2025/sbhagi/L.mulieris_L.jensenii_Project/results_sb.tsv"
ANI_DISPLAY_FILE = "ani_scores.txt"
LOG_FILE = "processing_log.txt"
THREADS = 4
MIN_KMERS = 10  
MIN_ANI = 90    

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")

def verify_tools():
    log_message("Verifying required tools...")
    for cmd in ['prefetch', 'fasterq-dump', 'sylph']:
        if os.system(f"which {cmd} >/dev/null") != 0:
            raise RuntimeError(f"Required tool not found: {cmd}")
    log_message("All required tools are available")

def get_sra_path(sra_dir, sra_id):
    possible_paths = [
        os.path.join(sra_dir, f"{sra_id}.sra"),
        os.path.join(sra_dir, sra_id, f"{sra_id}.sra")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"No SRA file found for {sra_id}")

def extract_ani(results_line):
    parts = results_line.strip().split('\t')
    if len(parts) >= 5:
        return parts[4]  # Adjusted_ANI
    return "N/A"

def run_sylph_analysis(sra_id, fastq_1, fastq_2, output_dir):
    # Sketching
    sketch_cmd = f"sylph sketch -k 21 -c 100 -1 {fastq_1} -2 {fastq_2} -d {output_dir}"
    if os.system(sketch_cmd) != 0:
        raise RuntimeError("Sketching failed")
    
    # Profiling with ANI capture and confidence 0.7
    sketch_file = f"{fastq_1}.paired.sylsp"
    temp_results = f"{output_dir}/temp_results.tsv"
    
    # Run profiling with confidence interval of 0.7
    profile_cmd = f"sylph profile --min-number-kmers 1 --confidence 0.7 {SYLPH_DB} {sketch_file} > {temp_results}"
    if os.system(profile_cmd) != 0:
        raise RuntimeError("Profiling failed")
    
    # Process and display results
    if os.path.exists(temp_results):
        with open(temp_results, 'r') as f:
            results = f.read().strip()
        
        if results and not results.startswith("Sample_file"):
            # Write to main results file
            with open(RESULTS_FILE, 'a') as out:
                out.write(f"{sra_id}\t{results}\n")
            
            # Extract and display ANI
            ani_score = extract_ani(results)
            print(f"\n=== ANI RESULT ===\nSample: {sra_id}\nANI: {ani_score}\nConfidence: 0.7\n", flush=True)
            
            # Store ANI score and confidence interval separately
            with open(ANI_DISPLAY_FILE, 'a') as ani_out:
                ani_out.write(f"{sra_id}\t{ani_score}\tConfidence_Interval_0.7\n")
            
            return True
    
    raise RuntimeError("No valid results produced")

def process_sra(sra_id):
    """Process a single SRA accession"""
    log_message(f"\n{'#'*80}")
    log_message(f"STARTING PROCESSING FOR: {sra_id}")
    log_message(f"{'#'*80}")
    
    sra_dir = os.path.join(OUTPUT_DIR, sra_id)
    os.makedirs(sra_dir, exist_ok=True)
    
    try:
        # 1. Download
        log_message("Downloading SRA file...")
        if os.system(f"prefetch {sra_id} -O {sra_dir} >/dev/null 2>&1") != 0:
            raise RuntimeError("Download failed")
        log_message("Download completed successfully")
        
        # 2. Convert to FASTQ
        log_message("Converting to FASTQ format...")
        sra_path = get_sra_path(sra_dir, sra_id)
        if os.system(f"fasterq-dump --split-files --outdir {sra_dir} {sra_path} >/dev/null 2>&1") != 0:
            raise RuntimeError("FASTQ conversion failed")
        log_message("FASTQ conversion completed successfully")
        
        # 3. Verify FASTQs
        fastq_1 = f"{sra_dir}/{sra_id}_1.fastq"
        fastq_2 = f"{sra_dir}/{sra_id}_2.fastq"
        if not (os.path.exists(fastq_1) and os.path.exists(fastq_2)):
            raise RuntimeError("Missing FASTQ files")
        log_message(f"Found FASTQ files:\n- {fastq_1}\n- {fastq_2}")

        # 4. Run analysis
        log_message("Starting sylph analysis...")
        if not run_sylph_analysis(sra_id, fastq_1, fastq_2, sra_dir):
            raise RuntimeError("Analysis produced no results")
            
        return True
        
    except Exception as e:
        log_message(f"ERROR PROCESSING {sra_id}: {str(e)}")
        return False
        
    finally:
        # Cleanup
        if os.path.exists(sra_dir):
            os.system(f"rm -rf {sra_dir}")
            log_message(f"Cleaned up temporary directory: {sra_dir}")
        log_message(f"{'#'*80}\n")

def parse_args():
    parser = argparse.ArgumentParser(description="SRA Processing Script")
    parser.add_argument("--sra_list", default=SRA_LIST_FILE, help="Path to SRA list file")
    parser.add_argument("--output_dir", default=OUTPUT_DIR, help="Directory for output files")
    parser.add_argument("--threads", type=int, default=THREADS, help="Number of threads for parallel processing")
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_args()

    # Initialize log file
    with open(LOG_FILE, 'w') as f:
        f.write(f"SRA Processing Log - Started at {datetime.now()}\n\n")
    
    try:
        verify_tools()
        
        # Initialize output files
        with open(RESULTS_FILE, "w") as f:
            f.write("\t".join([
                "Sample", "Genome", "Taxonomic_abundance", "Sequence_abundance",
                "Adjusted_ANI", "Eff_cov", "ANI_5-95_percentile", "Eff_lambda",
                "Lambda_5-95_percentile", "Median_cov", "Mean_cov_geq1",
                "Containment_ind", "Naive_ANI", "kmers_reassigned", "Contig_name"
            ]) + "\n")
        
        with open(ANI_DISPLAY_FILE, "w") as f:
            f.write("Sample\tANI_Score\n")
        
        # Process samples
        with open(args.sra_list) as f:
            sra_ids = [line.strip() for line in f if line.strip()]
        
        log_message(f"\nStarting processing of {len(sra_ids)} samples...")
        log_message(f"Using {args.threads} threads, min-kmers: {MIN_KMERS}, min-ANI: {MIN_ANI}")
        
        success_count = 0
        for sra_id in sra_ids:
            if process_sra(sra_id):
                success_count += 1
            else:
                log_message(f"WARNING: Failed to process {sra_id}, continuing with next sample")

        # Display final ANI results
        log_message("\n" + "="*80)
        log_message("FINAL PROCESSING SUMMARY")
        log_message("="*80)
        log_message(f"Successfully processed: {success_count}/{len(sra_ids)} samples")
        log_message("\nANI RESULTS SUMMARY:")
        log_message(f"{'Sample ID':<20} {'ANI Score':<15}")
        log_message("-"*35)
        with open(ANI_DISPLAY_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                sra_id, ani = line.strip().split('\t')
                log_message(f"{sra_id:<20} {ani:<15}")
        
        log_message("\nProcessing complete!")
        log_message(f"Full results saved to: {RESULTS_FILE}")
        log_message(f"ANI scores saved to: {ANI_DISPLAY_FILE}")
        log_message(f"Complete log saved to: {LOG_FILE}")
        
    except Exception as e:
        log_message(f"FATAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
