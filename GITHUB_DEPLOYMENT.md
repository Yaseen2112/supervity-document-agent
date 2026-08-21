# 🚀 Deployment Guide - GitHub

This guide will help you deploy your Document Extraction Agent to GitHub.

## Step 1: Create a GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to [GitHub](https://github.com)
2. Click **"New"** (top-left, near your profile)
3. Repository name: `supervity-document-agent`
4. Description: `A lightweight document processing agent that classifies and extracts vendor documents into structured JSON`
5. Choose **Public** (for open-source) or **Private** (for confidential)
6. Click **"Create repository"**

### Option B: Using GitHub CLI

```bash
gh repo create supervity-document-agent --public --source=. --remote=origin --push
```

## Step 2: Initialize Git in Your Project

```bash
cd c:\Users\Yaseen2112\supervity-document-agent

# Initialize git repository
git init

# Configure user (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Document extraction agent with PDF, OCR, and JSON output support"

# Add GitHub repository as remote
git remote add origin https://github.com/yourusername/supervity-document-agent.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 3: Verify GitHub Repository

1. Open your repository on GitHub: `https://github.com/yourusername/supervity-document-agent`
2. Verify all files are uploaded correctly
3. Check that README is displayed on the main page

## Step 4: Add GitHub Badges (Optional)

Add to your README.md:

```markdown
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)
```

## Step 5: Setup GitHub Actions (CI/CD - Optional)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: python run_tests.py
```

## Step 6: Setup GitHub Pages Documentation (Optional)

1. Go to Repository Settings → Pages
2. Select `main` branch and `/docs` folder
3. Your documentation will be available at: `https://yourusername.github.io/supervity-document-agent`

## File Checklist

Before pushing, ensure you have:

- ✅ README.md - Main documentation
- ✅ requirements.txt - Dependencies
- ✅ .gitignore - Ignore unnecessary files
- ✅ run_tests.py - Test suite
- ✅ app/ - Source code
- ✅ tests/ - Test cases
- ✅ sample_data/ - Sample documents
- ✅ LICENSE - License file (optional)

## Common Git Commands

```bash
# Check status
git status

# Add specific file
git add filename.py

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push

# Pull latest changes
git pull

# Create new branch
git checkout -b feature-name

# Switch branch
git checkout main

# View commit history
git log --oneline
```

## After Deployment

### 1. Share Your Repository
- Copy repository URL: `https://github.com/yourusername/supervity-document-agent`
- Share with team members via:
  - Email
  - Slack
  - LinkedIn
  - GitHub Issues/Discussions

### 2. Setup Collaborators
In Repository Settings → Collaborators:
- Add team members who can contribute
- Set appropriate permissions (Read, Write, Admin)

### 3. Enable Issues & Discussions
In Repository Settings:
- Enable Issues for bug tracking
- Enable Discussions for feature requests
- Enable Projects for project management

### 4. Create Releases (Optional)
When ready for production:
1. Go to Releases → Create new release
2. Tag: `v1.0.0`
3. Title: `Version 1.0.0 - Production Release`
4. Add release notes
5. Attach files if needed

## Troubleshooting

### Git Command Not Found
```bash
# Install Git from: https://git-scm.com/download/win
# Or use GitHub Desktop: https://desktop.github.com/
```

### Authentication Error
```bash
# Generate Personal Access Token:
# 1. GitHub Settings → Developer settings → Personal access tokens
# 2. Generate new token (repo scope)
# 3. Use as password when pushing
```

### Large Files
If files exceed 100MB:
```bash
# Install Git LFS
pip install git-lfs
git lfs install

# Track large files
git lfs track "*.pdf"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

## Next Steps

After deployment:

1. **Add Documentation**
   - Create `/docs` folder
   - Add API documentation
   - Add usage examples

2. **Setup CI/CD**
   - Add GitHub Actions workflows
   - Automate testing
   - Automate deployment

3. **Create Issues**
   - Known limitations
   - Feature requests
   - Bug tracking

4. **Community**
   - Add Contributing guidelines
   - Create Code of Conduct
   - Setup Discussions

## Success Checklist

- ✅ Repository created on GitHub
- ✅ All files pushed
- ✅ README is displaying correctly
- ✅ Tests pass on GitHub Actions (if configured)
- ✅ Repository is accessible
- ✅ Clone works: `git clone https://github.com/yourusername/supervity-document-agent.git`

---

**Ready to Deploy?**

Run these commands:
```bash
cd c:\Users\Yaseen2112\supervity-document-agent
git init
git add .
git commit -m "Initial commit: Document extraction agent"
git remote add origin https://github.com/yourusername/supervity-document-agent.git
git branch -M main
git push -u origin main
```

Replace `yourusername` with your actual GitHub username!
