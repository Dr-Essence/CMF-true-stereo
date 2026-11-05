#!/system/bin/sh
# Applies the routing actions and keeps them applied.
#
# The audio HAL rewrites mixer controls on every route change (stream start,
# device switch, call), so a one-shot write does not survive. This polls and
# re-asserts. It only holds the earpiece energised while audio is actually
# playing, unless MODE=always.

MODDIR=${MODDIR:-/data/adb/modules/cmf_stereo}
. "$MODDIR/scripts/common.sh"

if ! daemon_lock; then
  log info "another daemon is already running (pid $(cat "$LOCKDIR/pid" 2>/dev/null)) - exiting"
  exit 0
fi
rotate_log
# In stereo the amp is left on the full mix when the earpiece stops, so the
# speaker never plays one channel alone. The driver puts its own (left) slot
# back on the next stream start; README covers running stereo with the
# daemon off.
on_stop() {
  [ -n "${NAP_PID:-}" ] && kill "$NAP_PID" 2>/dev/null
  log info "daemon stopping"
  revert_actions
  stereo_active && amp_set_chsel mono
  daemon_unlock
  update_description
  exit 0
}
trap on_stop TERM INT

# Wait for boot to finish so the HAL has settled before we touch anything.
_w=0
while [ "$(getprop sys.boot_completed)" != 1 ] && [ $_w -lt 120 ]; do
  nap 2
  _w=$((_w + 2))
done
nap "${STARTUP_DELAY:-10}"
# Once, here in the top-level shell, so every mixer call below inherits it.
tinymix_ready

if [ "$(action_count)" -eq 0 ]; then
  log info "no actions configured - nothing to do (run 'stereoctl probe' first)"
  daemon_unlock
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
update_description
notify_apps

applied=0
was_playing=0
atten_tick=0
swap_tick=0
last_rot=
last_atten=

while true; do
  # Re-read config each cycle so stereoctl edits take effect without a reboot.
  [ -f "$CONF" ] && . "$CONF"

  if ! module_active; then
    [ $applied -eq 1 ] && { revert_actions; applied=0; log info "disabled - reverted"; }
    # Disabled with the stereo overlay mounted: keep the speaker on the full
    # mix, otherwise it would play the left channel alone.
    stereo_active && playback_active && amp_set_chsel mono
    nap "${WATCH_INTERVAL:-2}"
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
    _pb=0; playback_active && _pb=1
    # The Awinic driver writes a kernel log line for every volume read, so the
    # attenuation is checked when playback starts and every 10th cycle, not
    # every cycle (that flooded dmesg and pushed the boot messages out).
    # The protection's ceilings follow the settings and whether it runs; when
    # the wanted attenuation changes (boost, speaker level, the library starting)
    # the amp is set at once rather than at the next check.
    if hal_crash_loop; then
      log warn "the audio HAL restarted 3 times within a minute in stereo - back to mono (stock files)"
      sed -i 's/^CHANNELS=.*/CHANNELS=mono/' "$CONF" 2>/dev/null
      unstage_stereo
      live_switch mono >/dev/null 2>&1 || log warn "live switch to mono failed: mono after a reboot"
      rm -f "$HALWATCH"
      update_description
      notify_apps
      nap "${WATCH_INTERVAL:-2}"
      continue
    fi
    prot_apply
    _ad=$(prot_atten_db)
    if { [ $_pb -eq 1 ] && [ $was_playing -eq 0 ]; } || [ $atten_tick -le 0 ] || [ "$_ad" != "$last_atten" ]; then
      last_atten=$_ad
      amp_hold_atten
      atten_tick=10
    fi
    atten_tick=$((atten_tick - 1))
    # Apps whose track has its own effect (VLC): Android does not swap them
    # with the rotation, the HAL does, on the outputs named here. Only
    # needed at rotation 270, so the dump runs only then: when playback
    # starts, when the phone turns to 270, and every 3rd cycle.
    if [ $_pb -eq 1 ]; then
      _rot=$(getprop "$ROT_PROP")
      if [ "$_rot" = 270 ]; then
        if [ $was_playing -eq 0 ] || [ "$last_rot" != 270 ] || [ $swap_tick -le 0 ]; then
          swap_outputs_update
          swap_tick=3
        fi
        swap_tick=$((swap_tick - 1))
      fi
      last_rot=$_rot
    fi
    was_playing=$_pb
    # Idle: nothing to hold, and no point waking the amp's I2C bus.
    if [ $applied -eq 1 ]; then
      amp_set_chsel right
    elif [ $_pb -eq 1 ]; then
      amp_set_chsel mono
    fi
  fi

  nap "${WATCH_INTERVAL:-2}"
done
