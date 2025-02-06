# RebbleTool

An upgraded version of pebbletool that runs on modern python

How to use:
https://developer.rebble.io/developer.pebble.com/guides/tools-and-resources/pebble-tool/index.html

Setup:
```bash
mkdir ~/.rebbletool  # or any other folder, we do not care
cd ~/.rebbletool
git clone https://github.com/richinfante/rebbletool.git
cd rebbletool

python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt

# or your equivalent for your shell (e.g. ~/.zshrc)
echo 'export PATH=~/.rebbletool/rebbletool/bin:$PATH' >> ~/.bash_profile

rebble  # should print help!
```

```bash
export PATH="$PWD/bin/:$PATH"
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


notes:

We download the sdk and extract as per-normal, with some modifications to the requirements.txt file

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