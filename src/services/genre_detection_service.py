import librosa
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
from typing import List, Dict, Any, Optional, Tuple
import os
import pickle
from ..models.track_models import TrackInfo, GenreAnalysis, Genre, MusicResearchResult

logger = logging.getLogger(__name__)


class GenreDetectionService:
    """Service for detecting music genres using audio analysis and metadata"""
    
    def __init__(self, sample_rate: int = 22050, duration_limit: int = 30):
        self.sample_rate = sample_rate
        self.duration_limit = duration_limit
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Genre mapping for consistency with playlists
        self.genre_mapping = {
            'house': Genre.HOUSE,
            'deep house': Genre.DEEP_HOUSE,
            'progressive house': Genre.PROGRESSIVE,
            'techno': Genre.TECHNO,
            'trance': Genre.TRANCE,
            'progressive trance': Genre.TRANCE,
            'dubstep': Genre.DUBSTEP,
            'drum and bass': Genre.DRUM_AND_BASS,
            'dnb': Genre.DRUM_AND_BASS,
            'breakbeat': Genre.BREAKBEAT,
            'ambient': Genre.AMBIENT,
            'downtempo': Genre.DOWNTEMPO,
            'future bass': Genre.FUTURE_BASS,
            'trap': Genre.TRAP,
            'electronic': Genre.ELECTRONIC,
            'experimental': Genre.EXPERIMENTAL
        }
    
    def analyze_track(self, track: TrackInfo, research_result: MusicResearchResult) -> GenreAnalysis:
        """Analyze a track to determine its genre"""
        predicted_genre = Genre.UNKNOWN
        confidence = 0.0
        analysis_method = "metadata_only"
        audio_features = {}
        metadata_features = {}
        
        # Try audio analysis if file path is available
        if track.file_path and os.path.exists(track.file_path):
            try:
                audio_features = self._extract_audio_features(track.file_path)
                if self.is_trained and audio_features:
                    predicted_genre, confidence = self._predict_from_audio(audio_features)
                    analysis_method = "audio_analysis"
            except Exception as e:
                logger.warning(f"Audio analysis failed for {track.title}: {e}")
        
        # Fallback to metadata analysis
        if predicted_genre == Genre.UNKNOWN or confidence < 0.7:
            predicted_genre, confidence = self._predict_from_metadata(track, research_result)
            analysis_method = "metadata_analysis"
        
        # Extract metadata features for analysis
        metadata_features = self._extract_metadata_features(track, research_result)
        
        # Generate playlist suggestions
        playlist_suggestions = self._generate_playlist_suggestions(predicted_genre)
        
        return GenreAnalysis(
            track_id=track.id,
            predicted_genre=predicted_genre,
            confidence=confidence,
            is_remix=research_result.is_remix,
            analysis_method=analysis_method,
            audio_features=audio_features,
            metadata_features=metadata_features,
            playlist_suggestions=playlist_suggestions
        )
    
    def _extract_audio_features(self, file_path: str) -> Dict[str, Any]:
        """Extract audio features from a music file"""
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=self.sample_rate, duration=self.duration_limit)
            
            # Extract various audio features
            features = {}
            
            # Spectral features
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}'] = np.mean(mfccs[i])
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            for i in range(12):
                features[f'chroma_{i}'] = np.mean(chroma[i])
            
            # Rhythm features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = tempo
            features['beat_strength'] = np.mean(librosa.feature.rms(y=y))
            
            # Tonality features
            tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
            for i in range(6):
                features[f'tonnetz_{i}'] = np.mean(tonnetz[i])
            
            # Harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            features['harmonic_ratio'] = np.mean(y_harmonic) / (np.mean(y_harmonic) + np.mean(y_percussive))
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract audio features from {file_path}: {e}")
            return {}
    
    def _extract_metadata_features(self, track: TrackInfo, research_result: MusicResearchResult) -> Dict[str, Any]:
        """Extract features from track metadata"""
        features = {}
        
        # Basic track info
        features['duration'] = track.duration or 0
        features['bpm'] = track.bpm or 0
        features['year'] = track.year or 0
        features['is_remix'] = int(research_result.is_remix)
        
        # Title and artist length (can indicate genre)
        features['title_length'] = len(track.title)
        features['artist_length'] = len(track.artist)
        
        # Extract genres from research results
        genres = research_result.combined_genres or []
        features['genre_count'] = len(genres)
        
        # Spotify features if available
        if research_result.spotify_data and research_result.spotify_data.get('features'):
            spotify_features = research_result.spotify_data['features']
            features['danceability'] = spotify_features.get('danceability', 0)
            features['energy'] = spotify_features.get('energy', 0)
            features['valence'] = spotify_features.get('valence', 0)
            features['acousticness'] = spotify_features.get('acousticness', 0)
            features['instrumentalness'] = spotify_features.get('instrumentalness', 0)
            features['liveness'] = spotify_features.get('liveness', 0)
            features['speechiness'] = spotify_features.get('speechiness', 0)
        
        return features
    
    def _predict_from_audio(self, audio_features: Dict[str, Any]) -> Tuple[Genre, float]:
        """Predict genre from audio features using trained model"""
        if not self.is_trained or not self.model:
            return Genre.UNKNOWN, 0.0
        
        try:
            # Convert features to array
            feature_array = np.array([list(audio_features.values())])
            
            # Scale features
            feature_array_scaled = self.scaler.transform(feature_array)
            
            # Make prediction
            prediction = self.model.predict(feature_array_scaled)[0]
            probabilities = self.model.predict_proba(feature_array_scaled)[0]
            
            # Get confidence (max probability)
            confidence = np.max(probabilities)
            
            # Convert prediction to Genre enum
            genre_names = self.model.classes_
            predicted_genre_name = genre_names[prediction]
            
            # Map to our Genre enum
            predicted_genre = self.genre_mapping.get(predicted_genre_name.lower(), Genre.UNKNOWN)
            
            return predicted_genre, confidence
            
        except Exception as e:
            logger.error(f"Audio prediction failed: {e}")
            return Genre.UNKNOWN, 0.0
    
    def _predict_from_metadata(self, track: TrackInfo, research_result: MusicResearchResult) -> Tuple[Genre, float]:
        """Predict genre from metadata using rule-based approach"""
        genres = research_result.combined_genres or []
        confidence = 0.0
        predicted_genre = Genre.UNKNOWN
        
        if not genres:
            return predicted_genre, confidence
        
        # Count genre occurrences
        genre_counts = {}
        for genre in genres:
            genre_lower = genre.lower()
            genre_counts[genre_lower] = genre_counts.get(genre_lower, 0) + 1
        
        # Find the most common genre
        if genre_counts:
            most_common = max(genre_counts.items(), key=lambda x: x[1])
            predicted_genre_name = most_common[0]
            confidence = most_common[1] / len(genres)
            
            # Map to our Genre enum
            predicted_genre = self.genre_mapping.get(predicted_genre_name, Genre.UNKNOWN)
        
        # Special handling for remixes
        if research_result.is_remix and predicted_genre != Genre.UNKNOWN:
            # For remixes, we might want to adjust the genre based on the remix characteristics
            # This is a simplified approach - in practice, you'd analyze the remix more deeply
            confidence *= 0.8  # Slightly reduce confidence for remixes
        
        return predicted_genre, confidence
    
    def _generate_playlist_suggestions(self, genre: Genre) -> List[str]:
        """Generate playlist suggestions based on predicted genre"""
        suggestions = []
        
        # Map genres to common playlist names
        playlist_mapping = {
            Genre.HOUSE: ["House Music", "Deep House", "House Classics"],
            Genre.DEEP_HOUSE: ["Deep House", "House Music", "Chill House"],
            Genre.TECHNO: ["Techno", "Dark Techno", "Industrial Techno"],
            Genre.TRANCE: ["Trance", "Progressive Trance", "Uplifting Trance"],
            Genre.DUBSTEP: ["Dubstep", "Bass Music", "Electronic"],
            Genre.DRUM_AND_BASS: ["Drum & Bass", "DnB", "Liquid DnB"],
            Genre.BREAKBEAT: ["Breakbeat", "Big Beat", "Breaks"],
            Genre.AMBIENT: ["Ambient", "Chillout", "Relaxing"],
            Genre.DOWNTEMPO: ["Downtempo", "Chill", "Lounge"],
            Genre.PROGRESSIVE: ["Progressive", "Progressive House", "Progressive Trance"],
            Genre.FUTURE_BASS: ["Future Bass", "Bass Music", "Electronic"],
            Genre.TRAP: ["Trap", "Hip Hop", "Bass Music"],
            Genre.ELECTRONIC: ["Electronic", "EDM", "Electronic Music"],
            Genre.EXPERIMENTAL: ["Experimental", "Avant-garde", "Abstract"]
        }
        
        suggestions = playlist_mapping.get(genre, ["Electronic", "Music"])
        return suggestions
    
    def train_model(self, training_data: List[Tuple[Dict[str, Any], str]]) -> bool:
        """Train the genre classification model"""
        try:
            if not training_data:
                logger.warning("No training data provided")
                return False
            
            # Separate features and labels
            X = []
            y = []
            
            for features, genre in training_data:
                X.append(list(features.values()))
                y.append(genre)
            
            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            logger.info(f"Model trained successfully. Train score: {train_score:.3f}, Test score: {test_score:.3f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def save_model(self, file_path: str) -> bool:
        """Save the trained model to disk"""
        try:
            if not self.is_trained or not self.model:
                logger.warning("No trained model to save")
                return False
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, file_path: str) -> bool:
        """Load a trained model from disk"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Model file not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
