#!/system/bin/sh
# Mono / stereo speaker channels for the CMF Phone 1.
#
# Measured on the device (README, Findings): the speaker amp and the routing
# can carry a separate channel, but two stages fold the speaker to mono:
#
#   1. audio.primary.mt6878.so  AudioALSAPlaybackHandlerBase::
#      doStereoToMonoConversionIfNeed writes (L+R)/2 to both channels when the
#      phone is configured for one speaker;
#   2. Awinic's speaker-protection library on the audio DSP (Aurisys
#      "smartpa_awinic"): one speaker model, so it mixes L+R and protects that.
#
# Stereo mode switches both off and nothing else:
#
#   - the HAL function returns at once (8 bytes), and the DSP task is told the
#     speaker is stereo (hw_info bit 0x4, two branches -> NOP). This exact
#     binary was the one tested;
#   - AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA runs MediaTek's pass-through
#     "aurisys_demo" instead of "smartpa_awinic". aurisys_config_rv.xml already
#     declares aurisys_demo for that scenario (2ch in/out, IV reference), so this
#     is a configuration the vendor file provides, not a new code path.
#     Calls (DSP_CALL_FINAL) keep smartpa_awinic.
#
# Speaker protection on media is then down to the amp's own hardware cut-outs,
# so the daemon also holds a fixed attenuation on the amp (STEREO_ATTEN_DB).
#
# No vendor file ships in this module. The device's own files are patched in
# place, after their hashes prove they are the build that was analysed, and the
# result is hashed again before it is staged. Anything else is refused.
#
# The overlay is mounted at boot, so a change of mode needs a reboot.

HAL_NAMES="audio.primary.mt6878.so audio.primary.mediatek.so"
HAL_DIR=/vendor/lib64/hw
HAL_STOCK=28db2e24e9d4c4f88a67a7631ab581fa064bb03a47a87314b7599a2cb757a324
HAL_STEREO=2615f6e28e40a0520f6122e03513f374294e011fa3c654801e898f5ea62a5edf

AUR=/vendor/etc/aurisys_config_rv.xml
AUR_STOCK=f5818d29d40ce6a5e18765af96ab72a00db8c816e5a0c308c8003eff6e65f2cc
AUR_STEREO=f0f7512085d86e8707131a4e6b3f413d25115c88419c69193493957da4d30ced
# Left behind by the pre-release test module (same swap, no marker comment).
AUR_TEST=b9d136ceea184a7a1dec8b952cf115df7144af8e770930d513eb6df6329ab889
AUR_MARK='cmf_stereo: stereo'

# Where the overlay lives inside the module.
OV_HAL=$MODDIR/system/vendor/lib64/hw
OV_ETC=$MODDIR/system/vendor/etc

_sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }

# Patch a stock HAL copy in place: three spots, 16 bytes.
#   0x27b820 doStereoToMonoConversionIfNeed: mov w0, wzr ; ret
#   0x27f2d4 InitArsiTaskConfig         b.ne -> nop (always set hw_info 0x4)
#   0x1e0a00 SetArsiTaskConfig          b.ne -> nop (same, DSP stream manager)
_patch_hal() {
  printf '\340\003\037\052\300\003\137\326' | dd of="$1" bs=1 seek=2603040 conv=notrunc 2>/dev/null &&
  printf '\037\040\003\325' | dd of="$1" bs=1 seek=2618068 conv=notrunc 2>/dev/null &&
  printf '\037\040\003\325' | dd of="$1" bs=1 seek=1968640 conv=notrunc 2>/dev/null
}

_patch_aurisys() {
  # One library name, in one scenario, plus a marker comment.
  awk -v mark="$AUR_MARK" '
    /<aurisys_config>/ && !m { print; print "    <!-- " mark " (DSP_PLAYBACK_SMARTPA -> aurisys_demo) -->"; m=1; next }
    /aurisys_scenario="AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA"/ { inscn=1 }
    inscn && /<library name="smartpa_awinic"\/>/ { sub(/smartpa_awinic/, "aurisys_demo"); inscn=0 }
    /<\/aurisys_scenario>/ { inscn=0 }
    { print }
  ' "$1" > "$2"
}

# What the running system is using right now (the overlay is mounted at boot).
stereo_active() {
  grep -q "$AUR_MARK" "$AUR" 2>/dev/null
}

stereo_staged() {
  [ -f "$OV_ETC/aurisys_config_rv.xml" ]
}

