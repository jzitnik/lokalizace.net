# Extraktor dat z lokalizace.net Manageru
- ideální pro použití na Steam Decku
  

Závislosti:
 - dnfile

# Použití:
- stáhnout DLL z manageru (složka plugins)

```
./main.py DLL_FILE.dll
```

# Example:
```
honza@dell5490 ~ $ ./main.py RDR2_V1.3.dll 
invalid compressed int: leading byte: 0xec
invalid compressed int: leading byte: 0xe9
Resource <dnfile.resource.InternalResource object at 0x7f472ed9f0d0>
Resource file <dnfile.resource.ResourceEntry object at 0x7f472ed74d90>
Resource file <dnfile.resource.ResourceEntry object at 0x7f472ed74e10>
Found ZIP file!
Resource file <dnfile.resource.ResourceEntry object at 0x7f472ed74e90>
Resource file <dnfile.resource.ResourceEntry object at 0x7f472ed74f10>
Result {'getPluginID': 530768, 'getEXEname': 'RDR2.exe', 'getEXEversion': '1.0.1491.18', 'plugindatapassword': 'alka6549e*/wREcssd435374sd*'}
ZIP password 37CFB8B06A720E3053A6E5B72B82B268
./export_RDR2_V1.3.dll/NLog.dll
./export_RDR2_V1.3.dll/dinput8.dll
./export_RDR2_V1.3.dll/ModManager.Core.dll
./export_RDR2_V1.3.dll/out.zip
./export_RDR2_V1.3.dll/RDR2_Lokalizace.asi
./export_RDR2_V1.3.dll/vfs.asi
./export_RDR2_V1.3.dll/lml.ini
./export_RDR2_V1.3.dll/ModManager.NativeInterop.dll
./export_RDR2_V1.3.dll/lml/mods.xml
./export_RDR2_V1.3.dll/lml/LokalizaceNET/install.xml
./export_RDR2_V1.3.dll/lml/LokalizaceNET/lokalizace.net.strings
./export_RDR2_V1.3.dll/lml/LokalizaceNET/asset_replace/font_lib_efigs.gfx
DONE

```
