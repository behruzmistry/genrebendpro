import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    # Load .env file if it exists
    load_dotenv()
    
    config = {
        # Lexicon API Configuration
        'LEXICON_API_URL': os.getenv('LEXICON_API_URL', 'http://localhost:48624'),
        'LEXICON_API_VERSION': os.getenv('LEXICON_API_VERSION', 'v1'),
        
        # Last.fm API Configuration
        'LASTFM_API_KEY': os.getenv('LASTFM_API_KEY'),
        
        # MusicBrainz Configuration
        'MUSICBRAINZ_USER_AGENT': os.getenv('MUSICBRAINZ_USER_AGENT', 'GenreBendPro/1.0'),
        
        # Application Settings
        'BATCH_SIZE': int(os.getenv('BATCH_SIZE', '50')),
        'MAX_RETRIES': int(os.getenv('MAX_RETRIES', '3')),
        'RETRY_DELAY': float(os.getenv('RETRY_DELAY', '1.0')),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        
        # Audio Analysis Settings
        'AUDIO_SAMPLE_RATE': int(os.getenv('AUDIO_SAMPLE_RATE', '22050')),
        'AUDIO_DURATION_LIMIT': int(os.getenv('AUDIO_DURATION_LIMIT', '30')),
        'MFCC_FEATURES': int(os.getenv('MFCC_FEATURES', '13')),
        'CHROMA_FEATURES': int(os.getenv('CHROMA_FEATURES', '12')),
        
        # Genre Classification Settings
        'CONFIDENCE_THRESHOLD': float(os.getenv('CONFIDENCE_THRESHOLD', '0.7')),
        'REMIX_KEYWORDS': os.getenv('REMIX_KEYWORDS', 'remix,edit,version,mix,rework,reinterpretation').split(',')
    }
    
    return config

def setup_logging(log_level: str = 'INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('genrebend-pro.log')
        ]
    )

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate that required configuration is present"""
    required_keys = [
        'LEXICON_API_URL',
        'LASTFM_API_KEY'
    ]
    
    missing_keys = []
    for key in required_keys:
        if not config.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"Missing required configuration: {', '.join(missing_keys)}")
        print("Please check your .env file and ensure all required API keys are set.")
        return False
    
    return True
