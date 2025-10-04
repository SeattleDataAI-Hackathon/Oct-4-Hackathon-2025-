# Security Guidelines

## ✅ API Key Protection

**Your `.env` file is protected** - it's in `.gitignore` and will NEVER be committed.

### Verification

```bash
# Check before committing
git status              # .env should NOT appear
git check-ignore .env   # Should output: .gitignore:138:.env
```

### Emergency: Accidentally Committed API Key?

1. **Rotate key immediately** at https://console.anthropic.com/
2. Remove from git:
   ```bash
   git rm --cached .env
   git commit --amend
   ```

## 📋 Commit Safety

✅ **Safe to commit:**
- `.env.example` (template)
- All code in `src/`, `tests/`
- Documentation (`*.md`)
- Config files (`pyproject.toml`, `Makefile`)

❌ **NEVER commit:**
- `.env` (secrets)
- `*.key`, `credentials.json`
- Database files, logs with sensitive data

## 🔒 Security Features

| Feature | Status |
|---------|--------|
| `.env` gitignored | ✅ |
| Password hashing (bcrypt) | ✅ |
| JWT tokens | ✅ |
| SQL injection protection | ✅ |
| Input validation (Pydantic) | ✅ |

## 🛡️ Best Practices

1. **Never log secrets**
   ```python
   # Bad
   logger.info(f"Key: {api_key}")
   # Good
   logger.info(f"Key: {api_key[:8]}...")
   ```

2. **Different keys for dev/prod**
3. **Rotate keys regularly**
4. **Use secrets manager in production** (AWS/GCP/Vault)

## Pre-Commit Checklist

```bash
git status              # Verify .env not listed
git diff                # Check for secrets
make test               # Ensure tests pass
```

**Your secrets are secure!** 🔒
