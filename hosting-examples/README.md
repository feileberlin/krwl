# Hosting Configuration Examples

This directory contains example configuration files for various hosting platforms. Copy the relevant file(s) to your project root when deploying to that platform.

## Files

- `vercel.json.example` - Vercel configuration
- `netlify.toml.example` - Netlify configuration
- `Procfile.example` - Heroku configuration
- `railway.json.example` - Railway configuration
- `render.yaml.example` - Render configuration
- `fly.toml.example` - Fly.io configuration
- `Dockerfile.example` - Docker configuration (for Fly.io, Google Cloud Run, AWS ECS, etc.)
- `cloudbuild.yaml.example` - Google Cloud Build configuration
- `app.yaml.example` - DigitalOcean App Platform configuration
- `azure-static-web-apps-config.json.example` - Azure Static Web Apps configuration
- `_headers.example` - Cloudflare Pages headers
- `nginx.conf.example` - Nginx configuration for VPS

## Usage

1. Copy the example file for your platform
2. Rename it (remove `.example` suffix)
3. Customize for your project
4. The actual config files (without `.example`) are gitignored by default
5. Commit only if you want to share your specific configuration

## Why are these gitignored?

Platform-specific config files often contain:
- Environment-specific settings
- API tokens or keys
- Deployment-specific configuration
- Different settings for staging vs production

By gitignoring them by default, you can:
- Keep sensitive information out of git
- Have different configs per deployment
- Test different configurations locally
- Share examples without forcing your specific setup

## How to include in git (if needed)

If you want to commit your platform config:
1. Remove it from `.gitignore`
2. Or use `git add -f filename` to force add
3. Ensure no secrets are included
