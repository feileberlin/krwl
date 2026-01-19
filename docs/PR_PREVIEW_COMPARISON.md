# PR Preview Comparison - KISS vs Alternatives

> Comparing different PR preview methods to understand why we chose the KISS approach

## Quick Comparison Table

| Feature | **GitHub Actions Artifacts** (Our Choice) | Netlify/Vercel | GitHub Pages Per-Branch |
|---------|------------------------------------------|----------------|------------------------|
| **Complexity** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐ Moderate | ⭐⭐ Complex |
| **Setup Time** | 5 minutes | 15-30 minutes | 30-60 minutes |
| **External Services** | ❌ None | ✅ Required | ❌ None |
| **API Keys/Tokens** | ❌ None | ✅ Required | ✅ Required (PAT) |
| **Live URL** | ❌ No (download) | ✅ Yes | ✅ Yes |
| **Deployment Speed** | Fast (1-2 min) | Fast (2-3 min) | Moderate (3-5 min) |
| **Storage** | GitHub (free) | External | GitHub (many branches) |
| **Cleanup** | Automatic | Manual/Webhook | Manual |
| **Privacy** | 🔒 Private | 🌐 Public URL | 🌐 Public URL |
| **Cost** | Free | Free tier | Free |
| **Maintenance** | Zero | Account management | Branch cleanup |
| **KISS Score** | 10/10 | 6/10 | 4/10 |

## Detailed Analysis

### 1. GitHub Actions Artifacts (Our Choice) ⭐

**How it works:**
```
Developer → Push to PR → GitHub Actions → Build → Upload Artifact
                                                         ↓
Reviewer ← Download ZIP ← GitHub UI ← Click comment link
```

**Pros:**
- ✅ **Zero setup** - Just add workflow file
- ✅ **No external dependencies** - Pure GitHub
- ✅ **No secrets needed** - Uses GITHUB_TOKEN (automatic)
- ✅ **Auto cleanup** - 90-day expiration
- ✅ **Privacy** - Download and test locally
- ✅ **Offline testing** - Works without internet after download
- ✅ **Simple workflow** - ~170 lines of YAML
- ✅ **No account creation** - Works with existing GitHub

**Cons:**
- ❌ **No live URL** - Must download and open locally
- ❌ **Manual step** - Reviewer clicks download link
- ❌ **Not instant** - ~30 seconds to download and extract

**KISS Rating:** 10/10 - Perfectly simple!

**Best for:**
- Projects prioritizing simplicity
- Teams that value privacy
- Developers comfortable with local testing
- Projects with occasional PRs (not 100s/day)

### 2. Netlify/Vercel Deploy Previews

**How it works:**
```
Developer → Push to PR → GitHub Webhook → External Service → Build → Deploy → Live URL
                                                                                  ↓
Reviewer ← Click live URL ← PR Comment ← Webhook ← External Service
```

**Pros:**
- ✅ **Live URL** - Instant access in browser
- ✅ **Auto-deploy** - No manual download
- ✅ **Professional** - Industry-standard solution
- ✅ **CDN** - Fast global access
- ✅ **HTTPS** - Automatic SSL
- ✅ **Custom domains** - Can use your domain

**Cons:**
- ❌ **External service** - Dependency on Netlify/Vercel
- ❌ **Account required** - Sign up needed
- ❌ **Configuration** - netlify.toml or vercel.json
- ❌ **Secrets management** - API keys in GitHub
- ❌ **Service outages** - Depends on external uptime
- ❌ **Privacy** - Public URLs (anyone with link can access)
- ❌ **Cleanup** - Manual deletion or webhook setup
- ❌ **Cost** - Free tier limits (paid for heavy use)

**KISS Rating:** 6/10 - Adds complexity

**Best for:**
- Projects with many contributors
- Teams wanting instant previews
- Production-critical applications
- Projects with CI/CD budget

### 3. GitHub Pages Per-Branch Deployments

**How it works:**
```
Developer → Push to PR → GitHub Actions → Build → Deploy to gh-pages-pr-123
                                                                ↓
Reviewer ← Visit URL ← https://user.github.io/repo/pr-123
```

**Pros:**
- ✅ **Live URL** - Works like GitHub Pages
- ✅ **No external service** - All in GitHub
- ✅ **HTTPS** - Automatic SSL
- ✅ **Free** - No cost

**Cons:**
- ❌ **Complex workflow** - Branch management logic
- ❌ **Many branches** - One per PR (clutter)
- ❌ **Manual cleanup** - Old PR branches accumulate
- ❌ **PAT required** - Personal Access Token for deployment
- ❌ **URL management** - Need to track PR numbers
- ❌ **Force push issues** - Can conflict
- ❌ **Repository bloat** - Many deployment branches

