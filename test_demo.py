"""
Demo script to test CataBot functionality without real PDFs
演示腳本 - 無需真實 PDF 即可測試功能
"""

import os
import json
from catalog_generator import CatalogGenerator
from ai_classifier import AIClassifier


def create_sample_data():
    """創建示範數據"""
    sample_papers = [
        {
            'title': 'Deep Learning for Medical Image Segmentation',
            'authors': 'Zhang Wei, Li Ming, Wang Fang',
            'year': '2023',
            'volume': '15',
            'issue': '3',
            'pages': '245-267',
            'content_preview': 'This paper presents a novel deep learning approach for medical image segmentation using convolutional neural networks...',
            'file_path': 'sample1.pdf'
        },
        {
            'title': 'Quantum Computing: A Survey of Recent Advances',
            'authors': 'John Smith, Emily Brown',
            'year': '2023',
            'volume': '42',
            'issue': '1',
            'pages': '1-35',
            'content_preview': 'We survey recent advances in quantum computing, including quantum algorithms, error correction, and hardware implementations...',
            'file_path': 'sample2.pdf'
        },
        {
            'title': 'Climate Change Impact on Biodiversity',
            'authors': 'Maria Garcia, Ahmed Hassan',
            'year': '2022',
            'volume': '28',
            'issue': '4',
            'pages': '112-145',
            'content_preview': 'This study examines the impact of climate change on global biodiversity, focusing on ecosystem resilience and species adaptation...',
            'file_path': 'sample3.pdf'
        },
        {
            'title': 'Machine Learning in Financial Markets',
            'authors': 'David Lee, Sarah Johnson',
            'year': '2023',
            'volume': '19',
            'issue': '2',
            'pages': '78-95',
            'content_preview': 'We explore the application of machine learning algorithms in financial market prediction and risk management...',
            'file_path': 'sample4.pdf'
        },
        {
            'title': 'Neural Networks for Natural Language Processing',
            'authors': 'Chen Jing, Liu Xiao',
            'year': '2023',
            'volume': '33',
            'issue': '5',
            'pages': '301-328',
            'content_preview': 'This paper reviews neural network architectures for natural language processing, including transformers and attention mechanisms...',
            'file_path': 'sample5.pdf'
        },
        {
            'title': 'Renewable Energy Systems: A Comprehensive Review',
            'authors': 'Hans Mueller, Anna Schmidt',
            'year': '2022',
            'volume': '25',
            'issue': '3',
            'pages': '156-189',
            'content_preview': 'We provide a comprehensive review of renewable energy systems, including solar, wind, and hydroelectric power generation...',
            'file_path': 'sample6.pdf'
        },
        {
            'title': 'Cognitive Psychology and Learning Theory',
            'authors': 'Robert Wilson, Jennifer Taylor',
            'year': '2023',
            'volume': '44',
            'issue': '1',
            'pages': '23-48',
            'content_preview': 'This study investigates cognitive processes in learning, memory formation, and knowledge retention...',
            'file_path': 'sample7.pdf'
        },
        {
            'title': 'Blockchain Technology in Supply Chain Management',
            'authors': 'Kim Min-jun, Park Ji-woo',
            'year': '2023',
            'volume': '12',
            'issue': '2',
            'pages': '67-89',
            'content_preview': 'We examine the application of blockchain technology in supply chain management, focusing on transparency and traceability...',
            'file_path': 'sample8.pdf'
        },
        {
            'title': 'Ancient Chinese Philosophy and Modern Ethics',
            'authors': 'Wang Hui, Zhang Lei',
            'year': '2022',
            'volume': '38',
            'issue': '4',
            'pages': '201-225',
            'content_preview': 'This paper explores connections between ancient Chinese philosophical traditions and contemporary ethical frameworks...',
            'file_path': 'sample9.pdf'
        },
        {
            'title': 'Gene Editing Technologies: CRISPR and Beyond',
            'authors': 'Dr. Lisa Anderson, Dr. Michael Chen',
            'year': '2023',
            'volume': '56',
            'issue': '6',
            'pages': '445-478',
            'content_preview': 'We review recent developments in gene editing technologies, including CRISPR-Cas9 and emerging alternatives...',
            'file_path': 'sample10.pdf'
        }
    ]
    
    return sample_papers


