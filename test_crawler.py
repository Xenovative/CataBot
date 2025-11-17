import requests
from bs4 import BeautifulSoup
import re

url = 'https://library.cgst.edu/tc/journal/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print(f"Fetching: {url}\n")
r = requests.get(url, headers=headers)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}\n")

soup = BeautifulSoup(r.text, 'html.parser')

# Find all links
links = soup.find_all('a', href=True)
print(f"Total links found: {len(links)}\n")

# Check for PDFs
pdf_links = []
for link in links:
    href = link.get('href', '')
    text = link.get_text().strip()
    
    if '.pdf' in href.lower() or 'pdf' in text.lower():
        pdf_links.append((href, text))

print(f"PDF-related links: {len(pdf_links)}")
for href, text in pdf_links[:10]:
    print(f"  {href} - {text[:50]}")

print("\n--- First 20 links ---")
for i, link in enumerate(links[:20], 1):
    href = link.get('href', '')
    text = link.get_text().strip()[:50]
    print(f"{i}. {href} - {text}")

# Check for JavaScript or dynamic content
scripts = soup.find_all('script')
print(f"\n--- Scripts found: {len(scripts)} ---")
for script in scripts[:5]:
    src = script.get('src', '')
    if src:
        print(f"  Script: {src}")

# Check for iframes
iframes = soup.find_all('iframe')
print(f"\n--- Iframes found: {len(iframes)} ---")
for iframe in iframes:
    print(f"  {iframe.get('src', '')}")

# Look for data attributes or API endpoints
print("\n--- Looking for data-* attributes ---")
for tag in soup.find_all(attrs={'data-url': True}):
    print(f"  {tag.name}: {tag.get('data-url')}")

for tag in soup.find_all(attrs={'data-src': True}):
    print(f"  {tag.name}: {tag.get('data-src')}")

# Check page structure
print("\n--- Page structure ---")
print(f"Title: {soup.title.string if soup.title else 'No title'}")
main_content = soup.find('main') or soup.find('div', class_=re.compile('content|main'))
if main_content:
    print(f"Main content found: {len(main_content.get_text())} characters")
else:
    print("No main content div found")