**KISS Rating:** 4/10 - Too complex

**Best for:**
- Projects that already use GitHub Pages
- Teams wanting live URLs without external services
- Long-lived preview requirements

### 4. Manual Deployment (No Automation)

**How it works:**
```
Developer → Push to PR → Reviewer → Manual: git checkout, build, run
```

**Pros:**
- ✅ **Ultimate simplicity** - No automation needed
- ✅ **Full control** - Test exactly as deployed

**Cons:**
- ❌ **Time-consuming** - 5-10 minutes per PR
- ❌ **Error-prone** - Manual steps can be forgotten
- ❌ **Inconsistent** - Different reviewers, different setups
- ❌ **Knowledge required** - Must know build process

**KISS Rating:** 8/10 - Simple but inefficient

**Best for:**
- Very small teams (1-2 people)
- Occasional contributions
- Learning/experimental projects

## Why We Chose Artifacts

### Decision Factors

1. **KISS Philosophy Match**
   - Project values simplicity above all
   - No external dependencies is a core principle
   - Artifacts are the simplest automated solution

2. **PR Volume**
   - This project has moderate PR volume (not 50/day)
   - Manual download is acceptable trade-off
   - ~30 seconds to test vs ~5 seconds for live URL

3. **Privacy**
   - Community project with local event data
   - Better to test locally than expose on public URL
   - Reviewers can test without sharing link

4. **Zero Setup**
   - Just add workflow file - done!
   - No accounts, tokens, or configuration
   - Works immediately after merge

5. **Maintenance**
   - Auto-cleanup (90-day expiration)
   - No branch management
   - No service account maintenance

### When to Consider Alternatives

**Use Netlify/Vercel if:**
- You have 20+ PRs/day
- Contributors are non-technical (need instant URL)
- You already use these services for production
- Budget allows for premium features

**Use GitHub Pages per-branch if:**
- You need live URLs but no external services
- You have good branch cleanup automation
- Your team is comfortable with git gymnastics
- GitHub Pages is already part of your workflow

**Use manual testing if:**
- You have 1-2 contributors
- PRs are rare (1-2 per month)
- Team is technical and prefers local testing
- Automation overhead isn't worth it

## Migration Path

If you outgrow artifacts, migration is simple:

### To Netlify/Vercel
1. Create account and link repo
2. Add netlify.toml or vercel.json
3. Enable PR previews in service dashboard
4. Keep or remove artifact workflow

**Effort:** 30 minutes
**Reversible:** Yes (just disable service)

### To GitHub Pages per-branch
1. Create gh-pages branch
2. Add deployment workflow
3. Add branch cleanup workflow
4. Remove artifact workflow

**Effort:** 2-3 hours (includes testing)
**Reversible:** Yes (delete branches and workflow)

## Real-World Usage Examples

### Our Workflow (Artifacts)

```bash
# Reviewer sees PR comment
# Clicks "Download Preview Artifact"
# Downloads pr-123-preview.zip (2MB)
# Extracts in ~/Downloads
cd ~/Downloads/pr-123-preview/public
python3 -m http.server 8000
# Opens http://localhost:8000
# Tests the changes
# Leaves review on PR
```

**Time:** ~1 minute
**Complexity:** Low
**Satisfaction:** High (full control)

### Netlify Workflow (Example)

```bash
# Reviewer sees PR comment
# Clicks "View deployment"
# Opens in browser immediately
# Tests the changes
# Leaves review on PR
```

**Time:** ~10 seconds
**Complexity:** Low
**Satisfaction:** High (instant access)

### GitHub Pages per-branch (Example)

```bash
# Workflow builds and deploys
# Reviewer opens https://user.github.io/repo/pr-123
# Tests the changes
# Later: Cleanup workflow deletes old PR branches
```

**Time:** ~15 seconds
**Complexity:** High (setup)
**Satisfaction:** Moderate (cleanup needed)

## Conclusion

For the **KRWL HOF Community Events** project:

✅ **GitHub Actions Artifacts** is the perfect fit because:
- Aligns with KISS philosophy
- Zero external dependencies
- Simple to understand and maintain
- Adequate for our PR volume
- Privacy-friendly
- No ongoing costs or maintenance

The slightly longer testing time (download + extract) is a worthwhile trade-off for:
- Radical simplicity
- Zero configuration
- Complete independence
- Local testing control

## Further Reading

- [GitHub Actions Artifacts Documentation](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [Netlify Deploy Previews](https://docs.netlify.com/site-deploys/deploy-previews/)
- [Vercel Preview Deployments](https://vercel.com/docs/deployments/preview-deployments)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [KISS Principle](https://en.wikipedia.org/wiki/KISS_principle)

---

**Bottom line:** Choose the simplest solution that meets your needs. For us, that's artifacts! 🎯
