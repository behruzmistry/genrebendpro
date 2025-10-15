#!/usr/bin/env python3
"""
GenreBend Pro - Main Application
Automatically researches and labels music collection with accurate genres
"""

import argparse
import sys
import os
from colorama import init, Fore, Style

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import load_config, setup_logging, validate_config
from src.services.music_organizer_service import MusicOrganizerService

def main():
    """Main application entry point"""
    init(autoreset=True)  # Initialize colorama
    
    parser = argparse.ArgumentParser(description='GenreBend Pro')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run without making changes (preview mode)')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze collection without making changes')
    parser.add_argument('--train-model', type=str,
                       help='Train genre classification model with data file')
    parser.add_argument('--config', type=str, default='.env',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    print(f"{Fore.CYAN}Loading configuration...{Style.RESET_ALL}")
    config = load_config()
    
    # Validate configuration
    if not validate_config(config):
        sys.exit(1)
    
    # Setup logging
    setup_logging(config['LOG_LEVEL'])
    
    # Initialize service
    print(f"{Fore.CYAN}Initializing Music Organizer Service...{Style.RESET_ALL}")
    organizer = MusicOrganizerService(config)
    
    try:
        if args.analyze:
            # Analyze collection
            print(f"{Fore.YELLOW}Analyzing music collection...{Style.RESET_ALL}")
            analysis = organizer.analyze_collection()
            
            if 'error' in analysis:
                print(f"{Fore.RED}Analysis failed: {analysis['error']}{Style.RESET_ALL}")
                sys.exit(1)
            
            # Display analysis results
            print(f"\n{Fore.GREEN}Collection Analysis Results:{Style.RESET_ALL}")
            print(f"Total tracks: {analysis['total_tracks']}")
            print(f"Total playlists: {analysis['total_playlists']}")
            print(f"Tracks without genre: {analysis['tracks_without_genre']}")
            print(f"Tracks with low confidence: {analysis['tracks_with_low_confidence']}")
            
            if analysis['genre_distribution']:
                print(f"\n{Fore.BLUE}Genre Distribution:{Style.RESET_ALL}")
                for genre, count in sorted(analysis['genre_distribution'].items()):
                    print(f"  {genre}: {count}")
            
            if analysis['recommendations']:
                print(f"\n{Fore.YELLOW}Recommendations:{Style.RESET_ALL}")
                for rec in analysis['recommendations']:
                    print(f"  • {rec}")
        
        elif args.train_model:
            # Train model
            print(f"{Fore.YELLOW}Training genre classification model...{Style.RESET_ALL}")
            success = organizer.train_genre_model(args.train_model)
            
            if success:
                print(f"{Fore.GREEN}Model training completed successfully!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Model training failed!{Style.RESET_ALL}")
                sys.exit(1)
        
        else:
            # Organize collection
            mode = "DRY RUN" if args.dry_run else "LIVE"
            print(f"{Fore.YELLOW}Starting music organization ({mode})...{Style.RESET_ALL}")
            
            result = organizer.organize_music_collection(dry_run=args.dry_run)
            
            if not result['success']:
                print(f"{Fore.RED}Organization failed: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
                sys.exit(1)
            
            # Display results
            summary = result['summary']
            print(f"\n{Fore.GREEN}Organization Complete!{Style.RESET_ALL}")
            print(f"Tracks processed: {summary['total_processed']}")
            print(f"Tracks updated: {summary['tracks_updated']}")
            print(f"Playlist additions: {summary['playlist_additions']}")
            print(f"Errors: {summary['errors']}")
            print(f"Skipped: {summary['skipped']}")
            print(f"Success rate: {summary['success_rate']:.1%}")
            
            if summary['genre_distribution']:
                print(f"\n{Fore.BLUE}Genre Distribution:{Style.RESET_ALL}")
                for genre, count in sorted(summary['genre_distribution'].items()):
                    print(f"  {genre}: {count}")
            
            if summary['remix_analysis']['total_remixes'] > 0:
                print(f"\n{Fore.MAGENTA}Remix Analysis:{Style.RESET_ALL}")
                print(f"  Total remixes found: {summary['remix_analysis']['total_remixes']}")
                print(f"  Remixes processed: {summary['remix_analysis']['processed_remixes']}")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
