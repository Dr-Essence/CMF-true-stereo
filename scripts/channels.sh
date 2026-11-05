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
# The overlay is mounted at boot. A change of mode is also applied at once
# when it can be (live switching, below): the HAL is restarted on the wanted
# files instead of rebooting the phone.

HAL_NAMES="audio.primary.mt6878.so audio.primary.mediatek.so"
HAL_DIR=/vendor/lib64/hw
HAL_STOCK=28db2e24e9d4c4f88a67a7631ab581fa064bb03a47a87314b7599a2cb757a324
HAL_STEREO=8521fadc4ccb85e3a7f1f001519818f6ece720b22faa03f090826546c43b05dc
# v0.9.9 stereo (swap skipped in Dirac's MUSIC tuning): patched again in place.
HAL_STEREO_V3=c1f3dd1f02bd4afc34ab0dd76f8900ad3577893bfcae8b7f2a3c81946c61bd2c
# v0.9.5-v0.9.8 stereo (skipped the primary output, not Dirac's MUSIC tuning):
# patched again in place, which gives the current one.
HAL_STEREO_V2=58a5755e0203183ad7fa541528305a3040f204e503528ad9182f4118fe1368d9
# v0.9.0-v0.9.4 stereo (no orientation swap): converted on the next staging.
HAL_STEREO_V1=2615f6e28e40a0520f6122e03513f374294e011fa3c654801e898f5ea62a5edf

AUR=/vendor/etc/aurisys_config_rv.xml
AUR_STOCK=f5818d29d40ce6a5e18765af96ab72a00db8c816e5a0c308c8003eff6e65f2cc
AUR_STEREO=f0f7512085d86e8707131a4e6b3f413d25115c88419c69193493957da4d30ced
# Left behind by the pre-release test module (same swap, no marker comment).
AUR_TEST=b9d136ceea184a7a1dec8b952cf115df7144af8e770930d513eb6df6329ab889
AUR_MARK='cmf_stereo: stereo'

# Android's mixer. On this build AudioFlinger has its own speaker swap: at
# rotation 270, for a mixer thread playing to the speaker, it swaps left and
# right itself (a virtual method at 0x144f60 decides, 0x144e10 swaps; made for
# Nothing phones with two speakers, inaudible on this one in mono). It skips
# some apps (VLC and YouTube measured), so with it on no rule in the HAL could
# be right for every app. Stereo switches it off - one branch at 0x144fcc,
# b.ne -> b, so the decision always says "no swap" - and the HAL swap below
# is then the only one, the same for every app. Measured before: the same
# left-only beep came out right only where the HAL did not swap as well.
AF=/system/lib64/libaudioflinger.so
AF_STOCK=813cd2b791ca28970ed3d2e0f585a2817ee8e501aafb9d8eb8f7954e08543ae0
AF_STEREO=60f1d061a133edf2fbda6ad956d3a88034af0be4f2146fff1e84e97df1f5892c
_patch_af()   { printf '\046\000\000\024' | dd of="$1" bs=1 seek=1331148 conv=notrunc 2>/dev/null; }
_unpatch_af() { printf '\301\004\000\124' | dd of="$1" bs=1 seek=1331148 conv=notrunc 2>/dev/null; }

# Where the overlay lives inside the module.
OV_HAL=$MODDIR/system/vendor/lib64/hw
OV_ETC=$MODDIR/system/vendor/etc
OV_AF=$MODDIR/system/lib64

# Every file stereo replaces. _spec NAME sets its path (_dst), its stock and
# stereo hashes (_x, _y) and where the module keeps its stereo copy (_ovd).
STEREO_FILES="$HAL_NAMES aurisys_config_rv.xml libaudioflinger.so"
_spec() {
  case $1 in
    aurisys_config_rv.xml) _dst=$AUR; _x=$AUR_STOCK; _y=$AUR_STEREO; _ovd=$OV_ETC ;;
    libaudioflinger.so)    _dst=$AF;  _x=$AF_STOCK;  _y=$AF_STEREO;  _ovd=$OV_AF ;;
    *)                     _dst=$HAL_DIR/$1; _x=$HAL_STOCK; _y=$HAL_STEREO; _ovd=$OV_HAL ;;
  esac
}

_sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }

