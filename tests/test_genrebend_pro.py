#!/usr/bin/env python3
"""
Test suite for GenreBend Pro
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.track_models import TrackInfo, Genre, MusicResearchResult
from src.services.music_research_service import MusicResearchService


class TestTrackModels:
    """Test track model classes"""
    
    def test_track_info_creation(self):
        """Test TrackInfo creation"""
        track = TrackInfo(
            id="test_001",
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        assert track.id == "test_001"
        assert track.title == "Test Song"
        assert track.artist == "Test Artist"
        assert track.album == "Test Album"
        assert track.is_remix is False
    
    def test_genre_enum(self):
        """Test Genre enum values"""
        assert Genre.HOUSE.value == "House"
        assert Genre.TECHNO.value == "Techno"
        assert Genre.UNKNOWN.value == "Unknown"
    
    def test_music_research_result(self):
        """Test MusicResearchResult creation"""
        result = MusicResearchResult(track_id="test_001")
        
        assert result.track_id == "test_001"
        assert result.spotify_data is None
        assert result.lastfm_data is None
        assert result.musicbrainz_data is None
        assert result.combined_genres is None
        assert result.is_remix is False
        assert result.confidence == 0.0


class TestMusicResearchService:
    """Test MusicResearchService"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = MusicResearchService(
            lastfm_api_key="test_key",
            musicbrainz_user_agent="TestAgent/1.0"
        )
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert self.service.lastfm_api_key == "test_key"
        assert self.service.musicbrainz_user_agent == "TestAgent/1.0"
        assert len(self.service.remix_keywords) > 0
    
    def test_clean_title_for_search(self):
        """Test title cleaning"""
        # Test file extension removal
        clean = self.service._clean_title_for_search("song.mp3")
        assert clean == "song"
        
        # Test track number removal
        clean = self.service._clean_title_for_search("01 - song")
        assert clean == "song"
        
        # Test trailing numbers
        clean = self.service._clean_title_for_search("song 2023")
        assert clean == "song"
    
    def test_clean_artist_for_search(self):
        """Test artist name cleaning"""
        # Test "The" removal
        clean = self.service._clean_artist_for_search("The Beatles")
        assert clean == "beatles"
        
        # Test "A" removal
        clean = self.service._clean_artist_for_search("A Tribe Called Quest")
        assert clean == "tribe called quest"
    
    def test_detect_remix(self):
        """Test remix detection"""
        track = TrackInfo(id="test", title="Song (Remix)", artist="Artist")
        
        # Mock data
        lastfm_data = {"name": "Song (Remix)", "artist": {"name": "Artist"}}
        musicbrainz_data = {"title": "Song (Remix)"}
        
        is_remix = self.service._detect_remix(track, lastfm_data, musicbrainz_data)
        assert is_remix is True
    
    def test_calculate_similarity(self):
        """Test string similarity calculation"""
        # Test identical strings
        similarity = self.service._calculate_similarity("hello world", "hello world")
        assert similarity == 1.0
        
        # Test different strings
        similarity = self.service._calculate_similarity("hello", "world")
        assert similarity == 0.0
        
        # Test partial match
        similarity = self.service._calculate_similarity("hello world", "hello there")
        assert 0 < similarity < 1


class TestIntegration:
    """Integration tests"""
    
    @patch('src.services.music_research_service.requests.get')
    def test_lastfm_search_mock(self, mock_get):
        """Test Last.fm search with mocked response"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "track": {
                "name": "Test Song",
                "artist": {"name": "Test Artist"},
                "toptags": {"tag": [{"name": "electronic"}]}
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service = MusicResearchService(
            lastfm_api_key="test_key",
            musicbrainz_user_agent="TestAgent/1.0"
        )
        
        track = TrackInfo(id="test", title="Test Song", artist="Test Artist")
        result = service._search_lastfm(track)
        
        assert result is not None
        assert result["name"] == "Test Song"
        assert result["artist"]["name"] == "Test Artist"


if __name__ == "__main__":
    pytest.main([__file__])
