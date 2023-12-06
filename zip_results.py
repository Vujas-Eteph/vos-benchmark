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

TODO:
- [x] Add suffix or prefix to the outputs name to now which method produced it.
- [x] Exclude some type of files name, based on a list in the config.yaml file. (i.e., *.csv files) 
- [ ] Move the CONSTANTS to a config file.
'''

### - IMPORTS ---
import os
import zipfile
import tqdm
import multiprocessing
from argparse import ArgumentParser
from typing import List


### - FUNCTIONS ---
def is_extension_ignored(extension:str, ignored_extensions:List[str]) -> bool:
    '''
    Check if a given file extension is in the list of extensions to be ignored.
    '''
    return extension in ignored_extensions
    

def zip_subfolder(source_folder:str, source_with_subfolder:str, target_zip_folder:str, ignored_extensions:List[str]):
    '''
    Handles the zipping of a given subfolder.
    '''
    with zipfile.ZipFile(target_zip_folder, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Iterate through the files and subdirectories in the subfolder
        for root, dirs, files in os.walk(source_with_subfolder):
            for file in files:
                file_path = os.path.join(root, file)              
                
                if is_extension_ignored(file_path.split('.')[-1], ignored_extensions):
                    continue
                
                arcname = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arcname=arcname)
                

def add_suffix(list_of_strg:List[str], suffix:str) -> List[str]:
    '''
    Adds a suffix to each string in a list.
    '''
    return [f'{elem}{suffix}' for elem in list_of_strg]


### - MAIN ---   
def main():    
    # Arguments parsing
    parser = ArgumentParser()
    parser.add_argument(
        '--path',
        type = str,
        required=True,
        help='Results to be ZIPed.')
    parser.add_argument(
        '--num_workers',
        type = int,
        default = 4,
        help='Assign number of workers')
    parser.add_argument(
        '--suffix',
        type = str,
        default = '',
        help='Add a sufix at the end of the ZIP file.')
    args = parser.parse_args()
    
    ### - LOCAL NON-VARIABLES/PSEUDO-VARIABLES ---
    # Define the source folders and target folders ...
    SOURCE_FOLDERS = ["y18-val", "y19-val", "lvos-test", "mose-val"]
    SUBFOLDER_TO_ZIP = ["Annotations","Annotations","Annotations",""]
    TARGET_ZIP_FOLDERS = ["y18_val_submission", "y19_val_submission", "lvos_test_submission", "mose_val_submission"]
    FILES_TYPES_TO_IGNORE = ['csv']
    FILES_TYPES_TO_IGNORE = FILES_TYPES_TO_IGNORE or None
    
    # Check if the specified source path exists
    if not os.path.exists(args.path):
        print(f"Error: The specified path '{args.path}' does not exist.")
        return
    
    # Multiprocessing settings
    pool = multiprocessing.Pool(processes=args.num_workers)
    
    # Add the suffixes
    if '' != args.suffix:
        TARGET_ZIP_FOLDERS = add_suffix(TARGET_ZIP_FOLDERS, f'_{args.suffix}')
    TARGET_ZIP_FOLDERS = add_suffix(TARGET_ZIP_FOLDERS, '.zip')
    
    # Start the zipping !
    total_iterations = len(SOURCE_FOLDERS)
    with tqdm.tqdm(total=total_iterations, desc="Zipping") as pbar:
        for idx, (src_f, sub_f, trgt_f) in enumerate(zip(SOURCE_FOLDERS, SUBFOLDER_TO_ZIP, TARGET_ZIP_FOLDERS)):
            source_with_subfolder = os.path.join(src_f, sub_f)
            
            # Add args.path to the meta data
            meta_data = list((src_f, source_with_subfolder, trgt_f))
            for idx, elem in enumerate(meta_data):
                meta_data[idx] = os.path.join(args.path, elem) 
            meta_data.append(FILES_TYPES_TO_IGNORE)  # Add to the multiprocess arguments the black list 

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
    