# Patch a stock HAL copy in place (444 bytes in four spots):
#   0x27b820 doStereoToMonoConversionIfNeed: replaced by the orientation swap
#            and the rotation store (hal-swap/patch.S, 432 bytes, assembled
#            and tested in an ARM64 emulator: hal-swap/run.sh); swaps left and
#            right for the speaker-only route when the phone is turned with
#            the earpiece on the right (Android's rotation=270), except while
#            Nothing's Dirac is on in its MUSIC tuning, which swaps the
#            stream itself
#   0x2587c0 setParameters, "rotation" key: b to the rotation store, which
#            keeps the value in vendor.audiohal.cmf_rotation (the stock HAL
#            only drops it) and returns
#   0x27f2d4 InitArsiTaskConfig         b.ne -> nop (always set hw_info 0x4)
#   0x1e0a00 SetArsiTaskConfig          b.ne -> nop (same, DSP stream manager)
HAL_SWAP_BODY='\375\173\275\251\375\003\000\221\363\123\001\251\365\023\000\371\363\003\000\252\364\003\001\252\365\003\002\252\150\022\100\371\050\004\000\264\011\251\135\251\113\001\011\313\177\021\000\361\241\003\000\124\053\001\100\271\177\011\000\161\101\003\000\124\140\004\000\020\341\003\037\052\342\213\003\224\037\070\004\161\241\002\000\124\150\022\100\371\010\001\100\271\037\015\000\161\140\001\000\124\037\005\000\161\341\001\000\124\251\376\102\323\251\001\000\264\212\002\100\271\112\101\212\023\212\106\000\270\051\005\000\361\201\377\377\124\007\000\000\024\251\376\103\323\251\000\000\264\212\056\100\051\213\052\201\050\051\005\000\361\241\377\377\124\340\003\037\052\365\023\100\371\363\123\101\251\375\173\303\250\300\003\137\326\341\343\101\371\200\000\000\020\370\235\003\224\001\010\000\320\267\163\377\027\166\145\156\144\157\162\056\141\165\144\151\157\150\141\154\056\143\155\146\137\162\157\164\141\164\151\157\156\000\000\000\000'
# The stock bytes after it, up to the end of the longest earlier body (v0.9.9,
# 432 bytes): written too, so any earlier stereo HAL patches to the same file.
HAL_SWAP_RESTORE='\071\212\003\224\030\001\000\067\051\000\000\024\337\006\000\161\341\004\000\124\370\003\037\052\340\023\100\371\000\377\377\265\170\004\000\064\250\022\100\371\010\001\100\271\037\015\000\161\100\002\000\124\037\005\000\161\241\003\000\124\223\003\000\264\037\040\003\325\210\002\100\171\163\022\000\361\211\006\100\171\010\075\110\013\051\075\111\013\010\075\000\023\051\075\001\023\050\005\210\013\210\002\000\171\210\006\000\171\224\022\000\221\241\376\377\124\016\000\000\024\263\001\000\264\037\040\003\325\037\040\003\325\210\046\100\051\037\001\000\161\010\245\210\032\077\001\000\161\051\245\211\032\163\042\000\361\051\175\001\023\050\005\210\013\210\042\201\050\341\376\377\124\350\026\100\371\251\203\137\370\037\001\011\353\241\002\000\124\340\003\037\052\364\117\107\251'
# b rotcave, written at 0x2587c0 (rotcave sits inside the body above).
HAL_SWAP_B='\106\214\000\024'
_patch_hal() {
  printf "$HAL_SWAP_BODY$HAL_SWAP_RESTORE" | dd of="$1" bs=1 seek=2603040 conv=notrunc 2>/dev/null &&
  printf "$HAL_SWAP_B" | dd of="$1" bs=1 seek=2459584 conv=notrunc 2>/dev/null &&
  printf '\037\040\003\325' | dd of="$1" bs=1 seek=2618068 conv=notrunc 2>/dev/null &&
  printf '\037\040\003\325' | dd of="$1" bs=1 seek=1968640 conv=notrunc 2>/dev/null
}

