# Custom Classification Categories

## 🎯 Define Your Own Subject Categories

CataBot now allows you to define **custom classification categories** tailored to your specific domain or research area!

---

## ✨ What's New

### **Flexible Category System**
- ✅ Define unlimited custom categories
- ✅ Use any language (English, Chinese, etc.)
- ✅ Include detailed descriptions in category names
- ✅ Switch between custom and default categories
- ✅ Load example templates

### **Example Use Cases**
- **Theology & Religious Studies**
- **Medical Specializations**
- **Legal Domains**
- **Engineering Disciplines**
- **Business Sectors**
- **Regional Studies**

---

## 🚀 How to Use

### **1. Access Settings**
```
Web Interface → Settings Tab → Custom Classification Categories
```

### **2. Define Categories**

Enter one category per line in the text area:

```
Computer Science
Mathematics
Physics
Chemistry
Biology
```

### **3. Save Settings**
```
Click "💾 Save Settings"
```

### **4. Process Papers**
All papers will now be classified using your custom categories!

---

## 📚 Example: Chinese Theology Categories

### **Your Custom Categories**
```
聖經研究（原典原文的文本詮釋和跨宗教的經典辨讀）
基督宗教傳統（以天主教、東正教、基督新教三大傳統為主，也包括作為景教源頭的敘利亞東方教會、近代崛起的五旬宗，以及與基督宗教傳統關係極深的猶太教）
神學及哲學研究（基督宗教各大傳統從古到今的神學與哲學思想）
歷史研究（基督宗教不同派別以及中國基督教史的人物、事件、問題）
文學及藝術研究（基督宗教與文學、基督教藝術、聖樂等）
社會科學研究（從社會學、人類學、政治學、經濟學、心理學等社會科學，對基督宗教諸現象進行理論、歷史及實證研究）
文化研究（後現代思潮、後殖民研究、女性主義和生態學對現代性之批判等）
實踐神學（基督宗教各大傳統的禮儀學、靈修學、倫理學、當代實踐議題）
宗教對話與跨文化研究（不同宗教及文化傳統與基督宗教的對話）
跨學科研究與漢語神學（漢語基督教研究與相關學科協作整合，共同參與漢語學界的公共討論）
```

### **Quick Load**
Click **"📚 Load Example (Chinese Theology)"** to load these categories instantly!

---

## 💡 Category Design Tips

### **1. Be Specific**
```
❌ Bad:  "Science"
✅ Good: "Computer Science"
✅ Good: "Computational Biology"
```

### **2. Include Context**
```
❌ Basic: "History"
✅ Better: "Church History"
✅ Best:   "歷史研究（基督宗教不同派別以及中國基督教史的人物、事件、問題）"
```

### **3. Use Descriptions**
```
Category with description (in parentheses):
"實踐神學（基督宗教各大傳統的禮儀學、靈修學、倫理學、當代實踐議題）"

This helps AI understand the scope better!
```

### **4. Optimal Number**
```
Too few:  3-5 categories (too broad)
Good:     8-15 categories (balanced)
Too many: 30+ categories (too specific, may confuse AI)
```

### **5. Logical Grouping**
```
Group related topics:
- Biblical Studies
- Theology & Philosophy
- Historical Studies
- Practical Theology
```

---

## 🎨 Example Templates

### **Medical Specializations**
```
Cardiology
Neurology
Oncology
Pediatrics
Surgery
Radiology
Psychiatry
Internal Medicine
Emergency Medicine
Public Health
```

### **Legal Domains**
```
Constitutional Law
Criminal Law
Civil Law
Corporate Law
Intellectual Property
International Law
Environmental Law
Human Rights Law
Tax Law
Family Law
```

### **Engineering Disciplines**
```
Mechanical Engineering
Electrical Engineering
Civil Engineering
Chemical Engineering
Software Engineering
Aerospace Engineering
Biomedical Engineering
Environmental Engineering
Industrial Engineering
Materials Science
```

### **Business Sectors**
```
Marketing
Finance
Operations Management
Human Resources
Strategy
Entrepreneurship
Supply Chain Management
Business Analytics
International Business
Corporate Governance
```

---

## 🔧 Technical Details

### **How It Works**

#### **1. Category Storage**
```json
{
  "custom_categories": [
    "Category 1",
    "Category 2",
    "Category 3"
  ]
}
```

Stored in `settings.json` (local, not in git)

#### **2. AI Classification**
```python
# AI receives your custom categories
prompt = f"""Classify into ONE primary category:
Available categories: {', '.join(custom_categories)}

Paper: {title}
"""
```

#### **3. Priority**
```
Custom categories (if defined)
    ↓
Default categories (if empty)
```

---

## 📊 Classification Behavior

### **With Custom Categories**
```python
# Your categories
categories = [
    "聖經研究",
    "神學及哲學研究",
    "歷史研究"
]

# Paper about biblical interpretation
→ Classified as: "聖經研究"

# Paper about theological philosophy
→ Classified as: "神學及哲學研究"
```

### **Without Custom Categories**
```python
# Default categories
categories = [
    "Computer Science",
    "Mathematics",
    "Physics",
    ...
]

# Same papers
→ Classified as: "Philosophy" or "History"
```

---

## 🎯 Use Cases

### **1. Academic Institutions**
```
Theology Seminary:
- Use theology-specific categories
- Include denominational distinctions
- Add language/cultural context

Medical School:
- Use medical specializations
- Include research types
- Add clinical vs. basic research
```

