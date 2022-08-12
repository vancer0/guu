pyinstaller guu-win.spec
rd /s /q "build"

set VERSION=1

md bin
move dist\guu.exe bin\GUU-Win-x86_64.exe

rd /s /q "dist"
