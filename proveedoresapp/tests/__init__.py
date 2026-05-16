from pathlib import Path
import sys

package_root = str(Path(__file__).resolve().parents[1])
if package_root not in sys.path:
	sys.path.insert(0, package_root)
