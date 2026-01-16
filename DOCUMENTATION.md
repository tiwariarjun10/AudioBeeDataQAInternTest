# Ekantipur Scraper - Technical Documentation

## Overview
This document explains the development process, selector extraction methodology, Cursor AI usage, and overall code flow of the ekantipur.com web scraper.

---

## 1. How Selectors Were Extracted

### 1.1 Strategy: Multiple Fallback Selectors

Since we couldn't inspect the live website's HTML structure directly, we implemented a **defensive, multi-strategy approach** using multiple selector patterns. This ensures the scraper works even if the website structure changes.

### 1.2 Entertainment News Article Selectors

**Primary Strategy: Multiple CSS Selector Attempts**
```python
selectors = [
    "article",                    # Semantic HTML5 element
    ".news-item",                 # Common class pattern
    ".article-item",              # Alternative class pattern
    "[class*='news']",            # Partial class match (flexible)
    "[class*='article']"          # Partial class match (flexible)
]
```

**Rationale:**
- `article`: Modern websites use semantic HTML5 elements
- `.news-item`, `.article-item`: Common naming conventions
- `[class*='news']`: Attribute selector that matches any class containing "news" (e.g., "news-item", "news-card", "latest-news")
- This approach tries each selector until it finds at least 5 articles

### 1.3 Title Extraction Selectors

**Multiple Selector Patterns:**
```python
title_selectors = [
    "h2 a", "h3 a",              # Heading with link (most common)
    "h2", "h3",                  # Direct heading elements
    "a[href*='/entertainment']", # Links to entertainment section
    ".title",                    # Common class name
    "[class*='title']"           # Partial class match
]
```

**Why Multiple Selectors?**
- Different websites structure titles differently
- Some use `<h2><a>Title</a></h2>`, others use `<h2>Title</h2>` with separate link
- Fallback ensures we capture the title even if structure varies

### 1.4 Image URL Extraction

**Handles Multiple Image Loading Patterns:**
```python
img_selectors = ["img", "picture img", "[class*='image'] img"]
# Also checks both 'src' and 'data-src' attributes
img_src = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
```

**Key Features:**
- Checks `src` (standard) and `data-src` (lazy loading)
- Handles both absolute and relative URLs
- Uses `urljoin()` to convert relative URLs to absolute

### 1.5 Cartoon Section Selectors

**Three-Tier Strategy:**

**Strategy 1: Text-Based XPath Search**
```python
xpath_selector = f"//*[contains(text(), '{search_text}')]"
# Searches for: "व्यंग्यिचत्र", "cartoon", "Cartoon", "व्यंग्य"
```
- Uses XPath to find elements containing specific text
- Then navigates to parent container using `ancestor::*`

**Strategy 2: CSS Class/ID Selectors**
```python
cartoon_selectors = [
    "[class*='cartoon']",    # Any class containing "cartoon"
    "[id*='cartoon']",       # Any ID containing "cartoon"
    ".cartoon",              # Exact class match
    "#cartoon",              # Exact ID match
    "[class*='व्यंग्य']"     # Nepali text in class
]
```

**Strategy 3: Image Attribute Analysis**
```python
# Scans all images for cartoon-related keywords
if any(text in img_src.lower() or text in alt_text.lower() 
       for text in ["cartoon", "व्यंग्य", "cartoonist"]):
    # Extract parent container
```

---

## 2. How Cursor Was Used

### 2.1 Initial Development

**Step 1: Project Setup**
- Used Cursor's file reading capabilities to check existing project structure
- Read `pyproject.toml` to understand dependencies
- Identified Playwright was already configured

**Step 2: Code Generation**
- Provided task requirements to Cursor
- Cursor generated initial scraper structure with:
  - Playwright browser automation setup
  - Navigation logic
  - Basic extraction patterns

### 2.2 Iterative Refinement

**Error Handling:**
- When timeout errors occurred, Cursor helped:
  - Identify the problematic `networkidle` wait
  - Replace with more lenient `load` state
  - Add try-except blocks for graceful degradation

**Selector Refinement:**
- Cursor suggested multiple selector strategies
- Helped implement fallback mechanisms
- Added retry logic with multiple attempts

### 2.3 Feature Addition

