#!/system/bin/sh
# Applies the routing actions and keeps them applied.
#
# The audio HAL rewrites mixer controls on every route change (stream start,
# device switch, call), so a one-shot write does not survive. This polls and
# re-asserts. It only holds the earpiece energised while audio is actually
# playing, unless MODE=always.

MODDIR=${MODDIR:-/data/adb/modules/cmf_stereo}
. "$MODDIR/scripts/common.sh"

rotate_log
echo $$ > "$PIDFILE"
# In stereo the amp is left on the full mix when the earpiece stops, so the
# speaker never plays one channel alone. The driver puts its own (left) slot
# back on the next stream start; README covers running stereo with the
# daemon off.
on_stop() {
  log info "daemon stopping"
  revert_actions
  stereo_active && amp_set_chsel mono
  rm -f "$PIDFILE"
  exit 0
}
trap on_stop TERM INT

# Wait for boot to finish so the HAL has settled before we touch anything.
_w=0
while [ "$(getprop sys.boot_completed)" != 1 ] && [ $_w -lt 120 ]; do
  sleep 2
  _w=$((_w + 2))
done
sleep "${STARTUP_DELAY:-10}"

if [ "$(action_count)" -eq 0 ]; then
  log info "no actions configured - nothing to do (run 'stereoctl probe' first)"
  rm -f "$PIDFILE"
  exit 0
fi

if ! find_tinymix && action_lines | grep -q '^[[:space:]]*ctl'; then
  log warn "tinymix not found but ctl actions are configured; they will be skipped"
fi

if stereo_active; then
  log info "daemon started (mode=$MODE interval=${WATCH_INTERVAL}s actions=$(action_count) channels=stereo)"
else
  log info "daemon started (mode=$MODE interval=${WATCH_INTERVAL}s actions=$(action_count) channels=mono)"
  # Left over from an earlier stereo boot: give the amp its own gain back.
  amp_release_atten
fi

applied=0

while true; do
  # Re-read config each cycle so stereoctl edits take effect without a reboot.
  [ -f "$CONF" ] && . "$CONF"

  if ! module_active; then
    [ $applied -eq 1 ] && { revert_actions; applied=0; log info "disabled - reverted"; }
    # Disabled with the stereo overlay mounted: keep the speaker on the full
    # mix, otherwise it would play the left channel alone.
    stereo_active && playback_active && amp_set_chsel mono
    sleep "${WATCH_INTERVAL:-2}"
    continue
  fi

  want=0
  case $MODE in
    always)   guard_ok && want=1 ;;
    *)        playback_active && speaker_route_active && guard_ok && want=1 ;;
  esac

  if [ $want -eq 1 ]; then
    # Re-assert unconditionally: apply_actions is a no-op for controls that
    # already hold the wanted value, so this is cheap when nothing changed.
    apply_actions
    [ $applied -eq 0 ] && log info "stereo engaged"
    applied=1
  elif [ $applied -eq 1 ]; then
    revert_actions
    applied=0
    log info "playback stopped - reverted"
  fi

  # Stereo: the speaker plays the right channel while the earpiece carries the
  # left, and the full mix whenever the earpiece is not playing. Speaker
  # protection on media is the amp's hardware cut-outs plus this attenuation.
  if stereo_active; then
    amp_hold_atten
    # Idle: nothing to hold, and no point waking the amp's I2C bus.
    if [ $applied -eq 1 ]; then
      amp_set_chsel right
    elif playback_active; then
      amp_set_chsel mono
    fi
  fi

  sleep "${WATCH_INTERVAL:-2}"
done
