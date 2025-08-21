<img src="utils/banner.jpg" width="100%" alt="banner">

# tc-dx-sdk
A pre-release SDK validation tool from the CS Team. <br>
It offers both full and smoke tests across four key modules: APP, COM, RT, and STREAM.

## Installation
- Install required deb packages:
```console
wget https://github.com/allure-framework/allure2/releases/download/2.34.1/allure_2.34.1-1_all.deb --no-check-certificate
sudo apt install -y ./allure_2.34.1-1_all.deb
rm allure_2.34.1-1_all.deb
sudo apt install -y v4l-utils
sudo apt install -y openjdk-11-jdk # If fails, try 'openjdk-17-jdk'
```

- Create and activate a virtual environment and then install the required pip packages:
```console
python3 -m venv .venv-tc
source .venv-tc/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Mandatory Settings
- Set your dx-all-suite path
```

```

## Usage and Options
- Activate python virtual environment
- Full Test
```console
pytest
```
- Module Test
```
# DX RT test
pytest tests/rt

# DX APP test
pytest tests/app

# DX Stream test
pytest tests/stream

# DX COM test
pytest tests/com
```
### General Options:
- `-s`: Show all messages while pytest running
```console
pytest -s
```

## Report
```console
# Run on your local server only
allure serve allure-results
# Run for external view (share your IP in the same network)
allure serve allure-results --host 192.168.0.114
```

## Feedback
- Ask a question on CS team or <dgkim@deepx.ai>
