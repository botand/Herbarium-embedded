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

TODO

### Run the code

First you will need to declare the environment variable `CONFIG_YAML_FILE`,
which redirect to the `config.yaml` file. The file given in this repository is
**NOT FOR PRODUCTION USE**. So to start the code, execute the following:

```shell
export CONFIG_YAML_FILE='<YOUR-CONFIG-FILE>'
python3 -m src
```
