import os
import glob

# Get absolute parent dir of this file

absolute_parent_dir = os.path.dirname(os.path.abspath(__file__))
midi_test_dir = os.path.join(absolute_parent_dir, "examples/*.mid")

# List all midi examples files
midi_files = glob.glob(midi_test_dir)

midi_files_dict = {}
for file in midi_files:
    midi_files_dict[os.path.basename(file).replace('.mid', '')] = file


def get_list_of_midi_files():
    return list(midi_files_dict.keys())

def get_midi_file(name):
    return midi_files_dict[name]