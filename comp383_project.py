import os
import pandas as pd

#read in the csv file
df = pd.read_csv("hmgbd_1.csv")

#make a copy of the csv file
df_copy = df.copy()
df_copy.to_csv("hmgbd_1_copy.csv")

#remove all unecessary columns that we will not be utilizing
required_columns = df.columns[:7].tolist() + ["HMgDB_diagnosis", "sex"]
existing_columns = [col for col in required_columns if col in df.columns]
filtered_df = df[existing_columns]
#save the filtered column file to a csv
filtered_df.to_csv("hmgbd_1_filtered.csv", index=False)

#save only the run IDs to a csv in order to download 
sra_run_ids = filtered_df["library_id"]

sra_run_ids.to_csv("sra_run_ids.txt", index=False, header=False)


