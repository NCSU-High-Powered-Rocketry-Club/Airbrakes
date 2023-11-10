"""
Factory pattern :(
"""

import sys

if "MockIMU" in sys.argv or "MockAll" in sys.argv:
    from MockMSCLInterface import MockMSCLInterface
    interface = MockMSCLInterface()
else:
    from MSCLInterface import MSCLInterface
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") 
    interface = MSCLInterface("/dev/ttyACM0", open(f"./logs/{now}_rawLORDlog.csv", "w"),  open(f"./logs/{now}_estLORDlog.csv", "w"))