# Virtual Environment Guide

## 🔵 What is a Virtual Environment?

A virtual environment is an isolated Python environment that keeps your project dependencies separate from your system Python installation.

### Benefits
- ✅ **Isolation**: Project dependencies don't conflict with system packages
- ✅ **Reproducibility**: Easy to recreate exact environment
- ✅ **Clean**: No pollution of system Python
- ✅ **Version Control**: Lock specific package versions

## 🚀 Quick Start

### Create Virtual Environment

#### Windows
```bash
create_venv.bat
```

#### Manual Creation
```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows
```bash
venv\Scripts\activate.bat
```

#### Linux/Mac
```bash
source venv/bin/activate
```

### Deactivate
```bash
deactivate
```

## 🎯 Automatic Virtual Environment Detection

**All CataBot batch files now automatically detect and activate virtual environments!**

### Supported Virtual Environment Names
- `venv/` (recommended)
- `.venv/` (alternative)

### How It Works

When you run any batch file:
1. Checks if `venv\Scripts\activate.bat` exists
2. If found, automatically activates it
3. If not, checks for `.venv\Scripts\activate.bat`
4. Proceeds with normal operation

### Batch Files with Auto-Detection
- ✅ `setup.bat` - Installation script
- ✅ `run_demo.bat` - Demo launcher
- ✅ `run_webapp.bat` - Web app launcher
- ✅ `create_venv.bat` - Virtual environment creator

## 📋 Step-by-Step Setup

### Option 1: Automated Setup (Recommended)

```bash
# 1. Create virtual environment
create_venv.bat

# 2. Run any script - venv is automatically activated
run_webapp.bat
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run scripts (will auto-detect venv)
run_webapp.bat
```

## 🔧 Working with Virtual Environments

### Check if Virtual Environment is Active

Look for `(venv)` prefix in your command prompt:
```
(venv) C:\AIapps\CataBot>
```

### Install New Packages

```bash
# Activate venv first
venv\Scripts\activate.bat

# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Update Dependencies

```bash
# Activate venv
venv\Scripts\activate.bat

# Update all packages
pip install -r requirements.txt --upgrade

# Or update specific package
pip install --upgrade package-name
```

### Recreate Virtual Environment

```bash
# Delete old venv
rmdir /s /q venv

# Create new one
create_venv.bat
```

## 📊 Virtual Environment Structure

```
CataBot/
├── venv/                      # Virtual environment
│   ├── Scripts/
│   │   ├── activate.bat      # Activation script (Windows)
│   │   ├── python.exe        # Python interpreter
│   │   ├── pip.exe           # Package installer
│   │   └── ...
│   ├── Lib/
│   │   └── site-packages/    # Installed packages
│   └── pyvenv.cfg            # Configuration
│
├── create_venv.bat           # Create venv
├── setup.bat                 # Auto-detects venv
├── run_demo.bat              # Auto-detects venv
└── run_webapp.bat            # Auto-detects venv
```

## 💡 Best Practices

### 1. Always Use Virtual Environments
```bash
# Create venv for new projects
python -m venv venv
```

### 2. Keep requirements.txt Updated
```bash
pip freeze > requirements.txt
```

### 3. Don't Commit venv to Git
Already in `.gitignore`:
```
venv/
.venv/
```

### 4. Document Python Version
Create `.python-version` file:
```
3.11.0
```

### 5. Use Consistent Naming
- Recommended: `venv`
- Alternative: `.venv`

## 🐛 Troubleshooting

### Virtual Environment Not Detected

**Problem**: Batch file doesn't activate venv

**Solution**:
1. Ensure venv is named `venv` or `.venv`
2. Check if `venv\Scripts\activate.bat` exists
3. Manually activate: `venv\Scripts\activate.bat`

### Activation Script Not Found

**Problem**: `activate.bat` missing

**Solution**:
```bash
# Recreate virtual environment
rmdir /s /q venv
python -m venv venv
```

### Wrong Python Version in venv

**Problem**: venv uses different Python version

**Solution**:
```bash
# Specify Python version
py -3.11 -m venv venv

# Or use specific Python path
C:\Python311\python.exe -m venv venv
```

### Packages Not Found After Activation

**Problem**: Packages installed globally, not in venv

**Solution**:
```bash
# Ensure venv is active (look for (venv) prefix)
venv\Scripts\activate.bat

# Reinstall packages
pip install -r requirements.txt
```

### Permission Errors

**Problem**: Can't create/modify venv

**Solution**:
- Run Command Prompt as Administrator
- Check antivirus settings
- Ensure folder permissions

## 🔄 Migration Guide

### From Global Installation to Virtual Environment

```bash
# 1. Create virtual environment
create_venv.bat

# 2. Install dependencies
venv\Scripts\activate.bat
pip install -r requirements.txt

# 3. Test
python test_demo.py

# 4. All batch files now use venv automatically!
run_webapp.bat
```

### From Old venv to New venv

```bash
# 1. Export current packages
pip freeze > requirements_backup.txt

# 2. Delete old venv
rmdir /s /q venv

# 3. Create new venv
create_venv.bat

# 4. Verify installation
pip list
```

## 📚 Additional Resources

### Python venv Documentation
https://docs.python.org/3/library/venv.html

### Virtual Environment Tools
- **venv**: Built-in (recommended)
- **virtualenv**: Third-party alternative
- **conda**: For data science projects
- **pipenv**: Combines pip and venv

### IDE Integration

#### VS Code
1. Open Command Palette (Ctrl+Shift+P)
2. Select "Python: Select Interpreter"
3. Choose `.\venv\Scripts\python.exe`

#### PyCharm
1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `venv\Scripts\python.exe`

## 🎯 Quick Reference

### Create venv
```bash
create_venv.bat              # Automated
python -m venv venv          # Manual
```

### Activate venv
```bash
venv\Scripts\activate.bat    # Windows
source venv/bin/activate     # Linux/Mac
```

### Deactivate venv
```bash
deactivate
```

### Install packages
```bash
pip install -r requirements.txt
```

### Update requirements
```bash
pip freeze > requirements.txt
```

### Check active venv
```bash
where python                 # Should show venv path
pip list                     # Show installed packages
```

## ✅ Verification Checklist

After setting up virtual environment:

- [ ] Virtual environment created (`venv/` folder exists)
- [ ] Can activate manually (`venv\Scripts\activate.bat`)
- [ ] Batch files detect venv automatically
- [ ] All dependencies installed (`pip list`)
- [ ] Scripts run successfully
- [ ] `(venv)` prefix shows in command prompt
- [ ] `venv/` is in `.gitignore`

## 🚀 Next Steps

1. **Create venv**: Run `create_venv.bat`
2. **Test**: Run `run_demo.bat` (auto-activates venv)
3. **Develop**: All batch files now use venv automatically
4. **Deploy**: Document venv setup in deployment guide

---

**All CataBot batch files now support virtual environments automatically!** 🎉

Just create a venv once, and all scripts will use it.
