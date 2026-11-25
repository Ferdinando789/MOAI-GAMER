#!/usr/bin/env python3
"""MOAI v90: keep Flycast native engine optional, with release-bound verified metadata."""
from pathlib import Path
import re
import sys

root=Path(sys.argv[1])
java=root/'app/src/main/java/com/infomak/moailite/MoaiFlycastCoreInstaller.java'
src=java.read_text(encoding='utf-8')
old='"https://raw.githubusercontent.com/Ferdinando789/MOAI-Flycast-Catalogo/main/modules/flycast-vulkan-arm32-v82.json"'
new='"https://github.com/Ferdinando789/MOAI-GAMER/releases/download/v0.1.90-arm32-test/flycast-vulkan-arm32-v90.json"'
assert src.count(old)==1
src=src.replace(old,new,1)
old='''            return "github.com".equalsIgnoreCase(u.getHost()) &&
                   u.getPath().startsWith("/Ferdinando789/MOAI-Flycast-Catalogo/releases/download/");'''
new='''            return "github.com".equalsIgnoreCase(u.getHost()) &&
                   u.getPath().startsWith("/Ferdinando789/MOAI-GAMER/releases/download/v0.1.90-arm32-test/") &&
                   u.getPath().endsWith("/flycast_core_arm32.apk");'''
assert src.count(old)==1
src=src.replace(old,new,1)
src=src.replace('El módulo publicado no coincide con esta versión de MOAI.',
                'El módulo Flycast no corresponde a MOAI v0.1.90. Revisá la actualización.')
java.write_text(src,encoding='utf-8')
build=root/'app/build.gradle'
s=build.read_text(encoding='utf-8')
s,n=re.subn(r'versionCode\s+\d+','versionCode 90',s);assert n==1
s,n=re.subn(r'versionName\s+"[^"]+"','versionName "0.1.90"',s);assert n==1
build.write_text(s,encoding='utf-8')
print('Configured v90 installer: GitHub Release manifest and matching signed optional ARM32 module')
