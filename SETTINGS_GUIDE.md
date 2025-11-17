# Settings Tab Guide

## ⚙️ AI Configuration Settings

CataBot's web interface now includes a comprehensive **Settings** tab for configuring AI providers, API keys, and models!

## 🎯 Features

### AI Provider Selection
Choose from multiple AI providers:
- **OpenAI** - GPT models (GPT-4, GPT-3.5)
- **Anthropic Claude** - Claude 3 models
- **Keyword Matching** - Free, no API key required

### API Key Management
- Securely store API keys locally
- Password-masked input fields
- Test connection before saving
- Persistent storage

### Model Selection
- **OpenAI Models**:
  - GPT-4 (Best quality, slower)
  - GPT-4 Turbo (Fast & quality)
  - GPT-3.5 Turbo (Fast & cheap) - Default
  
- **Anthropic Models**:
  - Claude 3 Opus (Best quality)
  - Claude 3 Sonnet (Balanced)
  - Claude 3 Haiku (Fast & cheap) - Default

### Keyword Fallback
- Enable/disable keyword matching fallback
- Automatically uses keywords if AI fails
- Ensures processing never fails

## 🚀 How to Use

### Access Settings

1. **Launch Web App**: `run_webapp.bat`
2. **Open Browser**: http://localhost:5000
3. **Click Settings Tab**: Fourth tab in navigation

### Configure OpenAI

1. **Select Provider**: Choose "OpenAI" from dropdown
2. **Enter API Key**: Paste your OpenAI API key (starts with `sk-`)
3. **Select Model**: Choose GPT model (default: GPT-3.5 Turbo)
4. **Test Connection**: Click "🧪 Test Connection" button
5. **Save Settings**: Click "💾 Save Settings" button

### Configure Anthropic Claude

1. **Select Provider**: Choose "Anthropic Claude"
2. **Enter API Key**: Paste your Anthropic API key (starts with `sk-ant-`)
3. **Select Model**: Choose Claude model (default: Haiku)
4. **Test Connection**: Click "🧪 Test Connection"
5. **Save Settings**: Click "💾 Save Settings"

### Use Keyword Matching (Free)

1. **Select Provider**: Choose "Keyword Matching (Free)"
2. **Save Settings**: Click "💾 Save Settings"
3. No API key required!

## 📊 Settings Storage

### Local Storage
- Settings saved to `settings.json` file
- Located in CataBot root directory
- Automatically loaded on startup
- Gitignored for security

### Settings File Format
```json
{
  "ai_provider": "openai",
  "openai_api_key": "sk-...",
  "openai_model": "gpt-3.5-turbo",
  "anthropic_api_key": "",
  "anthropic_model": "claude-3-haiku-20240307",
  "use_keyword_fallback": true
}
```

## 🔌 API Endpoints

### Get Settings
```
GET /api/settings

Returns:
{
  "ai_provider": "openai",
  "openai_api_key": "sk-...",
  "openai_model": "gpt-3.5-turbo",
  ...
}
```

### Save Settings
```
POST /api/settings
Content-Type: application/json

{
  "ai_provider": "openai",
  "openai_api_key": "sk-...",
  "openai_model": "gpt-3.5-turbo",
  ...
}

Returns:
{
  "success": true,
  "message": "Settings saved successfully"
}
```

### Test API Connection
```
POST /api/test-api
Content-Type: application/json

{
  "provider": "openai",
  "api_key": "sk-..."
}

Returns:
{
  "success": true,
  "message": "OpenAI API connection successful"
}
```

## 🎨 UI Features

### Provider-Specific Sections
- **Dynamic Visibility**: Only shows settings for selected provider
- **OpenAI Section**: Appears when OpenAI is selected
- **Anthropic Section**: Appears when Anthropic is selected
- **Keyword Mode**: No additional settings needed

### Password Protection
- API keys displayed as password fields
- Masked with dots (•••)
- Can be revealed if needed

### Test Connection Button
- Validates API key before saving
- Shows success/error message
- Prevents saving invalid keys

### Success/Error Messages
- **Green Box**: Settings saved successfully
- **Red Box**: Error occurred
- **Auto-Hide**: Messages disappear after 3-5 seconds

## 🔒 Security

### API Key Storage
- Stored locally in `settings.json`
- Not transmitted over network (except to AI providers)
- Gitignored to prevent accidental commits
- Only accessible on local machine

### Best Practices
1. **Never Share API Keys**: Keep them private
2. **Use Environment Variables**: For production deployments
3. **Rotate Keys Regularly**: Change keys periodically
4. **Monitor Usage**: Check API usage on provider dashboards
5. **Set Spending Limits**: Configure limits on provider platforms

## 💡 Model Comparison

