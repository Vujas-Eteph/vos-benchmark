import os
from argparse import ArgumentParser
from vos_benchmark.benchmark import benchmark
import yaml


parser = ArgumentParser()
parser.add_argument(
    '-p',
    '--predictions',
    type=str,
    help='Path to the folder containing the predictions of your model')
parser.add_argument(
    '-d',
    '--dataset',
    type=str,
    help='[Optional] A list of dataset names. Will only performe the benchmarking only on those.')
parser.add_argument(
    '-n',
    '--num_processes',
    default=16,
    type=int,
    help='Number of concurrent processes')
parser.add_argument(
    '-s',
    '--strict',
    help='Make sure every video in the ground-truth has a corresponding video in the prediction',
    action='store_true')
# https://github.com/davisvideochallenge/davis2017-evaluation/blob/d34fdef71ce3cb24c1a167d860b707e575b3034c/davis2017/evaluation.py#L85
parser.add_argument(
    '--do_not_skip_first_and_last_frame',
    help=
    'By default, we skip the first and the last frame in evaluation following DAVIS semi-supervised evaluation.'
    'They should not be skipped in unsupervised evaluation.',
    action='store_true')
parser.add_argument(
    '-y',
    '--yamlConfig',
    type = str,
    default='config_copy.yaml',
    help=
    'By default, we skip the first and the last frame in evaluation following DAVIS semi-supervised evaluation.'
    'They should not be skipped in unsupervised evaluation.')

args = parser.parse_args()

# Open and read the YAML file
with open(args.yamlConfig, 'r') as file:
    try:
        yaml_data = yaml.safe_load(file)['datasets']
        # Now, yaml_data contains the parsed YAML content as a Python dictionary
    except yaml.YAMLError as e:
        print("Error reading the YAML file:", e)
        
        
# Get folders to work on
subdirectories = [d for d in os.listdir(args.predictions) if os.path.isdir(os.path.join(args.predictions, d))]
datasets_name = list(yaml_data.keys())
common_elements = list(set(datasets_name).intersection(subdirectories))


for dataset in sorted(common_elements):
    print(f'''
          \n -----------------------------
          \n ### Dataset: {dataset} ###\n''')
        
    path_to_dataset = [os.path.join('..', yaml_data[dataset]['mask_directory'])]
    path_to_prediction = [os.path.join(args.predictions, dataset, 'Annotations')] 

    benchmark(path_to_dataset, 
              path_to_prediction, 
              args.strict, 
              args.num_processes, 
              verbose=True, 
              skip_first_and_last=not args.do_not_skip_first_and_last_frame)