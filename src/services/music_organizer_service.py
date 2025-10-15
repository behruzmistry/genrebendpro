import logging
import time
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from ..models.track_models import TrackInfo, GenreAnalysis, PlaylistInfo
from .lexicon_service import LexiconService
from .music_research_service import MusicResearchService
from .genre_detection_service import GenreDetectionService
from .playlist_matching_service import PlaylistMatchingService

logger = logging.getLogger(__name__)


class MusicOrganizerService:
    """Main service that orchestrates the music organization process"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize services
        self.lexicon_service = LexiconService(
            base_url=config.get('LEXICON_API_URL', 'http://localhost:48624'),
            api_version=config.get('LEXICON_API_VERSION', 'v1')
        )
        
        self.music_research_service = MusicResearchService(
            lastfm_api_key=config.get('LASTFM_API_KEY'),
            musicbrainz_user_agent=config.get('MUSICBRAINZ_USER_AGENT', 'GenreBendPro/1.0')
        )
        
        self.genre_detection_service = GenreDetectionService(
            sample_rate=config.get('AUDIO_SAMPLE_RATE', 22050),
            duration_limit=config.get('AUDIO_DURATION_LIMIT', 30)
        )
        
        self.playlist_matching_service = PlaylistMatchingService()
        
        # Configuration
        self.batch_size = config.get('BATCH_SIZE', 50)
        self.max_retries = config.get('MAX_RETRIES', 3)
        self.retry_delay = config.get('RETRY_DELAY', 1.0)
        self.confidence_threshold = config.get('CONFIDENCE_THRESHOLD', 0.7)
    
    def organize_music_collection(self, dry_run: bool = False) -> Dict[str, Any]:
        """Main method to organize the entire music collection"""
        logger.info("Starting music collection organization...")
        
        # Test Lexicon connection
        if not self.lexicon_service.test_connection():
            logger.error("Cannot connect to Lexicon API. Please ensure Lexicon is running and API is enabled.")
            return {'success': False, 'error': 'Lexicon API connection failed'}
        
        try:
            # Get all tracks from Lexicon
            logger.info("Fetching tracks from Lexicon...")
            tracks = self.lexicon_service.get_all_tracks()
            logger.info(f"Found {len(tracks)} tracks to process")
            
            if not tracks:
                logger.warning("No tracks found in Lexicon library")
                return {'success': True, 'message': 'No tracks to process'}
            
            # Get existing playlists
            logger.info("Fetching existing playlists...")
            playlists = self.lexicon_service.get_playlists()
            logger.info(f"Found {len(playlists)} existing playlists")
            
            # Process tracks in batches
            results = self._process_tracks_batch(tracks, playlists, dry_run)
            
            # Generate summary
            summary = self._generate_summary(results)
            
            logger.info("Music collection organization completed successfully")
            return {
                'success': True,
                'summary': summary,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Music organization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_tracks_batch(self, tracks: List[TrackInfo], playlists: List[PlaylistInfo], 
                            dry_run: bool) -> Dict[str, Any]:
        """Process tracks in batches"""
        results = {
            'processed': 0,
            'updated': 0,
            'playlist_additions': 0,
            'errors': 0,
            'skipped': 0,
            'details': []
        }
        
        # Process tracks in batches
        for i in range(0, len(tracks), self.batch_size):
            batch = tracks[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(tracks) + self.batch_size - 1)//self.batch_size}")
            
            batch_results = self._process_batch(batch, playlists, dry_run)
            
            # Aggregate results
            for key in ['processed', 'updated', 'playlist_additions', 'errors', 'skipped']:
                results[key] += batch_results[key]
            
            results['details'].extend(batch_results['details'])
            
            # Add delay between batches to avoid overwhelming APIs
            if i + self.batch_size < len(tracks):
                time.sleep(self.retry_delay)
        
        return results
    
    def _process_batch(self, tracks: List[TrackInfo], playlists: List[PlaylistInfo], 
                      dry_run: bool) -> Dict[str, Any]:
        """Process a batch of tracks"""
        batch_results = {
            'processed': 0,
            'updated': 0,
            'playlist_additions': 0,
            'errors': 0,
            'skipped': 0,
            'details': []
        }
        
        for track in tqdm(tracks, desc="Processing tracks"):
            try:
                result = self._process_single_track(track, playlists, dry_run)
                batch_results['processed'] += 1
                
                if result['success']:
                    if result['updated']:
                        batch_results['updated'] += 1
                    if result['playlist_additions'] > 0:
                        batch_results['playlist_additions'] += result['playlist_additions']
                    if result['skipped']:
                        batch_results['skipped'] += 1
                else:
                    batch_results['errors'] += 1
                
                batch_results['details'].append(result)
                
            except Exception as e:
                logger.error(f"Error processing track {track.title}: {e}")
                batch_results['errors'] += 1
                batch_results['details'].append({
                    'track_id': track.id,
                    'track_title': track.title,
                    'success': False,
                    'error': str(e)
                })
        
        return batch_results
    
    def _process_single_track(self, track: TrackInfo, playlists: List[PlaylistInfo], 
                             dry_run: bool) -> Dict[str, Any]:
        """Process a single track"""
        result = {
            'track_id': track.id,
            'track_title': track.title,
            'track_artist': track.artist,
            'success': False,
            'updated': False,
            'playlist_additions': 0,
            'skipped': False,
            'error': None,
            'analysis': None
        }
        
        try:
            # Skip if track already has a genre and confidence is high
            if track.current_genre and track.confidence_score and track.confidence_score > 0.8:
                result['skipped'] = True
                result['success'] = True
                logger.debug(f"Skipping {track.title} - already has high-confidence genre")
                return result
            
            # Research the track
            logger.debug(f"Researching track: {track.title}")
            research_result = self.music_research_service.research_track(track)
            
            # Analyze genre
            logger.debug(f"Analyzing genre for: {track.title}")
            analysis = self.genre_detection_service.analyze_track(track, research_result)
            result['analysis'] = analysis
            
            # Check if confidence is sufficient
            if analysis.confidence < self.confidence_threshold:
                logger.debug(f"Low confidence ({analysis.confidence:.2f}) for {track.title}")
                result['skipped'] = True
                result['success'] = True
                return result
            
            # Update track genre if different from current
            if not dry_run and analysis.predicted_genre.value != track.current_genre:
                logger.info(f"Updating genre for {track.title}: {track.current_genre} -> {analysis.predicted_genre.value}")
                
                success = self.lexicon_service.update_track_genre(track.id, analysis.predicted_genre.value)
                if success:
                    result['updated'] = True
                else:
                    logger.error(f"Failed to update genre for {track.title}")
                    result['error'] = "Failed to update genre"
                    return result
            
            # Match to playlists
            matched_playlists = self.playlist_matching_service.match_track_to_playlists(
                track, analysis, playlists
            )
            
            # Add to playlists
            playlist_additions = 0
            if not dry_run and matched_playlists:
                for playlist_id in matched_playlists:
                    # Check if track is already in playlist
                    existing_tracks = self.lexicon_service.get_playlist_tracks(playlist_id)
                    if track.id not in existing_tracks:
                        success = self.lexicon_service.add_track_to_playlist(playlist_id, track.id)
                        if success:
                            playlist_additions += 1
                        else:
                            logger.warning(f"Failed to add {track.title} to playlist {playlist_id}")
            
            result['playlist_additions'] = playlist_additions
            result['matched_playlists'] = matched_playlists
            result['success'] = True
            
            logger.info(f"Processed {track.title}: Genre={analysis.predicted_genre.value}, "
                       f"Confidence={analysis.confidence:.2f}, Playlists={playlist_additions}")
            
        except Exception as e:
            logger.error(f"Error processing track {track.title}: {e}")
            result['error'] = str(e)
        
        return result
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the processing results"""
        summary = {
            'total_processed': results['processed'],
            'tracks_updated': results['updated'],
            'playlist_additions': results['playlist_additions'],
            'errors': results['errors'],
            'skipped': results['skipped'],
            'success_rate': 0.0,
            'genre_distribution': {},
            'remix_analysis': {'total_remixes': 0, 'processed_remixes': 0}
        }
        
        # Calculate success rate
        if results['processed'] > 0:
            summary['success_rate'] = (results['processed'] - results['errors']) / results['processed']
        
        # Analyze genre distribution
        for detail in results['details']:
            if detail.get('analysis'):
                analysis = detail['analysis']
                genre = analysis.predicted_genre.value
                summary['genre_distribution'][genre] = summary['genre_distribution'].get(genre, 0) + 1
                
                # Count remixes
                if analysis.is_remix:
                    summary['remix_analysis']['total_remixes'] += 1
                    if detail.get('success'):
                        summary['remix_analysis']['processed_remixes'] += 1
        
        return summary
    
    def analyze_collection(self) -> Dict[str, Any]:
        """Analyze the current music collection"""
        logger.info("Analyzing music collection...")
        
        try:
            # Get tracks and playlists
            tracks = self.lexicon_service.get_all_tracks()
            playlists = self.lexicon_service.get_playlists()
            
            # Analyze playlist consistency
            playlist_analysis = self.playlist_matching_service.analyze_playlist_consistency(playlists)
            
            # Analyze track genres
            genre_distribution = {}
            tracks_without_genre = 0
            tracks_with_low_confidence = 0
            
            for track in tracks:
                if not track.current_genre:
                    tracks_without_genre += 1
                else:
                    genre_distribution[track.current_genre] = genre_distribution.get(track.current_genre, 0) + 1
                
                if track.confidence_score and track.confidence_score < self.confidence_threshold:
                    tracks_with_low_confidence += 1
            
            analysis = {
                'total_tracks': len(tracks),
                'total_playlists': len(playlists),
                'tracks_without_genre': tracks_without_genre,
                'tracks_with_low_confidence': tracks_with_low_confidence,
                'genre_distribution': genre_distribution,
                'playlist_analysis': playlist_analysis,
                'recommendations': []
            }
            
            # Generate recommendations
            if tracks_without_genre > 0:
                analysis['recommendations'].append(
                    f"Consider processing {tracks_without_genre} tracks without genre tags"
                )
            
            if tracks_with_low_confidence > 0:
                analysis['recommendations'].append(
                    f"Review {tracks_with_low_confidence} tracks with low confidence genre tags"
                )
            
            analysis['recommendations'].extend(playlist_analysis.get('recommendations', []))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Collection analysis failed: {e}")
            return {'error': str(e)}
    
    def train_genre_model(self, training_data_path: str) -> bool:
        """Train the genre classification model with custom data"""
        logger.info("Training genre classification model...")
        
        try:
            # Load training data (this would need to be implemented based on your data format)
            # For now, we'll use a placeholder
            training_data = []  # Load from file
            
            success = self.genre_detection_service.train_model(training_data)
            
            if success:
                # Save the trained model
                model_path = "models/genre_classifier.pkl"
                self.genre_detection_service.save_model(model_path)
                logger.info("Model training completed successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
