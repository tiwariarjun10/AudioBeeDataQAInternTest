import json
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import time

BASE_URL = "https://ekantipur.com"
ENTERTAINMENT_URL = "https://ekantipur.com/entertainment"

def extract_cartoon_of_the_day(page):
    """
    Extract Cartoon of the Day (व्यंग्यिचत्र) from the page.
    Returns a dict with title, image_url, and author fields.
    """
    cartoon_data = {
        "title": None,
        "image_url": None,
        "author": None
    }
    
    print("Searching for Cartoon of the Day (व्यंग्यिचत्र)...")
    
    try:
        # Try multiple strategies to find the cartoon section
        # Strategy 1: Look for text containing "व्यंग्यिचत्र" or "cartoon"
        cartoon_section = None
        search_texts = ["व्यंग्यिचत्र", "cartoon", "Cartoon", "व्यंग्य"]
        
        for search_text in search_texts:
            try:
                # Find element containing the text
                xpath_selector = f"//*[contains(text(), '{search_text}')]"
                elements = page.locator(f"xpath={xpath_selector}").all()
                
                if elements:
                    # Find the parent container
                    for elem in elements:
                        try:
                            # Try to find the cartoon container (parent or nearby)
                            parent = elem.locator("xpath=ancestor::*[contains(@class, 'cartoon') or contains(@class, 'article') or contains(@class, 'section')]").first
                            if parent.count() > 0:
                                cartoon_section = parent
                                break
                        except:
                            continue
                    
                    if cartoon_section:
                        break
            except:
                continue
        
        # Strategy 2: Look for common cartoon selectors
        if not cartoon_section:
            cartoon_selectors = [
                "[class*='cartoon']",
                "[id*='cartoon']",
                ".cartoon",
                "#cartoon",
                "[class*='व्यंग्य']"
            ]
            
            for selector in cartoon_selectors:
                try:
                    section = page.locator(selector).first
                    if section.count() > 0:
                        cartoon_section = section
                        break
                except:
                    continue
        
        # Strategy 3: Look for images with cartoon-related attributes or nearby text
        if not cartoon_section:
            try:
                # Find all images and check if they're in a cartoon context
                images = page.locator("img").all()
                for img in images:
                    try:
                        # Check if image is near cartoon-related text
                        img_src = img.get_attribute("src") or ""
                        alt_text = img.get_attribute("alt") or ""
                        
                        if any(text in img_src.lower() or text in alt_text.lower() 
                               for text in ["cartoon", "व्यंग्य", "cartoonist"]):
                            # Get parent container
                            parent = img.locator("xpath=ancestor::*[contains(@class, 'article') or contains(@class, 'section') or contains(@class, 'item')]").first
                            if parent.count() > 0:
                                cartoon_section = parent
                                break
                    except:
                        continue
            except:
                pass
        
        # Extract data from the found section
        if cartoon_section:
            # Extract title
            try:
                title_selectors = [
                    "h2", "h3", "h4",
                    ".title", "[class*='title']",
                    "a", "span"
                ]
                for title_sel in title_selectors:
                    try:
                        title_elem = cartoon_section.locator(title_sel).first
                        if title_elem.count() > 0:
                            title_text = title_elem.inner_text().strip()
                            # Skip if it's just the section header
                            if title_text and title_text not in ["व्यंग्यिचत्र", "Cartoon", "Cartoon of the Day"]:
                                cartoon_data["title"] = title_text
                                break
                    except:
                        continue
                
                # If no title found, use default
                if not cartoon_data["title"]:
                    cartoon_data["title"] = "व्यंग्यिचत्र"
            except:
                cartoon_data["title"] = "व्यंग्यिचत्र"
            
            # Extract image URL
            try:
                img_elem = cartoon_section.locator("img").first
                if img_elem.count() > 0:
                    img_src = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                    if img_src:
                        if img_src.startswith("http"):
                            cartoon_data["image_url"] = img_src
                        else:
                            cartoon_data["image_url"] = urljoin(BASE_URL, img_src)
            except:
                pass
            
            # Extract author (cartoonist name)
            try:
                author_selectors = [
                    "[class*='author']",
                    "[class*='cartoonist']",
                    "[class*='artist']",
                    ".author",
                    ".byline",
                    "span",
                    "p"
                ]
                for auth_sel in author_selectors:
                    try:
                        auth_elems = cartoon_section.locator(auth_sel).all()
                        for auth_elem in auth_elems:
                            auth_text = auth_elem.inner_text().strip()
                            # Look for text that might be author name (not too long, not common words)
                            if auth_text and len(auth_text) < 50 and auth_text not in ["व्यंग्यिचत्र", "Cartoon"]:
                                # Check if it looks like a name (contains Nepali characters or is reasonable length)
                                if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in auth_text) or (len(auth_text.split()) <= 3):
                                    cartoon_data["author"] = auth_text
                                    break
                        if cartoon_data["author"]:
                            break
                    except:
                        continue
            except:
                pass
        else:
            # Fallback: Try to find cartoon image directly on the page
            try:
                all_images = page.locator("img").all()
                for img in all_images:
                    img_src = img.get_attribute("src") or ""
                    alt_text = img.get_attribute("alt") or ""
                    
                    if any(text in img_src.lower() for text in ["cartoon", "व्यंग्य"]):
                        if img_src.startswith("http"):
                            cartoon_data["image_url"] = img_src
                        else:
                            cartoon_data["image_url"] = urljoin(BASE_URL, img_src)
                        cartoon_data["title"] = alt_text if alt_text else "व्यंग्यिचत्र"
                        break
            except:
                pass
        
        if cartoon_data["image_url"]:
            print(f"✅ Found cartoon: {cartoon_data['title']}")
        else:
            print("⚠️  Cartoon section not found")
            
    except Exception as e:
        print(f"⚠️  Error extracting cartoon: {str(e)}")
    
    return cartoon_data

