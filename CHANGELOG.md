# Changelog

## v2.0
 - Fixed bug where only observations for first period were imported from MAPPS Timeline Dump
 - JUICE models are now included in the distribution, which greatly simplifies Cosmographia setup.
 - Implemented solar panel rotation calculation using spiceypy.
 - Linux and Mac support


## v1.0
 - Moved to Python3.6, Python2 compatibility removed.
 - Updated setup guide for JUICE SPICE Kernel Dataset v1.6.0
 - Added option to set custom start time.
 - The output folder can now be renamed after creation without breaking functionality.
 - Minor bugfixes.


## v0.2
First tracked release.

### Features
 - Import of attitude `.csv` and timeline `.asc` file into a Cosmographia scenario.
 - Configuration via `.ini` files.
 - Immediate launching of scenario after generation.