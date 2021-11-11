# Herbarium-embedded
Embedded software of Herbarium 

## What is it?

Herbarium is a semi-autonomous greenhouse that can help people growing plants in their house while proposing recipe to consume their in-house production.

This is an end of study project realized by three student of the [ÉTS](etsmtl.ca): 

- Charles Chaumienne (electrical engineering)
- Youssef Hammami (software engineering)
- [Xavier Chrétien (software engineering)](https://github.com/apomalyn).

## Code

### Requirements

- python3 or more

This project should run on a Raspberry Pi with bluetooth. For `Ubuntu/Debian/Raspbian`
install the following packages:

```shell
sudo apt-get install bluetooth bluez libbluetooth-dev libudev-dev
```

Install the python requirements:

```shell
pip3 install -r requirements.txt
```

### Local setup

#### Wi-Fi

If you don't want to set up the Wi-Fi of your device using bluetooth you can create a file `.wifi_credentials.yaml`
with the following content:

```yaml
ssid: <YOUR_SSID_AKA_WIFI_NAME>
psk: <YOUR_WIFI_PASSWORD>
```

This will connect your device to the Wi-Fi when the program starts.

To set up the Wi-Fi using BLE, you will need to sent two (2) packet on the `setup_wifi` characteristic.
The first one should be composed like this: `ssid:<YOUR_SSID>` and the second one: `psk:<YOUR_WIFI_PASSWORD>`

### Run the code

First you will need to declare the environment variable `CONFIG_YAML_FILE`,
which redirect to the `config.yaml` file. So to start the code, execute the following:

```shell
sudo su
export CONFIG_YAML_FILE='<YOUR-CONFIG-FILE>'
python3 -m src
```
You can also write the `CONFIG_YAML_FILE` variable into the `/etc/environment` file.
Note that you will have to logout and login to access the variable.

## Hooks

This project use hooks to ensure the quality of the code. To enable them use this command:

```shell
git config core.hooksPath githooks
```

### pre-commit

This hook will format and lint your code before every commit.

### pre-push

Before every push, the unit test of the application will be executed.
If you don't use the default SignalR server, don't forget to change it on the hook file (`.git/hooks/pre-push`)

##Installing SQLite to the Raspberry Pi
1. To make sure we don’t run into any issues when installing SQLite, we should first update the operating system.
You can update your Raspberry Pi’s operating system by running the following two commands>
```shell
sudo apt update
sudo apt full-upgrade
```
These commands will update the list of packages on your device and then upgrade any out-of-date packages.

2. Once the update process finishes, you can install SQLite to your Raspberry Pi.
All you need to do to install SQLite is to run the following command.

```shell
sudo apt install sqlite3
```
You will notice that we are using SQLite 3  which is the latest major version at the time of publishing.
The exact version the Raspbian repository provides is, at the time of publishing, “3.27.2“.
```shell
pi@:~ $ sqlite3 my_DB
SQLite version 3.27.2 2019-02-25 16:06:06
Enter ".help" for usage hints.
sqlite> .exit
pi@:~ $
```
##Auto-Run Python Program on Raspberry Pi Startup
The latest Raspbian have some of its boot sequences will lead some problems in running your python script using Cron or rc.local. so  “Systemd” is recommended to overcome such issues.  
Create a configuration file and edit it. This file will tell systemd which program needs to be executed :
```shell
sudo nano /lib/systemd/system/myscript.service
```
Add the following lines in the file:
```shell
[Unit]
Description=PiCube Pattern
After=multi-user.target
[Service]
Type=idle
ExecStart=/usr/bin/python3  /home/pi/myscript.py
[Install]
WantedBy=multi-user.target
```
Change the permissions on the configuration file to 644:
```shell
sudo chmod 644 /lib/systemd/system/myscript.service
```
Now tell the systemd to start the process on boot up :
```shell
sudo systemctl daemon-reload
sudo systemctl enable myscript.service
```
Now reboot your Pi and the process should run:
```shell
sudo reboot
```