# The reverse of the v0.9.0-v0.9.4 stereo patch: the stock bytes at its three
# spots (16 bytes). Verified: applied to that build it gives back the stock
# build's exact hash. The current patch is undone from the stock copy instead.
_unpatch_hal_v1() {
  printf '\377\003\002\321\375\173\004\251' | dd of="$1" bs=1 seek=2603040 conv=notrunc 2>/dev/null &&
  printf '\201\000\000\124' | dd of="$1" bs=1 seek=2618068 conv=notrunc 2>/dev/null &&
  printf '\201\000\000\124' | dd of="$1" bs=1 seek=1968640 conv=notrunc 2>/dev/null
}

# The reverse of _patch_aurisys (marker line out, smartpa_awinic back).
_unpatch_aurisys() {
  awk -v mark="$AUR_MARK" '
    index($0, "<!-- " mark " ") { next }
    /aurisys_scenario="AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA"/ { inscn=1 }
    inscn && /<library name="aurisys_demo"\/>/ { sub(/aurisys_demo/, "smartpa_awinic"); inscn=0 }
    /<\/aurisys_scenario>/ { inscn=0 }
    { print }
  ' "$1" > "$2"
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

# A vendor path as init (and so the audio HAL service) sees it. stereoctl can
# run in an app's mount namespace, which does not see a live switch.
LIVE_ROOT=${LIVE_ROOT-/proc/1/root}
_view() {
  if [ -n "$LIVE_ROOT" ] && [ -r "$LIVE_ROOT$1" ]; then echo "$LIVE_ROOT$1"; else echo "$1"; fi
}

# What the running system is using right now.
stereo_active() {
  grep -q "$AUR_MARK" "$(_view "$AUR")" 2>/dev/null
}

stereo_staged() {
  [ -f "$OV_ETC/aurisys_config_rv.xml" ]
}

# Is this phone's audio stack the build the patch was made for?
#   build_known -> 0 yes, 1 a different build (a Nothing OS update), 2 not a
#   CMF Phone 1 audio stack at all.
# Before Magisk mounts (post-fs-data) the files read are the vendor's own, so
# only the stock hashes match there; later the running view may also be our
# stereo files, which are this build too.
build_known() {
  for _n in $HAL_NAMES; do
    _f=$(_view "$HAL_DIR/$_n")
    [ -f "$_f" ] || return 2
    case $(_sha "$_f") in
      "$HAL_STOCK"|"$HAL_STEREO"|"$HAL_STEREO_V3"|"$HAL_STEREO_V2"|"$HAL_STEREO_V1") ;;
      *) return 1 ;;
    esac
  done
  case $(_sha "$(_view "$AF")") in
    "$AF_STOCK"|"$AF_STEREO") ;;
    *) return 1 ;;
  esac
  case $(_sha "$(_view "$AUR")") in
    "$AUR_STOCK"|"$AUR_STEREO"|"$AUR_TEST") return 0 ;;
  esac
  return 1
}

# The answer for this boot, kept for the status and the Magisk description:
# known | updated | absent.
BUILD_STATE=$DATADIR/build_state
build_check() {
  build_known
  case $? in 0) _b=known ;; 2) _b=absent ;; *) _b=updated ;; esac
  echo "$_b" > "$BUILD_STATE"
  echo "$_b"
}
build_state() {
  _b=$(cat "$BUILD_STATE" 2>/dev/null)
  echo "${_b:-known}"
}

