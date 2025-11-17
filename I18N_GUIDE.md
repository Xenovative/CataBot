# Traditional Chinese Language Support Guide

## 🌏 Bilingual Web Interface

CataBot's web interface now supports **English** and **Traditional Chinese (繁體中文)** with instant language switching!

## ✨ Features

### Language Switcher
- **Fixed Position Button**: Top-right corner of the page
- **One-Click Toggle**: Switch between English and Traditional Chinese
- **Persistent**: Language preference saved in browser
- **Instant Update**: All text updates immediately

### Supported Languages
- 🇬🇧 **English** (Default)
- 🇹🇼 **Traditional Chinese** (繁體中文)

## 🚀 How to Use

### Switch Language

1. **Open Web Interface**: http://localhost:5000
2. **Click Language Button**: Top-right corner
   - Shows "切換至繁體中文" (Switch to Traditional Chinese) in English mode
   - Shows "Switch to English" in Chinese mode
3. **Instant Switch**: All text updates immediately

### Language Persistence

Your language choice is automatically saved:
- Stored in browser's localStorage
- Persists across sessions
- Applies on page reload

## 📝 Translated Elements

### Complete Translation Coverage

#### Header
- App title and subtitle

#### Navigation Tabs
- Upload Files / 上傳檔案
- Crawl Website / 爬取網站
- Local Directory / 本地目錄

#### Upload Tab
- Drop zone text
- Format selection labels
- Button text

#### Crawl Tab
- URL input label
- Depth selection options
- Format selection
- Button text

#### Directory Tab
- Path input label
- Note/warning text
- Format selection
- Button text

#### Progress Section
- Processing title
- Status messages

#### Results Section
- Completion message
- Statistics labels
- Download buttons
- Subject distribution title
- Reset button

#### Configuration Section
- System configuration title
- AI classification status
- Category count

#### Messages
- Error messages
- Alert dialogs
- Validation messages

## 🔧 Technical Details

### Implementation

#### i18n.js
Located at: `static/i18n.js`

**Features**:
- Translation dictionary for both languages
- `t(key)` function for translations
- `updateLanguage()` updates all elements
- `toggleLanguage()` switches languages
- localStorage persistence

#### HTML Integration
All translatable elements have `data-i18n` attributes:
```html
<h1 data-i18n="app_title">📚 CataBot</h1>
<button data-i18n="upload_button">🚀 Start Processing</button>
```

#### Dynamic Content
JavaScript uses `t()` function for dynamic text:
```javascript
alert(t('msg_no_url'));
statsHtml = `<p>${t('results_stats_papers')}</p>`;
```

### Translation Keys

All translations are defined in `static/i18n.js`:

```javascript
const translations = {
    'en': {
        'app_title': 'CataBot',
        'upload_button': '🚀 Start Processing',
        // ... more keys
    },
    'zh-TW': {
        'app_title': 'CataBot',
        'upload_button': '🚀 開始處理',
        // ... more keys
    }
};
```

## 🎨 UI Design

### Language Switcher Button

**Styling**:
- White background with purple text
- Rounded corners (25px radius)
- Hover effect: Purple background, white text
- Shadow effects for depth
- Responsive sizing on mobile

**Position**:
- Desktop: Top-right, 20px from edges
- Mobile: Top-right, 10px from edges

### Visual Feedback
- Smooth transitions (0.3s)
- Hover animations
- Click effects

## 📱 Responsive Design

### Desktop
- Full-size button
- Fixed position top-right
- Clear visibility

### Tablet
- Slightly smaller button
- Maintains position
- Touch-friendly

### Mobile
- Compact button size
- Adjusted positioning
- Large touch target

## 🔄 Adding New Translations

### Step 1: Add Translation Keys

Edit `static/i18n.js`:

```javascript
const translations = {
    'en': {
        'new_key': 'English text',
        // ...
    },
    'zh-TW': {
        'new_key': '中文文字',
        // ...
    }
};
```

### Step 2: Add data-i18n Attribute

In HTML:
```html
<element data-i18n="new_key">English text</element>
```

### Step 3: Use in JavaScript

```javascript
const text = t('new_key');
element.textContent = t('new_key');
```

## 🌐 Adding More Languages

### Step 1: Add Language to Dictionary

```javascript
const translations = {
    'en': { /* ... */ },
    'zh-TW': { /* ... */ },
    'zh-CN': {  // Simplified Chinese
        'app_title': 'CataBot',
        'app_subtitle': 'AI 学术论文目录系统',
        // ... all keys
    }
};
```

