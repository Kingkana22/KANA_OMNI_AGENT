# KANA OMNI AGENT - Knowledge Base Intelligence System

## Overview

KANA adalah sistem otomatis untuk membangun, memperkaya, dan menganalisis knowledge_base dari berbagai sumber. Terdiri dari 4 modul utama:

- **Injector**: Clone GitHub repositories ke knowledge_base
- **Scraper**: Extract konten dari berbagai sumber (URL, topik, paste langsung)
- **Hunter**: Search dan audit knowledge_base dengan dork patterns
- **CLI Orchestrator**: Interface terpadu untuk semua operasi

---

## Quick Start

### 1. Using the CLI (Recommended)

```bash
python kana_cli.py
```

Menu interaktif akan muncul dengan 5 pilihan:
1. **Inject Repository** - Clone GitHub repos
2. **Scrape Content** - Extract dari URL, topik, atau paste
3. **Hunt Dorks** - Search knowledge_base dengan patterns
4. **Combined Workflow** - Semua operasi dalam satu alur
5. **Settings** - Check token, paths, etc.

---

## Detailed Module Usage

### Module 1: INJECTOR (Repository Cloning)

**Purpose**: Clone GitHub repositories ke `knowledge_base/reference_codes`

**Standalone Usage**:
```bash
python injector.py
```

**Features**:
- Deteksi duplikat (skip repo yang sudah ada)
- Normalisasi URL otomatis
- Hapus `.git` folder internal
- Commit hanya folder yang ditambahkan (aman)
- Push tanpa `--force`

**URL Format Support**:
- `https://github.com/user/repo`
- `https://github.com/user/repo.git`
- `github.com/user/repo` (auto-converted)

---

### Module 2: SCRAPER (Content Extraction)

**Purpose**: Extract konten dari berbagai sumber dan simpan ke knowledge_base

**Standalone Usage**:
```bash
python scraper.py
```

**Supported Sources**:

#### 1. GitHub Repositories
```
https://github.com/user/repo
```
→ Extract: Repo metadata + README content

#### 2. GitHub Topics
```
https://github.com/topics/topic-name
```
→ Extract: Top 20 repos dengan topic tersebut

#### 3. GitHub Gists
```
https://gist.github.com/user/gist-id
```
→ Extract: Semua files dalam gist

#### 4. Raw Files
```
https://raw.githubusercontent.com/user/repo/main/file.md
```
→ Extract: File content langsung

#### 5. Web Pages
```
https://example.com/article
```
→ Extract: Article content (cleanup HTML, remove nav/footer)

#### 6. Direct Paste
```
Paste any text, code, or markdown langsung
```
→ Extract: Content as-is

**Supported Content Types**:
- Markdown (`.md`)
- Plain text (`.txt`)
- JSON (`.json`)
- Code files (`.py`, `.sol`, `.js`, `.ts`, `.php`)
- HTML (`.html`)
- Configuration (`.yaml`, `.yml`, `.env`, `.ini`)

**Saved Output**:
- Location: `knowledge_base/scraped_data/`
- Format: `scraped_{source}_{timestamp}.{ext}`
- Metadata: `scrape_metadata.json` tracks all sources

---

### Module 3: HUNTER (Dork Search)

**Purpose**: Search knowledge_base dengan pattern-based queries

**Standalone Usage**:
```bash
# Default dorks
python hunter.py

# With niche specialization
python hunter.py --niche web3
python hunter.py --niche bugbounty
python hunter.py --niche infosec
```

**Dork Syntax**:
```
filename:pattern search-term
extension:sol delegatecall
path:knowledge_base vulnerability
language:Solidity 'unchecked'
```

**Available Niches**:

1. **web3**: Solidity vulnerabilities
   - `extension:sol reentrancy`
   - `extension:sol delegatecall`
   - `extension:sol selfdestruct`

2. **bugbounty**: Credentials & secrets
   - `filename:.env password`
   - `extension:php 'password'`
   - `filename:config.php DB_PASSWORD`

3. **infosec**: General exploits
   - `extension:php 'eval('`
   - `extension:js 'document.cookie'`
   - `extension:yaml secret`

**Features**:
- Live GitHub code search (jika `GITHUB_TOKEN` set)
- Fallback ke local knowledge_base audit
- Case-insensitive matching
- Recursive file scanning
- Error handling per file

---

### Module 4: CLI Orchestrator

**Purpose**: Unified interface untuk semua operasi

**Usage**:
```bash
python kana_cli.py
```

**Workflows**:

#### Individual Operations
- Menu 1-3: Run injector, scraper, hunter secara terpisah
- Interactive prompts untuk setiap step

