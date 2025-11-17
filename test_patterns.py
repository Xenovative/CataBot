import re

text = """《二十一世紀》網絡版 二○○九年三月號 總第 84 期 2009年3月31日
透視農村電影放映員──以二十世紀五十年代江蘇省為例"""

print("Testing improved patterns:")
print("=" * 50)

# Journal
journal_pattern = r'《([^》]{3,40})》'
match = re.search(journal_pattern, text)
print(f"Journal: {match.group(1) if match else 'Not found'}")

# Issue
issue_pattern = r'總第\s*(\d+)\s*期'
match = re.search(issue_pattern, text)
print(f"Issue (總第): {match.group(1) if match else 'Not found'}")

issue_pattern2 = r'第\s*(\d+)\s*期'
match2 = re.search(issue_pattern2, text)
print(f"Issue (第): {match2.group(1) if match2 else 'Not found'}")

# Year (Chinese)
year_pattern = r'([二三四五六七八九○一]{4})年'
match = re.search(year_pattern, text)
if match:
    chinese_year = match.group(1)
    chinese_to_arabic = {
        '○': '0', '一': '1', '二': '2', '三': '3', '四': '4',
        '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'
    }
    arabic = ''.join(chinese_to_arabic.get(c, c) for c in chinese_year)
    print(f"Year (Chinese): {chinese_year} -> {arabic}")

# Year (Arabic)
year_pattern2 = r'(\d{4})年'
match2 = re.search(year_pattern2, text)
print(f"Year (Arabic): {match2.group(1) if match2 else 'Not found'}")
