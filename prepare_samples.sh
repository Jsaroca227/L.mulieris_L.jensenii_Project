echo "Downloading SRA ids and sketching."

SRA_LIST=${1:-/home/2025/sbhagi/L.mulieris_L.jensenii_Project/final_sra_set/shreya.txt} #change file path to ur file path

 #loops thorugh each SRA ID in the input file; the -r is to prevent backlash escapes from being interpreted
while read -r SRA_ID; do
   SAMPLE_DIR="/home/2025/sbhagi/L.mulieris_L.jensenii_Project/sra_downloads/$SRA_ID"
     # this create a file for the SRA sample's file will be stored/sketched
   mkdir -p "$SAMPLE_DIR"
     # this creates a directory for the sample

#this checks if the download of the paired FASTQ files exsist
   if [[ -f "$SAMPLE_DIR/${SRA_ID}_1.fastq" && -f "$SAMPLE_DIR/${SRA_ID}_2.fastq" ]]; then 
       echo "FASTQs already exist for $SRA_ID" #if it already exists then it prints out that it already exists
   else #if it doesn't exist then this runs
       echo "Downloading $SRA_ID..." # this is to just to update what is happening
       fasterq-dump --split-files --outdir "$SAMPLE_DIR" --threads 4 "$SRA_ID" #this separates paired-end reads in _1.fastq and _2.fastq files and then saved in the directory created above
   fi #closes the if-else loop

#this is just if the .sylsp sketch file already exists, then this is prints out that it exists
   if [[ -f "$SAMPLE_DIR/${SRA_ID}_1.fastq.paired.sylsp" ]]; then
       echo "Sketch already exists for $SRA_ID" 
   else #if it doesn't already exists, then this runs creating it
       echo "Sketching $SRA_ID..." #this is again just so we are aware what is happening
       sylph sketch #this runs the sylph sketch on paired-end files
           -1 "$SAMPLE_DIR/${SRA_ID}_1.fastq" \
           -2 "$SAMPLE_DIR/${SRA_ID}_2.fastq" \
           -d "$SAMPLE_DIR" # it takes into both the fastq files made and the -d sets the output direcotry for not the .sylsp (the slyph sketch file) for the file we made earlier
   fi #closes the if-else loop