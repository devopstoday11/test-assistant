# VS Code Workspace Configuration

This directory contains VS Code workspace settings for the test-assistant project.

## Files

### `extensions.json`
Controls which extensions are recommended or unwanted for this project.

**Usage:**
- Add extension IDs to `recommendations` to suggest extensions users should install
- Add extension IDs to `unwantedRecommendations` to discourage certain extensions

**Example:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance"
  ],
  "unwantedRecommendations": [
    "ms-vscode.cpptools"
  ]
}
```

### `settings.json`
Workspace-specific settings that override user settings when this project is open.

**Current Strategy:**
- Minimal extension auto-behavior (no auto-updates, no auto-recommendations)
- Python project defaults
- Clean file exclusions to hide build artifacts

## How to Control Extensions

### Option 1: Per-Extension Control (Recommended)

1. **To enable an extension for this project:**
   - Add its ID to `extensions.json` → `recommendations`
   - Example: `"ms-python.python"`

2. **To disable an extension for this project:**
   - Add its ID to `extensions.json` → `unwantedRecommendations`
   - Or disable manually: Right-click extension → "Disable (Workspace)"

### Option 2: Extension-Specific Settings

Add settings to `settings.json` to control extension behavior:

```json
{
  "copilot.enable": false,           // Disable GitHub Copilot
  "python.analysis.autoImportCompletions": false,
  "git.enabled": false                // Disable Git integration
}
```

### Option 3: Find Extension IDs

To find an extension's ID:
1. Open VS Code Extensions view (Cmd/Ctrl + Shift + X)
2. Click on the extension
3. Look for the ID under the extension name (e.g., `ms-python.python`)
4. Or check the URL: `vscode:extension/<extension-id>`

## Current Configuration

**Status:** Minimal restrictions
- Auto-update: Disabled
- Auto-recommendations: Disabled
- Recommended extensions: None (add as needed)
- Unwanted extensions: None (add as needed)

## Adding Extensions Later

When you want to enable specific extensions:

1. **Edit `.vscode/extensions.json`:**
   ```json
   {
     "recommendations": [
       "ms-python.python",        // Python support
       "ms-python.vscode-pylance", // Python IntelliSense
       "charliermarsh.ruff"        // Python linter
     ]
   }
   ```

2. **Optionally configure in `.vscode/settings.json`:**
   ```json
   {
     "python.linting.ruffEnabled": true
   }
   ```

3. **Commit the changes** - Now everyone on the team gets the same extensions

## Notes

- These settings are **workspace-specific** and don't affect your global VS Code settings
- Users can still override workspace settings in their user settings if needed
- Extension recommendations appear when users open the project
- This approach works for team consistency without forcing installations
