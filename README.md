# GenreBend Pro

A professional music organization tool that integrates with the Lexicon music organizer API to automatically research and label your music collection with accurate genres, including proper handling of remixes.

## Features

- **🎵 Music Research**: Identifies songs using multiple APIs (MusicBrainz, Last.fm)
- **🔄 Remix Detection**: Recognizes when a song is a remix and analyzes its actual genre
- **🎯 Genre Classification**: Uses audio analysis and metadata to determine accurate genres
- **📋 Playlist Consistency**: Ensures genre tags match your existing playlist structure
- **🤖 Automatic Organization**: Adds songs to appropriate playlists based on genre tags
- **🔗 Lexicon Integration**: Updates song metadata directly in Lexicon

## Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd genrebend-pro
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Enable Lexicon Local API**:
   - Open Lexicon settings
   - Go to Integrations
   - Enable Local API (accessible at http://localhost:48624)

## Configuration

Edit the `.env` file with your API credentials:

```env
# Required API Keys
LASTFM_API_KEY=your_lastfm_api_key

# Optional Configuration
LEXICON_API_URL=http://localhost:48624
MUSICBRAINZ_USER_AGENT=GenreBendPro/1.0
BATCH_SIZE=50
CONFIDENCE_THRESHOLD=0.7
```

### Getting API Keys

- **Last.fm**: Get API key at [Last.fm API](https://www.last.fm/api/account/create)
- **MusicBrainz**: No API key required, but set a user agent

## Usage

### Basic Usage

```bash
# Organize your music collection
python main.py

# Preview changes without making them
python main.py --dry-run

# Analyze your collection
python main.py --analyze
```

### Advanced Usage

```bash
# Train custom genre model
python main.py --train-model training_data.csv

# Use custom config file
python main.py --config custom.env
```

## How It Works

### 1. Music Research
The application researches each track using multiple APIs:
- **Spotify**: Provides audio features, genres, and metadata
- **MusicBrainz**: Offers detailed music information
- **Last.fm**: Supplies additional genre tags and metadata

### 2. Remix Detection
Identifies remixes by analyzing:
- Track titles for keywords (remix, edit, version, etc.)
- Artist names for remix indicators
- Audio characteristics compared to originals

### 3. Genre Classification
Uses two approaches:
- **Audio Analysis**: Extracts features using librosa (MFCC, chroma, spectral features)
- **Metadata Analysis**: Combines genre information from all sources

### 4. Playlist Matching
Matches tracks to playlists by:
- Direct genre matching
- Similar genre matching
- Remix-specific playlist detection
- Consistency with existing playlist structure

## Supported Genres

The application recognizes these electronic music genres:
- House (including Deep House)
- Techno
- Trance (including Progressive Trance)
- Dubstep
- Drum & Bass
- Breakbeat
- Ambient
- Downtempo
- Progressive
- Future Bass
- Trap
- Electronic
- Experimental

## API Endpoints Used

- **Lexicon Local API**: `http://localhost:48624/v1/`
- **Spotify Web API**: `https://api.spotify.com/v1/`
- **MusicBrainz API**: `https://musicbrainz.org/ws/2/`
- **Last.fm API**: `http://ws.audioscrobbler.com/2.0/`

## Project Structure

```
lexicon_music_organizer/
├── src/
│   ├── services/
│   │   ├── lexicon_service.py          # Lexicon API integration
│   │   ├── music_research_service.py  # Music research and remix detection
│   │   ├── genre_detection_service.py # Genre classification
│   │   ├── playlist_matching_service.py # Playlist matching logic
│   │   └── music_organizer_service.py  # Main orchestration
│   ├── models/
│   │   └── track_models.py            # Data models
│   └── utils/
│       └── config.py                  # Configuration management
├── main.py                            # Main application entry point
├── requirements.txt                   # Python dependencies
├── .env.example                      # Configuration template
└── README.md                         # This file
```

## Error Handling

The application includes comprehensive error handling:
- API rate limiting and retries
- Graceful handling of missing files
- Detailed logging for debugging
- Batch processing to avoid overwhelming APIs

## Logging

Logs are written to both console and `lexicon_music_organizer.log` file. Log levels:
- `INFO`: General progress information
- `DEBUG`: Detailed processing information
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors

## Troubleshooting

### Common Issues

1. **Lexicon API Connection Failed**
   - Ensure Lexicon is running
   - Check that Local API is enabled in settings
   - Verify the API URL is correct

2. **Spotify API Errors**
   - Verify your client ID and secret
   - Check API quota limits
   - Ensure proper authentication

3. **Audio Analysis Failures**
   - Check file paths are accessible
   - Verify audio file formats are supported
   - Ensure librosa can read the files

### Performance Tips

- Use `--dry-run` to preview changes
- Adjust `BATCH_SIZE` based on your system
- Set appropriate `CONFIDENCE_THRESHOLD`
- Monitor API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information
