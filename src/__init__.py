"""
Fake Review Simulation Package (MESA-based)

This package contains modules for simulating fake review campaigns
and their impact on consumer purchase decisions using agent-based modeling
with MESA framework and LLM-powered agents.

Module Structure:
- config: Configuration constants and parameters
- llm_client: LLM client for review and decision generation
- prompts: Prompt templates for different agent personas
- agents: MESA agents (ReviewerAgent, ShopperAgent)
- model: Main MESA simulation model (FakeReviewModel)
"""

# Configuration
from src.config import (
    MODEL_NAME,
    LLM_TIMEOUT,
    KEEP_ALIVE,
    TOTAL_ITERATIONS,
    BURST_ITERATIONS,
    BURST_VOLUME,
    FAKE_CAMPAIGN_TARGETS,
    MAINTENANCE_VOLUME,
    GENUINE_REVIEWS_PER_PRODUCT,
    SHOPPERS_PER_PRODUCT_PER_PERSONA,
    REVIEWS_READ
)

# LLM and Prompts
from src.llm_client import LLMClient
from src.prompts import (
    GENUINE_REVIEWER_SYSTEM,
    FAKE_REVIEWER_SYSTEM,
    SHOPPER_SYSTEM_BASE,
    ReviewerPersonality,
    ShopperPersona,
    get_genuine_reviewer_prompt,
    get_fake_reviewer_prompt,
    get_shopper_prompt
)

# Agents
from src.agents import ReviewerAgent, ShopperAgent

# MESA Model
from src.model import FakeReviewModel, Product

# Version info
__version__ = "2.0.0"  # Updated for MESA migration
__author__ = "Ikrar"
__framework__ = "MESA"

# Public API
__all__ = [
    # Configuration
    "MODEL_NAME",
    "LLM_TIMEOUT",
    "KEEP_ALIVE",
    "TOTAL_ITERATIONS",
    "BURST_ITERATIONS",
    "BURST_VOLUME",
    "FAKE_CAMPAIGN_TARGETS",
    "MAINTENANCE_VOLUME",
    "GENUINE_REVIEWS_PER_PRODUCT",
    "SHOPPERS_PER_PRODUCT_PER_PERSONA",
    "REVIEWS_READ",
    
    # LLM and Prompts
    "LLMClient",
    "GENUINE_REVIEWER_SYSTEM",
    "FAKE_REVIEWER_SYSTEM",
    "SHOPPER_SYSTEM_BASE",
    "ReviewerPersonality",
    "ShopperPersona",
    "get_genuine_reviewer_prompt",
    "get_fake_reviewer_prompt",
    "get_shopper_prompt",
    
    # Agents
    "ReviewerAgent",
    "ShopperAgent",
    
    # Model
    "FakeReviewModel",
    "Product",
]


def get_version():
    """Get package version"""
    return __version__


def get_info():
    """Get package information"""
    return {
        "name": "Fake Review ABM Simulation",
        "version": __version__,
        "author": __author__,
        "framework": __framework__,
        "description": "Agent-based modeling of fake review campaigns using MESA and LLM"
    }