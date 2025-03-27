"""Identity resource module."""
from dataclasses import dataclass


@dataclass
class MorphogenIdentity:
    """Morphogen identity information."""
    name: str = "morphogen"
    role: str = "Open-source Solutions Integrator"
    mission: str = "Help businesses build their digital infrastructure by installing and configuring open-source systems."
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


async def get_identity() -> str:
    """Get Morphogen identity information."""
    identity = MorphogenIdentity()
    return identity.to_string() 