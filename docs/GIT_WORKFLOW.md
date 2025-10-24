# Git Workflow Guide

Guide for pushing Phase 1 implementation to your existing GitHub repository.

---

## Your Situation

You already have a GitHub repository named `nbti-promotion-automation` and you cloned it to work on the review and improvements. Now you need to push all the Phase 1 implementation back to GitHub.

---

## Preparation Steps

### Step 1: Clean Up Unnecessary Files

```bash
cd ~/nbti-promotion-automation

# Remove virtual environment (will be recreated by others)
rm -rf backend/nbti_api/venv

# Remove database files
rm -f backend/nbti_api/*.db
rm -f backend/nbti_api/*.sqlite
rm -f backend/nbti_api/*.sqlite3

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove node modules (if frontend was built)
rm -rf frontend/nbti-frontend/node_modules
rm -rf frontend/nbti-frontend/dist

# Remove test/temporary files
rm -f sample_users.csv
rm -f user_template.csv
rm -f exported_users.csv
rm -f *.log

# Remove old documentation (we have clean versions now)
rm -f CORRECTED_*.md
rm -f FIX_*.md
rm -f MANUAL_*.md
rm -f *_SUMMARY.md
rm -f INSTALL_*.md
rm -f troubleshoot_login.sh
rm -f test_user_import.sh
rm -f test_rrr_calculation.sh
rm -f testing-scripts.tar.gz
```

### Step 2: Verify .gitignore

```bash
# Check if .gitignore exists
cat .gitignore
```

If it doesn't exist or is incomplete, create it:

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/
*.egg

# Environment files
.env
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*.swn

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log
yarn-error.log
package-lock.json

# Testing
.pytest_cache/
.coverage
htmlcov/

# Temporary files
*.tmp
*.bak
*.orig
sample_users.csv
user_template.csv
exported_users.csv

# Celery
celerybeat-schedule
celerybeat.pid

# Redis
dump.rdb
EOF
```

### Step 3: Replace README with Clean Version

```bash
# Use the clean README we created
mv README_CLEAN.md README.md
```

---

## Git Workflow

### Step 1: Check Current Status

```bash
cd ~/nbti-promotion-automation

# Check current branch
git branch

# Check remote repository
git remote -v

# Check status
git status
```

### Step 2: Stage All Changes

```bash
# Add all new and modified files
git add .

# Check what will be committed
git status
```

### Step 3: Commit Changes

```bash
git commit -m "Phase 1: Complete backend implementation

Features Implemented:
- RRR calculation system (70% Exam + 20% PMS + 10% Seniority)
- Rank-based promotion allocation per CONRAISS grade
- Promotion step allocation with guaranteed salary increment
- CONRAISS-based eligibility checking (2/3/4 year cycles)
- Priority-based seniority ranking (step → date → age → file)
- Automated annual step increment with Celery
- Forensic audit logging with 10-year retention
- AWS S3 integration for file storage
- Bulk user import/export via CSV
- 74 RESTful API endpoints across 9 modules

Database:
- 21 tables with proper relationships
- 180 CONRAISS salary scale records (Grades 2-15)
- Complete schema for PMS, EMM, RRR, and System modules

Services:
- 7 business logic service modules
- 5 Celery background tasks
- JWT authentication with role-based access control
- Rate limiting and security headers

Documentation:
- Complete setup guide
- API documentation
- Troubleshooting guide
- Git workflow guide

Testing:
- All Phase 1 features tested and verified
- RRR calculation validated (70/20/10 formula)
- User import/export tested
- Database integrity confirmed
- All 74 API endpoints validated

Status: Production Ready"
```

### Step 4: Push to GitHub

```bash
# Push to main branch (or master, depending on your repo)
git push origin main

# If your default branch is 'master':
# git push origin master
```

If you encounter authentication issues:

```bash
# If using HTTPS and need to authenticate
# GitHub will prompt for username and personal access token

# Or configure SSH if you prefer
# See: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

---

## Handling Merge Conflicts

If there are conflicts with existing files:

### Option 1: Keep Your Changes (Recommended)

```bash
# Force push (use with caution - overwrites remote)
git push origin main --force

# Only use this if you're sure you want to replace everything on GitHub
```

### Option 2: Merge Existing Changes

```bash
# Pull existing changes first
git pull origin main

# If there are conflicts, resolve them manually
# Edit conflicted files, then:
git add .
git commit -m "Resolved merge conflicts"
git push origin main
```

---

## Verification

After pushing, verify on GitHub:

1. Go to https://github.com/YOUR_USERNAME/nbti-promotion-automation
2. Check that all files are uploaded
3. Verify `.env` is NOT visible (should be in .gitignore)
4. Check that README.md displays correctly
5. Verify docs/ folder contains all documentation

---

## Creating a Release (Optional)

Create a release tag for Phase 1:

```bash
# Create and push a tag
git tag -a v1.0.0 -m "Phase 1: Complete backend implementation"
git push origin v1.0.0
```

On GitHub:
1. Go to your repository
2. Click "Releases"
3. Click "Create a new release"
4. Select tag v1.0.0
5. Title: "Phase 1 - Backend Implementation"
6. Add release notes
7. Publish release

---

## Collaborator Setup

After pushing, team members can clone and set up:

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/nbti-promotion-automation.git
cd nbti-promotion-automation

# Follow setup guide
cat docs/SETUP_GUIDE.md
```

---

## Branch Strategy (For Future Development)

For Phase 2 and beyond, consider using branches:

```bash
# Create a development branch
git checkout -b development

# Make changes
git add .
git commit -m "Feature: Add new functionality"

# Push development branch
git push origin development

# When ready, merge to main via Pull Request on GitHub
```

---

## Common Git Commands

```bash
# Check status
git status

# See what changed
git diff

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes (dangerous!)
git reset --hard HEAD

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Pull latest changes
git pull origin main

# Push changes
git push origin main
```

---

## Troubleshooting Git Issues

### Authentication Failed

**Problem**: `Authentication failed`

**Solution**:
```bash
# Use personal access token instead of password
# Generate token at: https://github.com/settings/tokens

# Or set up SSH
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add ~/.ssh/id_ed25519.pub to GitHub SSH keys
```

### Large Files Error

**Problem**: `file exceeds GitHub's file size limit`

**Solution**:
```bash
# Remove large files from tracking
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit and push
git commit -m "Remove large file"
git push origin main
```

### Merge Conflicts

**Problem**: Conflicts when pulling/merging

**Solution**:
```bash
# Pull with rebase
git pull --rebase origin main

# Or manually resolve conflicts
# Edit files, remove conflict markers
git add .
git rebase --continue
```

---

## Summary

Your workflow:

1. ✅ Clean up unnecessary files
2. ✅ Verify .gitignore
3. ✅ Replace with clean README
4. ✅ Check git status
5. ✅ Add all changes: `git add .`
6. ✅ Commit with descriptive message
7. ✅ Push to GitHub: `git push origin main`
8. ✅ Verify on GitHub website
9. ✅ (Optional) Create release tag

---

**Git Workflow Guide Version**: 1.0.0  
**Last Updated**: October 2025

