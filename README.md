# speclab-sync
*Synchronize Spectrum Lab's VFO to HDSDR's*  

This Python 3 script connects HDSDR's VFO to Spectrum Lab's VFO via HDSDR's Omni-Rig support. It receives OmniRig messages for the "HRD" radio via a virtual serial loopback such as [com0com](https://sourceforge.net/projects/com0com/) and updates Spectrum Lab's VFO using WM_COPYDATA. 

## Usage
This script requires [Python 3](https://www.python.org/downloads/) (it was developed under 3.7.2) and [pywin32](https://pypi.org/project/pywin32/).  
A virtual serial port loopback is needed. [com0com](https://sourceforge.net/projects/com0com/) is open-source and works great.  
For HDSDR to function with this, [Omni-Rig](http://www.dxatlas.com/OmniRig/) needs to be installed. Once Omni-Rig is installed, configure HDSDR to use `CAT to Radio (OmniRig)`. Under `OmniRig Setup`, select "HRD" as the Rig Type and use one end of the serial loopback as the COM port. Disable `sync Modulation`, and make sure the Tune Frequency is being synced. Enable rig 1, and HDSDR is ready for use.  
Spectrum Lab should work almost out-of-the-box. This script is really only useful if HDSDR is outputting I/Q to an audio loopback such as [HI-FI Audio Cable](https://www.vb-audio.com/Cable/) and Spectrum Lab is using the other end of the loopback as an **I/Q** input.  

Once components are installed and configured, run the script as follows:  
`py -3 speclab_sync.py COM12 1`  
Change `COM12` to the output of the virtual serial loopback, and `1` to the instance number of Spectrum Lab you want to control (1 is the first run instance, 2 is the second run instance, etc.). If you want to see some basic program output, add `v` as a third argument to `speclab_sync.py`. 
