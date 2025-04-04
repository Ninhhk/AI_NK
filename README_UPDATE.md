# Project Update Scripts

This directory contains scripts to simplify the process of updating the project, managing dependencies, and running basic tests.

## Available Scripts

1. **Windows**: `update_project.bat`
2. **macOS/Linux**: `update_project.sh`
3. **Python Core**: `update_and_test.py`

## What these scripts do

When executed, these scripts will:

1. Pull the latest changes from git
2. Update the poetry lock file
3. Install all dependencies 
4. Run basic tests to verify key dependencies are working correctly

## Usage

### On Windows

Simply double-click on `update_project.bat` or run it from the command line:

```cmd
update_project.bat
```

### On macOS/Linux

Make the shell script executable (if not already) and run it:

```bash
chmod +x update_project.sh
./update_project.sh
```

### Advanced Usage

You can pass various flags to control the update process:

```
# Windows (Continue even if some steps fail)
update_project.bat --continue-on-error

# Linux/Mac (Continue even if some steps fail)
./update_project.sh --continue-on-error

# Skip stashing local changes (not recommended)
update_project.bat --skip-stash
./update_project.sh --skip-stash

# Only stash changes without updating (useful for quick context switching)
update_project.bat --stash-only
./update_project.sh --stash-only

# Don't restore stashed changes after updating
update_project.bat --no-restore
./update_project.sh --no-restore
```

### Git Stash Protection

The update scripts automatically handle local changes in your working directory:

1. **Auto-stashing**: Any local uncommitted changes are automatically stashed before pulling updates
2. **Conflict Detection**: After update, the script checks if restoring changes would cause conflicts
3. **Conflict Resolution Options**: If conflicts are detected, you'll be given options:
   - Apply stash anyway (might cause conflicts)
   - Keep changes stashed (with instructions to restore later)
   - Create a branch with your stashed changes (safest option)

This prevents the common issue of losing work or creating merge conflicts during updates.

## Requirements

These scripts require the following tools to be installed and available in your PATH:

1. Git
2. Python (3.8 or newer)
3. Poetry (Python package manager)

## Troubleshooting

If you encounter any issues:

1. **Python not found**: Ensure Python is installed and added to your PATH
2. **Git not found**: Install Git or add it to your PATH
3. **Poetry not found**: Install Poetry following instructions at [python-poetry.org](https://python-poetry.org/docs/#installation)
4. **Dependency errors**: Check that all required dependencies are properly installed

For more detailed assistance, please refer to the main project documentation. 