**Task 2 Implementation:**
- Used Cursor to add cartoon extraction function
- Cursor helped design the multi-strategy approach
- Assisted with XPath and CSS selector combinations
- Implemented homepage fallback logic

### 2.4 Code Quality

**Cursor Assisted With:**
- Proper error handling patterns
- Code organization and modularity
- Documentation strings
- Type hints consideration
- Linting error resolution

---

## 3. Overall Code Flow

### 3.1 High-Level Flow Diagram

```
main()
  │
  ├─→ extract_entertainment_news()
  │     │
  │     ├─→ Launch Playwright Browser
  │     │
  │     ├─→ Navigate to Entertainment Page
  │     │     ├─→ Wait for page load (lenient)
  │     │     ├─→ Scroll to trigger lazy loading
  │     │     └─→ Wait for content
  │     │
  │     ├─→ Find Articles (Multi-selector strategy)
  │     │     ├─→ Try selector 1: "article"
  │     │     ├─→ Try selector 2: ".news-item"
  │     │     ├─→ Try selector 3: "[class*='news']"
  │     │     └─→ Retry up to 3 times if needed
  │     │
  │     ├─→ Extract Top 5 Articles
  │     │     ├─→ For each article:
  │     │     │     ├─→ Extract Title (multi-selector)
  │     │     │     ├─→ Extract Image URL (with lazy load support)
  │     │     │     ├─→ Extract Category (default: "मनोरञ्जन")
  │     │     │     └─→ Extract Author (null if not found)
  │     │     └─→ Skip if no title found
  │     │
  │     ├─→ Extract Cartoon of the Day
  │     │     ├─→ Try Strategy 1: Text-based XPath
  │     │     ├─→ Try Strategy 2: CSS selectors
  │     │     ├─→ Try Strategy 3: Image attribute scan
  │     │     └─→ If not found, navigate to homepage and retry
  │     │
  │     └─→ Close Browser
  │
  ├─→ save_to_json(result)
  │     └─→ Write to output.json with UTF-8 encoding
  │
  └─→ Print Summary
```

### 3.2 Detailed Function Flow

#### `main()` Function
```python
1. Print startup messages
2. Call extract_entertainment_news()
3. Call save_to_json()
4. Print success summary
5. Handle exceptions
```

#### `extract_entertainment_news()` Function
```python
1. Initialize result dictionary
2. Launch Playwright browser (headless=False for debugging)
3. Create new page
4. Navigate to entertainment URL
5. Wait for page load (with timeout handling)
6. Scroll to trigger lazy-loaded images
7. Find articles using multiple selector strategies
8. Extract data from top 5 articles:
   - Title (try multiple selectors)
   - Image URL (handle lazy loading)
   - Category (with fallback)
   - Author (null if missing)
9. Extract cartoon (with homepage fallback)
10. Close browser
11. Return result dictionary
```

#### `extract_cartoon_of_the_day(page)` Function
```python
1. Initialize cartoon_data dictionary
2. Strategy 1: Search for text "व्यंग्यिचत्र" or "cartoon"
   - Use XPath to find elements
   - Navigate to parent container
3. Strategy 2: Try CSS selectors
   - [class*='cartoon'], [id*='cartoon'], etc.
4. Strategy 3: Scan images
   - Check src/alt attributes for cartoon keywords
   - Extract parent container
5. If section found:
   - Extract title (with validation)
   - Extract image URL (full URL conversion)
   - Extract author (with name validation)
6. Fallback: Direct image search
7. Return cartoon_data
```

### 3.3 Error Handling Strategy

**Defensive Programming Approach:**
- Every extraction step wrapped in try-except
- Multiple selector attempts prevent single-point failures
- Graceful degradation (use defaults if extraction fails)
- Continue processing even if individual elements fail

**Example:**
```python
try:
    title = article.locator("h2 a").first.inner_text().strip()
except:
    try:
        title = article.locator("h2").first.inner_text().strip()
    except:
        title = None
```

### 3.4 Data Flow

```
Website HTML
    ↓
Playwright Page Object
    ↓
Locator API (CSS/XPath selectors)
    ↓
Extracted Raw Data (strings)
    ↓
Data Processing (URL conversion, validation)
    ↓
Structured Dictionary
    ↓
JSON Serialization
    ↓
output.json file
```

