# Railway Zero-Secrets Deployment System

## 🎯 Overview

This repository includes a complete **Railway Zero-Secrets Bootstrapper** system that enables secure, cost-protected deployment without committing secrets to version control.

## 📁 System Files

| File | Purpose |
|------|---------|
| `.agents` | Machine-readable secret specifications |
| `master.secrets.json.template` | Local secret management template |
| `railway.toml` | Railway deployment config with cost protection |
| `nixpacks.toml` | Build configuration |
| `maintenance.html` | Free-tier breach landing page |
| `DEPLOYMENT.md` | Complete deployment guide |
| `COOLIFY_SUPPORT.md` | Alternative hosting scaffolding |
| `COOLIFY_MIGRATION.md` | Migration instructions |
| `scripts/stub_integrations.py` | Integration management tool |

## 🚀 Quick Start

### 1. Setup Local Secrets

```bash
# Copy template
cp master.secrets.json.template master.secrets.json

# Add your secrets (never commit this file!)
nano master.secrets.json
```

### 2. Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set secrets
railway variables set OPENAI_API_KEY="sk-your-key"
railway variables set OPENAI_BASE_URL="https://api.openai.com/v1"

# Deploy
railway up
```

### 3. Verify Deployment

```bash
# Check health
curl https://your-app.railway.app/health

# Monitor logs
railway logs
```

## 🛡️ Cost Protection

The system includes automatic guardrails:

- ✅ **Resource Limits** - 512MB RAM, 0.5 CPU cores
- ✅ **Free Tier Monitoring** - Tracks Railway usage
- ✅ **Auto-Shutdown** - Pauses service on limit breach
- ✅ **Maintenance Mode** - Shows professional landing page
- ✅ **Migration Ready** - Pre-configured Coolify support

## 🔐 Secret Management

### What Gets Committed

✅ `.agents` - Secret specifications (safe)
✅ `railway.toml` - Config with placeholders (safe)
✅ `maintenance.html` - Public landing page (safe)
✅ All documentation files (safe)

### What Never Gets Committed

❌ `master.secrets.json` - Your actual secrets
❌ `.env` files with real values
❌ Any files matching `*.secret` or `*.secrets`
❌ Railway environment backups

## 🧩 Integration Stubbing

Optional integrations are automatically stubbed when secrets are missing:

| Integration | Stub Behavior |
|-------------|---------------|
| **Tinker** | Falls back to local training |
| **Weights & Biases** | Logs to local files only |
| **AgentOps** | Uses internal dummy endpoint |
| **CrewAI Telemetry** | Disabled by default |

### Check Integration Status

```bash
# View current status
python scripts/stub_integrations.py --check

# Generate environment template
python scripts/stub_integrations.py --generate-env

# Validate required secrets
python scripts/stub_integrations.py --validate
```

## 📊 Monitoring

### View Status

```bash
# Railway CLI
railway status
railway metrics
railway logs --follow

# Check health endpoint
curl https://your-app.railway.app/health
```

### Cost Monitoring

```bash
# Current usage
railway billing

# Resource metrics
railway metrics --detailed
```

## 🔄 Migration to Coolify

If Railway free tier is insufficient:

```bash
# See detailed migration guide
cat COOLIFY_MIGRATION.md

# Quick summary:
# 1. Set up Coolify instance
# 2. Add Git repository
# 3. Import environment variables
# 4. Deploy (auto-detected)
```

## 🆘 Troubleshooting

### Build Fails

```bash
# Check logs
railway logs --deployment

# Verify nixpacks.toml exists
ls -la nixpacks.toml
```

### App Won't Start

```bash
# Check environment variables
railway variables list

# Ensure required secrets set
railway variables get OPENAI_API_KEY
```

### Maintenance Mode Activated

This means free-tier limits were reached:

1. Wait for billing cycle reset (automatic)
2. Upgrade to Railway Pro tier
3. Migrate to Coolify (see COOLIFY_MIGRATION.md)

## 📚 Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete deployment guide
- **[COOLIFY_SUPPORT.md](./COOLIFY_SUPPORT.md)** - Coolify hosting setup
- **[COOLIFY_MIGRATION.md](./COOLIFY_MIGRATION.md)** - Migration instructions
- **[.agents](./.agents)** - Secret specifications (JSON)

## ✅ Success Criteria

Your deployment is working when:

- [x] Build completes without errors
- [x] Application starts successfully  
- [x] Health checks pass (`/health` returns 200)
- [x] No secrets in Git repository
- [x] Cost protection guardrails active
- [x] Maintenance mode ready for activation

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/executiveusa/-lightning-claude-memory-agent/issues)
- **Railway Support**: help@railway.app
- **Agent Lightning Discord**: https://discord.gg/RYk7CdvDR7

## 🎓 Learn More

- [Railway Documentation](https://docs.railway.app/)
- [Nixpacks Documentation](https://nixpacks.com/)
- [Agent Lightning Docs](https://microsoft.github.io/agent-lightning/)

---

**System Status:** 🟢 Ready for Production

**Last Updated:** 2025-12-06

For detailed instructions, see **[DEPLOYMENT.md](./DEPLOYMENT.md)**
