# RebbleTool

An upgraded version of `pebbletoo`l that runs on modern python (tested on 3.13)

**_Very_ Experimental, Use At Your Own Risk!!!**

See [Setup](#setup) for installation instructions.

How to use:
https://developer.rebble.io/developer.pebble.com/guides/tools-and-resources/pebble-tool/index.html

## Tested on:
- macOS
  - `x86_64` - emulator works
  - `M1/M2` - emulator works, given x86 dylibs for pixman, etc. Running `sdk install latest` will ask you to install into the project directory if they are needed!
- Linux
  - `x86_64` - emulator works

## Working commands:
- `sdk install latest` - NOTE: patches currently only work for the latest 4.3
- `install --phone <ip>`
- `install --emulator`
- `build`
- `logs`
- `screenshot`
- `ping`
- `analyze-size` - runs, but returns blank data
- `wipe`
- `emu-time-format --format <12h/24h>`
- `emu-battery --percent [0-100] [--charging]`
- `emu-tap --direction <+x|-x|+y|-y|+z|-z>`
- `emu-compass --heading <0-360>`

## Setup
This doesn't really care about where it's installed. I've patched the sdk path to be inside the folder alongside this tool, so it's easier to clean up and manage without `cd`'ing all the time.

You also don't _need_ to add it to your path, although it's much easier to type `rebble` than some other long path to the .bin`

Prerequisites for Apple Silicon: Install Rosetta 2: `softwareupdate --install-rosetta`

```bash
mkdir ~/.rebbletool
cd ~/.rebbletool
git clone https://github.com/richinfante/rebbletool.git
cd rebbletool

python3 -m venv .env  # .env is the _required_ name, or it won't work
source .env/bin/activate
pip3 install -r requirements.txt

# Recommended - add to your $PATH
# or your equivalent for your shell (e.g. ~/.zshrc instead of ~/.bash_profile)
# if you don't, you need to run `~/.rebbletool/rebbletool/bin/rebble` instead of `rebble`
echo 'export PATH=~/.rebbletool/rebbletool/bin:$PATH' >> ~/.bash_profile
source ~/.bash_profile

# pull the latest SDK. This will only work for the latest sdk
rebble sdk install latest

# cd into your project, or our `dummy_project` to finish setting up the sdk
cd my_project

# configure, patch sdk, and build
rebble build

# install on your phone
rebble install --phone <ip>

# install on emulator
# this works on x86 mac, and x86 linux
rebble install --emulator <i>
```

## Updating SDK patches
If you're going to help us fix issues in the SDK, this is how you do it.

Essentially, we re-install the sdk and initialize the sdk folder as a git repo. We commit the initial version and use that to snapshot changes. We then apply the current patches, and can re-generate the patch file.

```bash
# do a fresh install (answer yes to "reinstall")
rebble sdk install latest

# cd to a project to do a build
# this project contains a minimal "dummy" that does nothing, for testing build scripts without a real app/watchface
cd ~/.rebbletool/rebbletool/dummy_project

# don't patch, so we can setup a git repo to generate one
rebble build --skip-patch-sdk
# this should print:
#> SDK needs patching, but skipping due to --skip-patch-sdk

# cd to the sdk
cd ../sdk

# remove all pyc files from the initial run
find . -name "__pycache__" -type d -exec rm -r {} +
git init
git add .
git commit -m "Snapshot"

# apply latest patch
patch -p1 < ../sdk.patch

# now, you can develop using `rebble` as usual, and then
# edit the files in the ~/.rebbletool/rebbletool/sdk

# when you're satisfied, then generate a latest patch
git diff > ../sdk.patch

# create branch & pr the patch
```

## Development Notes
### Emulator on macOS
To let the emulator run on macOS, you need the following libraries, compiled for x86:
- `libglib-2.0.0.dylib`
- `libintl.8.dylib`
- `libpixman-1.0.dylib`
- `libgthread-2.0.0.dylib`
- `libpcre2-8.0.dylib`

I have compiled these for you and zipped them here: https://public.richinfante.com/rebble/macos_x86_lib_pebble_qemu.tar.gz

We set `DYLD_FALLBACK_LIBRARY_PATH` when starting the emulator so macOS can find them. If you accept the install of these, they are placed in the `lib/` folder of this repo (if following the directions, `~/.rebbletool/rebbletool/lib`)

### SDK patching
Some notes on how this all works!

We download the sdk and extract as normal, with some modifications to the requirements.txt file

Then, we modify the waf file from the SDK. It doesn't execute in python3 since it contains null bytes, so we duplicate the file, and modify the original to remove the data and point the extract at the duplicate.

Then, the tool runs a waf configure. The first go-around, this extracts but crashes. We detect this and install our `sdk.patch`, which fixes the known issues for python3, and continues.

```bash
# this will crash, but extract the waf file
PATH="$DIR/pebble-sdk-4.5-mac/bin:$DIR/arm-cs-tools/bin:$PATH" NODE_PATH="$DIR/sdk/SDKs/current/sdk-core/../node_modules" '$DIR/sdk/SDKs/current/sdk-core/../.env/bin/python' '$DIR/sdk/SDKs/current/sdk-core/pebble/waf' 'configure'

# apply our patches
cd sdk && git apply ../sdk.patch

# re-configuring should work
PATH="$DIR/pebble-sdk-4.5-mac/bin:$DIR/arm-cs-tools/bin:$PATH" NODE_PATH="$DIR/sdk/SDKs/current/sdk-core/../node_modules" '$DIR/sdk/SDKs/current/sdk-core/../.env/bin/python' '$DIR/sdk/SDKs/current/sdk-core/pebble/waf' 'configure'
```

