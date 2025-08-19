#!/usr/bin/env python3

import argparse
import os
import subprocess
import tempfile
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
import httpx
from concurrent.futures import ThreadPoolExecutor
import glob


def extract_audio_from_video(video_path, audio_path):
    """Extract audio from video file using FFmpeg"""
    cmd = [
        "ffmpeg", "-i", video_path, "-vn", "-q:a", "0", "-map", "a", 
        audio_path, "-y"  # -y to overwrite without asking
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg to use video processing.")
        return False


def process_audio_file(file_path, args, api_key):
    """Process a single audio file or video file"""
    temp_audio_path = None
    video_extensions = ('.mp4', '.webm', '.mkv')
    is_video = file_path.lower().endswith(video_extensions)
    
    try:
        # Step 1: Handle video files by extracting audio
        if is_video:
            print(f"\nProcessing video file: {file_path}")
            
            # Create temporary audio file
            temp_fd, temp_audio_path = tempfile.mkstemp(suffix='.mp3')
            os.close(temp_fd)  # Close the file descriptor
            
            print(f"Extracting audio from {file_path}...")
            if not extract_audio_from_video(file_path, temp_audio_path):
                return
            
            audio_file_path = temp_audio_path
            print(f"Audio extracted to temporary file.")
        else:
            audio_file_path = file_path

        # Step 2: Process audio with Deepgram
        deepgram = DeepgramClient(api_key)

        with open(audio_file_path, "rb") as audio:
            buffer_data = audio.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model=args.model,
            language=args.language,
            smart_format=True,
            utterances=True,
            punctuate=True,
        )

        print(f"Sending request to Deepgram for transcription...")
        timeout_config = httpx.Timeout(300.0, connect=10.0)
        response = deepgram.listen.rest.v("1").transcribe_file(
            payload, options, timeout=timeout_config
        )

        print(f"Received response from Deepgram.")

        if args.transcript:
            print(f"\nTranscript for {file_path}:")
            print(response.results.channels[0].alternatives[0].transcript)
        else:
            print(f"Generating subtitles...")
            from deepgram_captions import DeepgramConverter, srt

            converter = DeepgramConverter(response)
            srt_captions = srt(converter)

            input_dir = os.path.dirname(file_path)
            base_filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]

            # Save SRT file for both audio and video files
            srt_filename = os.path.join(input_dir, f"{base_filename_no_ext}.srt")
            with open(srt_filename, "w") as f:
                f.write(srt_captions)
            print(f"SRT subtitles saved to: {srt_filename}")

    except Exception as e:
        print(f"An error occurred processing {file_path}: {e}")
    finally:
        # Cleanup temporary audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except OSError:
                pass


def main():
    load_dotenv()
    api_key = os.getenv("DEEPGRAM_API_KEY")

    if not api_key:
        print(
            "Error: DEEPGRAM_API_KEY not found in .env file or environment variables."
        )
        return

    parser = argparse.ArgumentParser(
        description="Deepgram CLI for transcription and subtitling."
    )
    parser.add_argument(
        "-m", "--model", required=False, default="nova-3", help="Deepgram model to use (e.g., nova-3) [default: nova-3]"
    )
    parser.add_argument(
        "-l", "--language", required=False, default="en", help="Language code (e.g., en) [default: en]"
    )

    # Create mutually exclusive group for file and video options
    file_group = parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument(
        "-f", "--file", help="Path to the audio file (MP3) or directory containing MP3 files"
    )
    file_group.add_argument(
        "-v", "--video", help="Path to the video file (MP4/WebM/MKV) or directory containing video files"
    )

    parser.add_argument(
        "-t",
        "--transcript",
        action="store_true",
        help="Generate transcript only (no subtitles)",
    )

    args = parser.parse_args()

    print(f"Model: {args.model}")
    print(f"Language: {args.language}")

    # Determine the file path and extension based on which option was used
    if args.file:
        file_path = args.file
        file_extension = "*.mp3"
        file_type = "MP3"
    else:  # args.video
        file_path = args.video
        file_extension = ["*.mp4", "*.webm", "*.mkv"]
        file_type = "video"

    print(f"File/Directory: {file_path}")
    print(f"Transcript only: {args.transcript}")

    # Check if the path is a directory or a file
    if os.path.isdir(file_path):
        # Find all files with the appropriate extension in the directory
        media_files = []
        if isinstance(file_extension, list):
            for ext in file_extension:
                media_files.extend(glob.glob(os.path.join(file_path, ext)))
        else:
            media_files = glob.glob(os.path.join(file_path, file_extension))
        if not media_files:
            print(f"No {file_type} files found in directory: {file_path}")
            return

        print(f"Found {len(media_files)} {file_type} files to process")

        # Process files in batches of 5
        batch_size = 5
        for i in range(0, len(media_files), batch_size):
            batch = media_files[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} files)")

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(process_audio_file, file_path, args, api_key) for file_path in batch]

                # Wait for all tasks in this batch to complete
                for future in futures:
                    future.result()

    elif os.path.isfile(file_path):
        # Process single file
        process_audio_file(file_path, args, api_key)
    else:
        print(f"Error: {file_path} is not a valid file or directory")


if __name__ == "__main__":
    main()
