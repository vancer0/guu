python-appimage build app -p 3.10 appimage
chmod +x GUU-x86_64.AppImage
./GUU-x86_64.AppImage --appimage-extract
rm GUU-x86_64.AppImage

# Copy AppImage files
rm squashfs-root/io.github.vancer0.guu.desktop
rm squashfs-root/usr/share/applications/io.github.vancer0.guu.desktop
cp appimage/io.github.vancer0.guu.desktop squashfs-root/io.github.vancer0.guu.desktop
cp appimage/io.github.vancer0.guu.desktop squashfs-root/usr/share/applications/io.github.vancer0.guu.desktop

# Copy GUU files
mkdir squashfs-root/src
cp src/*.py squashfs-root/src
cp -r src/ui squashfs-root/src/ui
cp -r src/languages squashfs-root/src/languages
mkdir squashfs-root/src/icon
cp src/icon/guu.png squashfs-root/src/icon/guu.png

# Make AppImage
export VERSION=1
export ARCH=x86_64 appimagetool
chmod -R 755 squashfs-root
wget -c https://github.com/$(wget -q https://github.com/probonopd/go-appimage/releases -O - | grep "appimagetool-.*-x86_64.AppImage" | head -n 1 | cut -d '"' -f 2)
chmod +x appimagetool-*.AppImage
./appimagetool-*-x86_64.AppImage squashfs-root/
rm appimagetool-*-x86_64.AppImage
rm -r squashfs-root

# Copy executable
rm -r bin
mkdir bin
mv GUU-$VERSION-$ARCH.AppImage bin/GUU-Linux-$ARCH.AppImage