#### Combined Workflow (Menu 4)
Alur otomatis:
1. Inject repository (optional)
2. Scrape content dari URL (optional)
3. Hunt dorks di knowledge_base (optional)

---

## Environment Setup

### GitHub Token (Optional but Recommended)

Untuk live GitHub search dan higher rate limits:

```powershell
# Windows PowerShell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"

# Or set permanently
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "ghp_xxxxxxxxxxxxx", "User")
```

```bash
# Linux/Mac
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
```

### Python Dependencies

```bash
pip install requests beautifulsoup4
```

---

## Directory Structure

```
KANA_OMNI_AGENT/
├── knowledge_base/
│   ├── reference_codes/          # Cloned repositories
│   ├── scraped_data/             # Extracted content
│   │   └── scrape_metadata.json  # Track all scraped sources
│   ├── brain_data.json           # AI learning memory
│   └── *.md files                # Research documents
├── agent.py                      # Core agent logic
├── analyzer.py                   # Code analysis
├── brain_builder.py              # Learning & memory
├── injector.py                   # Repo injector
├── scraper.py                    # Content scraper
├── hunter.py                     # Dork hunter
├── kana_cli.py                   # Orchestrator CLI
├── notifier.py                   # Alert system
└── .agent.md                     # Custom agent definition
```

---

## Workflow Examples

### Example 1: Add & Hunt Solidity Vulnerabilities

```
kana_cli.py → Menu 4 (Combined Workflow)
1. Inject: https://github.com/user/web3-contracts
2. Scrape: https://github.com/topics/smart-contract-security
3. Hunt: web3 niche
→ Find all reentrancy, delegatecall, selfdestruct patterns
```

### Example 2: Extract & Analyze Blog Posts

```
kana_cli.py → Menu 2 (Scraper)
Paste multiple blog post URLs:
- https://example.com/security-tips
- https://medium.com/@author/article
- https://dev.to/article
→ All content saved to knowledge_base/scraped_data/
→ Automatically indexed in scrape_metadata.json
```

### Example 3: Custom Knowledge Base from Paste

```
kana_cli.py → Menu 2 (Scraper)
Paste: [Copy-paste your notes, code, or documentation directly]
→ Save to knowledge_base
→ Make searchable via Hunter
```

---

## Advanced Usage

### Scripting Integration

```python
from scraper import ContentScraper
from injector import SmartInjector

scraper = ContentScraper()
injector = SmartInjector()

# Scrape and save
content, source = scraper.scrape_content("https://github.com/org/repo")
filepath, error = scraper.save_scraped_content(content, source)

# Inject repo
target = injector.process_repo("https://github.com/org/repo")
injector.commit_and_push(target)
```

### Batch Operations

Create `batch_scrape.txt`:
```
https://github.com/topics/web3-security
https://github.com/user/repo-1
https://github.com/user/repo-2
https://blog.example.com/article
my own notes here
```

Then automate via custom script.

---

## Troubleshooting

### GitHub API Rate Limit

**Problem**: "API error 403: API rate limit exceeded"

**Solution**: 
1. Set `GITHUB_TOKEN` environment variable
2. Or wait 1 hour for limit reset

### Scraper Returns Empty Content

**Problem**: Webpage scraper returns very little text

**Solution**:
- Direct paste the content instead of URL
- Use raw GitHub URLs for code files
- Check if page requires JavaScript (BeautifulSoup won't work)

### Git Push Fails

**Problem**: "Push rejected" or "no changes to commit"

**Solution**:
1. Check git status: `git status`
2. Ensure you're in repo root
3. Verify branch exists: `git branch -a`
4. Manually commit: `git add <path> && git commit -m "msg"`

---

## Output & Metadata

### Scraped Data Metadata

File: `knowledge_base/scraped_data/scrape_metadata.json`

```json
{
  "scraped_github_com_1776283434.md": {
    "source": "https://github.com/user/repo",
    "timestamp": "2026-04-17T10:30:00",
    "content_type": "markdown",
    "size": 15234
  }
}
```

Use this to track sources, audit trails, and content provenance.

---

## License & Credits

KANA = Knowledge Aggregation & Network Analysis

Designed for security research, knowledge management, and intelligent data extraction.

---

## Next Steps

1. **Run `kana_cli.py`** for interactive mode
2. **Set `GITHUB_TOKEN`** for full GitHub access
3. **Start with Menu 2** (Scraper) to add content
4. **Use Menu 3** (Hunter) to search & analyze
5. **Combine workflows** with Menu 4 for automated pipelines

Happy hacking! 🧠
