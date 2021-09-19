import argparse
import fileinput
import re
import os
import sys

FILE_EXTENSION_DVW = '.dvw'

# Example: a13ST-~~~65B;;;;0563;-1-1;7377;17.07.22;1;1;1;1;4603;;2;3;5;6;8;9;2;3;5;6;8;9;
# Match: a13ST-~~~65B
PATTERN_SERVE = re.compile('^([*a][0-9]{2}S[^;]*)')

# Example: *17RT+~~~65BM3;;;;;;;17.07.23;1;1;1;1;4604;;2;3;5;6;8;9;2;3;5;6;8;9;
# Match: *17RT+~~~65BM3
PATTERN_RECEPTION = re.compile('^([*a][0-9]{2}R[^;]*)')

def is_dvw_file(file_input):
    """Checks if a file is a dvw file.

    Parameters
    ----------
    file_input : str
        The absolute or relative path of the file.

    Returns
    -------
    bool
        True if the file is valid, false otherwise.
    """

    if not os.path.exists(file_input):
        return False

    if os.path.isdir(file_input):
        return False

    if not file_input.endswith(FILE_EXTENSION_DVW):
        return False

    return True

def get_verbose_service_codes(file_input):
    """Gets the verbose service codes included in the file.

    Parameters
    ----------
    file_input : str
        The absolute or relative path of the file that contains
        the verbose service codes.

    Returns
    -------
    list
        A list of tuples. Each tuple contains a serve code and its
        respective reception code.
    """

    service_codes = []
    with open(file_input, 'r') as file:
        for line in file:
            if result := PATTERN_SERVE.search(line):
                code = result.group(1)
                service_codes.append((code, None))
            elif result := PATTERN_RECEPTION.search(line):
                code = result.group(1)
                length = len(service_codes)
                if length == 0 or service_codes[length - 1][1]:
                    print("Uh oh... reception code before service code? That doesn't seem right...", file = sys.stderr)
                else:
                    service_codes[length - 1] = (service_codes[length - 1][0], code)
    return service_codes

def merge(service_codes, file_input, line_number):
    """Merge the verbose codes into the file that contains skeleton
    codes.

    Parameters
    ----------
    service_codes : list
        A list of tuples. Each tuple contains a serve code and its
        respective reception code.
    file_input : str
        The skeleton dvw file to update.
    line_number : int
        The line number to start the merge.

    Returns
    -------
    bool
        True if the merge is successful, false otherwise.
    """

    # Let's read in each line of the dvw file to update.
    with fileinput.FileInput(files=file_input, inplace = 1, backup = '.bak') as f:
        index = 0
        current_line = 0
        for line in f:
            current_line += 1
            # If a line number has been supplied as the starting point for a merge,
            # let's print all existing lines until we hit it.
            if line_number and current_line < line_number:
                print(line.rstrip())
                continue
            # Keep track of whether we've written the substituted reception line to the dvw file. If not,
            # we'll want to write the existing line.
            is_reception_substituted = False
            # If true then we've reached a serve code. Let's try to replace it.
            while serve_result := PATTERN_SERVE.search(line):
                # If true then we've replaced all the service codes that we could. Unfortunately, there appears
                # to be more service codes in the dvw file to update.
                if index == len(service_codes):
                    print("Uh oh... there is one or more service codes that have not been replaced!", file = sys.stderr)
                    break
                # Perform the replacement and write to file. Please note, invoking print() here re-directs stdout to
                # the file.
                old_serve_line = line.rstrip()
                new_serve_line = re.sub(PATTERN_SERVE, '%s' % service_codes[index][0], old_serve_line)
                print(new_serve_line)
                # Let's print to console all changes.
                print("< {}".format(old_serve_line), file = sys.stderr)
                print("> {}".format(new_serve_line), file = sys.stderr)
                # Sweet, we've dealt with the serve code, now let's replace our reception code.
                line = next(f, None)
                if not line:
                    break
                old_reception_line = line.rstrip()
                reception_result = PATTERN_RECEPTION.search(old_reception_line)
                # If true then we've reached a reception code. Let's try to replace it.
                if reception_result:
                    # We could get here and not have a reception code to merge in. Let's just check before
                    # performing this substitution. This may be None in one of two scenarios: (1) There was 
                    # a service ace without a reception error (2) There was a service error.
                    if (service_codes[index][1]):
                        # Perform the replacement and write to file. Please note, invoking print() here re-directs stdout to
                        # the file.
                        new_reception_line = re.sub(PATTERN_RECEPTION, '%s' % service_codes[index][1], old_reception_line)
                        print(new_reception_line)
                        # Let's print to console all changes.
                        print("< {}".format(old_reception_line), file = sys.stderr)
                        print("> {}".format(new_reception_line), file = sys.stderr)
                        is_reception_substituted = True
                # Only increment when we've found a serve code.
                index += 1
            # If true then there is no reception code to replace or there was never a reception code to begin with.
            if line and not is_reception_substituted:
                print(line.rstrip())
    return True

# Retrieve all possible arguments for this command.
parser = argparse.ArgumentParser(description='Merge Volleymetrics .dvw files.')
parser.add_argument('input', type=str, help='The .dvw file that should be updated to include merged codes.')
parser.add_argument('-s', '--serve-codes', type=str, help='Specify the .dvw that contains the full serve codes.')
parser.add_argument('-l', '--line-number', type=int, help='Specify the line number to start the merge.')
args = parser.parse_args()

# Because this is the only optional argument currently, we require it.
# TODO: As more merge code options are added, include them here. We'll
# only need one to be supplied.
if not (args.serve_codes):
    parser.error('No codes to merge, add --serve-codes.')
    quit()

# Ensure file supplied is, indeed, a DVW file. This file will be
# updated to include the full codes.
if not is_dvw_file(args.input):
    print("{} is not a valid dvw file, exiting...".format(args.input))
    quit()

# Ensure serve codes file supplied is, indeed, a DVW file. This file 
# will be used to obtain the full serve codes.
if not is_dvw_file(args.serve_codes):
    print("{} is not a valid dvw file, exiting...".format(args.serve_codes))
    quit()

# Obtain all codes that should be used for replacement.
# TODO: Add support for full attack/block/dig codes.
verbose_service_codes = get_verbose_service_codes(args.serve_codes)

if merge(verbose_service_codes, args.input, args.line_number):
    print("Successfully merged dvw files.")
else:
    print("Failed to merge dvw files.")
