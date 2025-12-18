"""
Agent scraping history tracker
Prevents duplicate agents across multiple scraping sessions
"""

import json
import os
from pathlib import Path
from typing import Set, List
from datetime import datetime


class ScrapingHistory:
    """
    Tracks scraped agent IDs across sessions to prevent duplicates

    Stores agent IDs in a hidden JSON file in the user's home directory
    """

    def __init__(self, history_file: str = None):
        """
        Initialize history tracker

        Args:
            history_file: Optional custom path to history file
                         Defaults to ~/.agentharvest_history.json
        """
        if history_file:
            self.history_file = Path(history_file)
        else:
            # Store in home directory as hidden file
            self.history_file = Path.home() / ".agentharvest_history.json"

        self.agent_ids: Set[str] = set()
        self.load()

    def load(self):
        """Load scraped agent IDs from history file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.agent_ids = set(data.get('agent_ids', []))
                    print(f"📋 Loaded {len(self.agent_ids)} previously scraped agent IDs")
            except Exception as e:
                print(f"⚠️  Could not load history file: {e}")
                self.agent_ids = set()
        else:
            print("📋 No previous scraping history found (first run)")

    def save(self):
        """Save scraped agent IDs to history file"""
        try:
            data = {
                'agent_ids': list(self.agent_ids),
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.agent_ids)
            }
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Saved {len(self.agent_ids)} agent IDs to history")
        except Exception as e:
            print(f"⚠️  Could not save history file: {e}")

    def add(self, agent_id: str):
        """Add a single agent ID to history"""
        self.agent_ids.add(agent_id)

    def add_many(self, agent_ids: List[str]):
        """Add multiple agent IDs to history"""
        before_count = len(self.agent_ids)
        self.agent_ids.update(agent_ids)
        new_count = len(self.agent_ids) - before_count
        if new_count > 0:
            print(f"➕ Added {new_count} new agent IDs to history")

    def contains(self, agent_id: str) -> bool:
        """Check if agent ID was already scraped"""
        return agent_id in self.agent_ids

    def filter_new(self, agents: List) -> List:
        """
        Filter out agents that were already scraped

        Args:
            agents: List of Agent objects

        Returns:
            List of Agent objects that haven't been scraped before
        """
        new_agents = [agent for agent in agents if agent.agent_id not in self.agent_ids]
        duplicates = len(agents) - len(new_agents)

        if duplicates > 0:
            print(f"🔍 Filtered out {duplicates} previously scraped agents")

        return new_agents

    def clear(self):
        """Clear all history (use with caution!)"""
        self.agent_ids.clear()
        if self.history_file.exists():
            self.history_file.unlink()
        print("🗑️  Cleared all scraping history")

    def get_count(self) -> int:
        """Get total number of scraped agents"""
        return len(self.agent_ids)

    def get_history_file(self) -> str:
        """Get path to history file"""
        return str(self.history_file)
