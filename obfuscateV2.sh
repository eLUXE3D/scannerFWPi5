#JM script to make install files for production units
#obfuscates, compiles to exe, adds extra files, zips.
#takes 15 mins
#license.lic goes in :
#sudo cp /home/pi/Teeth/license.lic /usr/local/lib/python3.7/dist-packages/pyarmor/
#once on pyarmor install

#echo on
set -x

#delete old
cd /home/pi/Teeth/release2
sudo rm dist -f -r

#obfuscate
cd /home/pi/Teeth
sudo pyarmor pack release2/main.py

#copy extra files from install folder
cd /home/pi/Teeth
sudo chown -R pi:pi release2/dist
sudo chmod -R o+rwx release2/dist
sudo cp installV2/update.py release2/dist/update.py
sudo cp -r installV2/* release2/dist/main/
sudo mkdir release2/dist/main/Images
sudo cp -r release2/Images/* release2/dist/main/Images

#zip
cd /home/pi/Teeth/release2/dist
sudo rm main.zip
sudo zip -r --password 'nb*I2$jxMnNl60I+t&EE1GU0HbWert!' main.zip main
sudo zip --password 'nb*I2$jxMnNl60I+t&EE1GU0HbWert!' main.zip update.py


#copy to 128GB usb disk
sudo rm /media/pi/KINGSTON/main.zip
sudo rm /media/pi/KINGSTON/update.py

sudo cp main.zip /media/pi/KINGSTON/main.zip
sudo cp update.py /media/pi/KINGSTON/update.py

echo done

sleep 99999