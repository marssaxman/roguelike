set -e

log () {
    ORANGE='\033[0;33m'
    NC='\033[0m'
    echo -e "${ORANGE}${*}${NC}"
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

log "\nInstalling packages..."
apt install build-essential
apt install python3-dev python3-pip python3-numpy
apt install python3.10-venv
apt install libsdl2-dev libffi-dev


log "\nCreating virtualenv..."
rm -rf venv
python3 -m venv --system-site-packages ./venv
source venv/bin/activate
pip install -r requirements.txt

log "\nBuild completed"

