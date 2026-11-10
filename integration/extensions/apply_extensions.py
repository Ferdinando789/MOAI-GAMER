#!/usr/bin/env python3
"""Add a TV extension screen inside Settings > Channels, Extensions & Backups."""
from pathlib import Path
import re,shutil,sys
root=Path(sys.argv[1]); patch=Path(sys.argv[2])
app=root/'app/src/main'
java=app/'java/com/infomak/moailite'
shutil.copy2(patch/'MoaiExtensionsActivity.java',java/'MoaiExtensionsActivity.java')
tools=java/'ToolsActivity.java'
s=tools.read_text(encoding='utf-8')
needle='section("FUENTES DE CANALES");for(String source:new String[]{'
assert s.count(needle)==1,'ToolsActivity source section changed'
s=s.replace(needle,'''section("FUENTES DE CANALES");
        button("Administrador de extensiones · DaddyLive y Argentina",
            ()->startActivity(new Intent(this,MoaiExtensionsActivity.class)));
        for(String source:new String[]{''',1)
tools.write_text(s,encoding='utf-8')
manifest=app/'AndroidManifest.xml'
s=manifest.read_text(encoding='utf-8')
assert '</application>' in s
s=s.replace('</application>','''<activity android:name="com.infomak.moailite.MoaiExtensionsActivity"
            android:exported="false" android:label="MOAI GAMER · Extensiones"/>
    </application>''',1)
manifest.write_text(s,encoding='utf-8')
build=root/'app/build.gradle'
s=build.read_text(encoding='utf-8')
s,n=re.subn(r'versionCode\s+\d+','versionCode 85',s);assert n==1
s,n=re.subn(r'versionName\s+"[^"]+"','versionName "0.1.85"',s);assert n==1
build.write_text(s,encoding='utf-8')
print('v0.1.85: Extensions Manager added under Channels, Extensions & Backups')
