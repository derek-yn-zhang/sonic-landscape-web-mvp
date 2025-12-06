#!/usr/bin/env python3
"""
Upload audio files to S3-compatible storage (AWS S3, Cloudflare R2, etc.)

Usage:
    python scripts/upload_audio.py /path/to/audio/folder

Environment variables required (can be set in .env file):
    AWS_ACCESS_KEY_ID      - Access key
    AWS_SECRET_ACCESS_KEY  - Secret key
    S3_BUCKET_NAME         - Bucket name
    S3_ENDPOINT_URL        - Endpoint URL (for R2: https://<account_id>.r2.cloudflarestorage.com)
    S3_PUBLIC_URL          - Public URL prefix for files (for R2: https://pub-xxx.r2.dev)
"""
import os
import sys
import boto3
from pathlib import Path
from botocore.config import Config
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent.parent / '.env')


def get_s3_client():
    """Create S3 client with configuration from environment."""
    endpoint_url = os.environ.get('S3_ENDPOINT_URL')

    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
    )


def upload_audio_files(audio_dir: str):
    """Upload all audio files from directory to S3."""
    bucket_name = os.environ['S3_BUCKET_NAME']
    public_url = os.environ.get('S3_PUBLIC_URL', '')

    s3 = get_s3_client()
    audio_path = Path(audio_dir)

    # Find all audio files
    extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    audio_files = [f for f in audio_path.iterdir() if f.suffix.lower() in extensions]

    print(f"Found {len(audio_files)} audio files in {audio_dir}")
    print(f"Uploading to bucket: {bucket_name}")

    uploaded = []
    for i, audio_file in enumerate(audio_files):
        key = f"audio/{audio_file.name}"

        # Check content type
        content_type = 'audio/mpeg' if audio_file.suffix == '.mp3' else 'audio/wav'

        print(f"[{i+1}/{len(audio_files)}] Uploading {audio_file.name}...", end=' ')

        try:
            s3.upload_file(
                str(audio_file),
                bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'
                }
            )
            url = f"{public_url}/{key}" if public_url else f"s3://{bucket_name}/{key}"
            uploaded.append({'file': audio_file.name, 'url': url})
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")

    print(f"\nUploaded {len(uploaded)}/{len(audio_files)} files")

    if public_url:
        print(f"\nPublic URL base: {public_url}/audio/")
        print("\nSet this as AUDIO_BASE_URL in Heroku:")
        print(f"  heroku config:set AUDIO_BASE_URL={public_url}/audio")

    return uploaded


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/upload_audio.py /path/to/audio/folder")
        print("\nRequired environment variables:")
        print("  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME")
        print("\nOptional:")
        print("  S3_ENDPOINT_URL  - For R2/MinIO (not needed for AWS S3)")
        print("  S3_PUBLIC_URL    - Public URL prefix for files")
        sys.exit(1)

    # Check required env vars
    required = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    audio_dir = sys.argv[1]
    if not Path(audio_dir).is_dir():
        print(f"Error: {audio_dir} is not a directory")
        sys.exit(1)

    upload_audio_files(audio_dir)


if __name__ == '__main__':
    main()