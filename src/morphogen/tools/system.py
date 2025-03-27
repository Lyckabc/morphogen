"""System compatibility and recommendation tools."""
from typing import Optional
import platform
from dataclasses import dataclass

from mcp.server.fastmcp import Context


@dataclass
class SystemInfo:
    """System information data structure."""
    os: str
    release: str
    version: str
    
    @classmethod
    def current(cls) -> "SystemInfo":
        """Get current system information."""
        return cls(
            os=platform.system(),
            release=platform.release(),
            version=platform.version()
        )


def get_normalized_os(raw_system: str) -> str:
    """Normalize OS name for consistency.
    
    Args:
        raw_system: Raw system name from platform.system()
        
    Returns:
        Normalized OS name
    """
    if raw_system == "Darwin":
        return "MacOS"
    return raw_system


COMPATIBILITY_MATRIX = {
    "docker": ["Ubuntu", "Debian", "Rocky", "CentOS", "MacOS", "Windows"],
    "teleport": ["Linux", "MacOS", "Windows"],
    "netbox": ["Ubuntu", "Debian", "Rocky"],
}


async def check_compatibility(
    component: str,
    system: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """Check component compatibility with system.
    
    Args:
        component: Component name to check
        system: Target system (auto-detected if None)
        ctx: MCP context for logging
        
    Returns:
        Compatibility report string
    """
    sys_info = SystemInfo.current()
    target_system = system or get_normalized_os(sys_info.os)
    
    if ctx:
        ctx.info(f"Checking compatibility for {component} on {target_system}")
    
    supported = COMPATIBILITY_MATRIX.get(component.lower(), [])
    
    is_compatible = target_system in supported
    status = "compatible" if is_compatible else "unknown or unverified"
    
    response = [
        f"{component} is {status} with {target_system}.",
        "",
        "System detected:",
        f"- OS: {target_system}",
        f"- Release: {sys_info.release}",
        f"- Version: {sys_info.version}"
    ]
    
    if target_system == "MacOS" and sys_info.release.startswith("10."):
        response.append("\n⚠️ Note: Some modern tools may not support MacOS 10.x or older versions.")
        
    return "\n".join(response)


def recommend_os_stack(purpose: str) -> str:
    """Recommend a stack based on business purpose."""
    recommendations = {
        "web server": "Recommended stack: Ubuntu Server + Nginx + Certbot + Docker",
        "data warehouse": "Recommended stack: Debian + PostgreSQL + Apache Superset",
        "network monitoring": "Recommended stack: Rocky Linux + NetBox + Prometheus + Grafana",
        "devops": "Recommended stack: Ubuntu + Jenkins + GitLab + Ansible",
    }
    return recommendations.get(purpose.lower(), "No stack recommendation available for that purpose.")


def get_compatibility_matrix() -> dict[str, list[str]]:
    """Get compatibility matrix for components."""
    return {
        "docker": ["Ubuntu", "Debian", "Rocky", "CentOS", "MacOS", "Windows"],
        "teleport": ["Linux", "MacOS", "Windows"],
        "netbox": ["Ubuntu", "Debian", "Rocky"],
    } 