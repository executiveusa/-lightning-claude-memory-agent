# Migration Guide: Railway to Coolify

This guide provides a comprehensive checklist and instructions for migrating Agent Lightning from Railway to Coolify when free-tier limits are reached or for cost optimization.

## When to Migrate

✅ **Trigger Conditions:**
- Railway free-tier execution hours exceeded (500/month)
- Monthly costs exceeding $5 threshold
- Maintenance mode automatically activated
- Resource limits causing performance issues
- Need for more control over infrastructure

## Pre-Migration Checklist

- [ ] Coolify instance set up and accessible
- [ ] Server meets minimum requirements (2GB RAM, 2 CPU cores, 20GB storage)
- [ ] SSH access to Coolify host configured
- [ ] Domain name configured (optional)
- [ ] SSL certificate provisioning method chosen
- [ ] Backup of current Railway environment variables
- [ ] Export of `master.secrets.json` with all required secrets
- [ ] VPN configuration ready (if using Hostinger VPN)

## Migration Timeline

Estimated time: **2-4 hours**

| Phase | Duration | Description |
|-------|----------|-------------|
| Preparation | 30 min | Export configs, backup data |
| Setup | 60 min | Configure Coolify, import settings |
| Testing | 30 min | Verify deployment, run health checks |
| Cutover | 30 min | Update DNS, switch traffic |
| Monitoring | 30 min | Verify stability, monitor logs |

## Step-by-Step Migration Process

### Phase 1: Preparation (Railway)

#### 1.1 Export Current Configuration

```bash
# Export environment variables from Railway
# Via Railway dashboard: Settings → Variables → Export
# Save as railway-env-backup.json

# Or use Railway CLI
railway variables --json > railway-env-backup.json
```

#### 1.2 Document Current Setup

```bash
# Note down:
- Current Railway service name
- Region/location
- Custom domains
- Build/start commands
- Resource limits
- Health check configuration
```

#### 1.3 Backup Application Data

```bash
# If using persistent storage, backup data
# Railway doesn't persist data by default, but check for:
- Database connections
- File uploads
- Cached data
```

#### 1.4 Test Current Deployment

```bash
# Verify current health endpoint
curl https://your-app.railway.app/health

# Check logs for any errors
railway logs
```

### Phase 2: Coolify Setup

#### 2.1 Create Coolify Project

1. Log into Coolify dashboard
2. Click "New Project"
3. Name: `agent-lightning-production`
4. Click "Create"

#### 2.2 Add Git Repository

1. In project, click "New Resource"
2. Select "Git Repository"
3. Repository URL: `https://github.com/executiveusa/-lightning-claude-memory-agent`
4. Branch: `main` (or your production branch)
5. Click "Continue"

#### 2.3 Configure Build Settings

```yaml
# Coolify will auto-detect from nixpacks.toml
# Verify settings:
Build Pack: Nixpacks
Build Command: (auto-detected)
Start Command: python -m agentlightning.server
Port: 8080
```

#### 2.4 Import Environment Variables

```bash
# In Coolify dashboard: Environment Variables

# REQUIRED - Copy from master.secrets.json:
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# OPTIONAL - Based on your needs:
TINKER_API_KEY=
WANDB_API_KEY=
AGENTOPS_API_KEY=dummy

# RUNTIME:
PORT=8080
AGL_SERVER_HOST=0.0.0.0
PYTHONUTF8=1
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# MONITORING:
LOG_LEVEL=info
DEBUG=false
```

#### 2.5 Configure Resource Limits

```yaml
# In Coolify: Resources tab
CPU Limit: 1.0 cores
Memory Limit: 1024 MB
CPU Reservation: 0.5 cores
Memory Reservation: 512 MB
```

### Phase 3: Hostinger VPN Setup (Optional)

#### 3.1 Install VPN Client

```bash
# SSH into Coolify host
ssh user@your-coolify-server

# Install OpenVPN
sudo apt-get update
sudo apt-get install openvpn -y

# Download Hostinger VPN config
# (Get from Hostinger control panel)
sudo wget -O /etc/openvpn/hostinger.conf https://your-vpn-config-url

# Start VPN
sudo systemctl enable openvpn@hostinger
sudo systemctl start openvpn@hostinger
```

#### 3.2 Verify VPN Connection

```bash
# Check VPN interface
ip addr show tun0

# Should see something like:
# tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP>
#     inet 10.x.x.x/24

# Test external IP (should show VPN IP)
curl ifconfig.me
```

#### 3.3 Configure Coolify for VPN

```bash
# Update Coolify to bind to VPN interface
# In Coolify settings: Network → Advanced
Bind IP: 0.0.0.0  # or specific VPN IP
```

