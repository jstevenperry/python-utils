#
# Counts the number of DL4J Networks in the specified directory
# and sorts them by Training Years then evaluation years, then
# displays a little information about the networks
import argparse
import json
import time
from operator import itemgetter
from pathlib import Path

__DEBUG = False


def process_index_file(file):
    # Read the file and return the training and evaluation years lists
    with file.open() as index_file:
        index_file_json = json.load(index_file)
        if __DEBUG:
            print('process_index_file: Index file: {}'.format(json.dumps(index_file_json)))
        return tuple(sorted(index_file_json['yearsToTrainNetwork'])), tuple(sorted(index_file_json['yearsToEvaluateNetwork']))


def main(command_line_args):
    start_time = round(time.time() * 1000)
    index_directory = command_line_args.index_directory
    print('main: Reading index files from: {}'.format(index_directory))
    # A map of training and evaluation years to other metadata about the index file
    metadata_map = {}
    # Read the files in that directory
    file_count = 0
    for file in Path(index_directory).glob('*.json'):
        # If the file is a JSON file, read it and process its contents
        training_years, evaluation_years = process_index_file(file)
        te_tuple = tuple([training_years, evaluation_years])
        count = 1
        if (training_years, evaluation_years) in metadata_map.keys():
            count = metadata_map[te_tuple] + 1
        metadata_map[te_tuple] = count
        file_count += 1

    # Sort the results by count desc (count is at index 1)
    sorted_map = sorted(metadata_map.items(), key=itemgetter(1), reverse=True)
    #    sorted_map = sorted(metadata_map.items(), key=itemgetter(1), reverse=False)
    # Print out the results
    print('main: Processed {} files in {}ms'.format(file_count, (round(time.time() * 1000)) - start_time))
    print_results(sorted_map)


def print_results(sorted_map):
    max_count, max_ty, max_ey = compute_max_column_lengths(sorted_map)
    print('')
    format_string = '{{:>{}}}: {{:<{}}}\t{{:<{}}}'.format(max_count, max_ty, max_ey)
    print(format_string.format('Count', 'Training Years', 'Evaluation Years'))
    print('{}  {}\t{}'.format('-'*max_count, '-'*max_ty, '-'*max_ey))
    for item in sorted_map:
        ty = [year for year in item[0][0]]
        ey = [year for year in item[0][1]]
        print(format_string.format(item[1], format(ty), format(ey)))


def compute_max_column_lengths(sorted_map):
    max_count = 5
    max_ty = len('Training Years')
    max_ey = len('Evaluation Years')
    for item in sorted_map:
        ty = format([year for year in item[0][0]])
        ey = format([year for year in item[0][1]])
        if len(str(item[1])) > max_count:
            max_count = len(str(item[1]))
        if len(ty) > max_ty:
            max_ty = len(ty)
        if len(ey) > max_ey:
            max_ey = len(ey)

    return max_count, max_ty, max_ey


if __name__ == "__main__":
    # Build a command line argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('index_directory',
                        help='The full path to the directory where the network index files are located')
    # Parse the arguments and pass them to the main function
    arguments = parser.parse_args()
    main(arguments)
