import platform
import urllib.request
import json
from pathlib import Path
import os
import sys
import subprocess
from platformdirs import user_cache_dir

def get_system_info():
    """Get system and architecture info"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        system = "macos"
    
    if machine == "x86_64":
        machine = "x64"
    elif machine == "aarch64":
        machine = "arm64"
        
    return system, machine

def get_fastwand_version():
    """Get latest version of fastwand CLI"""
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/banditburai/fastwandCLI/releases/latest",
            headers={'User-Agent': 'fastwand'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read())["tag_name"]
    except Exception as e:
        return "v0.1.00"  # Updated fallback version

def install_fastwand(directory: Path) -> Path:
    """Download and install fastwand CLI"""
    system, machine = get_system_info()
    version = get_fastwand_version()
    
    filename = f"fastwand-{system}-{machine}"
    if system == "windows":
        filename += ".exe"
    
    url = f"https://github.com/banditburai/fastwandCLI/releases/download/{version}/{filename}"
    
    final_path = directory / filename
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'fastwand'})
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(final_path, 'wb') as f:
                f.write(response.read())
    except Exception as e:
        print(f"Error downloading fastwand CLI: {e}")
        if final_path.exists():
            final_path.unlink()
        raise
    
    # Make executable on Unix systems
    if system != "windows":
        os.chmod(final_path, 0o755)
    
    return final_path

def ensure_fastwand_installed() -> Path:
    """Ensure fastwand CLI is installed and return path"""
    cache_dir = Path(user_cache_dir("fastwand"))
    cache_dir.mkdir(exist_ok=True)
    
    cli_path = cache_dir / "fastwand"
    if not cli_path.exists():
        cli_path = install_fastwand(cache_dir)
    
    return cli_path

def main():
    """Main CLI entrypoint"""
    cli = ensure_fastwand_installed()
    
    # Forward all arguments to the Go CLI
    try:
        subprocess.run([str(cli)] + sys.argv[1:], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()