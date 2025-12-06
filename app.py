"""
Sonic Landscape - Flask Web Application
Serves the interactive music terrain visualization with audio playback.
"""
import os
import json
import pandas as pd
import numpy as np
from urllib.parse import quote
from flask import Flask, render_template, jsonify
from functools import lru_cache

app = Flask(__name__)

# Configuration
AUDIO_BASE_URL = os.environ.get(
    'AUDIO_BASE_URL',
    'https://pub-e5e3662d4f2642aeba430bbac3b12024.r2.dev/audio'
)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Terrain feature columns used for PCA
TERRAIN_COLS = ['warmth', 'spatiality', 'distance', 'density', 'groundedness']


def load_json(filename):
    """Load a JSON file from the data directory."""
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_all_data():
    """
    Load and process all data needed for the visualization.
    Cached to avoid reloading on every request.
    """
    # Load raw data
    df = pd.read_csv(os.path.join(DATA_DIR, 'tracks.csv'))
    cluster_info = load_json('cluster_info.json')
    pca_data = load_json('pca_data.json')

    # Extract PCA loadings for computing PC coordinates
    loadings = pca_data['loadings']
    pc1_loadings = np.array(loadings['pc1'])
    pc2_loadings = np.array(loadings['pc2'])
    pc3_loadings = np.array(loadings['pc3'])

    # Compute PC coordinates for each track
    terrain_matrix = df[TERRAIN_COLS].values

    # Standardize features (z-score normalization)
    means = terrain_matrix.mean(axis=0)
    stds = terrain_matrix.std(axis=0)
    standardized = (terrain_matrix - means) / stds

    # Project onto principal components
    df['pc1'] = standardized @ pc1_loadings
    df['pc2'] = standardized @ pc2_loadings
    df['pc3'] = standardized @ pc3_loadings

    # Helper to safely get string values (NaN becomes default)
    def safe_str(val, default=''):
        return default if pd.isna(val) else str(val)

    # Helper to safely get numeric values (NaN becomes default)
    def safe_float(val, default=0.0):
        return default if pd.isna(val) else float(val)

    # Build track list
    tracks = []
    for _, row in df.iterrows():
        filename = os.path.basename(row['file_path'])

        track = {
            'name': safe_str(row.get('name'), filename.replace('.mp3', '')),
            'artist': safe_str(row.get('artist'), 'Unknown Artist'),
            'album': safe_str(row.get('album'), 'Unknown Album'),
            'album_art': safe_str(row.get('album_art'), ''),
            'file_path': f"{AUDIO_BASE_URL}/{quote(filename)}",
            'popularity': int(safe_float(row.get('popularity'), 0)),
            'cluster': int(safe_float(row.get('cluster'), 0)),
            'pc1': round(safe_float(row['pc1']), 6),
            'pc2': round(safe_float(row['pc2']), 6),
            'pc3': round(safe_float(row['pc3']), 6),
            'warmth': round(safe_float(row['warmth']), 6),
            'spatiality': round(safe_float(row['spatiality']), 6),
            'distance': round(safe_float(row['distance']), 6),
            'density': round(safe_float(row['density']), 6),
            'groundedness': round(safe_float(row['groundedness']), 6),
        }
        tracks.append(track)

    # Build cluster names and descriptions
    cluster_names = {}
    cluster_descriptions = {}
    centroids = cluster_info.get('centroids', {})

    for cluster_id, info in cluster_info.get('clusters', {}).items():
        cluster_names[cluster_id] = info.get('name', f'Cluster {cluster_id}')
        cluster_descriptions[cluster_id] = info.get('description', '')

    return {
        'tracks': tracks,
        'loadings': loadings,
        'variance': pca_data['variance'],
        'centroids': centroids,
        'terrain_cols': TERRAIN_COLS,
        'cluster_names': cluster_names,
        'cluster_descriptions': cluster_descriptions,
        'n_clusters': cluster_info.get('n_clusters', 2),
        'cluster_sizes': cluster_info.get('cluster_sizes', []),
    }


@app.route('/')
def index():
    """Serve the main visualization page."""
    return render_template('index.html')


@app.route('/api/data')
def get_all_data():
    """
    Single API endpoint that returns all data needed for the visualization.
    This minimizes HTTP requests and simplifies the frontend.
    """
    return jsonify(load_all_data())


@app.route('/api/tracks')
def get_tracks():
    """API endpoint for track data only."""
    data = load_all_data()
    return jsonify(data['tracks'])


@app.route('/api/config')
def get_config():
    """API endpoint for configuration (useful for debugging)."""
    return jsonify({
        'audio_base_url': AUDIO_BASE_URL,
        'terrain_cols': TERRAIN_COLS,
    })


@app.route('/health')
def health():
    """Health check endpoint for Heroku."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)