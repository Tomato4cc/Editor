A savedata editor for PES18.

Keyboard shortcuts:

 - Main Window:
	- CTRL+S, Save
	- CTRL+Shift+S, Save As
	- Enter with a player selected, open editor window for that player
  - Player Window:
	- Esc, Close
	- CTRL+Enter, Accept/Save
	
Building:
  - .exe releases are built with pyinstaller. The standard build command for
    a release is `pyinstaller -F -w -i icon.ico editor.py`. Only the .py, 
	the .ico and the **ui** folder are required for building.