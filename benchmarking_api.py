"""
Goal: Automatic benchmarking of a model's predictions with DAVIS-type metrics (J&F, J, and F).
Quick use: python benchmarking_api.py --predictions [path/to/output/folder/with/all/results]

by Stéphane Vujasinovic
"""

### - IMPORTS ---
import os
from argparse import ArgumentParser
from vos_benchmark.benchmark import benchmark
import yaml


### - ARGPARSER ---
parser = ArgumentParser()
parser.add_argument(
    '-p',
    '--predictions',
    type=str,
    required=True,
    help='Folder containing all the predictions of a model for all datasets.')
parser.add_argument(
    '-d',
    '--dataset',
    type=str,
    help='[Optional] Input a list of dataset aliases to skip those datasets [Note implemented yet].')
parser.add_argument(
    '-n',
    '--num_processes',
    default=16,
    type=int,
    help='Number of concurrent processes.')
parser.add_argument(
    '-s',
    '--strict',
    help='Make sure every video in the ground-truth has a corresponding video in the prediction.',
    action='store_true')
# https://github.com/davisvideochallenge/davis2017-evaluation/blob/d34fdef71ce3cb24c1a167d860b707e575b3034c/davis2017/evaluation.py#L85
parser.add_argument(
    '--do_not_skip_first_and_last_frame',
    help=
    'By default, we skip the first and the last frame in evaluation following DAVIS semi-supervised evaluation.'
    'They should not be skipped in unsupervised evaluation.',
    action='store_true')
parser.add_argument(
    '-c',
    '--config',
    type = str,
    default='config.yaml',
    help=
    'Align the alias of a dataset to the corresponding name of the dataset and the path.')
args = parser.parse_args()


### - PRE-PROCESSING ---
with open(args.config, 'r') as file:
    try:
        yaml_data = yaml.safe_load(file)['datasets']
    except yaml.YAMLError as e:
        print("Error reading the YAML file:", e)
        
subdirectories = [d for d in os.listdir(args.predictions) if os.path.isdir(os.path.join(args.predictions, d))] # list subdirectories (level 1 deep)
datasets_aliases = list(yaml_data.keys())
common_elements = list(set(datasets_aliases).intersection(subdirectories))


### - BENCHMARKING ---
for dataset_alias in sorted(common_elements):
    print(f'''
          ------------------------------------------
          ### Dataset Alias: {dataset_alias} ###''')
    
    path_to_dataset = os.path.join('..', yaml_data[dataset_alias]['mask_directory'])
    path_to_prediction = os.path.join(args.predictions, dataset_alias, 'Annotations')

    # Benchmarking (Thanks to the code of hkchengrex)
    benchmark(
        [path_to_dataset], 
        [path_to_prediction], 
        args.strict, 
        args.num_processes, 
        verbose=True, 
        skip_first_and_last=not args.do_not_skip_first_and_last_frame)

