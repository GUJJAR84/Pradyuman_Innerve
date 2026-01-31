"""
Voice-Authenticated Folder Lock - Professional GUI Application
Modern, user-friendly interface following HCI principles
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
from datetime import datetime
import json

from voice_authenticator import VoiceAuthenticator
from folder_encryption import FolderEncryption
from credential_manager import CredentialManager
from browser_automation import BrowserAutomation

# Configure theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VoiceLockGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Voice-Authenticated Folder Lock")
        self.root.geometry("1000x700")
        
        # Initialize backend
        self.voice_auth = None
        self.encryption = FolderEncryption()
        self.cred_manager = CredentialManager()
        self.current_user = None
        self.config_file = 'folder_lock_config.json'
        self.config = self._load_config()
        
        # Show login screen
        self.show_login_screen()
        
    def _load_config(self):
        """Load system configuration"""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            'locked_folders': {},
            'access_log': [],
            'created_at': datetime.now().isoformat()
        }
    
    def _save_config(self):
        """Save system configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ==================== LOGIN SCREEN ====================
    
    def show_login_screen(self):
        """Display login/registration screen"""
        self.clear_window()
        
        # Main container
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(pady=(20, 40))
        
        title = ctk.CTkLabel(
            header_frame,
            text="🎤 Voice Lock",
            font=("Segoe UI", 42, "bold")
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Secure your files with your voice",
            font=("Segoe UI", 16),
            text_color="gray"
        )
        subtitle.pack(pady=(5, 0))
        
        # Login card
        login_card = ctk.CTkFrame(container, corner_radius=15)
        login_card.pack(pady=20, padx=100, fill="both", expand=True)
        
        # Card title
        card_title = ctk.CTkLabel(
            login_card,
            text="Welcome Back",
            font=("Segoe UI", 28, "bold")
        )
        card_title.pack(pady=(40, 10))
        
        card_subtitle = ctk.CTkLabel(
            login_card,
            text="Select or create a user profile",
            font=("Segoe UI", 14),
            text_color="gray"
        )
        card_subtitle.pack(pady=(0, 30))
        
        # Initialize voice auth to get enrolled users
        if self.voice_auth is None:
            self.voice_auth = VoiceAuthenticator()
            self.voice_auth.load_enrollments()
        
        enrolled_users = self.voice_auth.list_enrolled_users()
        
        # User selection
        if enrolled_users:
            user_label = ctk.CTkLabel(
                login_card,
                text="Select User:",
                font=("Segoe UI", 14)
            )
            user_label.pack(pady=(0, 10))
            
            self.selected_user = ctk.StringVar(value=enrolled_users[0])
            user_dropdown = ctk.CTkOptionMenu(
                login_card,
                variable=self.selected_user,
                values=enrolled_users,
                width=300,
                height=40,
                font=("Segoe UI", 14)
            )
            user_dropdown.pack(pady=(0, 20))
            
            # Login button
            login_btn = ctk.CTkButton(
                login_card,
                text="🔐 Login with Voice",
                command=self.handle_login,
                width=300,
                height=50,
                font=("Segoe UI", 16, "bold"),
                fg_color="#2563eb",
                hover_color="#1e40af"
            )
            login_btn.pack(pady=10)
        
        # Register button
        register_btn = ctk.CTkButton(
            login_card,
            text="➕ Register New User",
            command=self.show_registration_screen,
            width=300,
            height=50,
            font=("Segoe UI", 16),
            fg_color="#059669",
            hover_color="#047857"
        )
        register_btn.pack(pady=10)
        
        # Footer
        footer = ctk.CTkLabel(
            container,
            text="Powered by ECAPA-TDNN AI • AES-128 Encryption",
            font=("Segoe UI", 11),
            text_color="gray"
        )
        footer.pack(pady=(20, 10))
    
    def handle_login(self):
        """Authenticate user with voice"""
        username = self.selected_user.get()
        
        # Show loading dialog with countdown
        loading_window = ctk.CTkToplevel(self.root)
        loading_window.title("Authenticating")
        loading_window.geometry("450x380")
        loading_window.transient(self.root)
        loading_window.grab_set()
        
        loading_label = ctk.CTkLabel(
            loading_window,
            text=f"🎤 Authenticating {username}",
            font=("Segoe UI", 18, "bold")
        )
        loading_label.pack(pady=(30, 10))
        
        countdown_label = ctk.CTkLabel(
            loading_window,
            text="",
            font=("Segoe UI", 48, "bold"),
            text_color="#2563eb"
        )
        countdown_label.pack(pady=15)
        
        status_label = ctk.CTkLabel(
            loading_window,
            text="Get ready to speak...",
            font=("Segoe UI", 14)
        )
        status_label.pack(pady=10)
        
        timer_label = ctk.CTkLabel(
            loading_window,
            text="",
            font=("Segoe UI", 16, "bold"),
            text_color="#059669"
        )
        timer_label.pack(pady=5)
        
        progress = ctk.CTkProgressBar(loading_window, width=350)
        progress.pack(pady=20)
        progress.set(0)
        
        def authenticate():
            import time
            import sounddevice as sd
            
            try:
                # Countdown 3, 2, 1
                for count in [3, 2, 1]:
                    loading_window.after(0, lambda c=count: countdown_label.configure(text=str(c)))
                    loading_window.after(0, lambda: status_label.configure(text="Recording will start in..."))
                    time.sleep(1)
                
                # Recording
                duration = 5
                loading_window.after(0, lambda: countdown_label.configure(text="🔴"))
                loading_window.after(0, lambda: status_label.configure(text="🔴 RECORDING NOW! Please speak..."))
                
                # Start recording with timer updates
                start_time = time.time()
                audio_data = sd.rec(
                    int(duration * self.voice_auth.sample_rate),
                    samplerate=self.voice_auth.sample_rate,
                    channels=1,
                    dtype='float32'
                )
                
                # Update timer during recording
                while time.time() - start_time < duration:
                    elapsed = time.time() - start_time
                    remaining = duration - elapsed
                    progress_val = elapsed / duration
                    loading_window.after(0, lambda p=progress_val: progress.set(p))
                    loading_window.after(0, lambda r=remaining: timer_label.configure(text=f"⏱️ {r:.1f}s remaining"))
                    time.sleep(0.1)
                
                sd.wait()
                audio_data = audio_data.squeeze()
                
                # Processing
                loading_window.after(0, lambda: countdown_label.configure(text=""))
                loading_window.after(0, lambda: status_label.configure(text="Processing..."))
                loading_window.after(0, lambda: timer_label.configure(text=""))
                loading_window.after(0, lambda: progress.set(1.0))
                
                # Preprocess and extract embedding
                audio_data = self.voice_auth.preprocess_audio(audio_data)
                
                if username not in self.voice_auth.enrolled_embeddings:
                    raise ValueError(f"User {username} not enrolled")
                
                stored_embedding = self.voice_auth.enrolled_embeddings[username]['embedding']
                test_embedding = self.voice_auth.extract_embedding(audio_data)
                distance = self.voice_auth.compute_similarity(test_embedding, stored_embedding)
                authenticated = distance < self.voice_auth.threshold
                
                # Update history
                self.voice_auth._update_auth_history(username, distance, authenticated)
                
                loading_window.after(0, loading_window.destroy)
                
                if authenticated:
                    self.current_user = username
                    self.root.after(0, self.show_main_dashboard)
                    messagebox.showinfo(
                        "Success",
                        f"✅ Welcome back, {username}!\n\nSimilarity: {(1-distance)*100:.1f}%"
                    )
                else:
                    messagebox.showerror(
                        "Authentication Failed",
                        f"❌ Voice authentication failed!\n\nDistance: {distance:.4f}\nThreshold: {self.voice_auth.threshold}\n\nPlease try again."
                    )
            except Exception as e:
                loading_window.after(0, loading_window.destroy)
                messagebox.showerror("Error", f"Authentication error: {str(e)}")
        
        # Run authentication in thread
        thread = threading.Thread(target=authenticate, daemon=True)
        thread.start()
    
    # ==================== REGISTRATION SCREEN ====================
    
    def show_registration_screen(self):
        """Display user registration screen"""
        self.clear_window()
        
        # Main container
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(pady=(20, 30))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Register New User",
            font=("Segoe UI", 32, "bold")
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Enroll your voice for authentication",
            font=("Segoe UI", 14),
            text_color="gray"
        )
        subtitle.pack(pady=(5, 0))
        
        # Registration card
        reg_card = ctk.CTkFrame(container, corner_radius=15)
        reg_card.pack(pady=20, padx=80, fill="both", expand=True)
        
        # Username input
        username_label = ctk.CTkLabel(
            reg_card,
            text="Username:",
            font=("Segoe UI", 14)
        )
        username_label.pack(pady=(40, 5))
        
        self.username_entry = ctk.CTkEntry(
            reg_card,
            width=350,
            height=40,
            font=("Segoe UI", 14),
            placeholder_text="Enter your name"
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Instructions
        instructions = ctk.CTkTextbox(
            reg_card,
            width=500,
            height=120,
            font=("Segoe UI", 12)
        )
        instructions.pack(pady=20)
        instructions.insert("1.0", 
            "📋 Registration Instructions:\n\n"
            "1. You'll record 5 voice samples (5 seconds each)\n"
            "2. Speak your passphrase clearly (e.g., 'My voice is my password')\n"
            "3. Use the same phrase for all 5 samples\n"
            "4. Maintain consistent volume and speaking style"
        )
        instructions.configure(state="disabled")
        
        # Register button
        register_btn = ctk.CTkButton(
            reg_card,
            text="🎤 Start Voice Enrollment",
            command=self.handle_registration,
            width=300,
            height=50,
            font=("Segoe UI", 16, "bold"),
            fg_color="#059669",
            hover_color="#047857"
        )
        register_btn.pack(pady=20)
        
        # Back button
        back_btn = ctk.CTkButton(
            reg_card,
            text="← Back to Login",
            command=self.show_login_screen,
            width=200,
            height=40,
            font=("Segoe UI", 14),
            fg_color="transparent",
            border_width=2
        )
        back_btn.pack(pady=(10, 30))
    
    def handle_registration(self):
        """Handle user voice enrollment"""
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        # Create enrollment window
        enroll_window = ctk.CTkToplevel(self.root)
        enroll_window.title("Voice Enrollment")
        enroll_window.geometry("500x450")
        enroll_window.transient(self.root)
        enroll_window.grab_set()
        
        title = ctk.CTkLabel(
            enroll_window,
            text=f"Enrolling: {username}",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(30, 10))
        
        sample_label = ctk.CTkLabel(
            enroll_window,
            text="Preparing...",
            font=("Segoe UI", 18, "bold")
        )
        sample_label.pack(pady=10)
        
        countdown_label = ctk.CTkLabel(
            enroll_window,
            text="",
            font=("Segoe UI", 48, "bold"),
            text_color="#2563eb"
        )
        countdown_label.pack(pady=20)
        
        instruction = ctk.CTkLabel(
            enroll_window,
            text="Get ready to speak...",
            font=("Segoe UI", 14),
            text_color="gray"
        )
        instruction.pack(pady=10)
        
        progress = ctk.CTkProgressBar(enroll_window, width=400)
        progress.pack(pady=20)
        progress.set(0)
        
        status = ctk.CTkLabel(
            enroll_window,
            text="",
            font=("Segoe UI", 12),
            text_color="#059669"
        )
        status.pack(pady=10)
        
        def enroll():
            import time
            import sounddevice as sd
            import numpy as np
            from pathlib import Path
            
            try:
                num_samples = 5
                duration = 5
                embeddings = []
                
                for i in range(num_samples):
                    # Update sample label
                    enroll_window.after(0, lambda i=i: sample_label.configure(
                        text=f"Sample {i+1} of {num_samples}"
                    ))
                    enroll_window.after(0, lambda: instruction.configure(
                        text="Recording will start in..."
                    ))
                    enroll_window.after(0, lambda: progress.set((i) / num_samples))
                    
                    # Countdown 3, 2, 1
                    for count in [3, 2, 1]:
                        enroll_window.after(0, lambda c=count: countdown_label.configure(
                            text=str(c)
                        ))
                        time.sleep(1)
                    
                    # Recording
                    enroll_window.after(0, lambda: countdown_label.configure(text="🔴"))
                    enroll_window.after(0, lambda: instruction.configure(
                        text="🔴 RECORDING NOW! Please speak..."
                    ))
                    
                    # Record audio
                    audio_data = sd.rec(
                        int(duration * self.voice_auth.sample_rate),
                        samplerate=self.voice_auth.sample_rate,
                        channels=1,
                        dtype='float32'
                    )
                    sd.wait()
                    audio_data = audio_data.squeeze()
                    
                    # Preprocess
                    audio_data = self.voice_auth.preprocess_audio(audio_data)
                    
                    # Extract embedding
                    enroll_window.after(0, lambda: instruction.configure(
                        text="Processing recording..."
                    ))
                    embedding = self.voice_auth.extract_embedding(audio_data)
                    embeddings.append(embedding)
                    
                    # Save sample
                    user_dir = Path("voice_profiles") / username
                    user_dir.mkdir(parents=True, exist_ok=True)
                    
                    import soundfile as sf
                    sf.write(user_dir / f"sample_{i+1}.wav", audio_data, self.voice_auth.sample_rate)
                    
                    # Update status
                    enroll_window.after(0, lambda i=i: status.configure(
                        text=f"✅ Sample {i+1} recorded successfully!"
                    ))
                    enroll_window.after(0, lambda: countdown_label.configure(text=""))
                    
                    time.sleep(0.5)
                
                # Average embeddings
                enroll_window.after(0, lambda: instruction.configure(
                    text="Creating voice profile..."
                ))
                enroll_window.after(0, lambda: progress.set(1.0))
                
                avg_embedding = np.mean(embeddings, axis=0)
                
                # Calculate consistency
                distances = []
                for emb in embeddings:
                    dist = self.voice_auth.compute_similarity(emb, avg_embedding)
                    distances.append(dist)
                mean_dist = np.mean(distances)
                
                # Store enrollment
                from datetime import datetime
                self.voice_auth.enrolled_embeddings[username] = {
                    'embedding': avg_embedding,
                    'num_samples': num_samples,
                    'enrolled_at': datetime.now().isoformat(),
                    'mean_distance': float(mean_dist)
                }
                
                # Save to disk
                self.voice_auth._save_enrollments()
                
                enroll_window.after(0, enroll_window.destroy)
                
                messagebox.showinfo(
                    "Success",
                    f"✅ User '{username}' enrolled successfully!\\n\\n"
                    f"Samples recorded: {num_samples}\\n"
                    f"Consistency score: {(1-mean_dist)*100:.1f}%\\n\\n"
                    f"You can now use your voice to lock/unlock folders."
                )
                self.show_login_screen()
                
            except Exception as e:
                enroll_window.after(0, enroll_window.destroy)
                messagebox.showerror("Error", f"Enrollment error: {str(e)}")
        
        # Run enrollment in thread
        thread = threading.Thread(target=enroll, daemon=True)
        thread.start()
    
    # ==================== MAIN DASHBOARD ====================
    
    def show_main_dashboard(self):
        """Display main application dashboard"""
        self.clear_window()
        
        # Top bar
        topbar = ctk.CTkFrame(self.root, height=70, corner_radius=0)
        topbar.pack(fill="x", padx=0, pady=0)
        
        # Logo and title
        title_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        
        app_title = ctk.CTkLabel(
            title_frame,
            text="🎤 Voice Lock",
            font=("Segoe UI", 24, "bold")
        )
        app_title.pack(side="left")
        
        # User info
        user_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        user_frame.pack(side="right", padx=20, pady=15)
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.current_user}",
            font=("Segoe UI", 14)
        )
        user_label.pack(side="left", padx=10)
        
        logout_btn = ctk.CTkButton(
            user_frame,
            text="Logout",
            command=self.handle_logout,
            width=100,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#dc2626",
            hover_color="#b91c1c"
        )
        logout_btn.pack(side="left")
        
        # Main content area
        content = ctk.CTkFrame(self.root)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left sidebar - Actions
        sidebar = ctk.CTkFrame(content, width=250)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)
        
        sidebar_title = ctk.CTkLabel(
            sidebar,
            text="Actions",
            font=("Segoe UI", 18, "bold")
        )
        sidebar_title.pack(pady=(20, 30))
        
        # Action buttons
        lock_btn = ctk.CTkButton(
            sidebar,
            text="🔒 Lock Folder",
            command=self.show_lock_dialog,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#2563eb",
            hover_color="#1e40af"
        )
        lock_btn.pack(pady=10, padx=20, fill="x")
        
        unlock_btn = ctk.CTkButton(
            sidebar,
            text="🔓 Unlock Folder",
            command=self.show_unlock_dialog,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#059669",
            hover_color="#047857"
        )
        unlock_btn.pack(pady=10, padx=20, fill="x")
        
        stats_btn = ctk.CTkButton(
            sidebar,
            text="📊 My Statistics",
            command=self.show_statistics,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#7c3aed",
            hover_color="#6d28d9"
        )
        stats_btn.pack(pady=10, padx=20, fill="x")
        
        # Separator
        separator = ctk.CTkLabel(
            sidebar,
            text="───────────",
            font=("Segoe UI", 10),
            text_color="gray"
        )
        separator.pack(pady=15)
        
        # Social Media Accounts Section
        social_title = ctk.CTkLabel(
            sidebar,
            text="🌐 Social Media Accounts",
            font=("Segoe UI", 14, "bold")
        )
        social_title.pack(pady=(10, 5), padx=20, anchor="w")
        
        # List saved platforms
        try:
            platforms = self.cred_manager.list_credentials(self.current_user)
            
            if platforms:
                for platform in platforms:
                    login_btn = ctk.CTkButton(
                        sidebar,
                        text=f"🚀 Login to {platform}",
                        command=lambda p=platform: self.voice_login_platform(p),
                        height=40,
                        font=("Segoe UI", 12),
                        fg_color="#059669",
                        hover_color="#047857"
                    )
                    login_btn.pack(pady=5, padx=20, fill="x")
        except Exception as e:
            pass  # Silently handle errors - button will still show below
        
        # Add account button (always show this)
        add_account_btn = ctk.CTkButton(
            sidebar,
            text="➕ Add Account",
            command=self.show_add_credential_dialog,
            height=40,
            font=("Segoe UI", 12),
            fg_color="#0891b2",
            hover_color="#0e7490"
        )
        add_account_btn.pack(pady=10, padx=20, fill="x")
        
        # Danger Zone Separator
        danger_sep = ctk.CTkLabel(sidebar, text="───────────", font=("Segoe UI", 10), text_color="gray")
        danger_sep.pack(pady=(20, 10))
        
        # Delete Profile Button
        delete_profile_btn = ctk.CTkButton(
            sidebar,
            text="⚠️ Delete Profile",
            command=self.handle_delete_profile,
            height=35,
            font=("Segoe UI", 12),
            fg_color="transparent",
            text_color="#ef4444",
            hover_color="#fee2e2",
            border_width=1,
            border_color="#ef4444"
        )
        delete_profile_btn.pack(pady=5, padx=20, fill="x")
        
        # Right panel - Locked folders list
        right_panel = ctk.CTkFrame(content)
        right_panel.pack(side="right", fill="both", expand=True)
        
        panel_title = ctk.CTkLabel(
            right_panel,
            text="🔒 Locked Folders",
            font=("Segoe UI", 22, "bold")
        )
        panel_title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Scrollable frame for folders
        self.folders_frame = ctk.CTkScrollableFrame(right_panel, height=500)
        self.folders_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        self.refresh_folders_list()
    
    def refresh_folders_list(self):
        """Refresh the locked folders list"""
        # Safety check - only refresh if folders_frame exists
        if not hasattr(self, 'folders_frame') or self.folders_frame is None:
            return
        
        # Clear existing widgets
        for widget in self.folders_frame.winfo_children():
            widget.destroy()
        
        user_folders = {k: v for k, v in self.config['locked_folders'].items() 
                        if v['owner'] == self.current_user}
        
        if not user_folders:
            no_folders = ctk.CTkLabel(
                self.folders_frame,
                text="No locked folders yet.\nClick 'Lock Folder' to get started!",
                font=("Segoe UI", 14),
                text_color="gray"
            )
            no_folders.pack(pady=50)
        else:
            for folder_path, info in user_folders.items():
                self.create_folder_card(folder_path, info)
    
    def create_folder_card(self, folder_path, info):
        """Create a card for a locked folder"""
        card = ctk.CTkFrame(self.folders_frame, corner_radius=10)
        card.pack(fill="x", pady=10, padx=5)
        
        # Folder icon and name
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        folder_name = Path(folder_path).name
        name_label = ctk.CTkLabel(
            header,
            text=f"📁 {folder_name}",
            font=("Segoe UI", 16, "bold")
        )
        name_label.pack(side="left")
        
        # Folder info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=5)
        
        path_label = ctk.CTkLabel(
            info_frame,
            text=f"Path: {folder_path}",
            font=("Segoe UI", 11),
            text_color="gray"
        )
        path_label.pack(anchor="w")
        
        locked_time = info.get('locked_at', '')[:19]
        time_label = ctk.CTkLabel(
            info_frame,
            text=f"Locked: {locked_time}",
            font=("Segoe UI", 11),
            text_color="gray"
        )
        time_label.pack(anchor="w")
        
        files_label = ctk.CTkLabel(
            info_frame,
            text=f"Files: {info.get('stats', {}).get('encrypted_files', 'N/A')}",
            font=("Segoe UI", 11),
            text_color="gray"
        )
        files_label.pack(anchor="w")
        
        # Unlock button
        unlock_btn = ctk.CTkButton(
            card,
            text="🔓 Unlock",
            command=lambda fp=folder_path: self.unlock_folder(fp),
            width=120,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#059669",
            hover_color="#047857"
        )
        unlock_btn.pack(pady=(10, 15), padx=15, side="right")
    
    def show_lock_dialog(self):
        """Show dialog to lock a folder"""
        folder_path = filedialog.askdirectory(
            title="Select Folder to Lock"
        )
        
        if folder_path:
            self.lock_folder(folder_path)
    
    def lock_folder(self, folder_path):
        """Lock a folder with voice authentication"""
        # Check if already locked
        if str(Path(folder_path).resolve()) in self.config['locked_folders']:
            messagebox.showwarning("Already Locked", "This folder is already locked!")
            return
        
        # Show authentication dialog with countdown
        auth_window = ctk.CTkToplevel(self.root)
        auth_window.title("Authenticating to Lock")
        auth_window.geometry("450x380")
        auth_window.transient(self.root)
        auth_window.grab_set()
        
        title = ctk.CTkLabel(
            auth_window,
            text="🔐 Authenticate to Lock Folder",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=(30, 10))
        
        countdown_label = ctk.CTkLabel(
            auth_window,
            text="",
            font=("Segoe UI", 48, "bold"),
            text_color="#2563eb"
        )
        countdown_label.pack(pady=15)
        
        instruction = ctk.CTkLabel(
            auth_window,
            text="Get ready to speak...",
            font=("Segoe UI", 14)
        )
        instruction.pack(pady=10)
        
        timer_label = ctk.CTkLabel(
            auth_window,
            text="",
            font=("Segoe UI", 16, "bold"),
            text_color="#059669"
        )
        timer_label.pack(pady=5)
        
        progress = ctk.CTkProgressBar(auth_window, width=350)
        progress.pack(pady=20)
        progress.set(0)
        
        def authenticate_and_lock():
            import time, sounddevice as sd
            
            try:
                # Countdown
                for count in [3, 2, 1]:
                    auth_window.after(0, lambda c=count: countdown_label.configure(text=str(c)))
                    auth_window.after(0, lambda: instruction.configure(text="Recording will start in..."))
                    time.sleep(1)
                
                # Recording
                duration = 5
                auth_window.after(0, lambda: countdown_label.configure(text="🔴"))
                auth_window.after(0, lambda: instruction.configure(text="🔴 RECORDING! Speak now..."))
                
                start_time = time.time()
                audio_data = sd.rec(int(duration * self.voice_auth.sample_rate),
                                   samplerate=self.voice_auth.sample_rate, channels=1, dtype='float32')
                
                while time.time() - start_time < duration:
                    elapsed = time.time() - start_time
                    remaining = duration - elapsed
                    progress_val = elapsed / duration
                    auth_window.after(0, lambda p=progress_val: progress.set(p))
                    auth_window.after(0, lambda r=remaining: timer_label.configure(text=f"⏱️ {r:.1f}s remaining"))
                    time.sleep(0.1)
                
                sd.wait()
                audio_data = audio_data.squeeze()
                
                # Processing
                auth_window.after(0, lambda: countdown_label.configure(text=""))
                auth_window.after(0, lambda: instruction.configure(text="Processing..."))
                auth_window.after(0, lambda: timer_label.configure(text=""))
                auth_window.after(0, lambda: progress.set(1.0))
                
                # Authenticate
                audio_data = self.voice_auth.preprocess_audio(audio_data)
                stored_embedding = self.voice_auth.enrolled_embeddings[self.current_user]['embedding']
                test_embedding = self.voice_auth.extract_embedding(audio_data)
                distance = self.voice_auth.compute_similarity(test_embedding, stored_embedding)
                authenticated = distance < self.voice_auth.threshold
                self.voice_auth._update_auth_history(self.current_user, distance, authenticated)
                
                auth_window.after(0, auth_window.destroy)
                
                if not authenticated:
                    messagebox.showerror("Failed", "Voice authentication failed!")
                    return
                
                # Generate key and encrypt
                key = self.encryption.generate_key()
                self.encryption.set_key(key)
                
                # Save key
                import os
                os.makedirs("keys", exist_ok=True)
                key_file = f"keys/{self.current_user}_{Path(folder_path).name}_key.bin"
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # Encrypt folder
                stats = self.encryption.encrypt_folder(str(folder_path), delete_original=False)
                
                # Delete originals
                deleted = 0
                for root, dirs, files in os.walk(str(folder_path)):
                    for file in files:
                        if not file.endswith('.encrypted'):
                            os.remove(os.path.join(root, file))
                            deleted += 1
                
                # Update config
                self.config['locked_folders'][str(Path(folder_path).resolve())] = {
                    'owner': self.current_user,
                    'locked_at': datetime.now().isoformat(),
                    'key_file': key_file,
                    'stats': stats
                }
                self._save_config()
                
                self.refresh_folders_list()
                messagebox.showinfo(
                    "Success",
                    f"✅ Folder locked successfully!\n\nFiles encrypted: {stats['encrypted_files']}\nOriginals deleted: {deleted}"
                )
            except Exception as e:
                auth_window.after(0, progress.stop)
                auth_window.after(0, auth_window.destroy)
                messagebox.showerror("Error", f"Failed to lock folder: {str(e)}")
        
        thread = threading.Thread(target=authenticate_and_lock, daemon=True)
        thread.start()
    
    def show_unlock_dialog(self):
        """Show dialog to select folder to unlock"""
        user_folders = {k: v for k, v in self.config['locked_folders'].items() 
                        if v['owner'] == self.current_user}
        
        if not user_folders:
            messagebox.showinfo("No Folders", "You don't have any locked folders.")
            return
        
        # Create selection dialog
        select_window = ctk.CTkToplevel(self.root)
        select_window.title("Select Folder to Unlock")
        select_window.geometry("600x400")
        select_window.transient(self.root)
        select_window.grab_set()
        
        title = ctk.CTkLabel(
            select_window,
            text="Select Folder to Unlock",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=20)
        
        folders_list = list(user_folders.keys())
        selected_folder = ctk.StringVar(value=folders_list[0])
        
        for folder in folders_list:
            folder_name = Path(folder).name
            radio = ctk.CTkRadioButton(
                select_window,
                text=f"📁 {folder_name}\n    {folder}",
                variable=selected_folder,
                value=folder,
                font=("Segoe UI", 12)
            )
            radio.pack(pady=10, padx=30, anchor="w")
        
        unlock_btn = ctk.CTkButton(
            select_window,
            text="🔓 Unlock Selected Folder",
            command=lambda: [select_window.destroy(), self.unlock_folder(selected_folder.get())],
            height=45,
            font=("Segoe UI", 14)
        )
        unlock_btn.pack(pady=20)
    
    def unlock_folder(self, folder_path):
        """Unlock a folder with voice authentication"""
        folder_info = self.config['locked_folders'].get(str(folder_path))
        
        if not folder_info:
            messagebox.showerror("Error", "Folder not found in locked list")
            return
        
        # Show authentication dialog with countdown
        auth_window = ctk.CTkToplevel(self.root)
        auth_window.title("Authenticating to Unlock")
        auth_window.geometry("450x380")
        auth_window.transient(self.root)
        auth_window.grab_set()
        
        title = ctk.CTkLabel(
            auth_window,
            text="🔐 Authenticate to Unlock Folder",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=(30, 10))
        
        countdown_label = ctk.CTkLabel(
            auth_window,
            text="",
            font=("Segoe UI", 48, "bold"),
            text_color="#2563eb"
        )
        countdown_label.pack(pady=15)
        
        instruction = ctk.CTkLabel(
            auth_window,
            text="Get ready to speak...",
            font=("Segoe UI", 14)
        )
        instruction.pack(pady=10)
        
        timer_label = ctk.CTkLabel(
            auth_window,
            text="",
            font=("Segoe UI", 16, "bold"),
            text_color="#059669"
        )
        timer_label.pack(pady=5)
        
        progress = ctk.CTkProgressBar(auth_window, width=350)
        progress.pack(pady=20)
        progress.set(0)
        
        def authenticate_and_unlock():
            import time, sounddevice as sd
            
            try:
                # Countdown
                for count in [3, 2, 1]:
                    auth_window.after(0, lambda c=count: countdown_label.configure(text=str(c)))
                    auth_window.after(0, lambda: instruction.configure(text="Recording will start in..."))
                    time.sleep(1)
                
                # Recording
                duration = 5
                auth_window.after(0, lambda: countdown_label.configure(text="🔴"))
                auth_window.after(0, lambda: instruction.configure(text="🔴 RECORDING! Speak now..."))
                
                start_time = time.time()
                audio_data = sd.rec(int(duration * self.voice_auth.sample_rate),
                                   samplerate=self.voice_auth.sample_rate, channels=1, dtype='float32')
                
                while time.time() - start_time < duration:
                    elapsed = time.time() - start_time
                    remaining = duration - elapsed
                    progress_val = elapsed / duration
                    auth_window.after(0, lambda p=progress_val: progress.set(p))
                    auth_window.after(0, lambda r=remaining: timer_label.configure(text=f"⏱️ {r:.1f}s remaining"))
                    time.sleep(0.1)
                
                sd.wait()
                audio_data = audio_data.squeeze()
                
                # Processing
                auth_window.after(0, lambda: countdown_label.configure(text=""))
                auth_window.after(0, lambda: instruction.configure(text="Processing..."))
                auth_window.after(0, lambda: timer_label.configure(text=""))
                auth_window.after(0, lambda: progress.set(1.0))
                
                # Authenticate  
                audio_data = self.voice_auth.preprocess_audio(audio_data)
                stored_embedding = self.voice_auth.enrolled_embeddings[self.current_user]['embedding']
                test_embedding = self.voice_auth.extract_embedding(audio_data)
                distance = self.voice_auth.compute_similarity(test_embedding, stored_embedding)
                authenticated = distance < self.voice_auth.threshold
                self.voice_auth._update_auth_history(self.current_user, distance, authenticated)
                
                auth_window.after(0, auth_window.destroy)
                
                if not authenticated:
                    messagebox.showerror("Failed", "Voice authentication failed!")
                    return
                
                # Load key
                key_file = folder_info['key_file']
                with open(key_file, 'rb') as f:
                    key = f.read()
                
                self.encryption.set_key(key)
                
                # Decrypt folder
                stats = self.encryption.decrypt_folder(str(folder_path), delete_encrypted=False)
                
                # Ask to delete encrypted files
                delete = messagebox.askyesno(
                    "Delete Encrypted Files?",
                    f"Folder unlocked successfully!\n\nFiles decrypted: {stats['decrypted_files']}\n\nDelete encrypted files?"
                )
                
                if delete:
                    import os
                    deleted = 0
                    for root, dirs, files in os.walk(str(folder_path)):
                        for file in files:
                            if file.endswith('.encrypted'):
                                os.remove(os.path.join(root, file))
                                deleted += 1
                
                # Remove from config
                del self.config['locked_folders'][str(folder_path)]
                self._save_config()
                
                self.refresh_folders_list()
                messagebox.showinfo("Success", f"✅ Folder unlocked successfully!")
                
            except Exception as e:
                auth_window.after(0, progress.stop)
                auth_window.after(0, auth_window.destroy)
                messagebox.showerror("Error", f"Failed to unlock folder: {str(e)}")
        
        thread = threading.Thread(target=authenticate_and_unlock, daemon=True)
        thread.start()
    
    def show_statistics(self):
        """Show user authentication statistics"""
        stats = self.voice_auth.get_user_stats(self.current_user)
        
        # Create statistics window
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title(f"Statistics - {self.current_user}")
        stats_window.geometry("600x600")
        stats_window.transient(self.root)
        
        # Title
        title = ctk.CTkLabel(
            stats_window,
            text=f"📊 Authentication Statistics",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(30, 20))
        
        subtitle = ctk.CTkLabel(
            stats_window,
            text=self.current_user,
            font=("Segoe UI", 18),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 30))
        
        if stats['total_attempts'] == 0:
            no_data = ctk.CTkLabel(
                stats_window,
                text="No authentication attempts yet.",
                font=("Segoe UI", 14),
                text_color="gray"
            )
            no_data.pack(pady=50)
        else:
            # Stats cards
            stats_frame = ctk.CTkFrame(stats_window)
            stats_frame.pack(fill="both", expand=True, padx=30, pady=20)
            
            # Overall performance
            perf_card = ctk.CTkFrame(stats_frame, corner_radius=10)
            perf_card.pack(fill="x", pady=10, padx=10)
            
            perf_title = ctk.CTkLabel(
                perf_card,
                text="📈 Overall Performance",
                font=("Segoe UI", 16, "bold")
            )
            perf_title.pack(pady=(15, 10), padx=15, anchor="w")
            
            perf_text = ctk.CTkTextbox(perf_card, height=100, font=("Segoe UI", 12))
            perf_text.pack(fill="x", padx=15, pady=(0, 15))
            perf_text.insert("1.0", 
                f"Total attempts: {stats['total_attempts']}\n"
                f"Successful: {stats['successful']} ✅\n"
                f"Failed: {stats['failed']} ❌\n"
                f"Success rate: {stats['success_rate']*100:.1f}%"
            )
            perf_text.configure(state="disabled")
            
            # Distance metrics (if available)
            if 'avg_success_distance' in stats:
                dist_card = ctk.CTkFrame(stats_frame, corner_radius=10)
                dist_card.pack(fill="x", pady=10, padx=10)
                
                dist_title = ctk.CTkLabel(
                    dist_card,
                    text="🎯 Distance Metrics",
                    font=("Segoe UI", 16, "bold")
                )
                dist_title.pack(pady=(15, 10), padx=15, anchor="w")
                
                dist_text = ctk.CTkTextbox(dist_card, height=120, font=("Segoe UI", 12))
                dist_text.pack(fill="x", padx=15, pady=(0, 15))
                dist_text.insert("1.0",
                    f"Average distance: {stats['avg_success_distance']:.4f}\n"
                    f"Std deviation: {stats['std_success_distance']:.4f}\n"
                    f"Current threshold: {self.voice_auth.threshold}\n"
                    f"Suggested threshold: {stats.get('suggested_threshold', 'N/A'):.4f}"
                )
                dist_text.configure(state="disabled")
        
        close_btn = ctk.CTkButton(
            stats_window,
            text="Close",
            command=stats_window.destroy,
            width=150,
            height=40,
            font=("Segoe UI", 14)
        )
        close_btn.pack(pady=20)
    
    def show_add_credential_dialog(self):
        """Show dialog to add social media credentials"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Social Media Account")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text="🌐 Add New Account", font=("Segoe UI", 20, "bold"))
        title.pack(pady=20)
        
        platform_label = ctk.CTkLabel(dialog, text="Platform:", font=("Segoe UI", 13))
        platform_label.pack(pady=(10, 5))
        platform_var = ctk.StringVar(value="Gmail")
        platform_menu = ctk.CTkOptionMenu(dialog, variable=platform_var, values=["Gmail", "Instagram", "Twitter", "GitHub"], width=300, font=("Segoe UI", 12))
        platform_menu.pack(pady=5)
        
        username_label = ctk.CTkLabel(dialog, text="Username / Email:", font=("Segoe UI", 13))
        username_label.pack(pady=(15, 5))
        username_entry = ctk.CTkEntry(dialog, width=300, font=("Segoe UI", 12), placeholder_text="Enter username or email")
        username_entry.pack(pady=5)
        
        password_label = ctk.CTkLabel(dialog, text="Password:", font=("Segoe UI", 13))
        password_label.pack(pady=(15, 5))
        password_entry = ctk.CTkEntry(dialog, width=300, font=("Segoe UI", 12), placeholder_text="Enter password", show="•")
        password_entry.pack(pady=5)
        
        def save_credential():
            platform = platform_var.get()
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "Please fill in all fields!")
                return
            success = self.cred_manager.add_credential(platform, username, password, self.current_user)
            if success:
                dialog.destroy()
                messagebox.showinfo("Success", f"✅ {platform} account saved securely!\\n\\nYou can now login using your voice.")
                self.show_main_dashboard()
            else:
                messagebox.showerror("Error", f"Failed to save {platform} account")
        
        save_btn = ctk.CTkButton(dialog, text="💾 Save Account", command=save_credential, height=45, font=("Segoe UI", 14, "bold"), fg_color="#059669", hover_color="#047857")
        save_btn.pack(pady=30)
    
    def voice_login_platform(self, platform):
        """Voice-authenticated login to social media platform"""
        auth_window = ctk.CTkToplevel(self.root)
        auth_window.title(f"Login to {platform}")
        auth_window.geometry("400x350")
        auth_window.transient(self.root)
        auth_window.grab_set()
        
        title = ctk.CTkLabel(auth_window, text=f"🎤 Voice Authentication", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(30, 10))
        instruction = ctk.CTkLabel(auth_window, text=f"Authenticate to login to {platform}", font=("Segoe UI", 14))
        instruction.pack(pady=10)
        countdown_label = ctk.CTkLabel(auth_window, text="Get ready to speak...", font=("Segoe UI", 16))
        countdown_label.pack(pady=20)
        progress = ctk.CTkProgressBar(auth_window, mode="determinate")
        progress.pack(pady=20, padx=40, fill="x")
        progress.set(0)
        
        def authenticate_and_login():
            for i in range(3, 0, -1):
                auth_window.after(0, lambda count=i: countdown_label.configure(text=f"🎯 {count}"))
                import time
                time.sleep(1)
            auth_window.after(0, lambda: countdown_label.configure(text="🔴 RECORDING! Speak now..."))
            audio = self.voice_auth.record_audio(duration=5, show_countdown=False)
            auth_window.after(0, lambda: countdown_label.configure(text="🔄 Verifying..."))
            embedding = self.voice_auth.extract_embedding(audio)
            distance = self.voice_auth.compute_similarity(embedding, self.voice_auth.enrolled_embeddings[self.current_user]['embedding'])
            auth_window.after(0, auth_window.destroy)
            if distance > 0.3:
                messagebox.showerror("Authentication Failed", f"❌ Voice authentication failed!\\n\\nDistance: {distance:.4f}")
                return
            try:
                credentials = self.cred_manager.get_credential(platform, self.current_user)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to retrieve credentials: {str(e)}")
                return
            browser = BrowserAutomation()
            try:
                if platform == "GitHub":
                    success = browser.login_github(credentials['username'], credentials['password'])
                elif platform == "Instagram":
                    success = browser.login_instagram(credentials['username'], credentials['password'])
                elif platform == "Gmail":
                    success = browser.login_gmail(credentials['username'], credentials['password'])
                elif platform == "Twitter":
                    success = browser.login_twitter(credentials['username'], credentials['password'])
                else:
                    success = False
                credentials = None
                if success:
                    messagebox.showinfo("Success", f"✅ Logged into {platform}!\\n\\nBrowser window will stay open.")
                    browser.keep_alive()
                else:
                    messagebox.showerror("Login Failed", f"❌ Failed to login to {platform}\\n\\nPlease check your credentials.")
                    browser.close()
            except Exception as e:
                messagebox.showerror("Error", f"Browser automation error: {str(e)}")
                browser.close()
        
        thread = threading.Thread(target=authenticate_and_login, daemon=True)
        thread.start()
    
    def handle_delete_profile(self):
        """Delete current user profile after voice authentication"""
        if not messagebox.askyesno("Delete Profile", "⚠️ DANGER: This will PERMANENTLY delete your voice profile and all saved credentials!\n\nThis action cannot be undone.\n\nAre you sure you want to proceed?"):
            return
            
        # Voice authentication window
        auth_window = ctk.CTkToplevel(self.root)
        auth_window.title("Confirm Deletion")
        auth_window.geometry("400x350")
        auth_window.transient(self.root)
        auth_window.grab_set()
        
        title = ctk.CTkLabel(auth_window, text="⚠️ Confirm Identity", font=("Segoe UI", 18, "bold"), text_color="#ef4444")
        title.pack(pady=(30, 10))
        
        instruction = ctk.CTkLabel(auth_window, text=f"Authenticate to DELETE profile for '{self.current_user}'", font=("Segoe UI", 14), wraplength=350)
        instruction.pack(pady=10)
        
        countdown_label = ctk.CTkLabel(auth_window, text="Get ready to speak...", font=("Segoe UI", 16))
        countdown_label.pack(pady=20)
        
        progress = ctk.CTkProgressBar(auth_window, mode="determinate", progress_color="#ef4444")
        progress.pack(pady=20, padx=40, fill="x")
        progress.set(0)
        
        def authenticate_and_delete():
            # Countdown
            for i in range(3, 0, -1):
                auth_window.after(0, lambda count=i: countdown_label.configure(text=f"🎯 {count}"))
                import time
                time.sleep(1)
            
            # Record
            auth_window.after(0, lambda: countdown_label.configure(text="🔴 RECORDING! Speak now..."))
            audio = self.voice_auth.record_audio(duration=5, show_countdown=False)
            
            # Verify
            auth_window.after(0, lambda: countdown_label.configure(text="🔄 Verifying..."))
            embedding = self.voice_auth.extract_embedding(audio)
            
            # Get enrolled embedding
            enrolled_embedding = self.voice_auth.enrolled_embeddings[self.current_user]['embedding']
            distance = self.voice_auth.compute_similarity(embedding, enrolled_embedding)
            
            # Check result
            auth_window.after(0, auth_window.destroy)
            
            if distance > 0.3:
                messagebox.showerror("Authentication Failed", f"❌ Voice mismatch! Profile deletion cancelled.\n\nDistance: {distance:.4f}")
                return
            
            # Proceed with deletion if authenticated
            if messagebox.askyesno("Final Confirmation", "✅ Identity Verified.\n\nType DELETE to confirm (wait, actually just click Yes).\n\nAre you ABSOLUTELY sure?"):
                try:
                    user_to_delete = self.current_user
                    
                    # 1. Delete all credentials
                    cred_count = self.cred_manager.delete_all_credentials_for_user(user_to_delete)
                    
                    # 2. Delete voice profile
                    self.voice_auth.remove_user(user_to_delete)
                    
                    messagebox.showinfo("Profile Deleted", f"🗑️ Profile for '{user_to_delete}' has been permanently deleted.\n- {cred_count} credentials removed\n- Voice profile removed")
                    
                    # 3. Force logout
                    self.current_user = None
                    self.show_login_screen()
                    
                except Exception as e:
                    messagebox.showerror("Deletion Error", f"An error occurred while deleting profile: {e}")
        
        thread = threading.Thread(target=authenticate_and_delete, daemon=True)
        thread.start()

    def handle_logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.show_login_screen()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = VoiceLockGUI()
    app.run()
