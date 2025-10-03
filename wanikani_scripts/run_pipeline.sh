#!/bin/bash
# Quick wrapper script for WaniKani → Anki pipeline

set -e  # Exit on error

cd "$(dirname "$0")"  # Change to script directory

echo "=================================="
echo "WaniKani → Anki Deck Generator"
echo "=================================="
echo ""

# Check if env.py exists
if [ ! -f "env.py" ]; then
    echo "❌ Error: env.py not found!"
    echo ""
    echo "Please create env.py with your credentials:"
    echo ""
    echo "WANIKANI_TOKEN = \"your-api-token\""
    echo "DATABASE_URL = \"postgresql://user:pass@localhost:5432/wanikani\""
    echo ""
    exit 1
fi

# Parse command line arguments
MODE="default"

while [[ $# -gt 0 ]]; do
    case $1 in
        --fresh|-f)
            MODE="fresh"
            shift
            ;;
        --no-cache|-n)
            MODE="no-cache"
            shift
            ;;
        --help|-h)
            echo "Usage: ./run_pipeline.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no options)     Use cached data if < 180 days old (default)"
            echo "  --fresh, -f      Force fresh data from WaniKani API"
            echo "  --no-cache, -n   Never use cache, always fetch fresh"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_pipeline.sh              # Smart caching"
            echo "  ./run_pipeline.sh --fresh      # Get latest data"
            echo "  ./run_pipeline.sh --no-cache   # Always fetch fresh"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the pipeline
case $MODE in
    fresh)
        echo "🔄 Fetching fresh data from WaniKani API..."
        python wanikani_prefect_flow.py --fresh
        ;;
    no-cache)
        echo "🔄 Running without cache (always fresh)..."
        python wanikani_prefect_flow.py --no-cache
        ;;
    *)
        echo "💡 Using smart caching (fetch if cache > 180 days old)..."
        python wanikani_prefect_flow.py
        ;;
esac

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Pipeline completed successfully!"
    echo "=================================="
    echo ""
    echo "📦 Generated decks in: ankidecks/"
    echo ""
    echo "Import these files into Anki:"
    echo "  • WaniKani_Complete_Deck.apkg (all cards)"
    echo "  • WaniKani_Radical_Deck.apkg"
    echo "  • WaniKani_Kanji_Deck.apkg"
    echo "  • WaniKani_Vocabulary_Deck.apkg"
else
    echo ""
    echo "=================================="
    echo "❌ Pipeline failed!"
    echo "=================================="
    echo ""
    echo "Check the error messages above for details."
    exit $EXIT_CODE
fi
