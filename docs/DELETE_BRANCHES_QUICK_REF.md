# 🗑️ Branch Deletion - Quick Reference

## ⚡ Quick Start

### 1️⃣ Preview (Dry Run)
1. Go to: **Actions** → **🗑️ Delete All Branches Except Main** → **Run workflow**
2. Set: `Dry run mode` = ✅ **true**
3. Type: `DELETE ALL BRANCHES`
4. Click: **Run workflow**
5. Review the list of branches that would be deleted

### 2️⃣ Execute Deletion
1. Go to: **Actions** → **🗑️ Delete All Branches Except Main** → **Run workflow**
2. Set: `Dry run mode` = ❌ **false**
3. Type: `DELETE ALL BRANCHES` (exact spelling!)
4. Click: **Run workflow**
5. Wait for completion and verify results

---

## 🛡️ Safety Checklist

Before running the live deletion:

- [ ] Ran dry-run mode first
- [ ] Reviewed the list of branches to delete
- [ ] Confirmed no important branches are included
- [ ] Checked for open pull requests
- [ ] Communicated with team (if applicable)
- [ ] Ready to proceed with deletion

---

## ⚠️ Important Notes

- **Irreversible:** Deleted branches cannot be recovered from remote
- **Main Protected:** Main branch is automatically excluded
- **Manual Only:** Workflow never runs automatically
- **Confirmation Required:** Must type exact phrase (case-sensitive)

---

## 📊 Current Status

**Total Branches:** 67  
**To Delete:** 66 (all except main)  
**To Keep:** 1 (main only)

### Branches to be deleted:
- All `copilot/*` branches (65 branches)
- `feileberlin-patch-1` branch (1 branch)

---

## 📚 Full Documentation

For detailed instructions, troubleshooting, and safety information:
→ See [`docs/DELETE_BRANCHES_GUIDE.md`](DELETE_BRANCHES_GUIDE.md)

---

## 🆘 Need Help?

1. Check workflow logs in Actions tab
2. Review [`DELETE_BRANCHES_GUIDE.md`](DELETE_BRANCHES_GUIDE.md)
3. Contact repository maintainer

---

**Workflow File:** `.github/workflows/delete-branches.yml`  
**Created:** January 2026  
**Repository:** feileberlin/krwl-hof
