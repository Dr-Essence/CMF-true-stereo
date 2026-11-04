#!/system/bin/sh
# Runs before module files are mounted. This is the boot watchdog: if the
# previous two boots never reached sys.boot_completed while our audio policy
# or stereo overlay was active, that overlay is removed before it can be
# mounted again.
#
# That turns a bad policy into "reboot once more and it is gone" instead of a
# trip to recovery - which is exactly how the Hi-Res Audio module bricks boots.

MODDIR=${0%/*}
. "$MODDIR/scripts/common.sh"

OVERLAY_XML=$(find "$MODDIR/system" -name 'audio_policy_configuration*.xml' 2>/dev/null)

if [ -n "$OVERLAY_XML" ] && [ "$(boot_strikes)" -ge 2 ]; then
  log warn "boot watchdog: $(boot_strikes) failed boots with the policy overlay active - removing it"
  for f in $OVERLAY_XML; do rm -f "$f"; log warn "  removed $f"; done
  find "$MODDIR/system" -type d -empty -delete 2>/dev/null
  mkdir -p "$MODDIR/system/bin"
  touch "$DATADIR/xml_overlay_auto_removed"
  boot_strike_clear
fi

# Same for the stereo overlay (patched audio HAL + DSP config): two failed
# boots with it in place and it goes, leaving the phone on stock mono audio.
if stereo_staged && [ "$(boot_strikes)" -ge 2 ]; then
  log warn "boot watchdog: $(boot_strikes) failed boots with the stereo overlay - back to mono"
  unstage_stereo
  sed -i 's/^CHANNELS=.*/CHANNELS=mono/' "$CONF" 2>/dev/null
  touch "$DATADIR/stereo_auto_removed"
  boot_strike_clear
fi

# A daemon lock from the previous boot names a pid that no longer exists, and
# the mounts a live switch made are gone with the previous boot.
rm -rf "$DATADIR/daemon.lock" "$DATADIR/daemon.pid" "$LIVEFILE"

# Anything active this boot counts as a strike until service.sh clears it.
if [ -n "$OVERLAY_XML" ] || stereo_staged || [ "$(action_count)" -gt 0 ]; then
  boot_strike_add
fi

exit 0
