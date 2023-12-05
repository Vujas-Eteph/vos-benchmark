'''
Goal: Automatically ZIP the results for YouTuve VOS 2018/2019 (val/test), LVOS (test) and MOSE (val/test).

Comments: 
- The ZIP format is required by the evaluation servers on CodaLab.
- Server are :
        - YouTubeVOS 2018 : https://codalab.lisn.upsaclay.fr/competitions/7685#learn_the_details
        - YouTubeVOS 2019 : https://codalab.lisn.upsaclay.fr/competitions/6066#learn_the_details
        - LVOS : https://codalab.lisn.upsaclay.fr/competitions/8767#learn_the_details
        - MOSE: https://codalab.lisn.upsaclay.fr/competitions/10703#results

Quick use: python zip_results.py --path [path/to/the/resuls] --num_workers [# of cores to use]

by Stéphane Vujasinovic
'''

### - IMPORTS ---
import os
import zipfile
import tqdm
import multiprocessing
from argparse import ArgumentParser


### - GLOBAL VARIABLES ---
# Define the source folders and target folders
SOURCE_FOLDERS = ["y18-val", "y19-val", "lvos-test", "mose-val"]

SUBFOLDER_TO_ZIP = "Annotations"
TARGET_ZIP_FOLDERS = ["y18_val_submission.zip", "y19_val_submission.zip", "lvos_test_submission.zip", "mose_val_submission.zip"]


### - FUNCTIONS ---
# Create the zip files          
def zip_subfolder(source_folder:str, source_with_subfolder:str, target_zip_folder:str):
    '''
    Create the zip file
    '''
    with zipfile.ZipFile(target_zip_folder, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Iterate through the files and subdirectories in the subfolder
        for root, dirs, files in os.walk(source_with_subfolder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arcname=arcname)
                
                
### - MAIN ---   
def main():    
    # Arguments parsing
    parser = ArgumentParser()
    parser.add_argument(
        '--path',
        type = str,
        required=True,
        help='Path to look into for the YouTube VOS results ti zip.')
    parser.add_argument(
        '--num_workers',
        type = int,
        default = 4,
        help='Assign the numer of workers for zipping the folders.')
    args = parser.parse_args()
    
    # Check if the specified source path exists
    if not os.path.exists(args.path):
        print(f"Error: The specified path '{args.path}' does not exist.")
        return
    
    # Multiprocessing settings
    pool = multiprocessing.Pool(processes=args.num_workers)
    
    # Start the zipping !
    total_iterations = len(SOURCE_FOLDERS)
    with tqdm.tqdm(total=total_iterations, desc="Zipping") as pbar:
        for idx, (src_f, trgt_f) in enumerate(zip(SOURCE_FOLDERS, TARGET_ZIP_FOLDERS)):
            if idx != 3:
                continue
            source_with_subfolder = os.path.join(src_f, SUBFOLDER_TO_ZIP)
            
            # Add args.path to the meta data
            meta_data = list((src_f, source_with_subfolder, trgt_f))
            for idx, elem in enumerate(meta_data):
                meta_data[idx] = os.path.join(args.path, elem) 

            # Create a list of arguments for the zip_subfolder function
            args_list = [(meta_data) for _ in range(args.num_workers)]
            
            # Use the pool of workers to execute the zip_subfolder function in parallel
            pool.starmap(zip_subfolder, args_list)
            
            pbar.update(1)
            
            print(f'Successfully created {trgt_f}.')
    
    print('All folders successfully zipped.')
    

### - RUN SCRIPT ---
if __name__ == "__main__":
    main()
    


