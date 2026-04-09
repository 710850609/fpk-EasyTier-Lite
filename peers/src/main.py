import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch import update_peers as fetch
from check_peers_easytier import main as check

if __name__ == "__main__":
    fetch()
    check()
