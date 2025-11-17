import json
import logging
from typing import Dict, List
from openai import OpenAI
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIClassifier:
    """AI-powered subject classification for academic papers"""
    
    def __init__(self, api_key: str = None, custom_categories: List[str] = None):
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("No OpenAI API key found. Classification will use fallback method.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        # Load custom categories if provided, otherwise use default
        if custom_categories:
            self.categories = custom_categories
            logger.info(f"Using {len(custom_categories)} custom categories")
        else:
            self.categories = config.SUBJECT_CATEGORIES
    
    def classify_paper(self, title: str, content: str = "", authors: str = "") -> Dict:
        """Classify a paper into subject categories"""
        
        if self.client:
            return self._classify_with_ai(title, content, authors)
        else:
            return self._classify_with_keywords(title, content)
    
    def _classify_with_ai(self, title: str, content: str, authors: str) -> Dict:
        """Use OpenAI API for classification"""
        try:
            # Prepare content for classification
            text_to_classify = f"Title: {title}\n"
            if authors:
                text_to_classify += f"Authors: {authors}\n"
            if content:
                # Use first 1000 characters of content
                text_to_classify += f"Abstract/Content: {content[:1000]}\n"
            
            prompt = f"""Classify the following academic paper into ONE primary subject category and up to 2 secondary categories.

Available categories: {', '.join(self.categories)}

Paper information:
{text_to_classify}

Respond in JSON format:
{{
    "primary_subject": "category name",
    "secondary_subjects": ["category1", "category2"],
    "confidence": "high/medium/low",
    "reasoning": "brief explanation"
}}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert academic librarian specializing in subject classification."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text)
            
            return {
                'primary_subject': result.get('primary_subject', 'Other'),
                'secondary_subjects': result.get('secondary_subjects', []),
                'confidence': result.get('confidence', 'medium'),
                'reasoning': result.get('reasoning', ''),
                'method': 'ai'
            }
        
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            # Fallback to keyword-based
            return self._classify_with_keywords(title, content)
    
    def _classify_with_keywords(self, title: str, content: str) -> Dict:
        """Fallback keyword-based classification with Chinese support"""
        
        text = (title + " " + content[:500]).lower()
        
        # Keyword mapping (English + Chinese)
        keyword_map = {
            "Computer Science": [
                "computer", "algorithm", "software", "programming", "machine learning", 
                "artificial intelligence", "data", "network", "computing",
                "計算機", "算法", "軟件", "軟體", "程序", "機器學習", "人工智能", "人工智慧", 
                "數據", "資料", "網絡", "網路", "計算"
            ],
            "Mathematics": [
                "theorem", "proof", "equation", "mathematical", "algebra", "geometry", 
                "calculus", "topology", "number theory",
                "定理", "證明", "方程", "數學", "代數", "幾何", "微積分", "拓撲", "數論"
            ],
            "Physics": [
                "quantum", "particle", "energy", "force", "relativity", "mechanics", 
                "thermodynamics", "electromagnetic",
                "量子", "粒子", "能量", "力", "相對論", "力學", "熱力學", "電磁"
            ],
            "Chemistry": [
                "chemical", "molecule", "reaction", "compound", "synthesis", "catalyst", 
                "organic", "inorganic",
                "化學", "分子", "反應", "化合物", "合成", "催化劑", "有機", "無機"
            ],
            "Biology": [
                "cell", "gene", "protein", "organism", "evolution", "ecology", "species", 
                "molecular biology",
                "細胞", "基因", "蛋白質", "生物", "進化", "演化", "生態", "物種", "分子生物學"
            ],
            "Medicine": [
                "clinical", "patient", "disease", "treatment", "diagnosis", "therapy", 
                "medical", "health",
                "臨床", "病人", "患者", "疾病", "治療", "診斷", "醫學", "健康", "醫療"
            ],
            "Engineering": [
                "design", "system", "control", "optimization", "manufacturing", 
                "mechanical", "electrical", "civil",
                "設計", "系統", "控制", "優化", "製造", "機械", "電氣", "電機", "土木", "工程"
            ],
            "Social Sciences": [
                "social", "society", "culture", "behavior", "community", "policy",
                "社會", "文化", "行為", "社區", "政策", "社會學"
            ],
            "Economics": [
                "economic", "market", "trade", "finance", "investment", "monetary", "fiscal",
                "經濟", "市場", "貿易", "金融", "投資", "貨幣", "財政"
            ],
            "Psychology": [
                "psychological", "cognitive", "behavior", "mental", "perception", "emotion",
                "心理", "認知", "行為", "精神", "感知", "情緒", "心理學"
            ],
            "Education": [
                "teaching", "learning", "student", "pedagogy", "curriculum", "educational",
                "教學", "學習", "學生", "教育", "課程", "教學法"
            ],
            "Literature": [
                "literary", "novel", "poetry", "narrative", "author", "text analysis",
                "文學", "小說", "詩歌", "詩詞", "敘事", "作者", "文本分析"
            ],
            "History": [
                "historical", "century", "period", "ancient", "medieval", "war", "civilization",
                "歷史", "世紀", "時期", "古代", "中世紀", "戰爭", "文明"
            ],
            "Philosophy": [
                "philosophical", "ethics", "metaphysics", "epistemology", "logic", "moral",
                "哲學", "倫理", "形而上學", "認識論", "邏輯", "道德"
            ],
            "Law": [
                "legal", "court", "justice", "law", "regulation", "statute", "judicial",
                "法律", "法院", "正義", "司法", "法規", "條例", "法學"
            ],
            "Business": [
                "business", "management", "strategy", "marketing", "organization", "corporate",
                "商業", "管理", "策略", "營銷", "行銷", "組織", "企業"
            ],
            "Environmental Science": [
                "environment", "climate", "ecology", "pollution", "sustainability", "conservation",
                "環境", "氣候", "生態", "污染", "可持續", "永續", "保護", "環保"
            ]
        }
        
        # Score each category
        scores = {}
        for category, keywords in keyword_map.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return {
                'primary_subject': 'Other',
                'secondary_subjects': [],
                'confidence': 'low',
                'reasoning': 'No matching keywords found',
                'method': 'keyword'
            }
        
        # Sort by score
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_categories[0][0]
        secondary = [cat for cat, score in sorted_categories[1:3]]
        
        confidence = 'high' if sorted_categories[0][1] >= 3 else 'medium' if sorted_categories[0][1] >= 2 else 'low'
        
        return {
            'primary_subject': primary,
            'secondary_subjects': secondary,
            'confidence': confidence,
            'reasoning': f'Keyword matches: {sorted_categories[0][1]}',
            'method': 'keyword'
        }
    
    def batch_classify(self, papers: List[Dict]) -> List[Dict]:
        """Classify multiple papers"""
        results = []
        
        for paper in papers:
            classification = self.classify_paper(
                title=paper.get('title', ''),
                content=paper.get('content_preview', ''),
                authors=paper.get('authors', '')
            )
            
            paper['classification'] = classification
            results.append(paper)
        
        return results
