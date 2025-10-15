#!/usr/bin/env python3
"""
Basic usage example for GenreBend Pro
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import load_config
from src.services.music_organizer_service import MusicOrganizerService

def main():
    """Example of basic usage"""
    print("GenreBend Pro - Basic Usage Example")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Initialize service
    organizer = MusicOrganizerService(config)
    
    # Analyze collection first
    print("1. Analyzing collection...")
    analysis = organizer.analyze_collection()
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    print(f"Found {analysis['total_tracks']} tracks")
    print(f"Found {analysis['total_playlists']} playlists")
    print(f"Tracks without genre: {analysis['tracks_without_genre']}")
    
    # Run organization (dry run)
    print("\n2. Running organization (dry run)...")
    result = organizer.organize_music_collection(dry_run=True)
    
    if result['success']:
        summary = result['summary']
        print(f"Would process {summary['total_processed']} tracks")
        print(f"Would update {summary['tracks_updated']} tracks")
        print(f"Would add {summary['playlist_additions']} playlist entries")
    else:
        print(f"Error: {result['error']}")

if __name__ == '__main__':
    main()