# stage_stereo -> 0 when the overlay is in place; prints the reason otherwise
stage_stereo() {
  _tmp=$DATADIR/stage.$$
  mkdir -p "$_tmp" || return 1
  _fail=

  for _n in $HAL_NAMES; do
    _src=$HAL_DIR/$_n
    [ -f "$_src" ] || { _fail="$_src missing - not a CMF Phone 1 audio stack"; break; }
    # A checked stock copy is the best source: it patches into this build from
    # whatever stereo build is running now.
    [ "$(_sha "$STOCKDIR/$_n")" = "$HAL_STOCK" ] && _src=$STOCKDIR/$_n
    _h=$(_sha "$_src")
    cp -f "$_src" "$_tmp/$_n" || { _fail="cannot copy $_src"; break; }
    case $_h in
      "$HAL_STOCK")  _patch_hal "$_tmp/$_n" || { _fail="patching $_n failed"; break; } ;;
      "$HAL_STEREO") ;;   # already ours (overlay mounted): keep as is
      "$HAL_STEREO_V2"|"$HAL_STEREO_V3")   # v0.9.5-v0.9.9: same spots, the patch rewrites them all
        _patch_hal "$_tmp/$_n" || { _fail="converting the earlier stereo $_n failed"; break; } ;;
      "$HAL_STEREO_V1")   # the earlier stereo build: back to stock, then patch
        { _unpatch_hal_v1 "$_tmp/$_n" && [ "$(_sha "$_tmp/$_n")" = "$HAL_STOCK" ] && _patch_hal "$_tmp/$_n"; } ||
          { _fail="converting the earlier stereo $_n failed"; break; } ;;
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

  # The mixer, from a checked stock copy when there is one.
  if [ -z "$_fail" ]; then
    _src=$AF
    [ "$(_sha "$STOCKDIR/libaudioflinger.so")" = "$AF_STOCK" ] && _src=$STOCKDIR/libaudioflinger.so
    cp -f "$_src" "$_tmp/libaudioflinger.so" || _fail="cannot copy $_src"
  fi
  if [ -z "$_fail" ]; then
    case $(_sha "$_tmp/libaudioflinger.so") in
      "$AF_STOCK") _patch_af "$_tmp/libaudioflinger.so" ;;
      "$AF_STEREO") ;;
      *) _fail="$AF is not the analysed build - refusing" ;;
    esac
    [ -z "$_fail" ] && [ "$(_sha "$_tmp/libaudioflinger.so")" != "$AF_STEREO" ] && \
      _fail="patched libaudioflinger.so does not match the expected result"
  fi

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
  mkdir -p "$OV_AF"
  mv -f "$_tmp/libaudioflinger.so" "$OV_AF/libaudioflinger.so"
  chmod 0644 "$OV_AF/libaudioflinger.so"
  chcon "$(ls -Z "$AF" | awk '{print $1}')" "$OV_AF/libaudioflinger.so" 2>/dev/null
  rm -rf "$_tmp"
  log info "stereo: overlay staged (takes effect after reboot)"
  return 0
}

unstage_stereo() {
  for _n in $HAL_NAMES; do rm -f "$OV_HAL/$_n"; done
  rm -f "$OV_ETC/aurisys_config_rv.xml" "$OV_AF/libaudioflinger.so"
  # Leave system/bin in place: it carries the stereoctl shim.
  rmdir "$OV_HAL" "$MODDIR/system/vendor/lib64" "$OV_ETC" "$MODDIR/system/vendor" "$OV_AF" 2>/dev/null
  log info "stereo: overlay removed (mono after reboot)"
  return 0
}

##############################################################################
# Live switching (no reboot)
#
# Measured on the CMF Phone 1: `setprop ctl.restart vendor.audio-hal` brings
# the HAL back within seconds, audioserver reconnects on its own and calls
# work; players pause and need play again. So a mode change mounts the wanted
# files over the vendor paths and restarts the HAL instead of the phone.
#
# Magisk mounts each of this module's files over its vendor path at boot, in
# init's mount namespace, which the HAL service shares (measured: same mnt
# namespace id). A live switch takes our own mounts off (never anyone else's)
# and mounts what the wanted mode still needs: nothing for mono (the vendor
# files are stock), the staged files for stereo. Where the vendor view is not
# stock without our mounts (a root manager that mounts differently), a
# hash-checked copy of the stock files is mounted instead. Every file is read
# back through /proc/1/root against the expected hash; anything that does not
# check out ends on the stock files, and the change waits for a reboot.
##############################################################################

STOCKDIR=$DATADIR/stock
HAL_SVC=vendor.audio-hal

# Run a command in init's mount namespace.
_global() {
  if [ -z "$LIVE_ROOT" ] || \
     [ "$(readlink /proc/self/ns/mnt 2>/dev/null)" = "$(readlink /proc/1/ns/mnt 2>/dev/null)" ]; then
    "$@"
  else
    nsenter -t 1 -m -- "$@"
  fi
}

