cd /Users/jim/git/guu

pyinstaller guu-mac.spec

mkdir tmp

mv dist/guu.app "tmp/GayTor.rent Upload Utility.app"

rm -r bin

create-dmg \
	--volname "GayTor.rent Upload Utility" \
	--icon-size 100 \
	--window-pos 200 120 \
	--window-size 800 400 \
	--icon "GayTor.rent Upload Utility.app" 200 190 \
	--hide-extension "GayTor.rent Upload Utility.app" \
	--app-drop-link 600 185 \
	"GUU-Mac-x86_64.dmg" \
	"tmp"
	
mkdir bin
mv GUU-Mac-x86_64.dmg bin/GUU-Mac-x86_64.dmg
	
rm -r build dist tmp