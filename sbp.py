#!/usr/bin/env python3

import os
import subprocess
import re
import argparse

def parse_arguments():
    """Parse command-line arguments using argparse."""
    parser = argparse.ArgumentParser(
        description="Convert and optionally normalize WAV files to a specified sample rate and bit depth using sox."
    )
    parser.add_argument('-p', '--path', type=str, required=True, help='The directory containing WAV files to process')
    parser.add_argument('-b', '--bitdepth', type=int, required=True, help='Target bit depth (e.g., 16, 24, etc.)')
    parser.add_argument('-r', '--samplerate', type=int, required=True, help='Target sample rate in Hz (e.g., 48000 for 48kHz)')
    parser.add_argument('--no-dither', action='store_true', help="Disable dither during conversion (adds '-D' to sox command)")
    parser.add_argument('-n', '--normalize', action='store_true', help="Normalize audio files to 0 dB using sox")
    parser.add_argument('--debug', action='store_true', help="Enable debugging output")
    return parser.parse_args()


def translate_icloud_path(path: str) -> str:
    """Übersetzt Finder-Pfade ins echte Dateisystem (iCloud Besonderheit)."""
    return path.replace("comappleCloudDocs", "com~apple~CloudDocs")


def get_wav_files(directory):
    """Get a list of all WAV files in the specified directory and its subdirectories."""
    list_of_files = []
    for (dirpath, _, filenames) in os.walk(directory):
        list_of_files += [os.path.join(dirpath, file) for file in filenames if file.lower().endswith(".wav")]
    return list_of_files


def get_file_info(file, debug):
    """Extract sample rate and bit depth from a WAV file using sox."""
    result = subprocess.run(['sox', '--i', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    if debug:
        print(f"Output for file {file}:\n{output}")

    try:
        sample_rate = int(re.search(r'Sample Rate\s+: (\d+)', output).group(1))
    except AttributeError:
        print(f"⚠️ Could not extract sample rate from {file}")
        sample_rate = None

    try:
        bit_depth_match = re.search(r'Sample Encoding:\s+(\d+)-bit', output)
        if bit_depth_match:
            bit_depth = int(bit_depth_match.group(1))
        else:
            bit_depth_match = re.search(r'Precision\s+: (\d+)-bit', output)
            if bit_depth_match:
                bit_depth = int(bit_depth_match.group(1))
            else:
                print(f"⚠️ Could not extract bit depth from {file}")
                bit_depth = None
    except AttributeError:
        print(f"⚠️ Could not apply regex to bit depth for {file}")
        bit_depth = None

    return sample_rate, bit_depth


def should_convert(file_bitdepth, target_bitdepth, file_samplerate, target_samplerate):
    """Determine whether a file needs conversion based on sample rate and bit depth."""
    return (file_bitdepth != target_bitdepth) or (file_samplerate != target_samplerate)


def convert_file(file, target_bitdepth, target_samplerate, no_dither, normalize, tmp_outfile):
    """Convert and optionally normalize the WAV file."""
    sox_command = ['sox', file, '-b', str(target_bitdepth), '-r', str(target_samplerate)]
    if no_dither:
        sox_command.append('-D')
    if normalize:
        sox_command.append('--norm')
    sox_command.append(tmp_outfile)

    action = "Normalizing and converting" if normalize else "Converting"
    print(f"{action} {file} → {target_bitdepth}-bit / {target_samplerate} Hz ...")

    convert_process = subprocess.run(sox_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if convert_process.returncode != 0:
        print(f"❌ sox failed for {file}: {convert_process.stderr.decode('utf-8')}")
    return convert_process.returncode == 0


def process_files(directory, target_bitdepth, target_samplerate, no_dither, normalize, debug):
    """Process each WAV file, converting and normalizing if necessary."""
    wav_files = get_wav_files(directory)

    for file in wav_files:
        file_samplerate, file_bitdepth = get_file_info(file, debug)
        if file_samplerate is None or file_bitdepth is None:
            continue

        if should_convert(file_bitdepth, target_bitdepth, file_samplerate, target_samplerate) or normalize:
            tmp_outfile = os.path.join(directory, "tmp_out.wav")
            if convert_file(file, target_bitdepth, target_samplerate, no_dither, normalize, tmp_outfile):
                subprocess.run(['mv', tmp_outfile, file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"✅ Processed {file} (bit depth: {target_bitdepth}, sample rate: {target_samplerate})")
            else:
                print(f"❌ Processing failed for {file}")
        else:
            print(f"✔️ {file} already meets the requirements")


def main():
    """Main function to parse arguments and start the processing."""
    args = parse_arguments()
    directory = translate_icloud_path(args.path)

    if not os.path.isdir(directory):
        print(f"❌ Ordner nicht gefunden: {directory}")
        return

    process_files(directory, args.bitdepth, args.samplerate, args.no_dither, args.normalize, args.debug)


if __name__ == "__main__":
    main()