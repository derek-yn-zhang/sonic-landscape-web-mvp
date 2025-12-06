# Sonic Landscape

Interactive visualization of a music collection analyzed through audio terrain dimensions.

## Features

- **Interactive Scatter Plot**: Explore tracks across 5 terrain dimensions
- **Cluster Analysis**: Discover natural groupings in your music
- **Audio Playback**: Click any point to hear the track
- **Responsive Design**: Works on desktop and mobile

## Terrain Dimensions

| Dimension | Description |
|-----------|-------------|
| **Warmth** | Tonal quality from bright/cool to warm/rich |
| **Spatiality** | Width and depth of the stereo image |
| **Distance** | Perceived proximity of the sound source |
| **Density** | Fullness and complexity of the arrangement |
| **Groundedness** | Rhythmic stability and pulse clarity |

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set audio directory for local files
export AUDIO_DIR=/path/to/terrain/audio

# Run the app
python app.py

# Visit http://localhost:5000
```

## Deployment to Heroku with Cloudflare R2

### Step 1: Set up Cloudflare R2

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) → R2
2. Create a new bucket (e.g., `sonic-landscape-audio`)
3. In bucket settings → Public access → Enable public access via r2.dev subdomain
4. Copy your public URL (looks like `https://pub-xxxx.r2.dev`)
5. Go to R2 → Manage R2 API Tokens → Create API Token
   - Select "Object Read & Write" permissions
   - Copy the Access Key ID and Secret Access Key

### Step 2: Upload Audio Files

```bash
cd /path/to/sonic-landscape-web

# Set R2 credentials (get these from Cloudflare dashboard)
export AWS_ACCESS_KEY_ID=your_r2_access_key_id
export AWS_SECRET_ACCESS_KEY=your_r2_secret_access_key
export S3_BUCKET_NAME=sonic-landscape-audio
export S3_ENDPOINT_URL=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
export S3_PUBLIC_URL=https://pub-xxxx.r2.dev

# Upload all audio files (2.2GB, takes ~5-10 min)
python scripts/upload_audio.py /path/to/terrain/audio/
```

### Step 3: Deploy to Heroku

```bash
# Create Heroku app
heroku create sonic-landscape

# Set the audio URL (use your R2 public URL)
heroku config:set AUDIO_BASE_URL=https://pub-xxxx.r2.dev/audio

# Commit and deploy
git add .
git commit -m "Initial commit"
git push heroku main

# Open the app
heroku open
```

### R2 Free Tier Limits

- 10 GB storage (your audio is ~2.2GB)
- 10 million Class B operations/month (reads)
- 1 million Class A operations/month (writes)
- No egress fees (unlike S3!)

## Project Structure

```
sonic-landscape-web/
├── app.py              # Flask application
├── templates/
│   └── index.html      # Main visualization page
├── data/
│   ├── track_files.json       # Track metadata (Spotify info)
│   ├── audio_features.csv     # Audio features + terrain scores
│   └── cluster_info.json      # Cluster analysis results
├── scripts/
│   └── upload_audio.py        # R2/S3 audio upload script
├── Procfile            # Heroku process config
├── requirements.txt    # Python dependencies
└── runtime.txt         # Python version
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main visualization page |
| `GET /api/tracks` | Track data with terrain scores |
| `GET /api/clusters` | Cluster information |
| `GET /api/stats` | Overall statistics |
| `GET /audio/<filename>` | Audio file (local dev only) |
| `GET /health` | Health check |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AUDIO_BASE_URL` | Base URL for audio files (R2 public URL) | Yes (production) |
| `AUDIO_DIR` | Local audio directory | Yes (local dev) |
| `PORT` | Server port | Auto (Heroku sets this) |

## Updating Data

To update the track data after re-running analysis:

```bash
# Copy fresh data from terrain project
cp /path/to/terrain/data/audio_features.csv data/
cp /path/to/terrain/data/track_files.json data/
cp /path/to/terrain/data/cluster_info.json data/

# Commit and deploy
git add data/
git commit -m "Update track data"
git push heroku main
```