### Phase 4: Initial Deployment

#### 4.1 Trigger First Build

```bash
# In Coolify dashboard
# Click "Deploy" button

# Monitor build logs in real-time
# Logs tab will show:
# - Git clone
# - Dependency installation
# - Application startup
```

#### 4.2 Wait for Build Completion

```bash
# Build should take 3-5 minutes
# Look for: "Build successful"
# Then: "Starting application..."
# Finally: "Application is running"
```

#### 4.3 Verify Health Check

```bash
# Get deployment URL from Coolify
# (Will be something like: https://agent-lightning-xxx.coolify.app)

# Test health endpoint
curl https://your-coolify-url.coolify.app/health

# Expected response: 200 OK
```

### Phase 5: Testing & Validation

#### 5.1 Functional Testing

```bash
# Test main endpoints
curl https://your-coolify-url.coolify.app/

# Test with sample request (if applicable)
curl -X POST https://your-coolify-url.coolify.app/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

#### 5.2 Performance Testing

```bash
# Monitor response times
time curl https://your-coolify-url.coolify.app/health

# Check resource usage in Coolify dashboard
# CPU should be < 50% idle
# Memory should be < 80% usage
```

#### 5.3 Log Verification

```bash
# Check application logs
# In Coolify: Logs tab

# Should see:
# - Application startup messages
# - No error traces
# - Successful health checks
```

### Phase 6: Domain & SSL Setup

#### 6.1 Configure Custom Domain (Optional)

```bash
# In Coolify: Domains tab
# Add domain: agent-lightning.yourdomain.com

# Update DNS records at your provider:
# Type: A or CNAME
# Name: agent-lightning
# Value: your-coolify-server-ip (or CNAME target)
# TTL: 300
```

#### 6.2 Enable SSL

```bash
# In Coolify: SSL tab
# Click "Enable Auto SSL"
# Coolify will provision Let's Encrypt certificate

# Wait 1-2 minutes for certificate issuance
# Verify: https://agent-lightning.yourdomain.com/health
```

### Phase 7: Traffic Cutover

#### 7.1 Parallel Testing

```bash
# Keep Railway running
# Test Coolify deployment in parallel
# Compare responses:

# Railway
curl https://your-app.railway.app/health

# Coolify
curl https://your-coolify-url.coolify.app/health

# Ensure identical behavior
```

#### 7.2 Update References

```bash
# Update any hard-coded URLs in:
- Documentation
- Client applications
- API consumers
- Monitoring systems
- External integrations
```

#### 7.3 Graceful Shutdown of Railway

```bash
# In Railway dashboard:
# 1. Reduce replicas to 0 (Settings → Deploy)
# 2. Or pause service (Settings → General → Pause)
# 3. Or delete service (Settings → Danger Zone)

# Keep project for 24-48 hours before permanent deletion
# in case rollback is needed
```

### Phase 8: Post-Migration Monitoring

#### 8.1 Set Up Monitoring

```bash
# In Coolify: Monitoring tab
# Enable alerts for:
- High CPU usage (> 80%)
- High memory usage (> 90%)
- Application crashes
- Failed health checks

# Configure notification channels:
- Email
- Slack
- Discord
- Webhook
```

#### 8.2 Monitor for 24 Hours

```bash
# Check hourly for first 24 hours:
- Application logs
- Error rates
- Response times
- Resource usage
- Health check status

# Use Coolify dashboard or CLI:
coolify logs agent-lightning --follow
```

#### 8.3 Performance Baseline

```bash
# Document new baseline metrics:
- Average response time
- Peak CPU usage
- Peak memory usage
- Request throughput
- Error rate
```

### Phase 9: Optimization

#### 9.1 Resource Tuning

```bash
# After 24-48 hours of monitoring, adjust:

# If CPU consistently < 30%:
# Reduce CPU allocation to 0.5 cores

# If Memory consistently < 60%:
# Reduce memory to 768 MB

# If experiencing slowness:
# Increase resources accordingly
```

#### 9.2 Caching Configuration

```bash
# Add caching layer if needed:
# In environment variables:
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_TYPE=memory
```

#### 9.3 Cost Analysis

```bash
# Compare costs:

# Railway (before migration):
- Monthly cost: $X
- Resource limits: 512MB RAM, 0.5 CPU

# Coolify (after migration):
- Server cost: $Y (e.g., $5-10/month)
- No resource limits (server-dependent)
- Unlimited execution hours

# Expected savings: $(X-Y) per month
```

## Rollback Plan

If migration encounters issues:

### Quick Rollback (< 1 hour)

```bash
# 1. Unpause Railway service
railway service:unpause

# 2. Verify Railway is healthy
curl https://your-app.railway.app/health

