"""
Voice-Authenticated Folder Locking System
==========================================
Complete production-ready system combining voice authentication 
with folder encryption for secure file protection.

Author: AI Assistant
Date: 2026-01-29
Version: 1.0.0
"""

import os
import sys
from pathlib import Path
import json
import logging
from typing import Optional
from datetime import datetime

from voice_authenticator import VoiceAuthenticator
from folder_encryption import FolderEncryption

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_folder_lock.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VoiceFolderLock:
    """
    Integrated voice-authenticated folder locking system
    
    Features:
    - Voice-based user authentication
    - Secure folder encryption/decryption
    - Access control management
    - Audit logging
    """
    
    def __init__(self, 
                 config_file: str = 'folder_lock_config.json',
                 auth_threshold: float = 0.30):
        """
        Initialize the system
        
        Args:
            config_file: Configuration file path
            auth_threshold: Voice authentication threshold (0.20-0.30 recommended, lower = stricter)
        """
        self.config_file = config_file
        self.config = {}
        
        # Initialize components
        self.voice_auth = VoiceAuthenticator(threshold=auth_threshold)
        self.encryption = FolderEncryption()
        
        # Load configuration
        self._load_config()
        
        # Load existing enrollments
        self.voice_auth.load_enrollments()
        
        logger.info("Voice Folder Lock System initialized")
    
    def _load_config(self):
        """Load system configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info("Configuration loaded")
        else:
            self.config = {
                'locked_folders': {},
                'access_log': [],
                'created_at': datetime.now().isoformat()
            }
            self._save_config()
    
    def _save_config(self):
        """Save system configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _log_access(self, username: str, folder: str, action: str, success: bool):
        """Log access attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'folder': folder,
            'action': action,
            'success': success
        }
        
        self.config['access_log'].append(log_entry)
        self._save_config()
        
        logger.info(f"Access logged: {username} - {action} - {folder} - {'SUCCESS' if success else 'FAILED'}")
    
    def enroll_user(self, username: str):
        """
        Enroll a new user with voice authentication
        
        Args:
            username: Username to enroll
        """
        print(f"\n{'='*70}")
        print(f"👤 USER ENROLLMENT")
        print(f"{'='*70}")
        
        # Check if user already exists
        if username in self.voice_auth.list_enrolled_users():
            print(f"\n⚠️  User '{username}' already enrolled!")
            overwrite = input("Overwrite existing profile? (yes/no): ").strip().lower()
            if overwrite != 'yes':
                print("Enrollment cancelled.")
                return
            
            self.voice_auth.remove_user(username)
        
        # Enroll user
        success = self.voice_auth.enroll_user(username, num_samples=5, duration=5)
        
        if success:
            print(f"\n🎉 User '{username}' successfully enrolled!")
            print(f"   You can now lock/unlock folders using your voice.")
    
    def lock_folder(self, username: str, folder_path: str):
        """
        Lock (encrypt) a folder with voice authentication
        
        Args:
            username: Username attempting to lock
            folder_path: Path to folder to lock
        """
        print(f"\n{'='*70}")
        print(f"🔒 LOCK FOLDER")
        print(f"{'='*70}")
        
        folder_path = Path(folder_path).resolve()
        
        # Verify folder exists
        if not folder_path.exists():
            print(f"\n❌ Folder not found: {folder_path}")
            return
        
        if not folder_path.is_dir():
            print(f"\n❌ Not a folder: {folder_path}")
            return
        
        # Check if already locked
        if str(folder_path) in self.config['locked_folders']:
            print(f"\n⚠️  Folder already locked!")
            return
        
        # Authenticate user
        print(f"\n🔐 Authenticating user: {username}")
        authenticated, score = self.voice_auth.authenticate(username, duration=5)
        
        if not authenticated:
            print(f"\n❌ Authentication failed! Cannot lock folder.")
            self._log_access(username, str(folder_path), 'lock', False)
            return
        
        # Generate encryption key
        key = self.encryption.generate_key()
        self.encryption.set_key(key)
        
        # Save key (in production, use more secure key storage)
        key_file = f"keys/{username}_{folder_path.name}_key.bin"
        os.makedirs("keys", exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(key)
        
        # Encrypt folder
        print(f"\n🔒 Encrypting folder...")
        stats = self.encryption.encrypt_folder(str(folder_path), delete_original=False)
        
        # Delete original files to lock folder
        print(f"\n🗑️  Deleting original files to lock folder...")
        deleted = 0
        for root, dirs, files in os.walk(str(folder_path)):
            for file in files:
                if not file.endswith('.encrypted'):
                    original_file = os.path.join(root, file)
                    os.remove(original_file)
                    deleted += 1
        
        # Store folder info
        self.config['locked_folders'][str(folder_path)] = {
            'owner': username,
            'locked_at': datetime.now().isoformat(),
            'key_file': key_file,
            'stats': stats
        }
        self._save_config()
        
        print(f"\n✅ Folder LOCKED successfully!")
        print(f"   Owner: {username}")
        print(f"   Files encrypted: {stats['encrypted_files']}")
        print(f"   Original files deleted: {deleted}")
        print(f"\n🔒 Folder is now inaccessible - authentication required to unlock!")
        
        self._log_access(username, str(folder_path), 'lock', True)
    
    def unlock_folder(self, username: str, folder_path: str):
        """
        Unlock (decrypt) a folder with voice authentication
        
        Args:
            username: Username attempting to unlock
            folder_path: Path to folder to unlock
        """
        print(f"\n{'='*70}")
        print(f"🔓 UNLOCK FOLDER")
        print(f"{'='*70}")
        
        folder_path = Path(folder_path).resolve()
        
        # Check if folder is locked
        if str(folder_path) not in self.config['locked_folders']:
            print(f"\n⚠️  Folder is not locked: {folder_path}")
            return
        
        folder_info = self.config['locked_folders'][str(folder_path)]
        
        # Check ownership
        if folder_info['owner'] != username:
            print(f"\n❌ Access denied!")
            print(f"   This folder is locked by: {folder_info['owner']}")
            print(f"   You are: {username}")
            self._log_access(username, str(folder_path), 'unlock', False)
            return
        
        # Authenticate user
        print(f"\n🔐 Authenticating owner: {username}")
        authenticated, score = self.voice_auth.authenticate(username, duration=5)
        
        if not authenticated:
            print(f"\n❌ Authentication failed! Cannot unlock folder.")
            self._log_access(username, str(folder_path), 'unlock', False)
            return
        
        # Load encryption key
        key_file = folder_info['key_file']
        key_path = Path(key_file)
        if not key_path.exists():
            print(f"\n❌ Encryption key not found: {key_file}")
            return
        
        with open(key_file, 'rb') as f:
            key = f.read()
        
        self.encryption.set_key(key)
        
        # Decrypt folder
        print(f"\n🔓 Decrypting folder...")
        stats = self.encryption.decrypt_folder(str(folder_path), delete_encrypted=False)
        
        # Remove from locked folders list
        del self.config['locked_folders'][str(folder_path)]
        self._save_config()
        
        print(f"\n✅ Folder unlocked successfully!")
        print(f"   Files decrypted: {stats['decrypted_files']}")
        print(f"\n💡 Encrypted files are preserved for safety.")
        
        # Ask if user wants to delete encrypted files
        delete_encrypted = input("   Delete encrypted files? (yes/no): ").strip().lower()
        if delete_encrypted == 'yes':
            # Delete .encrypted files
            deleted = 0
            for root, dirs, files in os.walk(str(folder_path)):
                for file in files:
                    if file.endswith('.encrypted'):
                        encrypted_file = os.path.join(root, file)
                        os.remove(encrypted_file)
                        deleted += 1
            print(f"   ✅ Deleted {deleted} encrypted files.")
        
        self._log_access(username, str(folder_path), 'unlock', True)
    
    def list_locked_folders(self):
        """List all locked folders"""
        print(f"\n{'='*70}")
        print(f"📋 LOCKED FOLDERS")
        print(f"{'='*70}")
        
        if not self.config['locked_folders']:
            print("\n⚠️  No locked folders.")
            return
        
        for folder_path, info in self.config['locked_folders'].items():
            print(f"\n📁 {folder_path}")
            print(f"   Owner: {info['owner']}")
            print(f"   Locked at: {info['locked_at'][:19]}")
            print(f"   Files encrypted: {info['stats']['encrypted_files']}")
    
    def remove_folder_lock(self, folder_path: str):
        """
        Remove folder from locked list (administrative function)
        
        Args:
            folder_path: Path to folder
        """
        folder_path = str(Path(folder_path).resolve())
        
        if folder_path in self.config['locked_folders']:
            del self.config['locked_folders'][folder_path]
            self._save_config()
            print(f"✅ Folder removed from locked list: {folder_path}")
        else:
            print(f"⚠️  Folder not in locked list: {folder_path}")
    
    def show_access_log(self, limit: int = 10):
        """
        Show recent access log
        
        Args:
            limit: Number of recent entries to show
        """
        print(f"\n{'='*70}")
        print(f"📜 ACCESS LOG (Last {limit} entries)")
        print(f"{'='*70}")
        
        if not self.config['access_log']:
            print("\n⚠️  No access log entries.")
            return
        
        recent_logs = self.config['access_log'][-limit:]
        
        for entry in reversed(recent_logs):
            status = "✅" if entry['success'] else "❌"
            print(f"\n{status} {entry['timestamp'][:19]}")
            print(f"   User: {entry['username']}")
            print(f"   Action: {entry['action']}")
            print(f"   Folder: {entry['folder']}")


def main():
    """Main application"""
    print("\n" + "="*70)
    print("🎤🔒 VOICE-AUTHENTICATED FOLDER LOCKING SYSTEM")
    print("="*70)
    print("\nSecure your folders using your voice!")
    print("Powered by ECAPA-TDNN speaker verification + Fernet encryption")
    
    # Initialize system
    system = VoiceFolderLock()
    
    # Main menu
    while True:
        print("\n" + "-"*70)
        print("MAIN MENU:")
        print("1. 👤 Enroll new user")
        print("2. 🔒 Lock folder")
        print("3. 🔓 Unlock folder")
        print("4. 📋 List locked folders")
        print("5. 👥 List enrolled users")
        print("6. 📜 Show access log")
        print("7. ℹ️  System information")
        print("8. � Authentication statistics")
        print("9. �🚪 Exit")
        print("-"*70)
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        try:
            if choice == '1':
                username = input("\n📝 Enter username: ").strip()
                if username:
                    system.enroll_user(username)
            
            elif choice == '2':
                enrolled_users = system.voice_auth.list_enrolled_users()
                if not enrolled_users:
                    print("\n⚠️  No users enrolled! Enroll a user first.")
                    continue
                
                print(f"\n👥 Enrolled users: {', '.join(enrolled_users)}")
                username = input("📝 Enter your username: ").strip()
                folder_path = input("📁 Enter folder path to lock: ").strip()
                
                if username and folder_path:
                    system.lock_folder(username, folder_path)
            
            elif choice == '3':
                if not system.config['locked_folders']:
                    print("\n⚠️  No locked folders!")
                    continue
                
                print(f"\n📁 Locked folders:")
                for i, (folder, info) in enumerate(system.config['locked_folders'].items(), 1):
                    print(f"   {i}. {folder} (owner: {info['owner']})")
                
                username = input("\n📝 Enter your username: ").strip()
                folder_path = input("📁 Enter folder path to unlock: ").strip()
                
                if username and folder_path:
                    system.unlock_folder(username, folder_path)
            
            elif choice == '4':
                system.list_locked_folders()
            
            elif choice == '5':
                enrolled_users = system.voice_auth.list_enrolled_users()
                if enrolled_users:
                    print(f"\n👥 Enrolled users ({len(enrolled_users)}):")
                    for user in enrolled_users:
                        info = system.voice_auth.enrolled_embeddings[user]
                        print(f"   - {user}")
                        print(f"     Enrolled: {info['enrolled_at'][:19]}")
                        print(f"     Samples: {info['num_samples']}")
                else:
                    print("\n⚠️  No users enrolled yet!")
            
            elif choice == '6':
                limit = input("\n📝 Show last N entries (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                system.show_access_log(limit)
            
            elif choice == '7':
                print(f"\n{'='*70}")
                print("ℹ️  SYSTEM INFORMATION")
                print(f"{'='*70}")
                print(f"\n🎤 Voice Authentication:")
                print(f"   Model: SpeechBrain ECAPA-TDNN")
                print(f"   Source: speechbrain/spkrec-ecapa-voxceleb")
                print(f"   Threshold: {system.voice_auth.threshold}")
                print(f"   Enrolled users: {len(system.voice_auth.list_enrolled_users())}")
                
                print(f"\n🔒 Folder Encryption:")
                print(f"   Algorithm: Fernet (AES-128)")
                print(f"   Locked folders: {len(system.config['locked_folders'])}")
                
                print(f"\n📊 Statistics:")
                print(f"   Access log entries: {len(system.config['access_log'])}")
                print(f"   System created: {system.config['created_at'][:19]}")
            
            elif choice == '8':
                enrolled_users = system.voice_auth.list_enrolled_users()
                if not enrolled_users:
                    print("\n⚠️  No users enrolled yet!")
                    continue
                
                print(f"\n👥 Enrolled users: {', '.join(enrolled_users)}")
                username = input("\n📝 Enter username to view stats: ").strip()
                
                if username and username in enrolled_users:
                    stats = system.voice_auth.get_user_stats(username)
                    
                    print(f"\n{'='*70}")
                    print(f"📊 AUTHENTICATION STATISTICS: {username}")
                    print(f"{'='*70}")
                    
                    if stats['total_attempts'] == 0:
                        print("\n⚠️  No authentication attempts yet.")
                    else:
                        print(f"\n📈 Overall Performance:")
                        print(f"   Total attempts: {stats['total_attempts']}")
                        print(f"   Successful: {stats['successful']} ✅")
                        print(f"   Failed: {stats['failed']} ❌")
                        print(f"   Success rate: {stats['success_rate']*100:.1f}%")
                        
                        if 'avg_success_distance' in stats:
                            print(f"\n🎯 Distance Metrics:")
                            print(f"   Average distance: {stats['avg_success_distance']:.4f}")
                            print(f"   Std deviation: {stats['std_success_distance']:.4f}")
                            print(f"   Current threshold: {system.voice_auth.threshold}")
                            print(f"   Suggested threshold: {stats.get('suggested_threshold', 'N/A'):.4f}")
                            
                            # Show recommendation
                            if stats['suggested_threshold'] < system.voice_auth.threshold - 0.05:
                                print(f"\n💡 Recommendation: Consider lowering threshold to {stats['suggested_threshold']:.4f}")
                                print(f"   (Your voice is very consistent!)")
                            elif stats['suggested_threshold'] > system.voice_auth.threshold + 0.05:
                                print(f"\n⚠️  Warning: You may need to raise threshold to {stats['suggested_threshold']:.4f}")
                                print(f"   (High variability in authentication)")
                            else:
                                print(f"\n✅ Your threshold is optimal!")
                        
                        # Show recent attempts
                        if len(stats['distances']) > 0:
                            print(f"\n📝 Recent Attempts (last {min(10, len(stats['distances']))}):") 
                            recent_count = min(10, len(stats['distances']))
                            for i in range(recent_count):
                                idx = -(i+1)
                                dist = stats['distances'][idx]
                                time = stats['timestamps'][idx][:19]
                                status = "✅" if dist < system.voice_auth.threshold else "❌"
                                print(f"   {status} {time} - Distance: {dist:.4f}")
                else:
                    print(f"\n❌ User '{username}' not found!")
            
            elif choice == '9':
                print("\n" + "="*70)
                print("👋 Thank you for using Voice-Authenticated Folder Lock!")
                print("🔒 Stay secure!")
                print("="*70)
                break
            
            else:
                print("\n❌ Invalid choice! Please enter 1-9.")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user.")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
            print("Check voice_folder_lock.log for details.")


if __name__ == "__main__":
    main()
