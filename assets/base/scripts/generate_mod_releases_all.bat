@echo off

cd "%~dp0"

cd ..

taskkill /f /im "unreal_auto_mod.exe" > nul 2>&1

set exe_file="%CD%/unreal_auto_mod.exe"
set settings_json="%CD%/presets/default/settings.json"
set arg=generate_mod_releases_all
set base_files_directory=%CD%/presets/default/mod_packaging/releases
set output_directory=%CD%/dist

%exe_file% %arg% --settings_json "%settings_json%" --base_files_directory "%base_files_directory%" --output_directory "%output_directory%"

exit /b
