# Deepgram CLI

A command-line interface for transcribing audio files using Deepgram's speech-to-text API.

## Features

- Transcribe individual audio files or entire directories
- Generate SRT subtitles or plain text transcripts
- **Speaker diarization** - Identify and label different speakers in the audio
- Support for audio files (MP3, M4A, WAV, etc.) and video files (MP4, WebM, MKV)
- FFmpeg integration for automatic audio extraction from video files
- Batch processing with concurrent execution (5 files at a time)
- Multiple Deepgram model support
- Built on Deepgram SDK v4.8.1 (stable release)
- Extended timeout support for large files (up to 5 minutes processing time)

## Installation

### Prerequisites

- Python 3.6+
- FFmpeg (required for video processing)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Setup

1. Install Python dependencies:
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
- `-f, --file`: Path to audio file (supports any format Deepgram accepts) or directory containing MP3 files
- `-v, --video`: Path to video file (MP4/WebM/MKV) or directory containing video files
- `-t, --transcript`: Generate transcript only (no subtitles)
- `-d, --diarize`: Enable speaker diarization (identify different speakers)

### Examples

**Transcribe a single audio file with subtitles:**
```bash
./deepgram_cli.py -f audio.mp3
```

**Transcribe M4A audio file:**
```bash
./deepgram_cli.py -f audio.m4a
```

**Transcribe with specific model and language:**
```bash
./deepgram_cli.py -m nova-2 -l hi -f audio.m4a
```

**Generate transcript only (no SRT file):**
```bash
./deepgram_cli.py -f audio.mp3 -t
```

**Process all MP3 files in a directory:**
```bash
./deepgram_cli.py -f /path/to/audio/directory
```

**Process a single video file (MP4/WebM/MKV):**
```bash
./deepgram_cli.py -v video.mp4
./deepgram_cli.py -v video.webm
./deepgram_cli.py -v video.mkv
```

**Process all video files in a directory:**
```bash
./deepgram_cli.py -v /path/to/video/directory
```

**Transcribe with speaker diarization:**
```bash
./deepgram_cli.py -f audio.mp3 -d
```

**Transcribe interview/podcast with multiple speakers:**
```bash
./deepgram_cli.py -m nova-3 -l en -f interview.m4a -d
```

**Diarization with transcript-only mode:**
```bash
./deepgram_cli.py -f meeting.mp3 -d -t
```

## Output

- **Subtitles mode (default)**: Creates `.srt` files alongside the original audio files
  - With `-d` flag: SRT files include speaker labels (e.g., "Speaker 0", "Speaker 1")
- **Transcript mode (`-t` flag)**: Prints transcripts to console
  - With `-d` flag: Transcript shows which speaker said what

## Requirements

### System Requirements
- Python 3.6+
- FFmpeg (for video processing)
- Deepgram API key

### Python Dependencies
- `python-dotenv==1.1.1` - Environment variable management
- `deepgram-sdk==4.8.1` - Official Deepgram SDK (stable release)
- `deepgram-captions==1.2.0` - SRT/WebVTT caption generation
- `httpx>=0.27.0` - HTTP client for timeout configuration

All dependencies are listed in `requirements.txt` with pinned versions for stability.