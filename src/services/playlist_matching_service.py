import logging
from typing import List, Dict, Any, Optional, Tuple
from ..models.track_models import TrackInfo, PlaylistInfo, GenreAnalysis, Genre

logger = logging.getLogger(__name__)


class PlaylistMatchingService:
    """Service for matching tracks to appropriate playlists based on genre"""
    
    def __init__(self):
        self.playlist_genre_mapping = {}
        self.genre_similarity_matrix = self._build_genre_similarity_matrix()
    
    def match_track_to_playlists(self, track: TrackInfo, analysis: GenreAnalysis, 
                               available_playlists: List[PlaylistInfo]) -> List[str]:
        """Match a track to appropriate playlists based on genre analysis"""
        matched_playlists = []
        
        # Direct genre matches
        direct_matches = self._find_direct_genre_matches(analysis.predicted_genre, available_playlists)
        matched_playlists.extend(direct_matches)
        
        # Similar genre matches
        similar_matches = self._find_similar_genre_matches(analysis.predicted_genre, available_playlists)
        matched_playlists.extend(similar_matches)
        
        # Remix-specific matching
        if analysis.is_remix:
            remix_matches = self._find_remix_specific_matches(track, analysis, available_playlists)
            matched_playlists.extend(remix_matches)
        
        # Remove duplicates and return
        return list(set(matched_playlists))
    
    def _find_direct_genre_matches(self, genre: Genre, playlists: List[PlaylistInfo]) -> List[str]:
        """Find playlists that directly match the predicted genre"""
        matches = []
        
        for playlist in playlists:
            playlist_genre = self._normalize_genre_name(playlist.genre)
            predicted_genre_name = self._normalize_genre_name(genre.value)
            
            # Direct match
            if playlist_genre == predicted_genre_name:
                matches.append(playlist.id)
            
            # Check if playlist name contains the genre
            playlist_name_lower = playlist.name.lower()
            if predicted_genre_name in playlist_name_lower:
                matches.append(playlist.id)
        
        return matches
    
    def _find_similar_genre_matches(self, genre: Genre, playlists: List[PlaylistInfo]) -> List[str]:
        """Find playlists with similar genres"""
        matches = []
        
        # Get similar genres
        similar_genres = self.genre_similarity_matrix.get(genre, [])
        
        for similar_genre in similar_genres:
            for playlist in playlists:
                playlist_genre = self._normalize_genre_name(playlist.genre)
                similar_genre_name = self._normalize_genre_name(similar_genre.value)
                
                if playlist_genre == similar_genre_name:
                    matches.append(playlist.id)
                
                # Check playlist name
                playlist_name_lower = playlist.name.lower()
                if similar_genre_name in playlist_name_lower:
                    matches.append(playlist.id)
        
        return matches
    
    def _find_remix_specific_matches(self, track: TrackInfo, analysis: GenreAnalysis, 
                                   playlists: List[PlaylistInfo]) -> List[str]:
        """Find playlists specifically for remixes"""
        matches = []
        
        for playlist in playlists:
            playlist_name_lower = playlist.name.lower()
            
            # Look for remix-specific playlists
            remix_keywords = ['remix', 'edit', 'version', 'mix', 'rework']
            for keyword in remix_keywords:
                if keyword in playlist_name_lower:
                    # Check if the playlist genre matches the predicted genre
                    playlist_genre = self._normalize_genre_name(playlist.genre)
                    predicted_genre_name = self._normalize_genre_name(analysis.predicted_genre.value)
                    
                    if playlist_genre == predicted_genre_name or predicted_genre_name in playlist_name_lower:
                        matches.append(playlist.id)
                        break
        
        return matches
    
    def _normalize_genre_name(self, genre_name: str) -> str:
        """Normalize genre name for comparison"""
        if not genre_name:
            return ""
        
        # Convert to lowercase and remove common variations
        normalized = genre_name.lower().strip()
        
        # Handle common variations
        variations = {
            'drum and bass': 'drum & bass',
            'dnb': 'drum & bass',
            'd&b': 'drum & bass',
            'progressive house': 'progressive',
            'progressive trance': 'progressive',
            'deep house': 'house',
            'future bass': 'bass',
            'trap': 'hip hop'
        }
        
        return variations.get(normalized, normalized)
    
    def _build_genre_similarity_matrix(self) -> Dict[Genre, List[Genre]]:
        """Build a matrix of similar genres for better matching"""
        return {
            Genre.HOUSE: [Genre.DEEP_HOUSE, Genre.PROGRESSIVE, Genre.TECHNO],
            Genre.DEEP_HOUSE: [Genre.HOUSE, Genre.AMBIENT, Genre.DOWNTEMPO],
            Genre.TECHNO: [Genre.HOUSE, Genre.INDUSTRIAL, Genre.EXPERIMENTAL],
            Genre.TRANCE: [Genre.PROGRESSIVE, Genre.AMBIENT, Genre.ELECTRONIC],
            Genre.DUBSTEP: [Genre.DRUM_AND_BASS, Genre.TRAP, Genre.FUTURE_BASS],
            Genre.DRUM_AND_BASS: [Genre.DUBSTEP, Genre.BREAKBEAT, Genre.TECHNO],
            Genre.BREAKBEAT: [Genre.DRUM_AND_BASS, Genre.TECHNO, Genre.EXPERIMENTAL],
            Genre.AMBIENT: [Genre.DOWNTEMPO, Genre.DEEP_HOUSE, Genre.EXPERIMENTAL],
            Genre.DOWNTEMPO: [Genre.AMBIENT, Genre.DEEP_HOUSE, Genre.CHILLOUT],
            Genre.PROGRESSIVE: [Genre.TRANCE, Genre.HOUSE, Genre.ELECTRONIC],
            Genre.FUTURE_BASS: [Genre.DUBSTEP, Genre.TRAP, Genre.ELECTRONIC],
            Genre.TRAP: [Genre.HIP_HOP, Genre.DUBSTEP, Genre.FUTURE_BASS],
            Genre.ELECTRONIC: [Genre.TECHNO, Genre.TRANCE, Genre.PROGRESSIVE],
            Genre.EXPERIMENTAL: [Genre.AMBIENT, Genre.TECHNO, Genre.BREAKBEAT]
        }
    
    def create_playlist_suggestions(self, genre: Genre, existing_playlists: List[PlaylistInfo]) -> List[str]:
        """Create suggestions for new playlists based on genre"""
        suggestions = []
        
        # Check if we already have playlists for this genre
        existing_genres = {self._normalize_genre_name(p.genre) for p in existing_playlists}
        predicted_genre_name = self._normalize_genre_name(genre.value)
        
        if predicted_genre_name not in existing_genres:
            suggestions.append(f"{genre.value} Music")
        
        # Suggest remix playlists if we don't have them
        has_remix_playlist = any('remix' in p.name.lower() for p in existing_playlists)
        if not has_remix_playlist:
            suggestions.append(f"{genre.value} Remixes")
        
        # Suggest sub-genre playlists
        sub_genre_suggestions = {
            Genre.HOUSE: ["Deep House", "Progressive House", "Tech House"],
            Genre.TECHNO: ["Dark Techno", "Industrial Techno", "Minimal Techno"],
            Genre.TRANCE: ["Uplifting Trance", "Progressive Trance", "Psy Trance"],
            Genre.DUBSTEP: ["Brostep", "Chillstep", "Future Bass"],
            Genre.DRUM_AND_BASS: ["Liquid DnB", "Neurofunk", "Jump Up"]
        }
        
        if genre in sub_genre_suggestions:
            for sub_genre in sub_genre_suggestions[genre]:
                if not any(sub_genre.lower() in p.name.lower() for p in existing_playlists):
                    suggestions.append(sub_genre)
        
        return suggestions
    
    def analyze_playlist_consistency(self, playlists: List[PlaylistInfo]) -> Dict[str, Any]:
        """Analyze the consistency of playlist genres"""
        analysis = {
            'total_playlists': len(playlists),
            'genre_distribution': {},
            'inconsistent_playlists': [],
            'missing_genres': [],
            'recommendations': []
        }
        
        # Count genre distribution
        for playlist in playlists:
            genre = self._normalize_genre_name(playlist.genre)
            analysis['genre_distribution'][genre] = analysis['genre_distribution'].get(genre, 0) + 1
        
        # Find inconsistent playlists (name doesn't match genre)
        for playlist in playlists:
            playlist_name_lower = playlist.name.lower()
            playlist_genre = self._normalize_genre_name(playlist.genre)
            
            if playlist_genre and playlist_genre not in playlist_name_lower:
                analysis['inconsistent_playlists'].append({
                    'name': playlist.name,
                    'genre': playlist.genre,
                    'issue': 'Genre tag does not match playlist name'
                })
        
        # Find missing genres
        common_genres = ['house', 'techno', 'trance', 'dubstep', 'drum & bass', 'ambient']
        existing_genres = set(analysis['genre_distribution'].keys())
        
        for genre in common_genres:
            if genre not in existing_genres:
                analysis['missing_genres'].append(genre)
        
        # Generate recommendations
        if analysis['missing_genres']:
            analysis['recommendations'].append(
                f"Consider creating playlists for missing genres: {', '.join(analysis['missing_genres'])}"
            )
        
        if analysis['inconsistent_playlists']:
            analysis['recommendations'].append(
                f"Review {len(analysis['inconsistent_playlists'])} playlists with inconsistent genre tags"
            )
        
        return analysis