# Keep a copy of the phone's own stock files, for switching back to mono live.
# From a mono boot they are copied; from a stereo boot they are rebuilt from
# the stereo files by putting the original bytes back. Either way a copy is
# kept only when it hashes to the analysed stock build.
save_stock() {
  mkdir -p "$STOCKDIR" || return 1
  # The mixer first: a HAL that cannot be rebuilt must not stop its copy.
  for _n in libaudioflinger.so $HAL_NAMES aurisys_config_rv.xml; do
    _spec "$_n"; _src=$(_view "$_dst")
    _t=$STOCKDIR/$_n
    [ "$(_sha "$_t")" = "$_x" ] && continue
    case $(_sha "$_src") in
      "$_x") cp -f "$_src" "$_t.tmp" || return 1 ;;
      "$_y"|"$HAL_STEREO_V1")
        case $_n in
          aurisys_config_rv.xml) _unpatch_aurisys "$_src" "$_t.tmp" || return 1 ;;
          libaudioflinger.so) cp -f "$_src" "$_t.tmp" && _unpatch_af "$_t.tmp" || return 1 ;;
          *) cp -f "$_src" "$_t.tmp" && _unpatch_hal_v1 "$_t.tmp" || return 1 ;;
        esac ;;
      *) return 1 ;;
    esac
    [ "$(_sha "$_t.tmp")" = "$_x" ] || { rm -f "$_t.tmp"; return 1; }
    mv -f "$_t.tmp" "$_t"
    chmod 0644 "$_t"
    chcon "$(ls -Z "$_src" | awk '{print $1}')" "$_t" 2>/dev/null
  done
  return 0
}

# Mounts of ours over a vendor path, in init's (and the HAL's) namespace: the
# root manager's boot mount of this module's files, and live-switch mounts of
# the stock copies. Magisk bind-mounts each file, so these can be taken off
# one by one; only a topmost mount whose source is ours is ever touched.
MOUNTINFO=${MOUNTINFO:-/proc/1/mountinfo}
OUR_MOUNTS=${OUR_MOUNTS:-/adb/modules/cmf_stereo/|/adb/cmf-stereo/}

_top_is_ours() {
  _r=$(awk -v mp="$1" '$5 == mp { r = $4 } END { print r }' "$MOUNTINFO" 2>/dev/null)
  [ -n "$_r" ] && echo "$_r" | grep -qE "$OUR_MOUNTS"
}

# Take our mounts off <path>, topmost first. Lazy: the running HAL still maps
# the library; the mount goes when it lets go (at the restart that follows).
# Fails when a mount that is not ours is left on <path> (on top of ours, or
# under it): the vendor file itself is never a mount of its own.
_peel() {
  _k=0
  while [ $_k -lt 6 ] && _top_is_ours "$1"; do
    _global umount -l "$1" 2>/dev/null || return 1
    _k=$((_k + 1))
  done
  ! awk -v mp="$1" '$5 == mp { f = 1 } END { exit !f }' "$MOUNTINFO" 2>/dev/null
}

live_unmount() {
  _ok=0
  for _n in $STEREO_FILES; do _spec "$_n"; _peel "$_dst" || _ok=1; done
  return $_ok
}

in_call() {
  dumpsys telephony.registry 2>/dev/null | grep -q 'mCallState=[12]'
}

# Restart the audio HAL and wait for a new process that stays up.
# audioserver and the audio HAL, together. libaudioflinger.so is loaded by
# audioserver, and init restarts the HAL with it (audioserver.rc onrestart,
# measured in the phone's log), so one restart brings both up on the files
# mounted now. Measured with the HAL alone: back within seconds, players
# pause, calls work.
AS_SVC=audioserver
hal_restart() {
  _oh=$(getprop "init.svc_debug_pid.$HAL_SVC")
  _oa=$(getprop "init.svc_debug_pid.$AS_SVC")
  setprop ctl.restart "$AS_SVC" || return 1
  _w=0; _nh=; _na=
  while [ $_w -lt 100 ]; do
    tick; _w=$((_w + 1))
    _nh=$(getprop "init.svc_debug_pid.$HAL_SVC")
    _na=$(getprop "init.svc_debug_pid.$AS_SVC")
    [ "$(getprop "init.svc.$HAL_SVC")" = running ] && [ "$(getprop "init.svc.$AS_SVC")" = running ] &&
      [ -n "$_nh" ] && [ "$_nh" != "$_oh" ] && [ -n "$_na" ] && [ "$_na" != "$_oa" ] && break
  done
  [ $_w -lt 100 ] || return 1
  # Still the same processes 3 s later: neither is crash-looping.
  _w=0; while [ $_w -lt 30 ]; do tick; _w=$((_w + 1)); done
  [ "$(getprop "init.svc.$HAL_SVC")" = running ] && [ "$(getprop "init.svc_debug_pid.$HAL_SVC")" = "$_nh" ] &&
    [ "$(getprop "init.svc.$AS_SVC")" = running ] && [ "$(getprop "init.svc_debug_pid.$AS_SVC")" = "$_na" ]
}

