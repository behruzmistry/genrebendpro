# GenreBend Pro - Quick Start Guide

## 1. Setup (5 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit configuration
cp .env.example .env
# Edit .env with your API keys
```

## 2. Get API Keys

- **Last.fm**: Go to [Last.fm API](https://www.last.fm/api/account/create)
  - Create an API account
  - Copy API key to .env

## 3. Enable Lexicon API

- Open Lexicon
- Go to Settings → Integrations
- Enable "Local API"
- Note: API runs on http://localhost:48624

## 4. Test the Application

```bash
# Analyze your collection (safe, no changes)
python main.py --analyze

# Preview changes (dry run)
python main.py --dry-run

# Run the actual organization
python main.py
```

## 5. Monitor Progress

- Watch the console output for progress
- Check `genrebend-pro.log` for detailed logs
- The app processes tracks in batches to avoid API limits

## Troubleshooting

**"Cannot connect to Lexicon API"**
- Ensure Lexicon is running
- Check that Local API is enabled
- Verify the API URL in .env

**"Last.fm API errors"**
- Verify your API key
- Check API quota limits

**"No tracks found"**
- Ensure your Lexicon library has tracks
- Check file paths are accessible

## Next Steps

- Review the full README.md for advanced features
- Check examples/basic_usage.py for code examples
- Customize genre detection in src/services/genre_detection_service.py
