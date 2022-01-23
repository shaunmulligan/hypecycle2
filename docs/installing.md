# Python setup:
add `export PATH="$HOME/.local/bin:$PATH"` to bottom of `~/.bashrc`
pip3 install --user pipx

# Install blinka:
```
sudo apt-get install libusb-1.0 libudev-dev
```
setup udev rule:
```
touch /etc/udev/rules.d/99-mcp2221.rules
```
then put this in the file:
```
SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", ATTR{idProduct}=="00dd", MODE="0666"
```