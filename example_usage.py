"""
Example usage scripts for CataBot
示範如何在 Python 程式中使用 CataBot
"""

import asyncio
from pdf_extractor import PDFExtractor
from ai_classifier import AIClassifier
from catalog_generator import CatalogGenerator
from web_crawler import AcademicCrawler


# Example 1: Process a single PDF
def example_single_pdf():
    """處理單個 PDF 文件"""
    print("Example 1: Processing a single PDF")
    print("-" * 50)
    
    extractor = PDFExtractor()
    classifier = AIClassifier()
    
    # Extract metadata
    paper = extractor.extract_from_pdf("example.pdf")
    
    # Classify
    classification = classifier.classify_paper(
        title=paper['title'],
        content=paper['content_preview'],
        authors=paper['authors']
    )
    
    paper['classification'] = classification
    
    print(f"Title: {paper['title']}")
    print(f"Authors: {paper['authors']}")
    print(f"Year: {paper['year']}")
    print(f"Subject: {classification['primary_subject']}")
    print(f"Confidence: {classification['confidence']}")
    print()


# Example 2: Process a directory
def example_directory():
    """處理整個目錄的 PDF"""
    print("Example 2: Processing a directory of PDFs")
    print("-" * 50)
    
    extractor = PDFExtractor()
    classifier = AIClassifier()
    generator = CatalogGenerator()
    
    # Find all PDFs
    crawler = AcademicCrawler()
    pdf_files = crawler.crawl_directory("./papers")
    
    # Process each PDF
    papers = []
    for pdf_path in pdf_files:
        paper = extractor.extract_from_pdf(pdf_path)
        papers.append(paper)
    
    # Classify all papers
    papers = classifier.batch_classify(papers)
    
    # Generate catalog
    output_files = generator.generate_catalog(papers, format='all')
    
    print(f"Processed {len(papers)} papers")
    print(f"Output files: {output_files}")
    print()


# Example 3: Crawl a website
async def example_web_crawl():
    """從網站爬取 PDF"""
    print("Example 3: Crawling a website for PDFs")
    print("-" * 50)
    
    async with AcademicCrawler() as crawler:
        # Crawl and download
        downloaded = await crawler.crawl_website(
            "https://example.com/papers",
            output_dir="downloaded_pdfs",
            max_depth=2
        )
    
    print(f"Downloaded {len(downloaded)} PDFs")
    
    # Process downloaded PDFs
    extractor = PDFExtractor()
    classifier = AIClassifier()
    
    papers = []
    for file_info in downloaded:
        paper = extractor.extract_from_pdf(file_info['filepath'])
        papers.append(paper)
    
    papers = classifier.batch_classify(papers)
    
    # Generate catalog
    generator = CatalogGenerator()
    generator.generate_catalog(papers)
    print()


# Example 4: Custom classification
def example_custom_classification():
    """自訂分類邏輯"""
    print("Example 4: Custom classification")
    print("-" * 50)
    
    classifier = AIClassifier()
    
    # Classify based on title and abstract
    result = classifier.classify_paper(
        title="Deep Learning for Medical Image Analysis",
        content="This paper presents a novel deep learning approach for analyzing medical images...",
        authors="John Doe, Jane Smith"
    )
    
    print(f"Primary Subject: {result['primary_subject']}")
    print(f"Secondary Subjects: {', '.join(result['secondary_subjects'])}")
    print(f"Confidence: {result['confidence']}")
    print(f"Method: {result['method']}")
    print(f"Reasoning: {result['reasoning']}")
    print()


# Example 5: Generate specific format
def example_specific_format():
    """只生成特定格式的輸出"""
    print("Example 5: Generate specific output format")
    print("-" * 50)
    
    # Prepare sample data
    papers = [
        {
            'title': 'Machine Learning in Healthcare',
            'authors': 'John Doe',
            'year': '2023',
            'volume': '15',
            'issue': '3',
            'pages': '45-67',
            'classification': {
                'primary_subject': 'Computer Science',
                'secondary_subjects': ['Medicine'],
                'confidence': 'high'
            }
        },
        {
            'title': 'Quantum Computing Applications',
            'authors': 'Jane Smith',
            'year': '2023',
            'volume': '20',
            'issue': '1',
            'pages': '1-25',
            'classification': {
                'primary_subject': 'Physics',
                'secondary_subjects': ['Computer Science'],
                'confidence': 'high'
            }
        }
    ]
    
    generator = CatalogGenerator()
    
    # Generate only Excel
    output = generator.generate_catalog(papers, format='excel')
    print(f"Excel file: {output['excel']}")
    
    # Generate only HTML
    output = generator.generate_catalog(papers, format='html')
    print(f"HTML file: {output['html']}")
    print()


# Example 6: Batch processing with progress
def example_batch_with_progress():
    """批次處理並顯示進度"""
    print("Example 6: Batch processing with progress")
    print("-" * 50)
    
    from tqdm import tqdm
    
    extractor = PDFExtractor()
    classifier = AIClassifier()
    
    pdf_files = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]  # Your PDF list
    
    papers = []
    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            paper = extractor.extract_from_pdf(pdf_path)
            papers.append(paper)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            continue
    
    print("Classifying papers...")
    papers = classifier.batch_classify(papers)
    
    print(f"Successfully processed {len(papers)} papers")
    print()


# Example 7: Filter and sort results
def example_filter_sort():
    """過濾和排序結果"""
    print("Example 7: Filter and sort results")
    print("-" * 50)
    
    # Sample papers
    papers = [
        {'title': 'Paper A', 'year': '2023', 'classification': {'primary_subject': 'Physics'}},
        {'title': 'Paper B', 'year': '2022', 'classification': {'primary_subject': 'Computer Science'}},
        {'title': 'Paper C', 'year': '2023', 'classification': {'primary_subject': 'Physics'}},
    ]
    
    # Filter by subject
    physics_papers = [p for p in papers if p['classification']['primary_subject'] == 'Physics']
    print(f"Physics papers: {len(physics_papers)}")
    
    # Filter by year
    recent_papers = [p for p in papers if p['year'] == '2023']
    print(f"2023 papers: {len(recent_papers)}")
    
    # Sort by year
    sorted_papers = sorted(papers, key=lambda x: x['year'], reverse=True)
    print(f"Latest paper: {sorted_papers[0]['title']} ({sorted_papers[0]['year']})")
    print()


def main():
    """Run all examples"""
    print("=" * 60)
    print("CataBot Usage Examples")
    print("=" * 60)
    print()
    
    # Uncomment the examples you want to run:
    
    # example_single_pdf()
    # example_directory()
    # asyncio.run(example_web_crawl())
    example_custom_classification()
    # example_specific_format()
    # example_batch_with_progress()
    example_filter_sort()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
