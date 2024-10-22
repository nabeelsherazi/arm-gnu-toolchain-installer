# arm-gnu-toolchain installer

The idea for this is kind of to be like nvm/pyenv but for arm-gnu-toolchain (fka gcc-arm-none-eabi)

Releases.yml has every production ready version ever released for 64-bit Linux platforms. Dates back to about 2016, behind which I don't care.

All installed versions are installed to /opt/, which helps some projects that hardcode expect arm-none-eabi-gcc in that directory. `update-alternatives` is used to register all installed versions. Their priority is set by the build date, so newest toolchain is the default highest priority. You can override with `./arm-gnu-toolchain-installer use VERSION` or manually with `sudo update-alternatives --config arm-none-eabi-gcc` yourself.

This tool doesn't do any fancy scraping of ARM Developers website -- I manually tabulated releases in releases.yml. If there's a new release this will need to be updated.

## Usage

```
# List all known versions
./arm-gnu-toolchain-installer list

# List all installed versions
./arm-gnu-toolchain-installer list --installed

# Install a version 
./arm-gnu-toolchain-installer install VERSION

# Set a version to be the current system-wide version
./arm-gnu-toolchain-installer use VERSION
```

## To Do

* Also register all other toolchain tools
* Probably use should set only for current shell and something like global to set in all shells?
* Rename tool to something better
* Package for pip or something else