# 3. Update DNS back to Railway (if changed)

# 4. Investigate Coolify issues without time pressure
```

### Permanent Rollback

```bash
# If Coolify doesn't meet requirements:

# 1. Keep Railway as production
# 2. Delete Coolify deployment
# 3. Consider upgrading Railway tier instead
# 4. Or wait and retry migration later
```

## Troubleshooting

### Issue: Build Fails on Coolify

**Symptoms:** Build logs show errors during pip install

**Solutions:**
```bash
# 1. Check Python version (should be 3.10+)
# 2. Verify nixpacks.toml is present
# 3. Try manual build:
#    SSH into Coolify host
#    docker exec -it <container> /bin/bash
#    pip install -e . --verbose
```

### Issue: Application Won't Start

**Symptoms:** Container starts but immediately crashes

**Solutions:**
```bash
# 1. Check environment variables are set
# 2. Verify PORT=8080
# 3. Check application logs for stack traces
# 4. Ensure all required secrets are present
```

### Issue: Health Check Failing

**Symptoms:** Coolify reports unhealthy status

**Solutions:**
```bash
# 1. Verify health check path: /health
# 2. Test manually: curl http://localhost:8080/health
# 3. Check if application implements health endpoint
# 4. Adjust health check timeout if needed
```

### Issue: High Resource Usage

**Symptoms:** CPU/Memory consistently at 100%

**Solutions:**
```bash
# 1. Increase resource limits
# 2. Check for memory leaks in logs
# 3. Add PYTHONDONTWRITEBYTECODE=1
# 4. Reduce concurrent requests if applicable
```

### Issue: VPN Connection Drops

**Symptoms:** Intermittent connectivity issues

**Solutions:**
```bash
# 1. Check VPN service status:
sudo systemctl status openvpn@hostinger

# 2. Restart VPN:
sudo systemctl restart openvpn@hostinger

# 3. Check VPN logs:
sudo journalctl -u openvpn@hostinger -n 100

# 4. Configure auto-reconnect in VPN config
```

## Cost Comparison Calculator

```python
# Railway Cost (Free Tier):
railway_hours = 500  # Free tier limit
railway_cost_per_hour = 0.01  # After free tier
railway_monthly = railway_hours * railway_cost_per_hour
# = $5/month minimum

# Coolify Cost (Self-Hosted):
server_cost = 5  # Basic VPS (e.g., Hetzner, DigitalOcean)
# No per-hour charges
# Unlimited execution hours
coolify_monthly = server_cost
# = $5/month flat

# Savings:
# - No surprise overage charges
# - Predictable costs
# - Better resource allocation
# - More control
```

## Success Metrics

After migration, you should observe:

✅ **Performance:**
- Response times similar or better than Railway
- No increase in error rates
- Stable resource usage

✅ **Cost:**
- Predictable monthly costs
- No overage charges
- Better cost per resource unit

✅ **Reliability:**
- 99.9%+ uptime
- Successful health checks
- No unexpected downtime

✅ **Operations:**
- Easier debugging with full server access
- More control over configuration
- Simpler secret management

## Next Steps

After successful migration:

1. **Document your deployment**
   - Update README with new deployment URL
   - Update API documentation
   - Notify stakeholders

2. **Set up backup strategy**
   - Configure automated backups
   - Test restore procedure
   - Document backup locations

3. **Implement monitoring**
   - Add application performance monitoring (APM)
   - Set up log aggregation
   - Configure alerting rules

4. **Plan for scaling**
   - Document resource thresholds for scaling
   - Set up horizontal scaling if needed
   - Plan for traffic growth

## Support Resources

- **Coolify Documentation:** https://coolify.io/docs
- **Community Discord:** https://coolify.io/discord
- **Agent Lightning Docs:** https://microsoft.github.io/agent-lightning/
- **This Repository Issues:** https://github.com/executiveusa/-lightning-claude-memory-agent/issues

## Status Checklist

Track your migration progress:

- [ ] Pre-migration backup complete
- [ ] Coolify instance set up
- [ ] VPN configured (if needed)
- [ ] Environment variables imported
- [ ] First deployment successful
- [ ] Health checks passing
- [ ] Performance validated
- [ ] Custom domain configured (if needed)
- [ ] SSL enabled
- [ ] Traffic cutover complete
- [ ] Railway paused/deleted
- [ ] 24-hour monitoring complete
- [ ] Documentation updated
- [ ] Stakeholders notified
- [ ] Migration complete ✅

---

**Migration Status:** 🟡 Ready for activation when Railway free-tier limits reached

**Last Updated:** 2025-12-06

**Maintained By:** Agent Lightning Deployment Team
