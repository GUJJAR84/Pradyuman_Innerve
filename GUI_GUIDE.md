# 🎨 Voice Lock GUI - Setup Instructions

## 📦 Installation

### Step 1: Install CustomTkinter

```powershell
# Make sure your virtual environment is activated
.venv\Scripts\activate

# Install CustomTkinter
pip install customtkinter

# Or install all dependencies
pip install -r requirements.txt
```

### Step 2: Run the GUI Application

```powershell
python gui_app.py
```

---

## ✨ Features

### **Login/Registration Screen**
- 🎨 Modern, professional design
- 👤 Select existing user or register new
- 🎤 Voice-based authentication
- 🔐 Secure enrollment process

### **Main Dashboard**
- 📊 Clean, intuitive interface
- 🔒 Lock folders with one click
- 🔓 Unlock folders with voice authentication
- 📋 View all your locked folders
- 📈 Real-time statistics

### **HCI Principles Applied**

1. **Consistency**
   - Uniform color scheme (dark theme)
   - Consistent button styles and sizes
   - Standard navigation patterns

2. **Feedback**
   - Loading indicators during authentication
   - Progress bars for long operations
   - Success/error messages with helpful tips

3. **Efficiency**
   - Quick access to common actions (lock/unlock)
   - Keyboard shortcuts (Enter to submit)
   - Minimal clicks to complete tasks

4. **User Control**
   - Clear logout option
   - Confirmation dialogs for destructive actions
   - Ability to cancel operations

5. **Error Prevention**
   - Validation of inputs
   - Clear instructions
   - Disabled buttons when not applicable

6. **Visual Hierarchy**
   - Important actions prominently displayed
   - Secondary actions less prominent
   - Clear section separation

---

## 🎯 Usage Guide

### **First Time Setup**

1. **Register a User**
   - Click "➕ Register New User"
   - Enter your username
   - Click "🎤 Start Voice Enrollment"
   - Speak 5 times when prompted

2. **Login**
   - Select your username from dropdown
   - Click "🔐 Login with Voice"
   - Speak to authenticate

### **Locking a Folder**

1. Click "🔒 Lock Folder" in sidebar
2. Select folder in file dialog
3. Speak to authenticate
4. Folder is encrypted and locked ✅

### **Unlocking a Folder**

1. Click "🔓 Unlock Folder" in sidebar
2. Select folder from list
3. Speak to authenticate
4. Choose whether to delete encrypted files
5. Folder is unlocked ✅

### **View Statistics**

1. Click "📊 My Statistics" in sidebar
2. View your authentication history
3. See success rates and metrics
4. Check suggested threshold

---

## 🎨 Design Features

### **Color Scheme**

- **Primary (Blue):** #2563eb - Lock actions, primary buttons
- **Success (Green):** #059669 - Unlock actions, success states
- **Purple:** #7c3aed - Statistics, analytics
- **Red:** #dc2626 - Logout, destructive actions
- **Gray:** #64748b - Secondary text, borders

### **Typography**

- **Main Font:** Segoe UI (modern, readable)
- **Title Size:** 42px (bold)
- **Heading Size:** 22-32px (bold)
- **Body Size:** 12-14px
- **Buttons:** 14-16px (bold for primary)

### **Spacing**

- **Card Padding:** 15-20px
- **Element Spacing:** 10-20px vertical
- **Page Margins:** 20px
- **Button Height:** 35-50px

---

## 🔍 Comparison: CLI vs GUI

| Feature | CLI (main.py) | GUI (gui_app.py) |
|---------|---------------|------------------|
| **Ease of Use** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Visual Appeal** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Learning Curve** | Medium | Low |
| **Accessibility** | Text-based | Visual + Text |
| **Multitasking** | Sequential | Simultaneous |
| **Best For** | Power users, scripting | General users, demos |

---

## 🚀 Next Enhancements

Future improvements to consider:

- [ ] **Drag & Drop** folder locking
- [ ] **System Tray** integration
- [ ] **Folder monitoring** (auto-lock on close)
- [ ] **Dark/Light theme** toggle
- [ ] **Custom colors** per user
- [ ] **Animations** for smoother UX
- [ ] **Charts** for statistics (matplotlib integration)
- [ ] **Export** statistics to PDF
- [ ] **Settings panel** for customization
- [ ] **Multi-language** support

---

## 💡 Tips for Best Experience

1. **Microphone Quality**
   - Use a good quality microphone
   - Reduce background noise
   - Speak at consistent volume

2. **Enrollment**
   - Use same environment for enrollment and authentication
   - Speak clearly and naturally
   - Use memorable passphrase

3. **Performance**
   - First authentication may be slower (model loading)
   - Subsequent authentications are faster
   - Close other audio applications

4. **Security**
   - Don't share your voice recordings
   - Keep encryption keys safe
   - Regular backups of voice profiles

---

## 🐛 Troubleshooting

### **GUI doesn't start**

```powershell
# Reinstall CustomTkinter
pip uninstall customtkinter
pip install customtkinter==5.2.0
```

### **Voice authentication fails**

- Check microphone permissions
- Run `test_microphone.py` to diagnose
- Re-enroll if necessary

### **Folders not showing**

- Check `folder_lock_config.json` exists
- Verify ownership matches current user
- Refresh by logging out/in

---

## 📸 Screenshots

The GUI includes:

1. **Welcome Screen** - Clean login with branding
2. **Registration Flow** - Step-by-step enrollment
3. **Main Dashboard** - Sidebar + folder list layout
4. **Folder Cards** - Information-rich, actionable
5. **Statistics View** - Comprehensive analytics
6. **Loading States** - Professional progress indicators

---

## ✅ Checklist: HCI Principles

- [x] **Visibility** - All options clearly visible
- [x] **Feedback** - Immediate response to actions
- [x] **Constraints** - Prevented invalid operations
- [x] **Consistency** - Uniform design language
- [x] **Affordance** - Buttons look clickable
- [x] **Mapping** - Logical control placement
- [x] **Recognition** - Icons + labels for clarity
- [x] **Flexibility** - Multiple ways to achieve goals
- [x] **Error Handling** - Graceful failure recovery
- [x] **Documentation** - This guide!

---

**Ready to launch! Run `python gui_app.py` to start using the professional interface.** 🚀
