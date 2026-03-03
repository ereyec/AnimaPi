# -- Print instruction for OS setup --
echo Instructions for OS setup
echo TSL2591:
echo sudo raspi-config
echo Then select Interface Options -> I2C -> Enable
echo 
echo Monkmakes Plant Monitor:
echo sudo raspi-config
echo Interface Options -> Serial port
echo Login shell over serial? Select No
echo Enable serial hardware? Select Yes
echo 

# -- Create directory and virtual environment --
mkdir ~/sensors
cd ~/sensors

sudo apt update
sudo apt install python3-venv

python3 -m venv .venv
source .venv/bin/activate

# -- Monkmakes setup --
sudo apt install -y python3-serial

# -- TSL2591 setup --
sudo apt-get install -y i2c-tools 
# Scan I2C bus 1, should see 0x29
sudo i2cdetect -y 1 

pip install adafruit-blinka adafruit-circuitpython-tsl2591 
sudo apt install -y python3-lgpio 
python -m pip install adafruit-blinka 
python -c "import board; import busio; print('board OK:', board.file)" 
python -m pip install adafruit-circuitpython-tsl2591 

# -- DHT22 --
sudo apt install -y python3-dev build-essential  
pip install adafruit-circuitpython-dht  

deactivate
sudo apt update 
sudo apt install -y gpiod libgpiod3 python3-libgpiod 

source .venv/bin/activate
pip install adafruit-circuitpython-dht

# -- Supabase --
pip install supabase 

# -- Camera setup --
sudo apt install libcamera-apps 
# check if the camera is detected
rpicam-still --list-cameras 


