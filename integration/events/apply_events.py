#!/usr/bin/env python3
"""Apply the optional MOAI Events TV catalog after the v82 gamer layout patch."""
from pathlib import Path
import re
import shutil
import sys

root = Path(sys.argv[1])
patch = Path(sys.argv[2])
main = root / "app/src/main"
java = main / "java/com/infomak/moailite"
layout = main / "res/layout/activity_main.xml"
manifest = main / "AndroidManifest.xml"
gradle = root / "app/build.gradle"

shutil.copy2(patch / "MoaiEventsActivity.java", java / "MoaiEventsActivity.java")

xml = layout.read_text(encoding="utf-8")
anchor = '<include layout="@layout/header_navigation"/>'
assert xml.count(anchor) == 1, "No se encontró la cabecera esperada"
extra = """<Button android:id="@+id/moaiEventsButton"
        android:layout_width="match_parent" android:layout_height="38dp"
        android:text="⚽  EVENTOS EN VIVO  ·  Agenda actualizable"
        android:textSize="13sp" android:textColor="#FFFFFF"
        android:backgroundTint="#17446F" android:allCaps="false"
        android:focusable="true" android:onClick="openMoaiEvents"/>"""
xml = xml.replace(anchor, anchor + "\n    " + extra, 1)
layout.write_text(xml, encoding="utf-8")

activity = java / "MainActivity.java"
source = activity.read_text(encoding="utf-8")
assert 'openMoaiEvents(' not in source
idx = source.rfind("}")
assert idx >= 0
source = source[:idx] + """
    /** Opens the independent live-events directory without touching TV channels. */
    public void openMoaiEvents(android.view.View view) {
        startActivity(new android.content.Intent(this, MoaiEventsActivity.class));
    }
""" + source[idx:]
activity.write_text(source, encoding="utf-8")

text = manifest.read_text(encoding="utf-8")
assert "</application>" in text
text = text.replace("</application>",
    '<activity android:name=".MoaiEventsActivity" android:exported="false" '
    'android:label="MOAI GAMER · Eventos en vivo" />\n    </application>', 1)
manifest.write_text(text, encoding="utf-8")

text = gradle.read_text(encoding="utf-8")
text, n = re.subn(r"versionCode\s+\d+", "versionCode 83", text)
assert n == 1
text, n = re.subn(r'versionName\s+"[^"]+"', 'versionName "0.1.83"', text)
assert n == 1
gradle.write_text(text, encoding="utf-8")
print("MOAI GAMER v0.1.83: catálogo de eventos instalado; canales originales intactos")
