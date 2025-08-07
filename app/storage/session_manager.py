"""Session Storage Manager - Handles persistent session storage"""

import json
import os
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages session persistence and retrieval"""
    
    def __init__(self, storage_path: str = "./sessions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        # Create users directory for profile storage
        self.users_path = self.storage_path / "users"
        self.users_path.mkdir(parents=True, exist_ok=True)
        self.sessions_index = self._load_index()
        self.users_index = self._load_users_index()
        
    def _load_index(self) -> Dict:
        """Load sessions index from file"""
        index_file = self.storage_path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                return {}
        return {}
    
    def _save_index(self):
        """Save sessions index to file"""
        index_file = self.storage_path / "index.json"
        try:
            with open(index_file, 'w') as f:
                json.dump(self.sessions_index, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def save_session(self, session_id: str, session_data: Dict) -> bool:
        """Save session data to disk"""
        try:
            session_file = self.storage_path / f"{session_id}.json"
            
            # Ensure datetime objects are serialized
            serializable_data = self._make_serializable(session_data)
            
            with open(session_file, 'w') as f:
                json.dump(serializable_data, f, indent=2, default=str)
            
            # Update index with user info
            user_profile = session_data.get('user_profile', {})
            self.sessions_index[session_id] = {
                "created_at": session_data.get("started_at", datetime.now()).isoformat(),
                "last_updated": datetime.now().isoformat(),
                "phase": session_data.get("phase", "initial"),
                "ready_for_generation": session_data.get("ready_for_generation", False),
                "user_name": user_profile.get('name', ''),
                "business_name": user_profile.get('business_name', ''),
                "onboarding_complete": session_data.get('onboarding_complete', False)
            }
            self._save_index()
            
            # Save user profile separately if complete
            if session_data.get('onboarding_complete') and user_profile.get('email'):
                self.save_user_profile(user_profile)
            
            logger.info(f"Session {session_id} saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load session data from disk"""
        try:
            session_file = self.storage_path / f"{session_id}.json"
            
            if not session_file.exists():
                logger.warning(f"Session {session_id} not found")
                return None
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Convert date strings back to datetime objects if needed
            if "started_at" in session_data and isinstance(session_data["started_at"], str):
                session_data["started_at"] = datetime.fromisoformat(session_data["started_at"])
            
            logger.info(f"Session {session_id} loaded successfully")
            return session_data
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session from storage"""
        try:
            session_file = self.storage_path / f"{session_id}.json"
            
            if session_file.exists():
                session_file.unlink()
            
            if session_id in self.sessions_index:
                del self.sessions_index[session_id]
                self._save_index()
            
            logger.info(f"Session {session_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions"""
        sessions = []
        for session_id, info in self.sessions_index.items():
            sessions.append({
                "id": session_id,
                "created_at": info["created_at"],
                "last_updated": info["last_updated"],
                "phase": info["phase"],
                "ready_for_generation": info.get("ready_for_generation", False)
            })
        return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)
    
    def cleanup_old_sessions(self, days: int = 30):
        """Remove sessions older than specified days"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions_to_delete = []
        
        for session_id, info in self.sessions_index.items():
            last_updated = datetime.fromisoformat(info["last_updated"])
            if last_updated < cutoff_date:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            self.delete_session(session_id)
        
        logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions")
    
    def _make_serializable(self, obj):
        """Convert non-serializable objects to serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj
    
    def export_session(self, session_id: str, export_path: str) -> bool:
        """Export a session to a specified path"""
        try:
            session_data = self.load_session(session_id)
            if not session_data:
                return False
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            logger.info(f"Session {session_id} exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting session {session_id}: {e}")
            return False
    
    def import_session(self, import_path: str, session_id: Optional[str] = None) -> Optional[str]:
        """Import a session from a file"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                logger.error(f"Import file {import_path} not found")
                return None
            
            with open(import_file, 'r') as f:
                session_data = json.load(f)
            
            # Generate new session ID if not provided
            if not session_id:
                import uuid
                session_id = str(uuid.uuid4())
            
            session_data["id"] = session_id
            
            if self.save_session(session_id, session_data):
                logger.info(f"Session imported as {session_id}")
                return session_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error importing session from {import_path}: {e}")
            return None
    
    def _load_users_index(self) -> Dict:
        """Load users index from file"""
        users_index_file = self.users_path / "index.json"
        if users_index_file.exists():
            try:
                with open(users_index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading users index: {e}")
                return {}
        return {}
    
    def _save_users_index(self):
        """Save users index to file"""
        users_index_file = self.users_path / "index.json"
        try:
            with open(users_index_file, 'w') as f:
                json.dump(self.users_index, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving users index: {e}")
    
    def save_user_profile(self, profile: Dict) -> bool:
        """Save user profile to disk"""
        try:
            email = profile.get('email', '').lower()
            if not email:
                logger.warning("Cannot save user profile without email")
                return False
            
            # Use email as filename (sanitized)
            safe_email = email.replace('@', '_at_').replace('.', '_')
            profile_file = self.users_path / f"{safe_email}.json"
            
            # Add metadata
            profile_data = {
                **profile,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            # Save profile
            serializable_data = self._make_serializable(profile_data)
            with open(profile_file, 'w') as f:
                json.dump(serializable_data, f, indent=2, default=str)
            
            # Update users index
            self.users_index[email] = {
                "name": profile.get('name', ''),
                "business_name": profile.get('business_name', ''),
                "business_type": profile.get('business_type', ''),
                "created_at": profile_data["created_at"],
                "last_updated": profile_data["last_updated"],
                "file": f"{safe_email}.json"
            }
            self._save_users_index()
            
            logger.info(f"User profile saved for {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return False
    
    def load_user_profile_by_email(self, email: str) -> Optional[Dict]:
        """Load user profile by email"""
        try:
            email = email.lower()
            if email not in self.users_index:
                return None
            
            profile_info = self.users_index[email]
            profile_file = self.users_path / profile_info["file"]
            
            if not profile_file.exists():
                logger.warning(f"Profile file not found for {email}")
                return None
            
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
            
            logger.info(f"User profile loaded for {email}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error loading user profile for {email}: {e}")
            return None
    
    def find_user_by_name(self, name: str) -> Optional[Dict]:
        """Find user profile by name (case insensitive)"""
        name_lower = name.lower()
        for email, profile_info in self.users_index.items():
            if profile_info.get('name', '').lower() == name_lower:
                return self.load_user_profile_by_email(email)
        return None
    
    def list_users(self) -> List[Dict]:
        """List all user profiles"""
        users = []
        for email, info in self.users_index.items():
            users.append({
                "email": email,
                "name": info.get("name", ""),
                "business_name": info.get("business_name", ""),
                "business_type": info.get("business_type", ""),
                "created_at": info.get("created_at", ""),
                "last_updated": info.get("last_updated", "")
            })
        return sorted(users, key=lambda x: x["last_updated"], reverse=True)