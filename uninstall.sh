#!/system/bin/sh
# Stop the daemon and put every touched control back before the module goes.

MODDIR=/data/adb/modules/cmf_stereo
if [ -f "$MODDIR/scripts/common.sh" ]; then
  . "$MODDIR/scripts/common.sh"
  stop_daemons
  revert_actions
  # The stereo overlay leaves with the module; give the amp its gain back.
  amp_release_atten
fi

# Keep the config and probe reports: reinstalling should not lose the routing
# you worked out. Remove /data/adb/cmf-stereo by hand for a clean slate.
rm -f /data/adb/cmf-stereo/daemon.pid /data/adb/cmf-stereo/boot_pending
