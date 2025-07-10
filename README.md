<p align="center">
  <img src="docs/banner.svg" alt="TaskMaster" width="600">
</p>

<h1 align="center">TaskMaster <img alt="Checklist" src="https://img.shields.io/badge/-v1.0.0-4caf50?style=flat-square&logo=todoist&logoColor=white"></h1>

<p align="center">
  A modern, portable and delightfully simple task-management app.<br>
  <b>No Python installation, no command line—just double-click and start working.</b>
</p>

---

## ✨ Key Features
- 📁 **Folder-based organisation** – Create, rename, delete and re-order folders any time.  
- 🔀 **Organize tasks** – Move tasks between folders from a floating, scrollable menu.  
- 🔍 **Real-time filter & search** – Filter by folder, status or free-text. Results update instantly.  
- 🌐 **Multi-language** – Switch between English and Spanish with one click.  
- 📊 **Progress indicators** – Each folder shows a progress bar and a “tasks remaining” counter.  
- 📱 **Responsive UI** – Clean, modern and mobile-friendly.  
- 💾 **Truly portable** – All data lives next to the executable (`todos.db`).  
- 🗑 **Safe deletion** – Confirmation dialogs protect you from accidental data loss.  
- 📝 **Smart limits & tooltips** – Long texts are gently truncated to keep the layout tidy.  
- 🖥 **Native window** – Runs in its own window via `pywebview`, not in a browser tab.  

---

## 📸 Sneak Peek
<!-- Replace with an actual screenshot or GIF -->
<p align="center">
  <img src="docs/screenshot.png" alt="TaskMaster screenshot" width="700">
</p>

---

## 📚 Table of Contents
1. [Getting Started](#-getting-started)
2. [Project Structure](#-project-structure)
3. [Tech Stack](#-tech-stack)
4. [Requirements](#️-requirements)
5. [Uninstall](#-uninstall)
6. [License](#license)

---

## 🚀 Getting Started

1. **Download `TaskMaster.exe`**  
   No installer, no admin rights—just grab the file from the latest
   [release](https://github.com/your-repo/TaskMaster/releases) and place it anywhere you like.

2. **Run it**  
   Double-click `TaskMaster.exe`. A window appears instantly and a local SQLite
   database (`todos.db`) is created beside it.

3. **Start organising**  
   Create folders, add tasks — all changes are saved automatically.

---

## 🗂️ Project Structure
```text
TMApp/
├── app.py            # Flask backend + pywebview launcher
├── requirements.txt  # Python dependencies
├── taskmaster.ico    # Application icon
├── TaskMaster-Release/
│   └── TaskMaster.exe   # EXECUTABLE APP
├── templates/
│   └── index.html    # Front-end (HTML / CSS / JS)
└── README.md         # You're reading it!
```

## 🔧 Tech Stack
`Flask` - Backend web framework
`pywebview` - Native window for web apps
[HTML/CSS/JS] - Frontend (in `templates/index.html`)

## ℹ️ Requirements

- Windows 10/11
- No internet connection required

## 🗑️ Uninstall

- Delete the folder that contains `TaskMaster.exe` and `todos.db`. Nothing is left
behind in the registry or elsewhere.

## License
TaskMaster is released under the MIT License – see LICENSE for details.

---

**🎉Enjoy organizing your tasks with TaskMaster!🎉**
