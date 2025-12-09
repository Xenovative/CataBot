import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CatalogGenerator:
    """Generate catalog outputs in various formats"""
    
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.periodical_summary = None
    
    def set_periodical_summary(self, summary: Dict):
        """Set the periodical summary to include in outputs"""
        self.periodical_summary = summary
    
    def generate_catalog(self, papers: List[Dict], format: str = 'all', periodical_summary: Dict = None) -> Dict[str, str]:
        """Generate catalog in specified format(s)"""
        
        # Use provided summary or instance summary
        if periodical_summary:
            self.periodical_summary = periodical_summary
        
        output_files = {}
        
        if format in ['excel', 'all']:
            excel_path = self._generate_excel(papers)
            output_files['excel'] = excel_path
        
        if format in ['json', 'all']:
            json_path = self._generate_json(papers)
            output_files['json'] = json_path
        
        if format in ['csv', 'all']:
            csv_path = self._generate_csv(papers)
            output_files['csv'] = csv_path
        
        if format in ['html', 'all']:
            html_path = self._generate_html(papers)
            output_files['html'] = html_path
        
        return output_files
    
    def _generate_excel(self, papers: List[Dict]) -> str:
        """Generate Excel catalog with multiple sheets"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'academic_catalog_{timestamp}.xlsx'
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare main data
        main_data = []
        for paper in papers:
            classification = paper.get('classification', {})
            
            row = {
                '標題 (Title)': paper.get('title', 'Unknown'),
                '作者 (Authors)': paper.get('authors', 'Unknown'),
                '年份 (Year)': paper.get('year', 'Unknown'),
                '期刊 (Journal)': paper.get('journal', 'N/A'),
                '卷號 (Volume)': paper.get('volume', 'N/A'),
                '期號 (Issue)': paper.get('issue', 'N/A'),
                '頁數 (Pages)': paper.get('pages', 'N/A'),
                '主要學科 (Primary Subject)': classification.get('primary_subject', 'Other'),
                '次要學科 (Secondary Subjects)': ', '.join(classification.get('secondary_subjects', [])),
                '分類信心度 (Confidence)': classification.get('confidence', 'N/A'),
                '檔案路徑 (File Path)': paper.get('file_path', 'N/A')
            }
            main_data.append(row)
        
        df_main = pd.DataFrame(main_data)
        
        # Create subject summary
        subject_counts = {}
        for paper in papers:
            subject = paper.get('classification', {}).get('primary_subject', 'Other')
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        df_summary = pd.DataFrame([
            {'學科 (Subject)': subject, '論文數量 (Count)': count}
            for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
        ])
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Add periodical summary sheet first if available
            if self.periodical_summary:
                summary_data = {
                    '項目 (Item)': [
                        '期刊名稱 (Journal)',
                        '期號資訊 (Issue Info)',
                        '論文數量 (Paper Count)',
                        '主要主題 (Key Themes)',
                        '摘要 (Summary)'
                    ],
                    '內容 (Content)': [
                        self.periodical_summary.get('journal_name', 'N/A'),
                        self.periodical_summary.get('issue_info', 'N/A'),
                        self.periodical_summary.get('paper_count', len(papers)),
                        ', '.join(self.periodical_summary.get('key_themes', [])),
                        self.periodical_summary.get('summary', 'N/A')
                    ]
                }
                df_periodical = pd.DataFrame(summary_data)
                df_periodical.to_excel(writer, sheet_name='期刊摘要 (Issue Summary)', index=False)
            
            df_main.to_excel(writer, sheet_name='論文目錄 (Catalog)', index=False)
            df_summary.to_excel(writer, sheet_name='學科統計 (Summary)', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logger.info(f"Excel catalog generated: {filepath}")
        return filepath
    
    def _generate_json(self, papers: List[Dict]) -> str:
        """Generate JSON catalog"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'academic_catalog_{timestamp}.json'
        filepath = os.path.join(self.output_dir, filename)
        
        catalog = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_papers': len(papers),
                'version': '1.0'
            },
            'periodical_summary': self.periodical_summary if self.periodical_summary else None,
            'papers': papers
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON catalog generated: {filepath}")
        return filepath
    
    def _generate_csv(self, papers: List[Dict]) -> str:
        """Generate CSV catalog"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'academic_catalog_{timestamp}.csv'
        filepath = os.path.join(self.output_dir, filename)
        
        data = []
        for paper in papers:
            classification = paper.get('classification', {})
            
            row = {
                'Title': paper.get('title', 'Unknown'),
                'Authors': paper.get('authors', 'Unknown'),
                'Year': paper.get('year', 'Unknown'),
                'Journal': paper.get('journal', 'N/A'),
                'Volume': paper.get('volume', 'N/A'),
                'Issue': paper.get('issue', 'N/A'),
                'Pages': paper.get('pages', 'N/A'),
                'Primary_Subject': classification.get('primary_subject', 'Other'),
                'Secondary_Subjects': ', '.join(classification.get('secondary_subjects', [])),
                'Confidence': classification.get('confidence', 'N/A'),
                'File_Path': paper.get('file_path', 'N/A')
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"CSV catalog generated: {filepath}")
        return filepath
    
    def _generate_html(self, papers: List[Dict]) -> str:
        """Generate HTML catalog with nice formatting"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'academic_catalog_{timestamp}.html'
        filepath = os.path.join(self.output_dir, filename)
        
        # Subject statistics
        subject_counts = {}
        for paper in papers:
            subject = paper.get('classification', {}).get('primary_subject', 'Other')
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>學術論文目錄 - Academic Paper Catalog</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2em;
        }}
        .stat-card p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .subject-tag {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            margin: 2px;
        }}
        .confidence-high {{ background: #d4edda; color: #155724; }}
        .confidence-medium {{ background: #fff3cd; color: #856404; }}
        .confidence-low {{ background: #f8d7da; color: #721c24; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>📚 學術論文目錄 Academic Paper Catalog</h1>
    """
        
        # Add periodical summary section if available
        if self.periodical_summary:
            html += f"""
    <div class="summary" style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);">
        <h2>📰 期刊摘要 Issue Summary</h2>
        <p><strong>期刊 Journal:</strong> {self.periodical_summary.get('journal_name', 'N/A')}</p>
        <p><strong>期號 Issue:</strong> {self.periodical_summary.get('issue_info', 'N/A')}</p>
        <p><strong>主要主題 Key Themes:</strong> {', '.join(self.periodical_summary.get('key_themes', []))}</p>
        <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #3498db;">
            <p style="margin: 0; line-height: 1.6;">{self.periodical_summary.get('summary', 'No summary available.')}</p>
        </div>
    </div>
"""
        
        html += f"""
    <div class="summary">
        <h2>📊 統計摘要 Statistics</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>{len(papers)}</h3>
                <p>總論文數 Total Papers</p>
            </div>
            <div class="stat-card">
                <h3>{len(subject_counts)}</h3>
                <p>學科類別 Subject Categories</p>
            </div>
        </div>
        
        <h3>學科分布 Subject Distribution</h3>
        <table>
            <tr>
                <th>學科 Subject</th>
                <th>論文數量 Count</th>
                <th>百分比 Percentage</th>
            </tr>
"""
        
        for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(papers)) * 100
            html += f"""
            <tr>
                <td><strong>{subject}</strong></td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <h2>📖 論文列表 Paper List</h2>
    <table>
        <tr>
            <th>標題 Title</th>
            <th>作者 Authors</th>
            <th>期刊 Journal</th>
            <th>年份 Year</th>
            <th>卷期 Vol/Issue</th>
            <th>頁數 Pages</th>
            <th>學科 Subject</th>
        </tr>
"""
        
        for paper in papers:
            classification = paper.get('classification', {})
            confidence = classification.get('confidence', 'low')
            
            html += f"""
        <tr>
            <td><strong>{paper.get('title', 'Unknown')}</strong></td>
            <td>{paper.get('authors', 'Unknown')}</td>
            <td>{paper.get('journal', 'N/A')}</td>
            <td>{paper.get('year', 'N/A')}</td>
            <td>{paper.get('volume', 'N/A')}/{paper.get('issue', 'N/A')}</td>
            <td>{paper.get('pages', 'N/A')}</td>
            <td>
                <span class="subject-tag confidence-{confidence}">
                    {classification.get('primary_subject', 'Other')}
                </span>
            </td>
        </tr>
"""
        
        html += f"""
    </table>
    
    <div class="footer">
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>CataBot - Academic Cataloging System</p>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"HTML catalog generated: {filepath}")
        return filepath
