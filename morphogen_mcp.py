"""
Morphogen MCP Server
-------------------
MCP server for Morphogen providing system compatibility and infrastructure tools.
"""

import logging
import platform
from dataclasses import dataclass
from typing import Optional
import asyncio
import tempfile
import os
import httpx


from mcp.server.fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("morphogen")

# Create MCP server
mcp = FastMCP(
    "morphogen",
    dependencies=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0"
    ]
)

# === Identity Resource ===
@dataclass
class MorphogenIdentity:
    """Morphogen identity information."""
    name: str = "morphogen"
    role: str = "Open-source Solutions Integrator"
    mission: str = "Help businesses build their digital infrastructure"
    version: str = "1.0.0"

    def to_string(self) -> str:
        """Convert identity to formatted string."""
        return (
            f"== Identity ==\n"
            f"Name: {self.name}\n"
            f"Role: {self.role}\n"
            f"Mission: {self.mission}\n"
            f"Version: {self.version}"
        )

@mcp.resource("identity://morphogen")
async def get_identity() -> str:
    """Return Morphogen's identity details."""
    identity = MorphogenIdentity()
    return identity.to_string()

# === System Tools ===
@mcp.tool()
async def check_compatibility(
    component: str,
    system: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """Check if a component is compatible with a given system."""
    # Get system info
    raw_system = platform.system()
    release = platform.release()
    version = platform.version()
    
    # Normalize system name
    if not system:
        system = "MacOS" if raw_system == "Darwin" else raw_system
    
    # Compatibility matrix
    compatibility = {
        "docker": ["Ubuntu", "Debian", "Rocky", "CentOS", "MacOS", "Windows"],
        "teleport": ["Linux", "MacOS", "Windows"],
        "netbox": ["Ubuntu", "Debian", "Rocky"],
    }
    
    if ctx:
        ctx.info(f"Checking compatibility for {component} on {system}")
    
    supported = compatibility.get(component.lower(), [])
    status = "compatible" if system in supported else "unknown or unverified"
    
    response = [
        f"{component} is {status} with {system}.",
        "",
        "System detected:",
        f"- OS: {system}",
        f"- Release: {release}",
        f"- Version: {version}"
    ]
    
    if system == "MacOS" and release.startswith("10."):
        response.append("\n⚠️ Note: Some modern tools may not support MacOS 10.x or older versions.")
        
    return "\n".join(response)

@mcp.tool()
def recommend_os_stack(purpose: str) -> str:
    """Recommend a stack based on business purpose."""
    recommendations = {
        "web server": "Recommended stack: Ubuntu Server + Nginx + Certbot + Docker",
        "data warehouse": "Recommended stack: Debian + PostgreSQL + Apache Superset",
        "network monitoring": "Recommended stack: Rocky Linux + NetBox + Prometheus + Grafana",
        "devops": "Recommended stack: Ubuntu + Jenkins + GitLab + Ansible",
    }
    return recommendations.get(purpose.lower(), "No stack recommendation available for that purpose.")

if __name__ == "__main__":
    logger.info("Starting Morphogen MCP server...")
    mcp.run()

@mcp.tool()
def validate_script(script_text: str, ctx: Optional[Context] = None) -> str:
    """Basic validation of script content."""
    blacklist = ["rm -rf /", "shutdown", "reboot", ":(){ :|:& };:", "mkfs", "dd if="]

    for bad in blacklist:
        if bad in script_text:
            return f"❌ Detected unsafe command: `{bad}`\nAborting installation."

    if ctx:
        ctx.info("Script validated successfully.")
    return "✅ Script passed basic validation."

@mcp.tool()
def detect_os_info(ctx: Optional[Context] = None) -> dict:
    system = platform.system()
    release = platform.release()
    version = platform.version()

    # Normalize OS name
    os_name = "MacOS" if system == "Darwin" else system

    if ctx:
        ctx.info(f"Detected OS: {os_name}, Release: {release}, Version: {version}")

    return {
        "os": os_name,
        "release": release,
        "version": version
    }

@mcp.tool()
async def run_install_script(script_text: str, ctx: Optional[Context] = None) -> str:
    """
    Run a given shell install script (as received from Claude or another LLM).
    """

    if ctx:
        ctx.info("Writing install script to temporary file...")

    try:
        # Create temporary bash script
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".sh") as tmp_script:
            tmp_script.write(script_text)
            tmp_path = tmp_script.name

        os.chmod(tmp_path, 0o755)

        if ctx:
            ctx.info(f"Executing install script: {tmp_path}")

        # Execute bash script
        proc = await asyncio.create_subprocess_exec(
            "bash", tmp_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        output = stdout.decode().strip()
        error = stderr.decode().strip()

        # Clean up
        os.remove(tmp_path)

        if proc.returncode == 0:
            return f"✅ Installation succeeded:\n\n{output}"
        else:
            return f"❌ Installation failed (exit code {proc.returncode}):\n\n{error}"

    except Exception as e:
        return f"❌ Error during installation: {str(e)}"
    
@mcp.tool()
def summarize_result(output: str) -> str:
    """Summarize the installation output."""
    if "error" in output.lower():
        return "⚠️ Some errors were detected during installation."
    if "success" in output.lower() or "started" in output.lower():
        return "✅ The service appears to be installed and running."
    return "ℹ️ Installation output reviewed. Manual verification may be needed."

@mcp.tool()
async def install_from_llm_script(script_text: str, ctx: Optional[Context] = None) -> str:
    """
    Toolchain: Validate and run a shell install script from LLM (e.g. Claude).
    """
    # Step 1: Validate
    validation = validate_script(script_text, ctx)
    if "❌" in validation:
        return validation

    # Step 2: Run
    result = await run_install_script(script_text, ctx)

    # Step 3: Summarize
    summary = summarize_result(result)

    return "\n".join([
        "=== Installation Result ===",
        result,
        "",
        "=== Summary ===",
        summary
    ])

def build_claude_prompt(component: str, os_info: dict) -> str:
    return f"""
Please generate a safe and minimal bash installation script for the following:

Component: {component}
OS: {os_info['os']} {os_info['release']} ({os_info['version']})

Requirements:
- Use native package managers if possible (e.g., apt for Ubuntu)
- Avoid interactive prompts (use -y flags)
- No dangerous commands like rm -rf or reboot
- Only installation and basic configuration

Return only the bash script.
"""
@mcp.tool()
async def install_component_with_os_detection(
    component: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Detect OS, ask LLM for install script, validate & run it.
    """

    # Step 1: Detect OS
    os_info = detect_os_info(ctx)

    # Step 2: Ask LLM (여기선 프롬프트만 생성, 실제 호출은 프런트/Obsidian에서)
    prompt = build_claude_prompt(component, os_info)

    return "\n".join([
        "=== Claude Prompt for Installation ===",
        prompt,
        "",
        "⚠️ Please copy this prompt to Claude and paste the bash script output here for execution."
    ])