def test_classification():
    """測試 AI 分類功能"""
    print("=" * 70)
    print("測試 AI 分類功能 | Testing AI Classification")
    print("=" * 70)
    print()
    
    classifier = AIClassifier()
    sample_papers = create_sample_data()
    
    print(f"處理 {len(sample_papers)} 篇論文...\n")
    
    # Classify papers
    classified_papers = classifier.batch_classify(sample_papers)
    
    # Display results
    for i, paper in enumerate(classified_papers, 1):
        classification = paper['classification']
        print(f"{i}. {paper['title']}")
        print(f"   作者: {paper['authors']}")
        print(f"   主要學科: {classification['primary_subject']}")
        if classification['secondary_subjects']:
            print(f"   次要學科: {', '.join(classification['secondary_subjects'])}")
        print(f"   信心度: {classification['confidence']}")
        print(f"   分類方法: {classification['method']}")
        print()
    
    return classified_papers


def test_catalog_generation(papers):
    """測試目錄生成功能"""
    print("=" * 70)
    print("生成目錄文件 | Generating Catalog Files")
    print("=" * 70)
    print()
    
    generator = CatalogGenerator(output_dir='demo_output')
    
    # Generate all formats
    output_files = generator.generate_catalog(papers, format='all')
    
    print("✅ 成功生成以下文件:\n")
    for format_type, filepath in output_files.items():
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"   📄 {format_type.upper()}: {filepath} ({file_size:.1f} KB)")
    
    print()
    return output_files


def display_statistics(papers):
    """顯示統計信息"""
    print("=" * 70)
    print("統計摘要 | Statistics Summary")
    print("=" * 70)
    print()
    
    # Subject distribution
    subject_counts = {}
    year_counts = {}
    
    for paper in papers:
        subject = paper['classification']['primary_subject']
        year = paper['year']
        
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        year_counts[year] = year_counts.get(year, 0) + 1
    
    print(f"📊 總論文數: {len(papers)}")
    print(f"📚 學科類別數: {len(subject_counts)}")
    print()
    
    print("學科分布:")
    for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(papers)) * 100
        bar = "█" * int(percentage / 5)
        print(f"  {subject:30s} {count:2d} ({percentage:5.1f}%) {bar}")
    
    print()
    print("年份分布:")
    for year, count in sorted(year_counts.items(), reverse=True):
        print(f"  {year}: {count} 篇")
    
    print()


def main():
    """主函數"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "CataBot 演示程式" + " " * 31 + "║")
    print("║" + " " * 15 + "Academic Cataloging Demo" + " " * 28 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    try:
        # Test classification
        classified_papers = test_classification()
        
        # Display statistics
        display_statistics(classified_papers)
        
        # Generate catalog files
        output_files = test_catalog_generation(classified_papers)
        
        # Final message
        print("=" * 70)
        print("✨ 演示完成！Demo Complete!")
        print("=" * 70)
        print()
        print("下一步 Next Steps:")
        print("  1. 查看 demo_output/ 目錄中的輸出文件")
        print("     Check output files in demo_output/ directory")
        print()
        print("  2. 使用真實 PDF 測試:")
        print("     Test with real PDFs:")
        print("     python main.py --directory ./your_papers")
        print()
        print("  3. 閱讀完整文檔:")
        print("     Read full documentation:")
        print("     - README.md")
        print("     - QUICKSTART.md")
        print()
        
        # Save sample data for reference
        sample_file = 'demo_output/sample_data.json'
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(classified_papers, f, ensure_ascii=False, indent=2)
        print(f"  💾 示範數據已保存: {sample_file}")
        print()
        
    except Exception as e:
        print(f"\n❌ 錯誤 Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
