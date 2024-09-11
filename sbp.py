#!/usr/bin/env python3

import os
import subprocess
import re
import argparse


def parse_arguments():
    """Parse command-line arguments using argparse."""
    parser = argparse.ArgumentParser(
        description="Convert WAV files to a specified sample rate and bit depth using sox."
    )
    parser.add_argument('-p', '--path', type=str, required=True, help='The directory containing WAV files to convert')
    parser.add_argument('-b', '--bitdepth', type=int, required=True, help='Target bit depth (e.g., 16, 24, etc.)')
    parser.add_argument('-r', '--samplerate', type=int, required=True, help='Target sample rate in Hz (e.g., 48000 for 48kHz)')
    parser.add_argument('--no-dither', action='store_true', help="Disable dither during conversion (adds '-D' to sox command)")
    parser.add_argument('--debug', action='store_true', help="Enable debugging output")
    return parser.parse_args()


def get_wav_files(directory):
    """Get a list of all WAV files in the specified directory and its subdirectories."""
    list_of_files = []
    for (dirpath, _, filenames) in os.walk(directory):
        list_of_files += [os.path.join(dirpath, file) for file in filenames if file.endswith(".wav")]
    return list_of_files


def get_file_info(file, debug):
    """Extract sample rate and bit depth from a WAV file using sox."""
    result = subprocess.run(['sox', '--i', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    if debug:
        print(f"Output for file {file}:")
        print(output)  # Debug output to verify the information

    try:
        sample_rate = int(re.search(r'Sample Rate\s+: (\d+)', output).group(1))
    except AttributeError:
        print(f"Could not extract sample rate from {file}")
        sample_rate = None

    try:
        # Adjust regex for bit depth based on actual output
        bit_depth_match = re.search(r'Sample Encoding:\s+(\d+)-bit', output)
        if bit_depth_match:
            bit_depth = int(bit_depth_match.group(1))
        else:
            # Alternative regex to capture bit depth
            bit_depth_match = re.search(r'Precision\s+: (\d+)-bit', output)
            if bit_depth_match:
                bit_depth = int(bit_depth_match.group(1))
            else:
                print(f"Could not extract bit depth from {file}")
                bit_depth = None
    except AttributeError:
        print(f"Could not apply regex to bit depth for {file}")
        bit_depth = None

    return sample_rate, bit_depth


def should_convert(file_samplerate, file_bitdepth, target_samplerate, target_bitdepth):
    """Determine whether a file needs conversion based on sample rate and bit depth."""
    return file_samplerate != target_samplerate or file_bitdepth != target_bitdepth


def convert_file(file, target_samplerate, target_bitdepth, no_dither, tmp_outfile):
    """Convert the WAV file to the specified sample rate and bit depth."""
    sox_command = ['sox', file, '-b', str(target_bitdepth), '-r', str(target_samplerate)]
    if no_dither:
        sox_command.append('-D')
    sox_command.append(tmp_outfile)

    convert_process = subprocess.run(sox_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_process.returncode == 0


def process_files(directory, target_samplerate, target_bitdepth, no_dither, debug):
    """Process each WAV file, converting if necessary."""
    wav_files = get_wav_files(directory)

    for file in wav_files:
        file_samplerate, file_bitdepth = get_file_info(file, debug)
        if file_samplerate is None or file_bitdepth is None:
            continue

        if should_convert(file_samplerate, file_bitdepth, target_samplerate, target_bitdepth):
            tmp_outfile = os.path.join(directory, "tmp_out.wav")
            if convert_file(file, target_samplerate, target_bitdepth, no_dither, tmp_outfile):
                subprocess.run(['mv', tmp_outfile, file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"Converted {file} to {target_bitdepth}-bit and {target_samplerate} Hz")
            else:
                print(f"Conversion failed for {file}")
        else:
            print(f"{file} already meets the bit depth and sample rate requirements")


def main():
    """Main function to parse arguments and start the processing."""
    args = parse_arguments()
    process_files(args.path, args.samplerate, args.bitdepth, args.no_dither, args.debug)


if __name__ == "__main__":
    main()