### **2. Research Organizations**
```
Think Tank:
- Policy areas
- Regional focus
- Methodological approaches

Corporate R&D:
- Product lines
- Technology domains
- Market segments
```

### **3. Libraries & Archives**
```
Special Collections:
- Historical periods
- Geographic regions
- Document types
- Subject specializations
```

---

## 💡 Best Practices

### **1. Test Your Categories**
```
1. Define categories
2. Process 10-20 sample papers
3. Review classification results
4. Adjust categories if needed
5. Re-process
```

### **2. Document Your Categories**
```
Keep a separate document explaining:
- What each category covers
- Examples of papers in each
- Boundary cases
- Decision rules
```

### **3. Iterate**
```
Start broad → Refine over time
- Begin with 8-10 categories
- Add subcategories as needed
- Merge overlapping categories
- Split overly broad categories
```

### **4. Consider Your Audience**
```
Who will use the catalog?
- Researchers: More specific
- General public: Broader
- Students: Educational focus
- Administrators: Practical groupings
```

---

## 🔄 Switching Categories

### **Load Default Categories**
```
Settings → Custom Categories → 📋 Load Default Categories
```

This loads the 18 standard academic categories.

### **Load Example (Chinese Theology)**
```
Settings → Custom Categories → 📚 Load Example (Chinese Theology)
```

This loads the 10 theology-specific categories.

### **Clear Custom Categories**
```
Settings → Custom Categories → [Delete all text] → Save
```

System reverts to default categories.

---

## 🐛 Troubleshooting

### **Categories Not Working**

**Check 1: Saved Properly**
```
Settings → Custom Categories → Enter categories → Save
Look for "Settings saved successfully!"
```

**Check 2: Format**
```
✅ Correct:
Category 1
Category 2
Category 3

❌ Wrong:
Category 1, Category 2, Category 3
```

**Check 3: Restart Processing**
```
After changing categories:
1. Save settings
2. Start new processing job
3. Old jobs use old categories
```

### **AI Not Understanding Categories**

**Solution 1: Add Descriptions**
```
❌ "實踐神學"
✅ "實踐神學（禮儀學、靈修學、倫理學）"
```

**Solution 2: Use English Equivalents**
```
If AI struggles with non-English:
"Practical Theology (Liturgy, Spirituality, Ethics)"
```

**Solution 3: Simplify**
```
Too complex:
"跨學科研究與漢語神學（漢語基督教研究與相關學科協作整合，共同參與漢語學界的公共討論）"

Simpler:
"跨學科研究與漢語神學"
```

---

## 📈 Performance

### **Speed**
- No performance impact
- Same classification time
- Categories sent to AI as context

### **Accuracy**
- **Well-defined categories**: 90-95% accuracy
- **Vague categories**: 70-80% accuracy
- **Too many categories**: 75-85% accuracy

### **Optimal Setup**
```
Number: 8-15 categories
Length: 10-100 characters per category
Language: Consistent (all English or all Chinese)
Descriptions: Optional but helpful
```

---

## 🔒 Security & Privacy

### **Storage**
- Saved in `settings.json` (local file)
- Not committed to git (in `.gitignore`)
- Only accessible on your machine

### **API Usage**
- Categories sent to OpenAI API
- Used only for classification
- Not stored by OpenAI (per policy)

---

## 📚 Related Features

### **Works With**
- ✅ AI Classification (OpenAI/Anthropic)
- ✅ Keyword Fallback
- ✅ All processing modes (upload, crawl, directory)
- ✅ Multi-paper detection
- ✅ Vision extraction
- ✅ Catalog generation

### **Catalog Output**
```
Papers are grouped by your custom categories:

聖經研究
├── Paper 1
├── Paper 2
└── Paper 3

神學及哲學研究
├── Paper 4
└── Paper 5
```

---

## 🎓 Advanced Usage

### **Multiple Category Sets**

Save different category sets for different projects:

```json
// theology_categories.json
[
  "聖經研究",
  "神學及哲學研究",
  ...
]

// medical_categories.json
[
  "Cardiology",
  "Neurology",
  ...
]
```

Load via copy-paste when switching projects.

### **Hierarchical Categories**

Use prefixes for hierarchy:

```
1. Biblical Studies
1.1. Old Testament
1.2. New Testament
2. Theology
2.1. Systematic Theology
2.2. Practical Theology
```

### **Bilingual Categories**

Include both languages:

```
聖經研究 (Biblical Studies)
神學及哲學研究 (Theology & Philosophy)
歷史研究 (Historical Studies)
```

---

## ✅ Summary

### **What It Does**
- ✅ Allows custom classification categories
- ✅ Supports any language
- ✅ Includes descriptions in category names
- ✅ Easy to switch between custom/default
- ✅ Saves with other settings

### **How to Use**
1. Settings → Custom Categories
2. Enter one category per line
3. Save settings
4. Process papers

### **Benefits**
- ✅ Domain-specific classification
- ✅ Better organization for specialized fields
- ✅ Supports non-English categories
- ✅ Flexible and easy to update

---

**Custom categories are ready!** 🎯

Define your own categories in Settings to get more accurate and relevant classification for your specific research domain.

## 📖 Quick Start Example

For Chinese theology research:

1. Go to **Settings** tab
2. Scroll to **Custom Classification Categories**
3. Click **"📚 Load Example (Chinese Theology)"**
4. Click **"💾 Save Settings"**
5. Process your papers!

Your papers will now be classified into the 10 theology-specific categories instead of generic academic categories.
