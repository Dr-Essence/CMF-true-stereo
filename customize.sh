#!/system/bin/sh
# Installer. Deliberately does nothing to the audio stack: it lays down the
# tooling and the config, and tells you what to run next.

SKIPMOUNT=false
PROPFILE=false
POSTFSDATA=true
LATESTARTSERVICE=true

DATADIR=/data/adb/cmf-stereo

ui_print " "
ui_print "  CMF Phone 1 - stereo speaker"
ui_print "  ----------------------------"
ui_print "  device   : $(getprop ro.product.model) ($(getprop ro.product.device))"
ui_print "  platform : $(getprop ro.board.platform) / $(getprop ro.soc.manufacturer)"
ui_print "  android  : $(getprop ro.build.version.release) (API $API)"
ui_print " "

if [ "$API" -lt 31 ]; then
  ui_print "  ! Android 12 or newer expected; continuing anyway."
fi

IS_CMF1=0
case "$(getprop ro.product.device)$(getprop ro.product.model)" in
  *[Tt]etris*|*A015*|*CMF*|*cmf*) IS_CMF1=1 ;;
  *)
    ui_print "  ! This does not look like a CMF Phone 1."
    ui_print "    Nothing is applied automatically, so it is safe to keep"
    ui_print "    going - the probe works on any device."
    ui_print " "
    ;;
esac

##############################################################################
# config in /data so it survives module updates
##############################################################################
mkdir -p "$DATADIR/state" "$DATADIR/bin"

if [ -f "$DATADIR/stereo.conf" ]; then
  # Keep the user's settings, but add keys introduced by newer versions -
  # otherwise an upgrade silently runs without them.
  ADDED=0
  for KEY in ENABLED MODE WATCH_INTERVAL STARTUP_DELAY REQUIRE_SPEAKER_ROUTE \
             GUARD_CTL GUARD_VALUE PLAYBACK_CTL PLAYBACK_VALUE \
             MIXER_CARD CHANNELS STEREO_ATTEN_DB SPEAKER_BOOST BASS_PROTECT EARPIECE_LIMIT EARPIECE_LEVELLER \
             LOG_LEVEL LOG_MAX_KB; do
    grep -q "^[[:space:]]*$KEY=" "$DATADIR/stereo.conf" && continue
    DEF=$(grep "^$KEY=" "$MODPATH/config/stereo.conf" | head -n 1)
    [ -n "$DEF" ] || continue
    [ "$ADDED" -eq 0 ] && echo "" >> "$DATADIR/stereo.conf" && \
      echo "# --- added by v$(grep_prop version "$MODPATH/module.prop") ---" >> "$DATADIR/stereo.conf"
    echo "$DEF" >> "$DATADIR/stereo.conf"
    ADDED=$((ADDED + 1))
  done
  if [ "$ADDED" -gt 0 ]; then
    ui_print "  kept stereo.conf, added $ADDED new setting(s)"
  else
    ui_print "  keeping existing stereo.conf"
  fi
else
  cp -f "$MODPATH/config/stereo.conf" "$DATADIR/stereo.conf"
  ui_print "  installed default stereo.conf"
fi

# The DSP task switches that mean "audio is playing" (any one of them).
CMF1_PLAYBACK_CTLS='dsp_music_runtime_en|dsp_fast_runtime_en|dsp_primary_runtime_en|dsp_deepbuf_runtime_en|dsp_voipdl_runtime_en|dsp_offload_runtime_en'

# The guard is device-specific, so set it where we know what it should be.
if [ "$IS_CMF1" = 1 ]; then
  sed -i "s/^GUARD_CTL=.*/GUARD_CTL='aw_dev_0_switch'/; s/^GUARD_VALUE=.*/GUARD_VALUE='Enable'/" \
    "$DATADIR/stereo.conf" 2>/dev/null
  ui_print "  guard: earpiece follows the speaker amp"
  # Each kind of output has its own DSP task switch, and the procfs scan never
  # sees DSP playback. Measured on the phone: games turn on dsp_fast, music
  # players dsp_music and dsp_primary; dsp_playback is always on (useless).
  sed -i "s/^PLAYBACK_CTL=.*/PLAYBACK_CTL='$CMF1_PLAYBACK_CTLS'/; s/^PLAYBACK_VALUE=.*/PLAYBACK_VALUE='1'/" \
    "$DATADIR/stereo.conf" 2>/dev/null
  ui_print "  playback detected on every DSP playback task (music, fast, primary, ...)"
fi

# Ship the verified routing on the device it was verified on. An actions.conf
# that already has real content is never overwritten - that is the user's
# tuning, and it may well be better than the default.
EXISTING=0
[ -f "$DATADIR/actions.conf" ] && \
  EXISTING=$(grep -vcE '^[[:space:]]*#|^[[:space:]]*$' "$DATADIR/actions.conf" 2>/dev/null)