### OpenAI Models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| GPT-4 | Slow | Excellent | High | Critical accuracy |
| GPT-4 Turbo | Fast | Excellent | Medium | Balanced needs |
| GPT-3.5 Turbo | Very Fast | Good | Low | High volume |

### Anthropic Models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| Claude 3 Opus | Slow | Excellent | High | Complex tasks |
| Claude 3 Sonnet | Medium | Very Good | Medium | General use |
| Claude 3 Haiku | Fast | Good | Low | Quick processing |

### Keyword Matching

| Feature | Value |
|---------|-------|
| Speed | Very Fast |
| Quality | Fair (75-80%) |
| Cost | Free |
| Best For | No API key, testing |

## 🧪 Testing Your Configuration

### Test Checklist

1. **Enter API Key**: Paste valid key
2. **Click Test**: Use "🧪 Test Connection" button
3. **Check Message**: 
   - ✅ Green = Success
   - ❌ Red = Failed
4. **Save Settings**: Click "💾 Save Settings"
5. **Process Test File**: Upload a PDF to verify

### Common Test Results

**Success**:
```
✅ API connection successful!
```

**Invalid Key**:
```
❌ API connection failed: Invalid API key
```

**Network Error**:
```
❌ API connection failed: Network request failed
```

## 🔄 Switching Providers

### Easy Provider Switch

1. **Open Settings Tab**
2. **Select New Provider**: Choose from dropdown
3. **Enter New API Key**: If required
4. **Test Connection**: Verify it works
5. **Save Settings**: Apply changes
6. **Process Files**: New provider used automatically

### Fallback Behavior

With "Use Keyword Fallback" enabled:
1. Tries selected AI provider first
2. If AI fails → Uses keyword matching
3. Ensures processing never fails
4. Logs which method was used

## 📱 Bilingual Support

### Language Support
- All settings text translated
- English and Traditional Chinese
- Switch language anytime
- Settings labels update instantly

### Translated Elements
- Tab name: "Settings" / "設定"
- Section titles
- Button labels
- Help text
- Success/error messages

## 🎓 Examples

### Example 1: Configure OpenAI

```
1. Click "⚙️ Settings" tab
2. Provider: "OpenAI"
3. API Key: "sk-proj-abc123..."
4. Model: "GPT-3.5 Turbo"
5. Click "🧪 Test Connection"
6. See: "✅ API connection successful!"
7. Click "💾 Save Settings"
8. See: "Settings saved successfully!"
```

### Example 2: Switch to Claude

```
1. Open Settings tab
2. Provider: "Anthropic Claude"
3. API Key: "sk-ant-xyz789..."
4. Model: "Claude 3 Haiku"
5. Test → Save
6. Upload PDF → Uses Claude now
```

### Example 3: Use Free Mode

```
1. Open Settings tab
2. Provider: "Keyword Matching (Free)"
3. Click "💾 Save Settings"
4. No API key needed!
5. Process files with keyword matching
```

## 🐛 Troubleshooting

### API Key Not Working

**Problem**: Test connection fails

**Solutions**:
1. Check key is complete (starts with `sk-` or `sk-ant-`)
2. Verify key is active on provider dashboard
3. Check internet connection
4. Ensure no extra spaces in key
5. Try regenerating key on provider site

### Settings Not Saving

**Problem**: Settings reset after reload

**Solutions**:
1. Check `settings.json` file exists
2. Verify write permissions
3. Check browser console for errors
4. Try clearing browser cache
5. Restart web application

### Wrong Provider Used

**Problem**: Using wrong AI provider

**Solutions**:
1. Open Settings tab
2. Verify correct provider selected
3. Click "💾 Save Settings" again
4. Restart processing job
5. Check `settings.json` file

### Test Connection Timeout

**Problem**: Test takes too long

**Solutions**:
1. Check internet connection
2. Verify provider API status
3. Try different model
4. Check firewall settings
5. Wait and retry

## 📚 Additional Resources

### Getting API Keys

**OpenAI**:
1. Visit: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy key immediately (shown once)
5. Paste into CataBot settings

**Anthropic**:
1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Generate new key
5. Copy and paste into CataBot

### Cost Management

**OpenAI**:
- Set usage limits in dashboard
- Monitor usage regularly
- Use GPT-3.5 for cost savings
- Enable spending alerts

**Anthropic**:
- Check usage in console
- Use Haiku for lower costs
- Set budget limits
- Monitor token usage

## ✅ Summary

The Settings tab provides:
- ✅ Multiple AI provider support
- ✅ Secure API key management
- ✅ Model selection
- ✅ Connection testing
- ✅ Persistent storage
- ✅ Keyword fallback
- ✅ Bilingual interface
- ✅ Easy provider switching

---

**Configure your AI settings now for better classification accuracy!** ⚙️

Access Settings: http://localhost:5000 → Click "⚙️ Settings" tab
