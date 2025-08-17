# Deepgram CLI

A command-line interface for transcribing audio files using Deepgram's speech-to-text API.

## Features

- Transcribe individual audio files or entire directories
- Generate SRT subtitles or plain text transcripts
- Support for MP3 and MP4 files
- Batch processing with concurrent execution
- Multiple Deepgram model support

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Deepgram API key in a `.env` file:
```bash
echo "DEEPGRAM_API_KEY=your_api_key_here" > .env
```

## Usage

### Basic Usage

```bash
./deepgram_cli.py -f PATH_TO_FILE_OR_DIRECTORY
```

### Command Options

- `-m, --model`: Deepgram model to use (default: nova-3)
- `-l, --language`: Language code (default: en) 
- `-f, --file`: Path to MP3 file or directory containing MP3 files
- `-v, --video`: Path to MP4 file or directory containing MP4 files
- `-t, --transcript`: Generate transcript only (no subtitles)

### Examples

**Transcribe a single file with subtitles:**
```bash
./deepgram_cli.py -f audio.mp3
```

**Transcribe with specific model and language:**
```bash
./deepgram_cli.py -m nova-2 -l es -f audio.mp3
```

**Generate transcript only (no SRT file):**
```bash
./deepgram_cli.py -f audio.mp3 -t
```

**Process all MP3 files in a directory:**
```bash
./deepgram_cli.py -f /path/to/audio/directory
```

**Process a single MP4 video file:**
```bash
./deepgram_cli.py -v video.mp4
```

**Process all MP4 files in a directory:**
```bash
./deepgram_cli.py -v /path/to/video/directory
```

## Output

- **Subtitles mode (default)**: Creates `.srt` files alongside the original audio files
- **Transcript mode (`-t` flag)**: Prints transcripts to console

## Requirements

- Python 3.6+
- Deepgram API key
- Dependencies listed in `requirements.txt`