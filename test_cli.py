#!/usr/bin/env python3
"""Quick test to verify MIOSA is working"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
print("Testing imports...")
try:
    from app.agents.base import BaseAgent
    print("✅ BaseAgent imported")
except ImportError as e:
    print(f"❌ Failed to import BaseAgent: {e}")

try:
    from app.agents.communication import CommunicationAgent
    print("✅ CommunicationAgent imported")
except ImportError as e:
    print(f"❌ Failed to import CommunicationAgent: {e}")

try:
    from app.orchestration.coordinator import ApplicationGenerationCoordinator
    print("✅ ApplicationGenerationCoordinator imported")
except ImportError as e:
    print(f"❌ Failed to import ApplicationGenerationCoordinator: {e}")

try:
    from app.services.groq_service import GroqService
    print("✅ GroqService imported")
except ImportError as e:
    print(f"❌ Failed to import GroqService: {e}")

# Test database connection
print("\nTesting database connection...")
import asyncio
import asyncpg

async def test_db():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            database='miosa',
            user='postgres'
        )
        
        # Test query
        result = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"✅ Database connected - {result} users found")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# Test coordinator
print("\nTesting coordinator initialization...")
try:
    coordinator = ApplicationGenerationCoordinator()
    print("✅ Coordinator initialized")
except Exception as e:
    print(f"❌ Failed to initialize coordinator: {e}")

# Run async tests
if __name__ == "__main__":
    print("\n" + "="*50)
    print("MIOSA System Check")
    print("="*50)
    
    # Check database
    db_ok = asyncio.run(test_db())
    
    if db_ok:
        print("\n✅ System is ready!")
        print("\nTo start the CLI, run:")
        print("  python3 -m app.cli")
    else:
        print("\n⚠️ Some components need attention")
        print("Make sure PostgreSQL is running and the database is set up")