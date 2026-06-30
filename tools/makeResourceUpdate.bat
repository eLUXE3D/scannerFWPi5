xcopy D:\eLUXE3D\_PlateFiles\*.npz D:\eLUXE3D\scannerFW\release2\plateFiles /Y
xcopy D:\eLUXE3D\_PlateFiles\*.npz D:\eLUXE3D\scannerFW\tools\main\plateFiles /Y

"C:\Program Files\7-Zip\7z.exe" a  -r update.zip -w main\* -p"nb*I2$jxMnNl60I+t&EE1GU0HbWert!"

echo Deleting plateFiles
del /Q D:\eLUXE3D\_PlateFiles\*.*
echo Plate files copied, zip created, plate files deleted
pause
