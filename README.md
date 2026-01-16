# Ekantipur Scraper

A Python web scraper that extracts entertainment news articles and the daily cartoon from [ekantipur.com](https://ekantipur.com), Nepal's leading news website.

## Features

- 🎬 **Entertainment News**: Extracts the top 5 entertainment news articles with:
  - Title
  - Image URL
  - Category
  - Author

- 🎨 **Cartoon of the Day**: Extracts the daily cartoon (व्यंग्यिचत्र) with:
  - Title
  - Image URL
  - Author/Cartoonist name

- 💾 **JSON Output**: Saves all extracted data to a structured JSON file

## Requirements

- Python 3.12 or higher
- Playwright

## Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd ekantipur-scraper
   ```

2. **Install dependencies** using `uv` (recommended):
   ```bash
   uv sync
   ```

   Or using `pip`:
   ```bash
   pip install playwright
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

## Usage

Run the scraper:

```bash
python scraper.py
```

Or if using `uv`:

```bash
uv run scraper.py
```

The scraper will:
1. Navigate to the ekantipur.com entertainment section
2. Extract the top 5 entertainment news articles
3. Extract the Cartoon of the Day
4. Save all data to `output.json`

## Output Format

The scraper generates a JSON file (`output.json`) with the following structure:

```json
{
  "entertainment_news": [
    {
      "title": "Article Title",
      "image_url": "https://...",
      "category": "मनोरञ्जन",
      "author": "Author Name"
    }
  ],
  "cartoon_of_the_day": {
    "title": "Cartoon Title",
    "image_url": "https://...",
    "author": "Cartoonist Name"
  }
}
```

## How It Works

The scraper uses **Playwright** to:
- Load the website in a headless browser
- Wait for dynamic content to load
- Use multiple fallback selectors to find articles and cartoons (ensuring robustness)
- Extract structured data from the HTML
- Save results to JSON

### Selector Strategy

The scraper implements a **defensive, multi-strategy approach** with multiple selector patterns to ensure reliability even if the website structure changes:

- Multiple CSS selectors for articles (`article`, `.news-item`, `[class*='news']`, etc.)
- Fallback selectors for titles, images, and authors
- XPath selectors for finding cartoon sections
- Automatic retry mechanisms with delays for dynamic content

## Project Structure

```
ekantipur-scraper/
├── scraper.py          # Main scraper implementation
├── main.py             # Entry point (placeholder)
├── output.json         # Generated output file
├── pyproject.toml      # Project dependencies
├── README.md           # This file
└── DOCUMENTATION.md    # Detailed technical documentation
```

## Technical Details

- **Browser**: Chromium (via Playwright)
- **Headless Mode**: Disabled by default (set `headless=True` in `scraper.py` to enable)
- **Timeout**: 60 seconds for page navigation
- **Wait Strategy**: DOM content loaded + additional delays for dynamic content

## Troubleshooting

### Browser Installation Issues
If Playwright browsers aren't installed:
```bash
playwright install chromium
```

### No Articles Found
- The website structure may have changed
- Check your internet connection
- The scraper uses multiple fallback selectors, but website updates may require selector adjustments

### Cartoon Not Found
- The cartoon may not be available on the entertainment page
- The scraper automatically checks the homepage as a fallback

## Development

For detailed technical documentation about selector extraction, development process, and code flow, see [DOCUMENTATION.md](DOCUMENTATION.md).

## License

This project is for educational purposes. Please respect ekantipur.com's terms of service and robots.txt when using this scraper.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Disclaimer

This scraper is for educational and personal use only. Always respect website terms of service and rate limits. The authors are not responsible for any misuse of this tool.
