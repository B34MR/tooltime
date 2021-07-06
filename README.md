![Supported Python versions](https://img.shields.io/badge/python-3.9-green.svg)

# ToolTime
A Python3 script that quickly downloads and or installs Pentesting tools from a customizable configuration file.

<br>

**Tool Configuration files are categorized by assessment type and are located at the following:**
```
- External Network: ./tooltime/configs/external.ini
- Internal Network: ./tooltime/configs/internal.ini
- WebApp: ./tooltime/configs/webapp.ini
- Wireless: ./tooltime/configs/wireless.ini

* A custom Tool configuration files can also be used and may contain any filename</i>
```
**Alias Configuration files can be used customize your aliases and Bash prompt:**
```
- Alaises: ./tooltime/configs/alaises.ini

* A custom Alias configuration files can also be used, however it must use the 'aliases.ini' filename.
```

**Tool Configuration file legend:** <br>
```
- tools_dir - The destination directory for Github and Binary tools.
- github_urls - Github repositories to download.
- binary_urls - Files from direct URLs to download.
- pip_packages - Python3-Pip packages to install.
- apt_packages - APT packages to install.
- '#' to comment out any tools you wish to omit.
```

**Sample Configuration File:**
```
[tools_dir]
/opt/tools/internal

[github_urls]
https://github.com/FortyNorthSecurity/EyeWitness
https://github.com/fox-it/BloodHound.py
# https://github.com/danielmiessler/SecLists

[binary_urls]
https://download.sysinternals.com/files/SysinternalsSuite.zip

[pip_packages]
virtualenv
mitm6

[apt_packages]
#powershell
tree
```
**Supported Operating System:**
```
Kali-Linux
```

**Installation:**
```
apt install python3-pip
cd tooltime/
python3 -m pip install -r requirements.txt
```

**Usage:**
```
Customize one of the built-in Tool Configuration files or create your own.
Tooltime uses a positional argument for the config file selection.
Examples below:

python3 tooltime.py (defaults to configs/internal.ini)
python3 tooltime.py configs/internal.ini
python3 tooltime.py configs/external.ini
python3 tooltime.py configs/webapp.ini
python3 tooltime.py configs/wireless.ini
python3 tooltime.py /root/mycustomconfig.ini
```
<br>

**Tooltime Demo:**

![Tooltime Demo](demo/demo.gif)