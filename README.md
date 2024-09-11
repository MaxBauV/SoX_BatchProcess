# SoX Batch Process (sbp)

**SoX Batch Process** (`sbp`) is a Python script designed to batch process WAV files using SoX (Sound eXchange). It allows you to convert the sample rate and bit depth of multiple WAV files in a directory, with options for disabling dither during conversion.

## Features

- Batch process WAV files in a specified directory.
- Convert sample rate and bit depth of WAV files.
- Optional dither disabling during conversion.
- Debugging output for troubleshooting.

## Prerequisites

- Python 3.x
- SoX (Sound eXchange) installed

## Installation

1. **Clone the repository:**

    ```$ git clone <repository_url>```

2. **Navigate to the script directory:**

    ```$ cd SoX_BatchProcess```

3. **Make the script executable (optional):**

    ```$ chmod +x sbp.py```

## Usage

```$ ./sbp.py -p <directory> -b <bitdepth> -r <samplerate> [--no-dither] [--debug]```

### Arguments
- -p, --path: The directory containing WAV files to convert. (Required)
- -b, --bitdepth: Target bit depth (e.g., 16, 24, etc.). (Required)
- -r, --samplerate: Target sample rate in Hz (e.g., 48000 for 48kHz). (Required)
- --no-dither: Disable dither during conversion. (Optional)
- --debug: Enable debugging output to show SoX command outputs for troubleshooting. (Optional)

### Examples
- Convert all WAV files in a directory to 16-bit and 48kHz with dither:

    ```$ ./sbp.py -p /path/to/wav/files -b 16 -r 48000```

- Convert all WAV files in a directory to 24-bit and 44.1kHz without dither:

    ```$ ./sbp.py -p /path/to/wav/files -b 24 -r 44100 --no-dither```

- Run with debugging output enabled:

    ```$ ./sbp.py -p /path/to/wav/files -b 16 -r 48000 --debug```

## Troubleshooting

- Ensure SoX is installed and available in your system's PATH.
- If you encounter issues with bit depth extraction, verify the output format of sox --i and adjust the regex in the script as needed.

## License

This project is licensed under the MIT License. See the LICENSE file for details.