#!/usr/bin/env python3

import argparse
import os
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
import httpx
from concurrent.futures import ThreadPoolExecutor
import glob


def process_audio_file(file_path, args, api_key):
    """Process a single audio file"""
    try:
        deepgram = DeepgramClient(api_key)

        with open(file_path, "rb") as audio:
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

        print(f"\nSending request to Deepgram for {file_path}...")
        timeout_config = httpx.Timeout(300.0, connect=10.0)
        response = deepgram.listen.rest.v("1").transcribe_file(
            payload, options, timeout=timeout_config
        )

        print(f"Received response from Deepgram for {file_path}.")

        if args.transcript:
            print(f"\nTranscript for {file_path}:")
            print(response.results.channels[0].alternatives[0].transcript)
        else:
            print(f"\nGenerating subtitles for {file_path}...")
            from deepgram_captions import DeepgramConverter, srt

            converter = DeepgramConverter(response)
            srt_captions = srt(converter)

            input_dir = os.path.dirname(file_path)
            base_filename_no_ext = os.path.splitext(os.path.basename(file_path))[
                0
            ]

            srt_filename = os.path.join(input_dir, f"{base_filename_no_ext}.srt")

            with open(srt_filename, "w") as f:
                f.write(srt_captions)
            print(f"SRT subtitles saved to: {srt_filename}")

    except Exception as e:
        print(f"An error occurred processing {file_path}: {e}")


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
        "-v", "--video", help="Path to the video file (MP4) or directory containing MP4 files"
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
        file_extension = "*.mp4"
        file_type = "MP4"

    print(f"File/Directory: {file_path}")
    print(f"Transcript only: {args.transcript}")

    # Check if the path is a directory or a file
    if os.path.isdir(file_path):
        # Find all files with the appropriate extension in the directory
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