### Step 2: Update Language Switcher

Modify `toggleLanguage()` function:
```javascript
function toggleLanguage() {
    const langs = ['en', 'zh-TW', 'zh-CN'];
    const currentIndex = langs.indexOf(currentLang);
    currentLang = langs[(currentIndex + 1) % langs.length];
    updateLanguage();
}
```

### Step 3: Update Button Text

Add language names to translations:
```javascript
'lang_switch': 'Switch to 简体中文'  // in zh-TW
'lang_switch': 'Switch to English'  // in zh-CN
```

## 🧪 Testing

### Test Checklist

- [ ] Language switcher button visible
- [ ] Click switches language instantly
- [ ] All text elements update
- [ ] Placeholders update
- [ ] Dynamic content translates
- [ ] Error messages in correct language
- [ ] Language persists on reload
- [ ] Mobile responsive
- [ ] No console errors

### Test Scenarios

1. **Initial Load**
   - Default language (English)
   - All text displays correctly

2. **Language Switch**
   - Click button
   - All text updates immediately
   - Button text changes

3. **Persistence**
   - Switch language
   - Reload page
   - Language remains selected

4. **Dynamic Content**
   - Upload files
   - Check progress messages
   - View results
   - All in selected language

5. **Error Messages**
   - Trigger validation errors
   - Messages in correct language

## 📊 Translation Coverage

### Statistics
- **Total Keys**: 40+
- **Languages**: 2 (English, Traditional Chinese)
- **Coverage**: 100%

### Translated Sections
- ✅ Header (2 keys)
- ✅ Tabs (3 keys)
- ✅ Upload Tab (5 keys)
- ✅ Crawl Tab (8 keys)
- ✅ Directory Tab (5 keys)
- ✅ Format Options (5 keys)
- ✅ Progress (2 keys)
- ✅ Results (7 keys)
- ✅ Configuration (5 keys)
- ✅ Messages (3 keys)

## 💡 Best Practices

### For Developers

1. **Always Use Keys**: Never hardcode text
2. **Consistent Naming**: Use descriptive key names
3. **Group Related Keys**: Organize by section
4. **Test Both Languages**: Verify all translations
5. **Handle Dynamic Content**: Use `t()` function

### For Translators

1. **Context Matters**: Understand where text appears
2. **Keep Length Similar**: Avoid breaking layouts
3. **Maintain Tone**: Professional and clear
4. **Test in UI**: See how it looks
5. **Cultural Sensitivity**: Appropriate for audience

## 🐛 Troubleshooting

### Text Not Translating

**Problem**: Some text doesn't change language

**Solutions**:
1. Check `data-i18n` attribute exists
2. Verify key in translation dictionary
3. Check for typos in key name
4. Ensure `updateLanguage()` is called

### Button Not Working

**Problem**: Language switcher doesn't respond

**Solutions**:
1. Check browser console for errors
2. Verify `i18n.js` is loaded
3. Check `toggleLanguage()` function
4. Ensure button has `onclick` attribute

### Language Not Persisting

**Problem**: Language resets on reload

**Solutions**:
1. Check localStorage is enabled
2. Verify browser allows localStorage
3. Check for console errors
4. Clear browser cache and retry

### Layout Breaking

**Problem**: Text too long in one language

**Solutions**:
1. Adjust CSS for longer text
2. Use responsive design
3. Shorten translation if possible
4. Test both languages

## 🎯 Future Enhancements

### Planned Features
- [ ] Simplified Chinese support
- [ ] Japanese support
- [ ] Korean support
- [ ] Auto-detect browser language
- [ ] Language dropdown (3+ languages)
- [ ] RTL language support
- [ ] Translation management UI

### Community Contributions
We welcome translations for additional languages!

## 📚 Resources

### Files
- `static/i18n.js` - Translation dictionary
- `templates/index.html` - HTML with i18n attributes

### Documentation
- This guide (I18N_GUIDE.md)
- WEBAPP_GUIDE.md - General web app guide
- README_CN.md - Chinese documentation

## ✅ Summary

CataBot's web interface now provides:
- ✅ Full bilingual support (English/Traditional Chinese)
- ✅ One-click language switching
- ✅ Persistent language preference
- ✅ 100% translation coverage
- ✅ Responsive design
- ✅ Easy to extend

---

**Enjoy CataBot in your preferred language!** 🌏

Switch languages anytime with the button in the top-right corner.
