# RebbleTool

An upgraded version of pebbletool that runs on modern python

**Very Experimental, Use At Your Own Risk!!!**

How to use:
https://developer.rebble.io/developer.pebble.com/guides/tools-and-resources/pebble-tool/index.html

## Setup
```bash
mkdir ~/.rebbletool  # or any other folder, we do not care
cd ~/.rebbletool
git clone https://github.com/richinfante/rebbletool.git
cd rebbletool

python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt

# or your equivalent for your shell (e.g. ~/.zshrc instead of ~/.bash_profile)
echo 'export PATH=~/.rebbletool/rebbletool/bin:$PATH' >> ~/.bash_profile
source ~/.bash_profile

rebble sdk install latest

# cd into your project
cd my_project

# configure, patch sdk, and build
rebble build

# install on your phone
rebble install --phone <ip>
```

## Working commands:
- `sdk install latest` - NOTE: patches currently only work for the latest 4.3
- `install --phone <ip>`
- `build`
- `logs`
- `screenshot`
- `ping`
- `analyze-size` - runs, but returns blank data

## Tested on:
- macOS (M2)

## Development Notes

We download the sdk and extract as normal, with some modifications to the requirements.txt file

Then, we modify the waf file, so that the data is split into a separate file. Python3 doesn't like the original packed waf since it has null bytes in it.

Then, we run a configure. This _mostly_ works, extracting the files we need. Then, we run our patch to allow it to actually function for our build.

```bash
# this will crash, but extract the waf file
PATH="$DIR/pebble-sdk-4.5-mac/bin:$DIR/arm-cs-tools/bin:$PATH" NODE_PATH="$DIR/sdk/SDKs/current/sdk-core/../node_modules" '$DIR/sdk/SDKs/current/sdk-core/../.env/bin/python' '$DIR/sdk/SDKs/current/sdk-core/pebble/waf' 'configure'

# apply our patches
cd sdk && git apply ../sdk.patch

# re-configuring should work
PATH="$DIR/pebble-sdk-4.5-mac/bin:$DIR/arm-cs-tools/bin:$PATH" NODE_PATH="$DIR/sdk/SDKs/current/sdk-core/../node_modules" '$DIR/sdk/SDKs/current/sdk-core/../.env/bin/python' '$DIR/sdk/SDKs/current/sdk-core/pebble/waf' 'configure'
```

When running build, macOS will complain about every binary. gotta do something about that.

## Updating SDK patches
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