# live_switch mono|stereo -> 0 when the running system now uses that mode;
# prints the reason otherwise (and leaves the system as it was).
# After a failed switch: back to stock, proven, before the HAL restarts.
# Without our mounts the vendor path is not always stock: Magisk 31 builds
# /vendor/lib64/hw as a tmpfs skeleton whose replaced files are EMPTY
# placeholders under the module's bind mounts (measured). The checked stock
# copies go over whatever does not read back as stock. The HAL is restarted
# only when all three files are proven stock; otherwise it is left running
# (it already has its files loaded) and a reboot puts everything back.
# Restarting it on empty files had it and audioserver crash-looping.
_stock_ok() {
  for _n in $STEREO_FILES; do
    _spec "$_n"
    [ "$(_sha "$(_view "$_dst")")" = "$_x" ] || return 1
  done
}
_live_fallback() {
  live_unmount
  for _n in $STEREO_FILES; do
    _spec "$_n"
    [ "$(_sha "$(_view "$_dst")")" = "$_x" ] && continue
    [ "$(_sha "$STOCKDIR/$_n")" = "$_x" ] && _global mount -o bind "$STOCKDIR/$_n" "$_dst"
  done
  if _stock_ok; then
    hal_restart
    log warn "$1 - back on the stock files"
  else
    log warn "$1 - the stock files could not be put back; the audio services were left running: reboot"
  fi
}

live_switch() {
  case $1 in stereo|mono) ;; *) echo "unknown mode $1"; return 1 ;; esac
  # The audio services loaded their files when they last started, so they
  # run what the system shows now; nothing to do if that is already the
  # wanted mode - for every file (an earlier stereo build, or one without
  # the mixer patch, is replaced live too).
  _now=$1
  for _n in $STEREO_FILES; do
    _spec "$_n"; [ "$1" = stereo ] && _x=$_y
    [ "$(_sha "$(_view "$_dst")")" = "$_x" ] || { _now=other; break; }
  done
  [ "$_now" = "$1" ] && { echo unchanged; return 0; }
  if in_call; then echo "a call is active"; return 1; fi
  # Stereo always mounts the staged files: check them before touching anything.
  if [ "$1" = stereo ]; then
    for _n in $STEREO_FILES; do
      _spec "$_n"
      [ "$(_sha "$_ovd/$_n")" = "$_y" ] || { echo "no verified $1 copy of $_n"; return 1; }
    done
  fi

  case $MODDIR$STOCKDIR in /*) ;; *) echo "internal: the module folder is not an absolute path"; return 1 ;; esac

  # Down to the system's own files, then mount what is still needed.
  live_unmount || { echo "a mount over the audio files is not ours - not touching it"; return 1; }
  _fail=
  for _n in $STEREO_FILES; do
    _spec "$_n"
    if [ "$1" = stereo ]; then _src=$_ovd/$_n; _x=$_y; else _src=$STOCKDIR/$_n; fi
    [ "$(_sha "$(_view "$_dst")")" = "$_x" ] && continue
    # Mono lands here only when the system file is not stock without our
    # mounts (Magisk's skeleton placeholders): use the checked copy.
    [ "$(_sha "$_src")" = "$_x" ] || { _fail="no verified $1 copy of ${_dst##*/}"; break; }
    _global mount -o bind "$_src" "$_dst" || { _fail="cannot mount over $_dst"; break; }
    [ "$(_sha "$(_view "$_dst")")" = "$_x" ] || { _fail="$_dst does not read back as the $1 file"; break; }
  done
  if [ -n "$_fail" ]; then
    _live_fallback "live $1: $_fail"
    echo "$_fail"
    return 1
  fi
  if ! hal_restart; then
    _live_fallback "live $1: the audio services did not come back"
    echo "the audio services did not come back on the $1 files"
    return 1
  fi
  log info "live $1: applied (audio services restarted)"
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
