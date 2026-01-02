# Deployment Guide - All Hosting Platforms

This guide provides deployment instructions for all major hosting platforms. The application automatically detects most environments, but manual configuration is provided for each platform.

## Important: Production File Protection

**Problem**: When you deploy to a hosting server and run `git pull` to update, git might overwrite your production-specific files (like `.env`, logs, SSL certificates, etc.).

**Solution**: Use hosting-specific gitignore to protect production files.

### Quick Setup (VPS/Self-Hosted)

On your production server, run:

```bash
cd /path/to/your/app
bash hosting-examples/setup-hosting-gitignore.sh
```

This script:
- ✅ Creates `.gitignore.hosting` to protect production files
- ✅ Configures git to use it: `git config core.excludesFile .gitignore.hosting`
- ✅ Creates production `.env` template
- ✅ Sets up production-only directories (logs, backups, ssl, etc.)
- ✅ Prevents `git pull` from overwriting production data

**Files Protected from Git Pull:**
- `.env` and environment variables
- `logs/` and log files
- `backups/` and backup data
- `ssl/` and SSL certificates
- `config.local.json` and local overrides
- Production-specific generated files

**How It Works:**
- The main `.gitignore` (in the repo) controls what developers commit
- The `.gitignore.hosting` (server only) controls what git pull overwrites
- Your production secrets stay safe on the server

For more details, see [`hosting-examples/README.md`](hosting-examples/README.md)

---

## Table of Contents

