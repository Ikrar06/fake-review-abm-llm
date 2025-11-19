"""
Fake Review Simulation Package

This package contains modules for simulating fake review campaigns
and their impact on consumer purchase decisions using LLM agents.
"""

from src.config import *
from src.database import init_database, get_session
from src.llm_client import LLMClient
from src.agents import ReviewerAgent, ShopperAgent
from src.products import ProductManager
from src.engine import SimulationEngine

__version__ = "1.0.0"
__author__ = "Ikrar"