# stage_stereo -> 0 when the overlay is in place; prints the reason otherwise
stage_stereo() {
  _tmp=$DATADIR/stage.$$
  mkdir -p "$_tmp" || return 1
  _fail=

  for _n in $HAL_NAMES; do
    _src=$HAL_DIR/$_n
    [ -f "$_src" ] || { _fail="$_src missing - not a CMF Phone 1 audio stack"; break; }
    _h=$(_sha "$_src")
    cp -f "$_src" "$_tmp/$_n" || { _fail="cannot copy $_src"; break; }
    case $_h in
      "$HAL_STOCK")  _patch_hal "$_tmp/$_n" || { _fail="patching $_n failed"; break; } ;;
      "$HAL_STEREO") ;;   # already ours (overlay mounted): keep as is
      *) _fail="$_src is not the analysed build ($_h) - refusing to patch an unknown binary"; break ;;
    esac
    [ "$(_sha "$_tmp/$_n")" = "$HAL_STEREO" ] || { _fail="patched $_n does not match the tested binary"; break; }
  done

  if [ -z "$_fail" ]; then
    case $(_sha "$AUR") in
      "$AUR_STOCK"|"$AUR_TEST") _patch_aurisys "$AUR" "$_tmp/aurisys_config_rv.xml" ;;
      "$AUR_STEREO") cp -f "$AUR" "$_tmp/aurisys_config_rv.xml" ;;
      *) _fail="$AUR is not the analysed file - refusing" ;;
    esac
  fi
  [ -z "$_fail" ] && [ "$(_sha "$_tmp/aurisys_config_rv.xml")" != "$AUR_STEREO" ] && \
    _fail="patched aurisys_config_rv.xml does not match the expected result"

  if [ -n "$_fail" ]; then
    rm -rf "$_tmp"
    log warn "stereo: $_fail"
    echo "$_fail"
    return 1
  fi

  mkdir -p "$OV_HAL" "$OV_ETC"
  for _n in $HAL_NAMES; do
    mv -f "$_tmp/$_n" "$OV_HAL/$_n"
    chmod 0644 "$OV_HAL/$_n"
    chcon "$(ls -Z "$HAL_DIR/$_n" | awk '{print $1}')" "$OV_HAL/$_n" 2>/dev/null
  done
  mv -f "$_tmp/aurisys_config_rv.xml" "$OV_ETC/aurisys_config_rv.xml"
  chmod 0644 "$OV_ETC/aurisys_config_rv.xml"
  chcon "$(ls -Z "$AUR" | awk '{print $1}')" "$OV_ETC/aurisys_config_rv.xml" 2>/dev/null
  rm -rf "$_tmp"
  log info "stereo: overlay staged (takes effect after reboot)"
  return 0
}

unstage_stereo() {
  for _n in $HAL_NAMES; do rm -f "$OV_HAL/$_n"; done
  rm -f "$OV_ETC/aurisys_config_rv.xml"
  # Leave system/bin in place: it carries the stereoctl shim.
  rmdir "$OV_HAL" "$MODDIR/system/vendor/lib64" "$OV_ETC" "$MODDIR/system/vendor" 2>/dev/null
  log info "stereo: overlay removed (mono after reboot)"
  return 0
}

##############################################################################
# speaker amp (Awinic aw882xx)
#
# Register 0x06 (I2SCTRL) bits 11:10 select the I2S slot the amp plays:
# 1 left (stock), 2 right, 3 mono = (L+R)/2. The driver rewrites the register
# from its profile on every stream start, so this is re-asserted while
# playing. Written through the driver's own 'reg' attribute.
##############################################################################

AMP_DIR=
amp_dir() {
  [ -n "$AMP_DIR" ] && [ -e "$AMP_DIR/reg" ] && { echo "$AMP_DIR"; return 0; }
  for _d in /sys/bus/i2c/devices/*; do
    [ -e "$_d/dbg_prof" ] && [ -e "$_d/reg" ] && { AMP_DIR=$_d; echo "$_d"; return 0; }
  done
  return 1
}

amp_chsel() {
  # amp_chsel -> left | right | mono | reserved | unknown
  _d=$(amp_dir) || { echo unknown; return 1; }
  _v=$(sed -n 's/^reg:0x06=//p' "$_d/reg" 2>/dev/null)
  [ -n "$_v" ] || { echo unknown; return 1; }
  case $(( (_v >> 10) & 3 )) in
    1) echo left ;; 2) echo right ;; 3) echo mono ;; *) echo reserved ;;
  esac
}

amp_set_chsel() {
  # amp_set_chsel left|right|mono
  case $1 in left) _c=1 ;; right) _c=2 ;; mono) _c=3 ;; *) return 1 ;; esac
  _d=$(amp_dir) || return 1
  _v=$(sed -n 's/^reg:0x06=//p' "$_d/reg" 2>/dev/null)
  [ -n "$_v" ] || return 1
  _new=$(( (_v & 0xF3FF) | (_c << 10) ))
  [ "$_new" -eq $((_v)) ] && return 0
  printf '0x06 0x%04x\n' "$_new" > "$_d/reg" 2>/dev/null || return 1
  log info "amp slot: $(printf '0x%04x' $((_v))) -> $(printf '0x%04x' "$_new") ($1)"
}

# aw_dev_0_volume is an attenuation in 1/8 dB steps (0..720 = 0..90 dB), from
# the aw882xx driver (VOL_STEP_DB = 6 * 8, MUTE_VOL = 90 * 8).
AMP_VOL_CTL=aw_dev_0_volume
amp_atten_steps() {
  _db=${STEREO_ATTEN_DB:-6}
  case $_db in ''|*[!0-9]*) _db=6 ;; esac
  [ "$_db" -gt 30 ] && _db=30
  echo $((_db * 8))
}

# Hold at least the configured attenuation while stereo is active. A larger
# attenuation already set (by the user, or the driver's own monitor) is kept.
amp_hold_atten() {
  _want=$(amp_atten_steps)
  _cur=$(ctl_get "$AMP_VOL_CTL" 2>/dev/null)
  case $_cur in ''|*[!0-9]*) return 1 ;; esac
  _save_original ctl "$AMP_VOL_CTL" "$_cur"
  [ "$_cur" -ge "$_want" ] && return 0
  ctl_set "$AMP_VOL_CTL" "$_want" && log info "amp attenuation: $_cur -> $_want (${STEREO_ATTEN_DB:-6} dB, stereo)"
}

# Back to what the amp had before stereo, once.
amp_release_atten() {
  _orig=$(_original ctl "$AMP_VOL_CTL")
  [ -n "$_orig" ] || return 0
  ctl_set "$AMP_VOL_CTL" "$_orig" && log info "amp attenuation restored to $_orig"
  rm -f "$STATEDIR/$(_state_key ctl "$AMP_VOL_CTL")"
}
