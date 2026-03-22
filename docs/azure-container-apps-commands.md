# Azure Container Apps - CLI Commands Reference

**Project:** Portfolio Backend  
**Date:** March 22, 2026  
**Resource Group:** rg-portfolio-dev-win  
**Container App:** portfolio-backend

---

## 1. Resource Setup

### Create Resource Group
```bash
az group create --name portfolio-rg --location eastus
```

### Create Container App Environment
```bash
az containerapp env create --name portfolio-env --resource-group portfolio-rg --location eastus
```

---

## 2. Deployment

### Deploy Container App (Docker Hub)
```bash
az containerapp create --name portfolio-backend --resource-group rg-portfolio-dev-win --environment portfolio-env --image sayansaha1999/portfolio-backend:latest --target-port 80 --ingress external --cpu 0.5 --memory 1.0Gi --min-replicas 0 --max-replicas 3
```

---

## 3. Container App Configuration

### Check Active Revision Mode (Single vs Multiple)
```cmd
az containerapp show --name portfolio-backend --resource-group rg-portfolio-dev-win --query "properties.configuration.activeRevisionsMode" --output tsv
```

### Update CPU and Memory
```cmd
az containerapp update --name portfolio-backend --resource-group rg-portfolio-dev-win --cpu 0.5 --memory 1.0Gi
```

---

## 4. Logs & Monitoring

### Stream Live Console Logs
```bash
az containerapp logs show --name portfolio-backend --resource-group rg-portfolio-dev-win --type console --follow
```

### View System Logs (Startup/Crash Issues)
```bash
az containerapp logs show --name portfolio-backend --resource-group rg-portfolio-dev-win --type system
```

### KQL Query (Azure Portal > Logs)
```kql
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "portfolio-backend"
| order by TimeGenerated desc
| take 50
```

---

## 5. Revision Management

### List Active Revisions
```cmd
az containerapp revision list --name portfolio-backend --resource-group rg-portfolio-dev-win --output table
```

### List All Revisions (Including Inactive)
```cmd
az containerapp revision list --name portfolio-backend --resource-group rg-portfolio-dev-win --all --output table
```

### Show Revision Details
```cmd
az containerapp revision show --name portfolio-backend --resource-group rg-portfolio-dev-win --revision <revision-name> --output json
```

### Activate a Revision
```cmd
az containerapp revision activate --name portfolio-backend --resource-group rg-portfolio-dev-win --revision <revision-name>
```

### Deactivate a Revision
```cmd
az containerapp revision deactivate --name portfolio-backend --resource-group rg-portfolio-dev-win --revision <revision-name>
```

### Restart a Revision
```cmd
az containerapp revision restart --name portfolio-backend --resource-group rg-portfolio-dev-win --revision <revision-name>
```

### Switch Revision Mode (Single / Multiple)
```cmd
az containerapp revision set-mode --name portfolio-backend --resource-group rg-portfolio-dev-win --mode multiple
```

### Check Revision Provisioning Error
```cmd
az containerapp revision show --name portfolio-backend --resource-group rg-portfolio-dev-win --revision <revision-name> --query "{state:properties.runningState, healthState:properties.healthState, provisionError:properties.provisioningError}" --output json
```

---

## 6. Ingress Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Ingress | external | Public HTTPS endpoint |
| Target Port | 80 | Must match container's listening port |
| Allow Insecure | false | Redirects HTTP → HTTPS |
| Transport | http | Azure handles TLS termination |

---

## 7. Notes

- **Minimum recommended resources:** 0.5 vCPU / 1 Gi RAM (due to LangChain, Cohere SDK, sentence-transformers)
- **0.25 vCPU / 0.5 Gi** causes activation failures (OOM)
- **Single revision mode:** Only latest revision is active; can't manually reactivate old revisions — push a new update instead
- **CMD line continuation:** Use `^` in CMD, `\` in bash/PowerShell
- Azure auto-provisions TLS on port 443; `targetPort` is the internal container port
