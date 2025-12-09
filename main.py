import os
import sys
import asyncio
import argparse
import logging
from typing import List, Dict
from tqdm import tqdm

from pdf_extractor import PDFExtractor
from web_crawler import AcademicCrawler
from ai_classifier import AIClassifier
from catalog_generator import CatalogGenerator
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CataBot:
    """Main application for academic paper cataloging"""
    
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.classifier = AIClassifier()
        self.catalog_generator = CatalogGenerator()
    
    async def process_from_url(self, url: str, max_depth: int = 2) -> List[Dict]:
        """Process papers from a website URL"""
        logger.info(f"Starting to crawl: {url}")
        
        # Crawl and download PDFs
        async with AcademicCrawler() as crawler:
            downloaded_files = await crawler.crawl_website(url, max_depth=max_depth)
        
        if not downloaded_files:
            logger.warning("No PDFs found or downloaded")
            return []
        
        # Process downloaded PDFs
        papers = []
        for file_info in tqdm(downloaded_files, desc="Extracting metadata"):
            paper_data = self.pdf_extractor.extract_from_pdf(file_info['filepath'])
            papers.append(paper_data)
        
        # Classify papers
        logger.info("Classifying papers...")
        papers = self.classifier.batch_classify(papers)
        
        return papers
    
    def process_from_directory(self, directory: str) -> List[Dict]:
        """Process papers from a local directory"""
        logger.info(f"Processing PDFs from: {directory}")
        
        # Find all PDFs
        crawler = AcademicCrawler()
        pdf_files = crawler.crawl_directory(directory)
        
        if not pdf_files:
            logger.warning("No PDFs found in directory")
            return []
        
        # Extract metadata
        papers = []
        for pdf_path in tqdm(pdf_files, desc="Extracting metadata"):
            paper_data = self.pdf_extractor.extract_from_pdf(pdf_path)
            papers.append(paper_data)
        
        # Classify papers
        logger.info("Classifying papers...")
        papers = self.classifier.batch_classify(papers)
        
        return papers
    
    def process_single_pdf(self, pdf_path: str) -> Dict:
        """Process a single PDF file"""
        logger.info(f"Processing: {pdf_path}")
        
        paper_data = self.pdf_extractor.extract_from_pdf(pdf_path)
        classification = self.classifier.classify_paper(
            title=paper_data.get('title', ''),
            content=paper_data.get('content_preview', ''),
            authors=paper_data.get('authors', '')
        )
        paper_data['classification'] = classification
        
        return paper_data
    
    def generate_catalog(self, papers: List[Dict], output_format: str = 'all'):
        """Generate catalog in specified format(s)"""
        if not papers:
            logger.warning("No papers to catalog")
            return
        
        # Generate periodical summary
        logger.info("Generating periodical summary...")
        periodical_summary = self.classifier.generate_periodical_summary(papers)
        
        if periodical_summary.get('summary'):
            logger.info(f"Summary generated: {periodical_summary.get('key_themes', [])}")
        
        logger.info(f"Generating catalog for {len(papers)} papers...")
        output_files = self.catalog_generator.generate_catalog(
            papers, format=output_format, periodical_summary=periodical_summary
        )
        
        logger.info("Catalog generation complete!")
        logger.info("Output files:")
        for format_type, filepath in output_files.items():
            logger.info(f"  - {format_type.upper()}: {filepath}")
        
        return output_files


async def main_async():
    """Async main function"""
    parser = argparse.ArgumentParser(
        description='CataBot - AI Academic Paper Cataloging System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process PDFs from a directory
  python main.py --directory ./papers
  
  # Crawl a website and process PDFs
  python main.py --url https://example.com/papers --depth 2
  
  # Process a single PDF
  python main.py --pdf paper.pdf
  
  # Specify output format
  python main.py --directory ./papers --format excel
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--url', help='URL to crawl for PDFs')
    input_group.add_argument('--directory', help='Local directory containing PDFs')
    input_group.add_argument('--pdf', help='Single PDF file to process')
    
    # Options
    parser.add_argument('--depth', type=int, default=2, 
                       help='Maximum crawl depth for URLs (default: 2)')
    parser.add_argument('--format', choices=['excel', 'json', 'csv', 'html', 'all'],
                       default='all', help='Output format (default: all)')
    parser.add_argument('--output-dir', default='output',
                       help='Output directory (default: output)')
    
    args = parser.parse_args()
    
    # Initialize CataBot
    bot = CataBot()
    bot.catalog_generator.output_dir = args.output_dir
    
    # Process based on input type
    papers = []
    
    try:
        if args.url:
            papers = await bot.process_from_url(args.url, max_depth=args.depth)
        elif args.directory:
            papers = bot.process_from_directory(args.directory)
        elif args.pdf:
            paper = bot.process_single_pdf(args.pdf)
            papers = [paper]
        
        # Generate catalog
        if papers:
            bot.generate_catalog(papers, output_format=args.format)
            
            # Print summary
            print("\n" + "="*60)
            print(f"✅ Successfully processed {len(papers)} papers")
            print("="*60)
            
            # Subject distribution
            subject_counts = {}
            for paper in papers:
                subject = paper.get('classification', {}).get('primary_subject', 'Other')
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
            
            print("\n📊 Subject Distribution:")
            for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {subject}: {count}")
            
        else:
            print("\n⚠️  No papers found or processed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point"""
    # Check for API key
    if not config.OPENAI_API_KEY:
        print("⚠️  Warning: No OpenAI API key found in .env file")
        print("   Classification will use keyword-based fallback method")
        print("   For better results, add OPENAI_API_KEY to .env file\n")
    
    # Run async main
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