### 3.5 Key Design Decisions

**1. Multiple Selector Strategy**
- **Why:** Websites change structure; single selector is fragile
- **How:** Try multiple selectors in order of specificity
- **Benefit:** Higher success rate, more resilient

**2. Lenient Page Loading**
- **Why:** `networkidle` times out on sites with continuous requests
- **How:** Use `domcontentloaded` + `load` with timeout handling
- **Benefit:** Works on sites with analytics/ads

**3. Lazy Loading Support**
- **Why:** Modern sites use lazy loading for images
- **How:** Check both `src` and `data-src` attributes
- **Benefit:** Captures images that load on scroll

**4. Retry Logic**
- **Why:** Dynamic content may not load immediately
- **How:** Multiple attempts with delays
- **Benefit:** Handles slow-loading content

**5. Homepage Fallback for Cartoon**
- **Why:** Cartoon might be on homepage, not entertainment page
- **How:** Check homepage if not found on entertainment page
- **Benefit:** Higher success rate for cartoon extraction

---

## 4. Selector Extraction Methodology

### 4.1 Why Multiple Selectors?

**Problem:** Without direct HTML inspection, we don't know the exact structure.

**Solution:** Use common web development patterns:
- Semantic HTML5 elements (`<article>`, `<section>`)
- Common class naming conventions (`.news-item`, `.article-item`)
- Partial attribute matching (`[class*='news']`)
- Multiple heading levels (`h2`, `h3`)

### 4.2 Selector Priority

**Order of Attempt:**
1. **Most Specific:** Exact class/ID matches (`.news-item`)
2. **Semantic:** HTML5 elements (`article`)
3. **Flexible:** Partial matches (`[class*='news']`)
4. **Fallback:** Generic elements (`img`, `a`)

### 4.3 XPath vs CSS Selectors

**CSS Selectors Used For:**
- Standard element selection
- Class/ID matching
- Attribute selection
- Simpler and more readable

**XPath Used For:**
- Text content search (`contains(text(), 'cartoon')`)
- Ancestor navigation (`ancestor::*`)
- Complex tree traversal
- More powerful but verbose

---

## 5. Testing and Validation

### 5.1 Validation Checks

**Title Extraction:**
- Skip articles without titles
- Validate title is not empty after strip()

**Image URL:**
- Convert relative URLs to absolute
- Handle both `src` and `data-src` attributes
- Validate URL format

**Author Extraction:**
- Check for reasonable length (< 50 chars)
- Validate it's not just section header text
- Use null if not found (as per requirements)

**Category:**
- Default to "मनोरञ्जन" if not found
- Validate extracted category contains expected keywords

### 5.2 Error Scenarios Handled

1. **Timeout Errors:** Lenient wait strategies
2. **Missing Elements:** Try-except with fallbacks
3. **Empty Results:** Validation before adding to results
4. **Lazy Loading:** Check multiple image attributes
5. **Relative URLs:** Convert to absolute using urljoin()

---

## 6. Output Structure

```json
{
  "entertainment_news": [
    {
      "title": "Article title in Nepali",
      "image_url": "https://full-url-to-image.jpg",
      "category": "मनोरञ्जन",
      "author": "Author name or null"
    },
    // ... 4 more articles
  ],
  "cartoon_of_the_day": {
    "title": "Cartoon title or 'व्यंग्यिचत्र'",
    "image_url": "https://full-url-to-cartoon.jpg",
    "author": "Cartoonist name or null"
  }
}
```

---

## 7. Future Improvements

1. **Selector Discovery:** Add browser DevTools integration to auto-discover selectors
2. **Caching:** Cache page structure to avoid repeated selector attempts
3. **Configuration:** Externalize selectors to config file for easy updates
4. **Monitoring:** Add logging for selector success rates
5. **Testing:** Add unit tests for selector patterns

---

## Conclusion

This scraper uses a **defensive, multi-strategy approach** that:
- Tries multiple selector patterns
- Handles errors gracefully
- Supports modern web features (lazy loading, dynamic content)
- Works without prior knowledge of exact HTML structure
- Provides fallback mechanisms for robustness

The combination of Cursor AI assistance and strategic selector design resulted in a robust, maintainable web scraper that can adapt to website structure changes.