# Before v0.9.2 the shipped gain was 31, which on this codec is -40 dB (its
# mute value), not the top. Anything outside the codec's 0-18 range is that
# mistake, so it is corrected rather than kept.
if [ "$EXISTING" -gt 0 ] && grep -qE '^ctl[|]Handset Volume[|](19|2[0-9]|3[0-9]|[4-9][0-9])[[:space:]]*$' "$DATADIR/actions.conf"; then
  sed -i -E 's/^ctl[|]Handset Volume[|][0-9]+[[:space:]]*$/ctl|Handset Volume|0/' "$DATADIR/actions.conf"
  rm -f "$DATADIR"/state/ctl_Handset_Volume*
  ui_print "  earpiece gain corrected: 31 was -40 dB (mute), now 0 = +8 dB"
fi
if [ "$EXISTING" -gt 0 ]; then
  ui_print "  keeping your actions.conf ($EXISTING actions)"
elif [ "$IS_CMF1" = 1 ]; then
  cp -f "$MODPATH/config/actions.cmf1.conf" "$DATADIR/actions.conf"
  ui_print "  installed the CMF Phone 1 routing profile"
else
  cp -f "$MODPATH/config/actions.conf" "$DATADIR/actions.conf"
  ui_print "  installed empty actions.conf (run 'stereoctl probe')"
fi
echo 0 > "$DATADIR/boot_pending"


set_perm_recursive "$MODPATH" 0 0 0755 0644
set_perm_recursive "$MODPATH/scripts" 0 0 0755 0755
set_perm "$MODPATH/system/bin/stereoctl" 0 0 0755
set_perm "$MODPATH/action.sh" 0 0 0755
chmod 0700 "$DATADIR" 2>/dev/null

##############################################################################
# speaker channels
#
# The stereo overlay lives inside the module directory, which an update
# replaces - so a phone that was in stereo is staged again here. Staging
# patches this phone's own vendor files after checking their hashes; on any
# mismatch it refuses and the phone stays on stock mono. This runs after the
# set_perm calls above, which would otherwise relabel the staged vendor files.
##############################################################################
if [ -d /data/adb/modules/cmf_stereo_halpatch_test ]; then
  touch /data/adb/modules/cmf_stereo_halpatch_test/remove
  ui_print "  the pre-release stereo test module will be removed at reboot"
fi
if grep -q "^CHANNELS=stereo" "$DATADIR/stereo.conf" 2>/dev/null; then
  if [ "$IS_CMF1" = 1 ] && WHY=$(MODDIR=$MODPATH DATADIR=$DATADIR sh -c '
        log() { :; }
        . "$MODDIR/scripts/channels.sh"
        stage_stereo'); then
    ui_print "  channels : stereo (left and right follow the screen)"
  else
    sed -i 's/^CHANNELS=.*/CHANNELS=mono/' "$DATADIR/stereo.conf"
    ui_print "  channels : mono - stereo could not be staged:"
    ui_print "             $WHY"
  fi
else
  ui_print "  channels : mono (stock). 'stereoctl channels stereo' for L/R"
fi

##############################################################################
# report what the device can and cannot do
##############################################################################
ui_print " "
set_perm "$MODPATH/bin/tinymix" 0 0 0755

VENDOR_TINYMIX=""
for c in /vendor/bin/tinymix /system/bin/tinymix /odm/bin/tinymix /data/local/tmp/tinymix; do
  [ -x "$c" ] && { VENDOR_TINYMIX=$c; break; }
done
if [ -n "$VENDOR_TINYMIX" ]; then
  ui_print "  tinymix  : $VENDOR_TINYMIX (from the system)"
else
  ui_print "  tinymix  : bundled (this device ships none)"
  ui_print "             static aarch64 build of upstream tinyalsa;"
  ui_print "             provenance in bin/README.md"
fi

ACT=0
[ -f "$DATADIR/actions.conf" ] && ACT=$(grep -vcE '^[[:space:]]*#|^[[:space:]]*$' "$DATADIR/actions.conf" 2>/dev/null)
ui_print "  actions  : $ACT configured"

ui_print " "
if [ "$IS_CMF1" = 1 ] && [ "$EXISTING" -eq 0 ]; then
  ui_print "  Next steps"
  ui_print "  ----------"
  ui_print "  1. reboot"
  ui_print "  2. play something"
  ui_print "  3. stereoctl status   (should show the routing applied)"
  ui_print " "
  ui_print "  Earpiece gain: Handset Volume 0 = +8 dB (loudest),"
  ui_print "  18 = -10 dB. Raise the number in actions.conf for a"
  ui_print "  quieter earpiece; back off at the first buzz."
else
  ui_print "  Next steps"
  ui_print "  ----------"
  ui_print "  1. reboot"
  ui_print "  2. in Termux:  su"
  ui_print "  3.             stereoctl probe"
  ui_print "  4. share the report from /sdcard/cmf-stereo-probe-*"
  ui_print " "
  ui_print "  Until actions.conf has routing in it, this module changes"
  ui_print "  nothing about how your phone sounds."
fi
ui_print " "
