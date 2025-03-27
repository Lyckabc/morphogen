from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
import logging

from mcp.server.fastmcp import FastMCP

# Set up logging
logger = logging.getLogger("morphogen")

@dataclass
class MorphogenContext:
    """Application context for Morphogen MCP server."""
    config: dict[str, Any]
    debug: bool = False


@asynccontextmanager
async def morphogen_lifespan(server: FastMCP) -> AsyncIterator[MorphogenContext]:
    """Manage Morphogen MCP server lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        MorphogenContext: Application context with initialized resources
    """
    # Initialize resources
    config = {
        "version": "1.0.0",
        "environment": "development",
    }
    
    ctx = MorphogenContext(config=config)
    
    try:
        logger.info("Initializing Morphogen MCP server...")
        yield ctx
    finally:
        logger.info("Shutting down Morphogen MCP server...") 