# Extension Control Guide

## Quick Reference: How to Control Extensions for This Project

### ⚠️ Important Limitation

**VS Code does NOT support "disable all extensions except whitelist" natively.**

However, you can achieve similar control using these methods:

---

## Method 1: Extension Recommendations (Current Setup)

### Files Created:
- `.vscode/extensions.json` - Lists wanted/unwanted extensions
- `.vscode/settings.json` - Workspace settings

### How It Works:
1. **Recommended extensions** - VS Code suggests these when project opens
2. **Unwanted extensions** - VS Code warns users about these
3. **Workspace settings** - Disable extension features at workspace level

### Current Status:
✅ Created with minimal restrictions
✅ Ready for you to add extension whitelist/blacklist

---

## Method 2: Manual Per-Extension Disable

**For users who want strict control:**

1. Open this project in VS Code
2. Go to Extensions view (⌘+Shift+X / Ctrl+Shift+X)
3. For each extension you want to disable:
   - Right-click the extension
   - Select **"Disable (Workspace)"**

This creates workspace-specific disable rules that **won't affect other projects**.

---

## Method 3: Use VS Code Profiles (Future)

VS Code is introducing **Profiles** feature that allows complete extension control.
When available, you can create a "test-assistant" profile with only specific extensions.

---

## How to Use This Setup

### Step 1: Define Your Extension Policy

Edit `.vscode/extensions.json`:

```json
{
  "recommendations": [
    // Extensions you WANT for this project
    "ms-python.python",
    "ms-python.vscode-pylance"
  ],
  "unwantedRecommendations": [
    // Extensions you DON'T WANT for this project
    "ms-vscode.cpptools",
    "golang.go"
  ]
}
```

### Step 2: Find Extension IDs

**Method A: From VS Code UI**
1. Open Extensions view
2. Click on extension
3. Copy the ID shown (e.g., `ms-python.python`)

**Method B: From Marketplace**
1. Visit https://marketplace.visualstudio.com/vscode
2. Search for extension
3. Check the URL or page for extension ID

**Common Extension IDs:**
```
ms-python.python              - Python
ms-python.vscode-pylance      - Python IntelliSense
charliermarsh.ruff           - Ruff (Python linter)
ms-toolsai.jupyter           - Jupyter
eamodio.gitlens              - GitLens
github.copilot               - GitHub Copilot
esbenp.prettier-vscode       - Prettier
dbaeumer.vscode-eslint       - ESLint
ms-vscode.cpptools           - C/C++
golang.go                    - Go
```

### Step 3: Disable Extension Features (Optional)

Edit `.vscode/settings.json` to disable specific extension features:

```json
{
  // Disable GitHub Copilot for this project
  "github.copilot.enable": {
    "*": false
  },

  // Disable GitLens
  "gitlens.enabled": false,

  // Disable Python type checking
  "python.analysis.typeCheckingMode": "off"
}
```

### Step 4: Commit These Files

```bash
git add .vscode/
git commit -m "Add VS Code workspace extension controls"
```

Now everyone who opens this project will see your recommendations/restrictions.

---

## Example Configurations

### Minimal Python Project (Current)

```json
// extensions.json
{
  "recommendations": [
    "ms-python.python"
  ],
  "unwantedRecommendations": []
}
```

### Strict Python-Only Project

```json
// extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff"
  ],
  "unwantedRecommendations": [
    "ms-vscode.cpptools",
    "golang.go",
    "ms-vscode.csharp",
    "redhat.java"
  ]
}
```

### No AI Assistance Project

```json
// settings.json
{
  "github.copilot.enable": {
    "*": false
  },
  "tabnine.experimentalAutoImports": false
}
```

---

## Testing Your Configuration

### Check What Extensions Are Active:

1. Open Command Palette (⌘+Shift+P / Ctrl+Shift+P)
2. Type: `Extensions: Show Enabled Extensions`
3. Verify only expected extensions are listed

### Check Workspace-Disabled Extensions:

1. Open Extensions view
2. Click filter icon
3. Select "Disabled (Workspace)"
4. See which extensions are disabled for this project only

---

## Troubleshooting

### Extensions Still Loading?

**VS Code doesn't prevent extensions from loading at the workspace level.**

You need to either:
1. Manually disable them per workspace (right-click → Disable Workspace)
2. Use extension-specific settings to disable features
3. Wait for VS Code Profiles feature

### Want Complete Control?

Create a `.vscode-insiders` or use different VS Code installation with minimal extensions installed globally.

---

## Summary

✅ **What This Setup Does:**
- Recommends extensions when project opens
- Warns about unwanted extensions
- Disables extension auto-updates
- Provides workspace-specific settings

❌ **What This Setup CANNOT Do:**
- Force disable all extensions except whitelist
- Prevent extensions from loading entirely
- Control extensions for users who don't respect recommendations

🎯 **Best Practice:**
- Use recommendations + unwanted lists
- Document required extensions in README
- Team members manually disable unwanted extensions per workspace
- Future: Use VS Code Profiles when available
