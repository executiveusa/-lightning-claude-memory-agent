# Coolify Deployment Support

This document provides scaffolding and configuration markers for deploying Agent Lightning to Coolify with Hostinger VPN integration.

## Overview

Coolify is a self-hosted platform-as-a-service (PaaS) alternative to Heroku, Netlify, and Railway. This guide helps you deploy Agent Lightning to your own Coolify instance, optionally tunneled through Hostinger VPN.

## Prerequisites

- Coolify instance (v4.0+) running on your server
- Optional: Hostinger VPN for secure tunneling
- Docker installed on host machine
- Git repository access

## Deployment Architecture

```
┌─────────────────┐
│  Hostinger VPN  │ (Optional)
│   (Tunneling)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Coolify     │
│   (Orchestrator)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Agent Lightning │
│    Container    │
└─────────────────┘
```

## Quick Start

### 1. Coolify Project Setup

```bash
# In Coolify dashboard:
# 1. Create new project: "agent-lightning"
# 2. Add Git source: https://github.com/executiveusa/-lightning-claude-memory-agent
# 3. Set build pack: Nixpacks
# 4. Configure environment variables (see below)
```

### 2. Environment Variables

Import secrets from your `master.secrets.json` file:

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_BASE_URL` - OpenAI API endpoint

**Optional:**
- `TINKER_API_KEY` - Tinker fine-tuning service
- `WANDB_API_KEY` - Weights & Biases tracking
- `AGENTOPS_API_KEY` - AgentOps monitoring

**Runtime:**
- `PORT` - Set to `8080` (default)
- `AGL_SERVER_HOST` - Set to `0.0.0.0`
- `PYTHONUTF8` - Set to `1`

### 3. Build Configuration

Coolify will automatically detect `nixpacks.toml` for build instructions.

**Build command:** (Auto-detected)
```bash
pip install -e .
```

**Start command:** (Auto-detected from nixpacks.toml)
```bash
python -m agentlightning.server
```

### 4. Port Configuration

- **Application Port:** 8080
- **Health Check Path:** `/health`
- **Protocol:** HTTP

## Hostinger VPN Integration

If you're using Hostinger VPN for secure tunneling:

### Setup Steps

1. **Configure VPN on Host**
   ```bash
   # Install OpenVPN client
   sudo apt-get install openvpn
   
   # Download Hostinger VPN config
   # Place in /etc/openvpn/hostinger.conf
   
   # Start VPN
   sudo openvpn --config /etc/openvpn/hostinger.conf --daemon
   ```

2. **Verify VPN Connection**
   ```bash
   # Check VPN status
   ip addr show tun0
   
   # Test external IP
   curl ifconfig.me
   ```

3. **Configure Coolify Networking**
   - Set Coolify to bind to VPN interface
   - Update firewall rules to allow traffic through VPN
   - Configure DNS if using custom domain

### Network Configuration

```yaml
# Coolify network settings (in docker-compose override)
networks:
  agent-lightning-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Firewall Rules

```bash
# Allow Coolify through VPN
sudo ufw allow in on tun0 to any port 8080
sudo ufw allow in on tun0 to any port 443
sudo ufw allow in on tun0 to any port 80
```

## Resource Allocation

Recommended settings for optimal performance:

```yaml
services:
  agent-lightning:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Health Checks

Coolify health check configuration:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Persistent Storage

If your application needs persistent data:

```yaml
volumes:
  agent-lightning-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/coolify/agent-lightning/data
```

## SSL/TLS Configuration

Coolify can automatically provision SSL certificates:

1. Enable "Auto SSL" in Coolify dashboard
2. Configure custom domain (if using)
3. Coolify will use Let's Encrypt for certificate provisioning

## Monitoring & Logs

### Access Logs

```bash
# Via Coolify dashboard
# Navigate to: Applications → agent-lightning → Logs

# Or via command line
docker logs -f <container-id>
```

### Resource Monitoring

Coolify provides built-in monitoring:
- CPU usage
- Memory usage
- Network I/O
- Disk usage

Access via: Dashboard → Applications → agent-lightning → Metrics

## Backup & Recovery

### Automated Backups

```bash
# Configure in Coolify
# Settings → Backups → Schedule

# Backup includes:
# - Application code
# - Environment variables (encrypted)
# - Persistent volumes
# - Configuration files
```

### Manual Backup

```bash
# Export environment variables
coolify env export agent-lightning > env.backup

# Backup persistent data
tar -czf agent-lightning-data.tar.gz /opt/coolify/agent-lightning/data
```

## Troubleshooting

### Common Issues

**1. Build Fails**
```bash
# Check build logs in Coolify dashboard
# Verify nixpacks.toml is present
# Ensure Python 3.10+ is available
```

**2. Application Won't Start**
```bash
# Check environment variables are set
# Verify PORT is set to 8080
# Check health check endpoint is accessible
```

**3. VPN Connection Issues**
```bash
# Verify VPN is running
sudo systemctl status openvpn@hostinger

# Check VPN interface
ip addr show tun0

# Test connectivity
ping 8.8.8.8
```

### Debug Mode

Enable debug logging:

```bash
# Add to environment variables
DEBUG=true
LOG_LEVEL=debug
```

## Migration from Railway

See [COOLIFY_MIGRATION.md](./COOLIFY_MIGRATION.md) for detailed migration instructions.

## Cost Comparison

| Feature | Railway (Free) | Coolify (Self-Hosted) |
|---------|---------------|------------------------|
| Monthly Cost | $5-20 | $5-10 (server only) |
| Resource Limits | 512MB RAM | Unlimited (server-dependent) |
| Execution Hours | 500/month | Unlimited |
| Build Minutes | 500/month | Unlimited |
| Bandwidth | 100GB | Unlimited (server-dependent) |
| Custom Domains | 1 | Unlimited |
| SSL Certificates | Included | Included (Let's Encrypt) |

## Security Considerations

1. **Secret Management**
   - Use Coolify's encrypted environment variables
   - Never commit secrets to Git
   - Rotate API keys regularly

2. **Network Security**
   - Enable VPN tunneling for production
   - Use SSL/TLS for all connections
   - Configure firewall rules appropriately

3. **Access Control**
   - Restrict Coolify dashboard access
   - Use SSH keys for server access
   - Enable 2FA where possible

## Support & Resources

- Coolify Documentation: https://coolify.io/docs
- Hostinger VPN Support: https://www.hostinger.com/tutorials/vpn
- Agent Lightning Docs: https://microsoft.github.io/agent-lightning/

## Status

🟡 **Scaffolding Complete** - Configuration markers in place, awaiting activation

To activate Coolify deployment:
1. Set up Coolify instance
2. Configure environment variables from `master.secrets.json`
3. Push code to trigger deployment
4. Monitor logs for successful startup

---

**Note:** This document provides scaffolding only. Coolify deployment is not active by default. Activate when ready to migrate from Railway or for new deployments.