- [GitHub Pages](#github-pages)
- [Vercel](#vercel)
- [Netlify](#netlify)
- [Heroku](#heroku)
- [Railway](#railway)
- [Render](#render)
- [Fly.io](#flyio)
- [Google Cloud Run](#google-cloud-run)
- [AWS (EC2, ECS, Elastic Beanstalk)](#aws)
- [DigitalOcean App Platform](#digitalocean-app-platform)
- [Azure Static Web Apps](#azure-static-web-apps)
- [Cloudflare Pages](#cloudflare-pages)
- [Generic VPS / Self-Hosted](#generic-vps--self-hosted)

---

## GitHub Pages

**Automatic Detection**: ✅ Yes (via `GITHUB_ACTIONS=true`)

### Deployment Steps

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` (or your default branch)
   - Folder: `/` (root) or `/static` depending on setup

2. **GitHub Actions Workflow** (recommended):
   Create `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy to GitHub Pages
   
   on:
     push:
       branches: [main]
     workflow_dispatch:
   
   permissions:
     contents: read
     pages: write
     id-token: write
   
   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         
         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.x'
         
         - name: Install dependencies
           run: pip install -r requirements.txt
         
         - name: Generate site
           run: python3 src/event_manager.py generate
         
         - name: Upload artifact
           uses: actions/upload-pages-artifact@v2
           with:
             path: ./static
         
         - name: Deploy to GitHub Pages
           uses: actions/deploy-pages@v2
   ```

3. **Add `.nojekyll` file** to static directory to disable Jekyll processing

### Manual Environment Configuration

If automatic detection fails, create `.env` file:
```bash
NODE_ENV=production
```

Or set in GitHub Actions workflow:
```yaml
env:
  NODE_ENV: production
```

---

## Vercel

**Automatic Detection**: ✅ Yes (via `VERCEL_ENV`)

### Deployment Steps

1. **Install Vercel CLI** (optional):
   ```bash
   npm install -g vercel
   ```

2. **Deploy via CLI**:
   ```bash
   vercel
   ```

3. **Deploy via Git** (recommended):
   - Connect your GitHub/GitLab/Bitbucket repository in Vercel dashboard
   - Vercel automatically deploys on push

4. **Configure Build Settings**:
   - Framework Preset: Other
   - Build Command: `pip install -r requirements.txt && python3 src/event_manager.py generate`
   - Output Directory: `static`
   - Install Command: `pip install -r requirements.txt`

5. **Create `vercel.json`** in root:
   ```json
   {
     "buildCommand": "pip install -r requirements.txt && python3 src/event_manager.py generate",
     "outputDirectory": "static",
     "installCommand": "pip install -r requirements.txt",
     "framework": null
   }
   ```

### Manual Environment Configuration

If automatic detection fails, add environment variable in Vercel dashboard:
- Go to Project Settings → Environment Variables
- Add: `NODE_ENV` = `production`

Or in `vercel.json`:
```json
{
  "env": {
    "NODE_ENV": "production"
  }
}
```

---

## Netlify

**Automatic Detection**: ✅ Yes (via `NETLIFY=true` + `CONTEXT=production`)

### Deployment Steps

1. **Install Netlify CLI** (optional):
   ```bash
   npm install -g netlify-cli
   ```

2. **Deploy via CLI**:
   ```bash
   netlify deploy --prod
   ```

3. **Deploy via Git** (recommended):
   - Connect your repository in Netlify dashboard
   - Netlify automatically deploys on push

4. **Create `netlify.toml`** in root:
   ```toml
   [build]
     command = "pip install -r requirements.txt && python3 src/event_manager.py generate"
     publish = "static"
   
   [build.environment]
     PYTHON_VERSION = "3.11"
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

5. **Configure Build Settings**:
   - Build command: `pip install -r requirements.txt && python3 src/event_manager.py generate`
   - Publish directory: `static`

### Manual Environment Configuration

If automatic detection fails, add environment variable in Netlify dashboard:
- Go to Site Settings → Environment Variables
- Add: `NODE_ENV` = `production`

Or in `netlify.toml`:
```toml
[build.environment]
  NODE_ENV = "production"
```

---

## Heroku

**Automatic Detection**: ✅ Yes (via `DYNO`)

### Deployment Steps

1. **Install Heroku CLI**:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

4. **Create `Procfile`** in root:
   ```
   web: python3 src/event_manager.py generate && cd static && python3 -m http.server $PORT
   ```

5. **Create `runtime.txt`** in root:
   ```
   python-3.11.6
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

### Manual Environment Configuration

If automatic detection fails, set environment variable:
```bash
heroku config:set NODE_ENV=production
```

Or in Heroku dashboard:
- Go to Settings → Config Vars
- Add: `NODE_ENV` = `production`

---

## Railway

**Automatic Detection**: ✅ Yes (via `RAILWAY_ENVIRONMENT`)

### Deployment Steps

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Project**:
   ```bash
   railway init
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Configure via `railway.json`** (optional):
   ```json
   {
     "build": {
       "builder": "nixpacks",
       "buildCommand": "pip install -r requirements.txt && python3 src/event_manager.py generate"
     },
     "deploy": {
       "startCommand": "cd static && python3 -m http.server $PORT",
       "restartPolicyType": "on-failure"
     }
   }
   ```

### Manual Environment Configuration

If automatic detection fails, set environment variable in Railway dashboard:
- Go to Variables tab
- Add: `NODE_ENV` = `production`

Or via CLI:
```bash
railway variables set NODE_ENV=production
```

---

## Render

**Automatic Detection**: ✅ Yes (via `RENDER=true`)

### Deployment Steps

1. **Create `render.yaml`** in root:
   ```yaml
   services:
     - type: web
       name: krwl-hof-events
       env: python
       buildCommand: pip install -r requirements.txt && python3 src/event_manager.py generate
       startCommand: cd static && python3 -m http.server $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.6
   ```

2. **Deploy via Dashboard**:
   - Connect your GitHub/GitLab repository
   - Render automatically deploys on push

3. **Configure Build Settings**:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt && python3 src/event_manager.py generate`
   - Start Command: `cd static && python3 -m http.server $PORT`

### Manual Environment Configuration

If automatic detection fails, add environment variable in Render dashboard:
- Go to Environment tab
- Add: `NODE_ENV` = `production`

---

## Fly.io

**Automatic Detection**: ✅ Yes (via `FLY_APP_NAME`)

### Deployment Steps

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly**:
   ```bash
   fly auth login
   ```

3. **Initialize App**:
   ```bash
   fly launch
   ```

4. **Create `fly.toml`** in root:
   ```toml
   app = "your-app-name"
   primary_region = "fra"
   
   [build]
     builder = "paketobuildpacks/builder:base"
     buildpacks = ["gcr.io/paketo-buildpacks/python"]
   
   [env]
     PORT = "8080"
   
   [[services]]
     internal_port = 8080
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   
   [deploy]
     release_command = "python3 src/event_manager.py generate"
   
   [[services.http_checks]]
     interval = 10000
     grace_period = "5s"
     method = "get"
     path = "/"
     protocol = "http"
     timeout = 2000
   ```

5. **Create `Dockerfile`** in root:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY . .
   
   RUN pip install --no-cache-dir -r requirements.txt
   RUN python3 src/event_manager.py generate
   
   EXPOSE 8080
   
   CMD ["python3", "-m", "http.server", "8080", "--directory", "static"]
   ```

6. **Deploy**:
   ```bash
   fly deploy
   ```

### Manual Environment Configuration

If automatic detection fails, set environment variable:
```bash
fly secrets set NODE_ENV=production
```

Or add to `fly.toml`:
```toml
[env]
  NODE_ENV = "production"
```

---

## Google Cloud Run

**Automatic Detection**: ✅ Yes (via `K_SERVICE`)

### Deployment Steps

1. **Install Google Cloud SDK**:
   ```bash
   curl https://sdk.cloud.google.com | bash
   ```

2. **Login and Set Project**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Create `Dockerfile`** in root:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY . .
   
   RUN pip install --no-cache-dir -r requirements.txt
   RUN python3 src/event_manager.py generate
   
   EXPOSE 8080
   
   CMD ["python3", "-m", "http.server", "8080", "--directory", "static"]
   ```

4. **Build and Push Container**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/krwl-hof
   ```

5. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy krwl-hof \
     --image gcr.io/YOUR_PROJECT_ID/krwl-hof \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Manual Environment Configuration

If automatic detection fails, set environment variable:
```bash
gcloud run services update krwl-hof \
  --set-env-vars NODE_ENV=production
```

Or in `cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/krwl-hof', '.']
    env:
      - 'NODE_ENV=production'
```

---

## AWS

**Automatic Detection**: ✅ Yes (via `AWS_EXECUTION_ENV`)

### AWS EC2

1. **Launch EC2 Instance**:
   - Ubuntu 22.04 LTS or similar
   - Open port 80 (HTTP) and 443 (HTTPS)

2. **SSH into Instance**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx git
   ```

4. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/krwl-hof.git
   cd krwl-hof
   ```

5. **Install Python Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

6. **Generate Site**:
   ```bash
   python3 src/event_manager.py generate
   ```

7. **Configure Nginx**:
   Create `/etc/nginx/sites-available/krwl-hof`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       root /home/ubuntu/krwl-hof/static;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

8. **Enable Site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/krwl-hof /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### AWS Elastic Beanstalk

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**:
   ```bash
   eb init
   ```

3. **Create `.ebextensions/python.config`**:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: app:application
     aws:elasticbeanstalk:application:environment:
       NODE_ENV: production
   ```

4. **Deploy**:
   ```bash
   eb create krwl-hof-env
   eb deploy
   ```

### Manual Environment Configuration

**EC2**: Create `.env` file in app directory:
```bash
echo "NODE_ENV=production" > .env
```

**Elastic Beanstalk**: Set environment variable:
```bash
eb setenv NODE_ENV=production
```

Or in EB console:
- Configuration → Software → Environment Properties
- Add: `NODE_ENV` = `production`

---

## DigitalOcean App Platform

**Automatic Detection**: ⚠️ Partial (set manually recommended)

### Deployment Steps

1. **Connect Repository** in DigitalOcean dashboard

2. **Configure App**:
   - Type: Web Service
   - Source: Your repository
   - Build Command: `pip install -r requirements.txt && python3 src/event_manager.py generate`
   - Run Command: `cd static && python3 -m http.server 8080`

3. **Create `.do/app.yaml`** in root:
   ```yaml
   name: krwl-hof-events
   region: fra
   
   services:
     - name: web
       github:
         repo: yourusername/krwl-hof
         branch: main
         deploy_on_push: true
       
       build_command: pip install -r requirements.txt && python3 src/event_manager.py generate
       run_command: cd static && python3 -m http.server 8080
       
       environment_slug: python
       
       http_port: 8080
       
       envs:
         - key: NODE_ENV
           value: production
   ```

4. **Deploy**:
   - Push to GitHub and DigitalOcean auto-deploys

### Manual Environment Configuration

**Required** (automatic detection may not work):

In DigitalOcean dashboard:
- Go to App Settings → Components → web → Environment Variables
- Add: `NODE_ENV` = `production`

---

## Azure Static Web Apps

**Automatic Detection**: ⚠️ Partial (set manually recommended)

### Deployment Steps

1. **Create `.github/workflows/azure-static-web-apps.yml`**:
   ```yaml
   name: Azure Static Web Apps CI/CD
   
   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]
   
   jobs:
     build_and_deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         
         - name: Install dependencies
           run: pip install -r requirements.txt
         
         - name: Generate site
           run: python3 src/event_manager.py generate
           env:
             NODE_ENV: production
         
         - name: Build And Deploy
           uses: Azure/static-web-apps-deploy@v1
           with:
             azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
             repo_token: ${{ secrets.GITHUB_TOKEN }}
             action: "upload"
             app_location: "/static"
             skip_app_build: true
   ```

2. **Create `staticwebapp.config.json`** in static directory:
   ```json
   {
     "navigationFallback": {
       "rewrite": "/index.html"
     },
     "routes": [
       {
         "route": "/*",
         "allowedRoles": ["anonymous"]
       }
     ]
   }
   ```

### Manual Environment Configuration

**Required** - Set in GitHub Actions workflow:
```yaml
env:
  NODE_ENV: production
```

---

## Cloudflare Pages

**Automatic Detection**: ⚠️ No (set manually required)

### Deployment Steps

1. **Connect Repository** in Cloudflare Pages dashboard

2. **Configure Build Settings**:
   - Framework preset: None
   - Build command: `pip install -r requirements.txt && python3 src/event_manager.py generate`
   - Build output directory: `static`

3. **Set Environment Variables** in Cloudflare dashboard:
   - `PYTHON_VERSION` = `3.11`
   - `NODE_ENV` = `production`

4. **Create `_headers`** file in static directory:
   ```
   /*
     X-Frame-Options: DENY
     X-Content-Type-Options: nosniff
     Referrer-Policy: no-referrer-when-downgrade
   ```

### Manual Environment Configuration

**Required** - In Cloudflare Pages dashboard:
- Go to Settings → Environment Variables
- Add: `NODE_ENV` = `production` (for Production environment)

---

## Generic VPS / Self-Hosted

**Automatic Detection**: ⚠️ No (set manually required)

### Deployment Steps (Ubuntu/Debian)

1. **Update System**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Dependencies**:
   ```bash
   sudo apt install python3 python3-pip nginx git certbot python3-certbot-nginx
   ```

3. **Clone Repository**:
   ```bash
   cd /var/www
   sudo git clone https://github.com/yourusername/krwl-hof.git
   sudo chown -R $USER:$USER /var/www/krwl-hof
   cd krwl-hof
   ```

4. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Set Environment Variable**:
   ```bash
   export NODE_ENV=production
   echo "export NODE_ENV=production" >> ~/.bashrc
   ```

6. **Generate Site**:
   ```bash
   python3 src/event_manager.py generate
   ```

7. **Configure Nginx**:
   Create `/etc/nginx/sites-available/krwl-hof`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       root /var/www/krwl-hof/static;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       # Caching for static assets
       location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg)$ {
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

8. **Enable Site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/krwl-hof /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

9. **Enable HTTPS with Let's Encrypt**:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

10. **Set Up Auto-Renewal**:
    ```bash
    sudo certbot renew --dry-run
    ```

### Manual Environment Configuration

**Required** - Create `.env` file:
```bash
cat > .env << EOF
NODE_ENV=production
EOF
```

Or set system-wide:
```bash
echo "export NODE_ENV=production" | sudo tee -a /etc/environment
```

---

## Troubleshooting

### Environment Not Detected

If automatic detection fails:

1. **Check Current Environment**:
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, 'src')
   from modules.utils import is_ci, is_production, is_development
   print(f'CI: {is_ci()}')
   print(f'Production: {is_production()}')
   print(f'Development: {is_development()}')
   "
   ```

2. **Force Production Mode**:
   - Create `.env` file with `NODE_ENV=production`
   - Or set environment variable in hosting platform
   - Or export in shell: `export NODE_ENV=production`

3. **Check Environment Variables**:
   ```bash
   python3 -c "import os; print(os.environ)"
   ```

### Debug Mode Still Enabled

If debug mode is still active in production:

1. **Verify config loading**:
   ```bash
   python3 -c "
   import sys
   from pathlib import Path
   sys.path.insert(0, 'src')
   from modules.utils import load_config
   config = load_config(Path('.'))
   print(f'Debug: {config[\"debug\"]}')
   print(f'Data source: {config[\"data\"][\"source\"]}')
   "
   ```

2. **Force production settings** by setting `NODE_ENV=production`

### Demo Events Still Showing

If demo events appear in production:

1. Ensure production mode is detected
2. Verify data source: should be `"real"`, not `"both"`
3. Regenerate site with `python3 src/event_manager.py generate`

---

## Platform Comparison

| Platform | Auto-Detection | Difficulty | Python Support | Free Tier | Best For |
|----------|----------------|------------|----------------|-----------|----------|
| GitHub Pages | ✅ Yes | Easy | Via Actions | ✅ Yes | Open source projects |
| Vercel | ✅ Yes | Easy | ✅ Yes | ✅ Yes | Fast deploys |
| Netlify | ✅ Yes | Easy | ✅ Yes | ✅ Yes | JAMstack sites |
| Heroku | ✅ Yes | Medium | ✅ Yes | ⚠️ Limited | Quick prototypes |
| Railway | ✅ Yes | Easy | ✅ Yes | ✅ Yes | Modern apps |
| Render | ✅ Yes | Easy | ✅ Yes | ✅ Yes | Full-stack apps |
| Fly.io | ✅ Yes | Medium | ✅ Yes | ✅ Yes | Global edge |
| Google Cloud Run | ✅ Yes | Medium | ✅ Yes | ✅ Yes | Scalable apps |
| AWS | ✅ Partial | Hard | ✅ Yes | ✅ Yes | Enterprise |
| DigitalOcean | ⚠️ Partial | Medium | ✅ Yes | ❌ No | Simple VPS |
| Azure | ⚠️ Partial | Medium | ✅ Yes | ✅ Yes | Enterprise |
| Cloudflare Pages | ❌ No | Easy | ⚠️ Limited | ✅ Yes | Static sites |
| Self-Hosted VPS | ❌ No | Hard | ✅ Yes | N/A | Full control |

---

## Support

For platform-specific issues:
- Check platform documentation
- Verify environment variables are set correctly
- Test locally with `NODE_ENV=production` first
- Open an issue on GitHub with platform details
