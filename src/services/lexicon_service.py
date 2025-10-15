import requests
import logging
from typing import List, Dict, Any, Optional
from ..models.track_models import TrackInfo, PlaylistInfo, GenreAnalysis

logger = logging.getLogger(__name__)


class LexiconService:
    """Service for interacting with Lexicon music organizer API"""
    
    def __init__(self, base_url: str = "http://localhost:48624", api_version: str = "v1"):
        self.base_url = base_url
        self.api_version = api_version
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make a request to the Lexicon API"""
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_tracks(self, limit: int = 100, offset: int = 0) -> List[TrackInfo]:
        """Get tracks from Lexicon library"""
        params = {'limit': limit, 'offset': offset}
        data = self._make_request('GET', 'tracks', params=params)
        
        if not data:
            return []
        
        tracks = []
        for track_data in data.get('tracks', []):
            track = TrackInfo(
                id=track_data.get('id', ''),
                title=track_data.get('title', ''),
                artist=track_data.get('artist', ''),
                album=track_data.get('album'),
                duration=track_data.get('duration'),
                file_path=track_data.get('filePath'),
                current_genre=track_data.get('genre'),
                bpm=track_data.get('bpm'),
                key=track_data.get('key'),
                year=track_data.get('year')
            )
            tracks.append(track)
        
        return tracks
    
    def get_all_tracks(self) -> List[TrackInfo]:
        """Get all tracks from the library (paginated)"""
        all_tracks = []
        offset = 0
        limit = 100
        
        while True:
            tracks = self.get_tracks(limit=limit, offset=offset)
            if not tracks:
                break
            
            all_tracks.extend(tracks)
            offset += limit
            
            # If we got fewer tracks than requested, we've reached the end
            if len(tracks) < limit:
                break
        
        return all_tracks
    
    def update_track_genre(self, track_id: str, genre: str) -> bool:
        """Update the genre of a track"""
        data = {'genre': genre}
        result = self._make_request('PUT', f'tracks/{track_id}', json=data)
        return result is not None
    
    def update_track_metadata(self, track_id: str, metadata: Dict[str, Any]) -> bool:
        """Update track metadata"""
        result = self._make_request('PUT', f'tracks/{track_id}', json=metadata)
        return result is not None
    
    def get_playlists(self) -> List[PlaylistInfo]:
        """Get all playlists"""
        data = self._make_request('GET', 'playlists')
        
        if not data:
            return []
        
        playlists = []
        for playlist_data in data.get('playlists', []):
            playlist = PlaylistInfo(
                id=playlist_data.get('id', ''),
                name=playlist_data.get('name', ''),
                genre=playlist_data.get('genre', ''),
                track_count=playlist_data.get('trackCount', 0),
                description=playlist_data.get('description')
            )
            playlists.append(playlist)
        
        return playlists
    
    def add_track_to_playlist(self, playlist_id: str, track_id: str) -> bool:
        """Add a track to a playlist"""
        data = {'trackId': track_id}
        result = self._make_request('POST', f'playlists/{playlist_id}/tracks', json=data)
        return result is not None
    
    def get_playlist_tracks(self, playlist_id: str) -> List[str]:
        """Get track IDs in a playlist"""
        data = self._make_request('GET', f'playlists/{playlist_id}/tracks')
        
        if not data:
            return []
        
        return [track.get('id') for track in data.get('tracks', [])]
    
    def test_connection(self) -> bool:
        """Test connection to Lexicon API"""
        try:
            response = self.session.get(f"{self.base_url}/{self.api_version}/status")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
