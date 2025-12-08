# Deployment Documentation

## GitHub Actions Workflow for GitHub Pages

This repository includes an automated deployment workflow that publishes the `static/` directory to GitHub Pages.

### How It Works

The workflow in `.github/workflows/deploy-static-to-gh-pages.yml` automatically runs when:
- Changes are pushed to the `main` branch
- The workflow is manually triggered via GitHub's Actions tab (workflow_dispatch)

When triggered, the workflow:
1. Checks out the repository code
2. Uses the `peaceiris/actions-gh-pages` action to publish the contents of the `static/` directory
3. Pushes the published files to the `gh-pages` branch as an orphan branch (no git history)
4. Ensures `.nojekyll` is created (via `enable_jekyll: false`) so files starting with underscore are not ignored

**Note:** The workflow uses `force_orphan: true` to keep the `gh-pages` branch clean without commit history. This is a best practice for deployment branches and prevents the branch from growing unnecessarily large over time.

### Configuration

To change the source branch that triggers deployment, edit the workflow file and modify:
```yaml
on:
  push:
    branches:
      - main  # Change this to your desired branch
```

To change the directory that gets published, update:
```yaml
publish_dir: ./static  # Change this to your desired directory
```

### GitHub Pages Settings

After the first successful deployment:
1. Go to your repository Settings → Pages
2. Select "Deploy from a branch" as the source
3. Choose the `gh-pages` branch and `/ (root)` directory
4. Save the settings

Your site will be available at `https://yourusername.github.io/repository-name/`

### Manual Deployment

You can trigger a deployment manually:
1. Go to the Actions tab in your repository
2. Select the "Deploy Static Site to GitHub Pages" workflow
3. Click "Run workflow" and select the branch
4. Click "Run workflow" button
