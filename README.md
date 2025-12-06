# Sonic Landscape

An interactive visualization tool for exploring music collections through perceptual audio dimensions.

## How It Works

Sonic Landscape analyzes audio files to extract perceptual characteristics, then projects tracks into a 3D space where similar-sounding music clusters together.

### Audio Analysis

Each track is analyzed across 5 perceptual dimensions:

| Dimension | What it measures |
|-----------|------------------|
| **Warmth** | Tonal quality from bright/cool to warm/rich (low-mid frequency balance, harmonic content) |
| **Spatiality** | Stereo width and reverb characteristics (how "wide" or "immersive" the mix sounds) |
| **Distance** | Perceived proximity of the sound source (intimate vs. distant production) |
| **Density** | Fullness and complexity of the arrangement (sparse vs. layered instrumentation) |
| **Groundedness** | Rhythmic stability and bass presence (floating/ethereal vs. rooted/driving) |

### Dimensionality Reduction

The 5-dimensional audio feature space is projected to 3D using PCA (Principal Component Analysis), preserving the relative distances between tracks. This means tracks that sound similar appear close together in the visualization.

### Clustering

K-means clustering groups tracks into sonic "neighborhoods" - collections of music that share similar acoustic characteristics regardless of genre labels.

## Features

- **3D Landscape View**: Navigate through your music collection spatially. Tracks are positioned by sonic similarity.
- **Searchable Playlist**: Filter and sort tracks by any dimension. Each card shows a radar chart of the track's audio profile.
- **Audio Playback**: Preview any track directly in the browser.
- **Cluster Exploration**: Discover natural groupings in your music that transcend genre.

## Tech Stack

- **Backend**: Flask (Python)
- **Visualization**: Three.js (3D), Plotly.js (2D scatter)
- **Audio**: HTML5 Audio with custom player UI
- **Data**: Pre-computed audio features stored as CSV/JSON

## Local Development

```bash
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```

## Data Format

The app expects:
- `data/tracks.csv` - Track metadata + audio features (warmth, spatiality, distance, density, groundedness)
- `data/pca_data.json` - PCA loadings for projecting features to 3D
- `data/cluster_info.json` - Cluster centroids and metadata