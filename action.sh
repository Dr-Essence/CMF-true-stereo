#!/system/bin/sh
# The Action button on the module's card (Magisk 28+, KernelSU, APatch):
# switches between Mono and Stereo, exactly as 'stereoctl channels' does.

# Magisk starts this as ./action.sh: make the folder absolute (common.sh
# would too; this keeps the stereoctl path below absolute as well).
MODDIR=$(cd "${0%/*}" 2>/dev/null && pwd) || MODDIR=/data/adb/modules/cmf_stereo
export MODDIR
. "$MODDIR/scripts/common.sh"

if stereo_staged; then _want=mono; else _want=stereo; fi
echo "CMF true stereo: switching to $_want"
echo
sh "$MODDIR/scripts/stereoctl" channels "$_want"
