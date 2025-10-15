import musicbrainzngs
import requests
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from ..models.track_models import TrackInfo, MusicResearchResult, Genre

logger = logging.getLogger(__name__)


class MusicResearchService:
    """Service for researching music tracks using various APIs (without Spotify)"""
    
    def __init__(self, lastfm_api_key: str, musicbrainz_user_agent: str):
        self.lastfm_api_key = lastfm_api_key
        self.musicbrainz_user_agent = musicbrainz_user_agent
        
        # Initialize MusicBrainz
        musicbrainzngs.set_useragent(musicbrainz_user_agent, "1.0", "https://github.com/genrebend-pro")
        
        # Remix detection keywords
        self.remix_keywords = [
            'remix', 'edit', 'version', 'mix', 'rework', 'reinterpretation',
            'bootleg', 'mashup', 'flip', 'flip', 'refix', 'vip', 'dub',
            'instrumental', 'acapella', 'extended', 'radio edit'
        ]
    
    def research_track(self, track: TrackInfo) -> MusicResearchResult:
        """Research a track using all available APIs"""
        result = MusicResearchResult(track_id=track.id)
        
        # Search Last.fm
        lastfm_data = self._search_lastfm(track)
        if lastfm_data:
            result.lastfm_data = lastfm_data
        
        # Search MusicBrainz
        musicbrainz_data = self._search_musicbrainz(track)
        if musicbrainz_data:
            result.musicbrainz_data = musicbrainz_data
        
        # Analyze for remix detection
        result.is_remix = self._detect_remix(track, lastfm_data, musicbrainz_data)
        
        # Combine genre information
        result.combined_genres = self._combine_genres(lastfm_data, musicbrainz_data)
        
        # Calculate confidence score
        result.confidence = self._calculate_confidence(result)
        
        return result
    
    def _search_lastfm(self, track: TrackInfo) -> Optional[Dict[str, Any]]:
        """Search for track on Last.fm with enhanced metadata"""
        try:
            # Clean track info for Last.fm search
            clean_title = self._clean_title_for_search(track.title)
            clean_artist = self._clean_artist_for_search(track.artist)
            
            # Search for track info
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'track.getInfo',
                'api_key': self.lastfm_api_key,
                'artist': clean_artist,
                'track': clean_title,
                'format': 'json'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'track' in data and data['track'].get('name'):
                track_data = data['track']
                
                # Get additional artist info for more metadata
                artist_data = self._get_lastfm_artist_info(clean_artist)
                if artist_data:
                    track_data['artist_info'] = artist_data
                
                # Get similar tracks for genre analysis
                similar_tracks = self._get_lastfm_similar_tracks(clean_artist, clean_title)
                if similar_tracks:
                    track_data['similar_tracks'] = similar_tracks
                
                return track_data
        
        except Exception as e:
            logger.error(f"Last.fm search failed for {track.title}: {e}")
        
        return None
    
    def _get_lastfm_artist_info(self, artist: str) -> Optional[Dict[str, Any]]:
        """Get additional artist information from Last.fm"""
        try:
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'artist.getInfo',
                'api_key': self.lastfm_api_key,
                'artist': artist,
                'format': 'json'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'artist' in data:
                return data['artist']
        
        except Exception as e:
            logger.debug(f"Last.fm artist info failed for {artist}: {e}")
        
        return None
    
    def _get_lastfm_similar_tracks(self, artist: str, track: str) -> Optional[List[Dict[str, Any]]]:
        """Get similar tracks from Last.fm for genre analysis"""
        try:
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                'method': 'track.getSimilar',
                'api_key': self.lastfm_api_key,
                'artist': artist,
                'track': track,
                'format': 'json'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'similartracks' in data and 'track' in data['similartracks']:
                return data['similartracks']['track'][:5]  # Limit to 5 similar tracks
        
        except Exception as e:
            logger.debug(f"Last.fm similar tracks failed for {track}: {e}")
        
        return None
    
    def _search_musicbrainz(self, track: TrackInfo) -> Optional[Dict[str, Any]]:
        """Search for track on MusicBrainz"""
        try:
            # Clean track info
            clean_title = self._clean_title_for_search(track.title)
            clean_artist = self._clean_artist_for_search(track.artist)
            
            # Search for recordings
            results = musicbrainzngs.search_recordings(
                recording=clean_title,
                artist=clean_artist,
                limit=5
            )
            
            if results['recording-list']:
                # Find the best match
                best_match = self._find_best_musicbrainz_match(track, results['recording-list'])
                if best_match:
                    return best_match
        
        except Exception as e:
            logger.error(f"MusicBrainz search failed for {track.title}: {e}")
        
        return None
    
    def _detect_remix(self, track: TrackInfo, lastfm_data: Optional[Dict], 
                     musicbrainz_data: Optional[Dict]) -> bool:
        """Detect if a track is a remix"""
        # Check track title for remix keywords
        title_lower = track.title.lower()
        for keyword in self.remix_keywords:
            if keyword in title_lower:
                return True
        
        # Check artist name for remix indicators
        artist_lower = track.artist.lower()
        for keyword in self.remix_keywords:
            if keyword in artist_lower:
                return True
        
        # Check Last.fm data
        if lastfm_data:
            lastfm_title = lastfm_data.get('name', '').lower()
            lastfm_artist = lastfm_data.get('artist', {}).get('name', '').lower()
            
            for keyword in self.remix_keywords:
                if keyword in lastfm_title or keyword in lastfm_artist:
                    return True
        
        # Check MusicBrainz data
        if musicbrainz_data:
            mb_title = musicbrainz_data.get('title', '').lower()
            mb_artist = musicbrainz_data.get('artist-credit-phrase', '').lower()
            
            for keyword in self.remix_keywords:
                if keyword in mb_title or keyword in mb_artist:
                    return True
        
        return False
    
    def _combine_genres(self, lastfm_data: Optional[Dict], 
                       musicbrainz_data: Optional[Dict]) -> List[str]:
        """Combine genre information from all sources"""
        genres = set()
        
        # Extract genres from Last.fm
        if lastfm_data:
            # Get tags from track
            lastfm_tags = lastfm_data.get('toptags', {}).get('tag', [])
            if isinstance(lastfm_tags, list):
                for tag in lastfm_tags:
                    if isinstance(tag, dict) and 'name' in tag:
                        genres.add(tag['name'])
            elif isinstance(lastfm_tags, dict) and 'name' in lastfm_tags:
                genres.add(lastfm_tags['name'])
            
            # Get tags from artist info
            artist_info = lastfm_data.get('artist_info', {})
            if artist_info:
                artist_tags = artist_info.get('tags', {}).get('tag', [])
                if isinstance(artist_tags, list):
                    for tag in artist_tags:
                        if isinstance(tag, dict) and 'name' in tag:
                            genres.add(tag['name'])
                elif isinstance(artist_tags, dict) and 'name' in artist_tags:
                    genres.add(artist_tags['name'])
            
            # Extract genres from similar tracks
            similar_tracks = lastfm_data.get('similar_tracks', [])
            for similar_track in similar_tracks:
                similar_tags = similar_track.get('toptags', {}).get('tag', [])
                if isinstance(similar_tags, list):
                    for tag in similar_tags:
                        if isinstance(tag, dict) and 'name' in tag:
                            genres.add(tag['name'])
                elif isinstance(similar_tags, dict) and 'name' in similar_tags:
                    genres.add(similar_tags['name'])
        
        # Extract genres from MusicBrainz
        if musicbrainz_data:
            musicbrainz_tags = musicbrainz_data.get('tag-list', [])
            if isinstance(musicbrainz_tags, list):
                for tag in musicbrainz_tags:
                    if isinstance(tag, dict) and 'name' in tag:
                        genres.add(tag['name'])
            elif isinstance(musicbrainz_tags, dict) and 'name' in musicbrainz_tags:
                genres.add(musicbrainz_tags['name'])
        
        return list(genres)
    
    def _calculate_confidence(self, result: MusicResearchResult) -> float:
        """Calculate confidence score for the research result"""
        confidence = 0.0
        
        # Base confidence from number of sources
        sources_found = 0
        if result.lastfm_data:
            sources_found += 1
        if result.musicbrainz_data:
            sources_found += 1
        
        # Confidence based on sources found
        if sources_found == 2:
            confidence = 0.8
        elif sources_found == 1:
            confidence = 0.6
        
        # Boost confidence if genres are consistent across sources
        if result.combined_genres and len(result.combined_genres) > 0:
            confidence += 0.1
        
        # Boost confidence if Last.fm has rich data
        if result.lastfm_data:
            # Check for artist info
            if result.lastfm_data.get('artist_info'):
                confidence += 0.05
            
            # Check for similar tracks
            if result.lastfm_data.get('similar_tracks'):
                confidence += 0.05
            
            # Check for play count (popularity indicator)
            if result.lastfm_data.get('playcount'):
                confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _clean_title_for_search(self, title: str) -> str:
        """Clean track title for better search results"""
        # Remove common suffixes and clean up
        clean_title = title.lower()
        
        # Remove file extensions
        clean_title = re.sub(r'\.(mp3|wav|flac|aac|m4a)$', '', clean_title)
        
        # Remove common prefixes/suffixes
        clean_title = re.sub(r'^\d+\s*[-.]?\s*', '', clean_title)  # Remove track numbers
        clean_title = re.sub(r'\s*[-.]?\s*\d+\s*$', '', clean_title)  # Remove trailing numbers
        
        return clean_title.strip()
    
    def _clean_artist_for_search(self, artist: str) -> str:
        """Clean artist name for better search results"""
        # Remove common prefixes
        clean_artist = artist.lower()
        clean_artist = re.sub(r'^(the|a|an)\s+', '', clean_artist)
        
        return clean_artist.strip()
    
    def _find_best_musicbrainz_match(self, track: TrackInfo, musicbrainz_tracks: List[Dict]) -> Optional[Dict]:
        """Find the best matching track from MusicBrainz results"""
        if not musicbrainz_tracks:
            return None
        
        # Similar logic to Spotify matching
        clean_title = self._clean_title_for_search(track.title)
        clean_artist = self._clean_artist_for_search(track.artist)
        
        best_match = None
        best_score = 0
        
        for mb_track in musicbrainz_tracks:
            mb_title = self._clean_title_for_search(mb_track.get('title', ''))
            mb_artist = self._clean_artist_for_search(
                mb_track.get('artist-credit-phrase', '')
            )
            
            title_similarity = self._calculate_similarity(clean_title, mb_title)
            artist_similarity = self._calculate_similarity(clean_artist, mb_artist)
            
            score = (title_similarity * 0.4) + (artist_similarity * 0.6)
            
            if score > best_score:
                best_score = score
                best_match = mb_track
        
        return best_match if best_score > 0.6 else None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using simple character overlap"""
        if not str1 or not str2:
            return 0.0
        
        # Convert to sets of words for better matching
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