def extract_entertainment_news():
    """
    Extract top 5 entertainment news articles and Cartoon of the Day from ekantipur.com
    Returns a dict with entertainment_news list and cartoon_of_the_day dict.
    """
    result = {
        "entertainment_news": [],
        "cartoon_of_the_day": {
            "title": None,
            "image_url": None,
            "author": None
        }
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to Entertainment section
        print(f"Navigating to {ENTERTAINMENT_URL}...")
        page.goto(ENTERTAINMENT_URL, timeout=60000, wait_until="domcontentloaded")
        
        # Wait for page to load (use lenient approach since networkidle may never occur)
        print("Waiting for page content to load...")
        try:
            page.wait_for_load_state("load", timeout=10000)
        except:
            pass  # Continue even if load state times out
        
        # Give extra time for dynamic content
        time.sleep(3)
        
        # Scroll to trigger lazy loading of images
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # Try multiple selectors to find articles
        articles = []
        selectors = [
            "article",
            ".news-item",
            ".article-item",
            "[class*='news']",
            "[class*='article']"
        ]
        
        # Wait a bit more and try to find articles
        max_attempts = 3
        for attempt in range(max_attempts):
            for selector in selectors:
                try:
                    articles = page.locator(selector).all()
                    if len(articles) >= 5:
                        break
                except:
                    continue
            if len(articles) >= 5:
                break
            if attempt < max_attempts - 1:
                print(f"Attempt {attempt + 1}: Found {len(articles)} articles, waiting a bit more...")
                time.sleep(2)
        
        print(f"Found {len(articles)} articles. Extracting top 5...")

        # Extract top 5 articles
        extracted_count = 0
        for article in articles:
            if extracted_count >= 5:
                break
                
            article_data = {}
            
            # Extract title
            try:
                title_selectors = [
                    "h2 a", "h3 a", "h2", "h3", 
                    "a[href*='/entertainment']",
                    ".title", "[class*='title']"
                ]
                title = None
                for title_sel in title_selectors:
                    try:
                        title_elem = article.locator(title_sel).first
                        if title_elem.count() > 0:
                            title = title_elem.inner_text().strip()
                            if title:
                                break
                    except:
                        continue
                article_data["title"] = title if title else None
            except Exception as e:
                article_data["title"] = None

            # Skip if no title found
            if not article_data["title"]:
                continue

            # Extract image URL (full URL)
            try:
                img_selectors = ["img", "picture img", "[class*='image'] img"]
                image_url = None
                for img_sel in img_selectors:
                    try:
                        img_elem = article.locator(img_sel).first
                        if img_elem.count() > 0:
                            img_src = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
                            if img_src:
                                # Convert to full URL if relative
                                if img_src.startswith("http"):
                                    image_url = img_src
                                else:
                                    image_url = urljoin(BASE_URL, img_src)
                                break
                    except:
                        continue
                article_data["image_url"] = image_url
            except Exception as e:
                article_data["image_url"] = None

            # Extract category (default to मनोरञ्जन)
            category = "मनोरञ्जन"
            try:
                category_selectors = [
                    "a[href*='/entertainment']",
                    "[class*='category']",
                    ".category",
                    ".section"
                ]
                for cat_sel in category_selectors:
                    try:
                        cat_elem = article.locator(cat_sel).first
                        if cat_elem.count() > 0:
                            cat_text = cat_elem.inner_text().strip()
                            if cat_text and ("मनोरञ्जन" in cat_text or "बिलउड" in cat_text or "entertainment" in cat_text.lower()):
                                category = cat_text
                                break
                    except:
                        continue
            except:
                pass
            article_data["category"] = category

            # Extract author (use null if not found)
            author = None
            try:
                author_selectors = [
                    ".author",
                    "[class*='author']",
                    "[class*='writer']",
                    "[class*='byline']",
                    ".byline"
                ]
                for auth_sel in author_selectors:
                    try:
                        auth_elem = article.locator(auth_sel).first
                        if auth_elem.count() > 0:
                            author_text = auth_elem.inner_text().strip()
                            if author_text:
                                author = author_text
                                break
                    except:
                        continue
            except:
                pass
            article_data["author"] = author if author else None

            # Add article to results
            result["entertainment_news"].append(article_data)
            extracted_count += 1
            print(f"Extracted article {extracted_count}: {article_data['title'][:50]}...")

        # Extract Cartoon of the Day
        print("\n" + "=" * 60)
        result["cartoon_of_the_day"] = extract_cartoon_of_the_day(page)
        
        # If cartoon not found on entertainment page, try homepage
        if not result["cartoon_of_the_day"]["image_url"]:
            print("Cartoon not found on entertainment page. Checking homepage...")
            try:
                page.goto(BASE_URL, timeout=60000, wait_until="domcontentloaded")
                time.sleep(2)
                result["cartoon_of_the_day"] = extract_cartoon_of_the_day(page)
            except Exception as e:
                print(f"⚠️  Error checking homepage for cartoon: {str(e)}")

        browser.close()

    return result

def save_to_json(data, filename="output.json"):
    """Save extracted data to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Data saved to {filename}")

def main():
    """Main function to run the scraper."""
    print("Starting ekantipur.com Scraper...")
    print("Task 1: Extract Entertainment News")
    print("Task 2: Extract Cartoon of the Day")
    print("=" * 60)
    
    try:
        result = extract_entertainment_news()
        save_to_json(result)
        
        print("=" * 60)
        print(f"✅ Task 1: Successfully extracted {len(result['entertainment_news'])} entertainment articles")
        if result["cartoon_of_the_day"]["image_url"]:
            print(f"✅ Task 2: Successfully extracted Cartoon of the Day")
        else:
            print(f"⚠️  Task 2: Cartoon of the Day not found")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
