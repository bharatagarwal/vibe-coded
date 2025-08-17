# Useful Scripts

A collection of useful command-line utilities for video/audio processing and transcription.

## Tools

### mp4len

A shell script that calculates and displays the total duration of video files in a directory.

**Features:**
- Supports multiple video formats: MP4, MKV, MOV, WebM
- Parallel processing for faster execution
- Unicode-aware filename display with proper truncation
- Formatted duration output (HH:MM:SS)
- Individual file durations plus total duration

**Usage:**
```bash
./mp4len [directory]
```

If no directory is specified, it processes the current directory.

**Example Output:**
```
File                                     Duration
---------------------------------------- --------
movie1.mp4                               01:23:45
very_long_filename_that_gets_trunca...   02:15:30
short.mkv                                00:45:12
---------------------------------------- --------
                                   Total: 04:24:27
```

### deepgram-cli

A Python command-line interface for transcribing audio and video files using Deepgram's speech-to-text API.

**Features:**
- Transcribe individual files or entire directories
- Generate SRT subtitles or plain text transcripts
- Support for MP3 and MP4 files
- Batch processing with concurrent execution
- Multiple Deepgram model support
- Configurable language and model options

**Setup:**
1. Install dependencies: `pip install -r deepgram-cli/requirements.txt`
2. Set up API key: `echo "DEEPGRAM_API_KEY=your_key" > deepgram-cli/.env`

**Usage:**
```bash
cd deepgram-cli
./deepgram_cli.py -f audio.mp3              # Generate subtitles
./deepgram_cli.py -f audio.mp3 -t           # Generate transcript only
./deepgram_cli.py -v video.mp4              # Process video file
./deepgram_cli.py -f /path/to/directory     # Process all MP3s in directory
```

## Requirements

- **mp4len**: zsh, ffprobe (from FFmpeg)
- **deepgram-cli**: Python 3.6+, Deepgram API key