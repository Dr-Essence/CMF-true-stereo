#!/usr/bin/env sh
# Off-device checks for the parts that do not need Android: the action engine,
# the XML structural validator, and the speaker-port rewrite.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$HERE")
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); echo "  ok   - $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  FAIL - $1"; }
check(){ if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (want '$3', got '$2')"; fi; }

export DATADIR="$TMP/data" MODDIR="$ROOT"
mkdir -p "$DATADIR/state"
. "$ROOT/scripts/common.sh"

echo "action engine"
# sysfs actions stand in for mixer controls: same save/apply/revert path.
mkdir -p "$TMP/sys"
echo 0 > "$TMP/sys/rcv_switch"
echo 3 > "$TMP/sys/rcv_gain"
cat > "$ACTIONS" <<CONF
# comment line, ignored
ctl|Nonexistent Control|1
sysfs|$TMP/sys/rcv_switch|1
sysfs|$TMP/sys/rcv_gain|7
sysfs|$TMP/sys/not_there|1
CONF
check "action_count skips comments and blanks" "$(action_count)" "4"
apply_actions
check "sysfs switch applied"   "$(cat "$TMP/sys/rcv_switch")" "1"
check "sysfs gain applied"     "$(cat "$TMP/sys/rcv_gain")"   "7"
check "original switch saved"  "$(_original sysfs "$TMP/sys/rcv_switch")" "0"
check "original gain saved"    "$(_original sysfs "$TMP/sys/rcv_gain")"   "3"

# A second apply must not overwrite the saved originals with our own values.
apply_actions
check "original survives re-apply" "$(_original sysfs "$TMP/sys/rcv_gain")" "3"

revert_actions
check "sysfs switch reverted" "$(cat "$TMP/sys/rcv_switch")" "0"
check "sysfs gain reverted"   "$(cat "$TMP/sys/rcv_gain")"   "3"

echo "kill switch"
check "armed by default" "$(module_active && echo yes || echo no)" "yes"
touch "$KILLSWITCH"
check "disarmed by killswitch" "$(module_active && echo yes || echo no)" "no"
rm -f "$KILLSWITCH"

echo "boot watchdog"
boot_strike_clear
boot_strike_add; boot_strike_add
check "strikes counted" "$(boot_strikes)" "2"
boot_strike_clear
check "strikes cleared" "$(boot_strikes)" "0"

echo "value normalisation"
mkdir -p "$TMP/bin"
export STUBLOG="$TMP/stub.log"
# Formats taken verbatim from tinymix on the CMF Phone 1.
check "enum -> selected entry" \
  "$(ctl_normalize 'Open, Mute, > Voice Playback, Test Mode,')" "Voice Playback"
check "enum, first entry selected" \
  "$(ctl_normalize '> Open, Mute, Voice Playback, Test Mode,')" "Open"
check "enum with underscores" \
  "$(ctl_normalize 'Disable, > Enable,')" "Enable"
# The range suffix contains "->", which must not be mistaken for an enum marker.
check "int -> bare number" "$(ctl_normalize '31 (range 0->18)')" "31"
check "int, zero"          "$(ctl_normalize '0 (range 0->65535)')" "0"
check "int, negative"      "$(ctl_normalize '-1 (range -2147483648->0)')" "-1"
check "bool On -> 1"       "$(ctl_normalize 'On')"  "1"
check "bool Off -> 0"      "$(ctl_normalize 'Off')" "0"
check "plain value passes through" "$(ctl_normalize '42')" "42"

# Round trip: what ctl_get returns must be accepted by ctl_set.
: > "$STUBLOG"
cat > "$TMP/bin/tinymix-fmt" <<'STUB'
#!/bin/sh
case "$1" in
  --help|-h) printf 'commands:\n\tget NAME|ID : x\n\tset NAME|ID VALUE : x\n'; exit 0 ;;
  get)
    case "$2" in
      'RCV Mux')                  echo 'Open, Mute, > Voice Playback, Test Mode,' ;;
      'Handset Volume')           echo '31 (range 0->18)' ;;
      'ADDA_DL_CH1 DL_24CH_CH1')  echo 'Off' ;;
      # Real tinymix errors out on an unknown control rather than
      # answering with a value.
      *) echo 'Invalid mixer control' >&2; exit 1 ;;
    esac
    exit 0 ;;
  set) echo "CALLED:set:$2:$3" >> "$STUBLOG"; exit 0 ;;
esac
exit 1
STUB
chmod +x "$TMP/bin/tinymix-fmt"
TINYMIX="$TMP/bin/tinymix-fmt"; unset TINYMIX_STYLE; MIXER_CARD=
check "enum round trip"  "$(ctl_get 'RCV Mux')" "Voice Playback"
check "int round trip"   "$(ctl_get 'Handset Volume')" "31"
check "bool round trip"  "$(ctl_get 'ADDA_DL_CH1 DL_24CH_CH1')" "0"
ctl_set 'RCV Mux' "$(ctl_get 'RCV Mux')"
check "revert sets a bare enum name" \
  "$(grep -c '^CALLED:set:RCV Mux:Voice Playback$' "$STUBLOG")" "1"
ctl_set 'Handset Volume' "$(ctl_get 'Handset Volume')"
check "revert sets a bare integer" \
  "$(grep -c '^CALLED:set:Handset Volume:31$' "$STUBLOG")" "1"
unset TINYMIX TINYMIX_STYLE

echo "no unbounded reads in the scripts"
# /proc/kmsg is a stream: cat on it never returns. A probe that hangs looks
# identical to a slow one, and cost four minutes of someone staring at a
# spinner before it was found.
KMSG=$(grep -c 'cat /proc/kmsg' "$ROOT"/scripts/* 2>/dev/null | grep -v ':0$' | wc -l | tr -d ' ')
check "nothing cats /proc/kmsg" "$KMSG" "0"
check "dmesg is bounded by timeout" \
  "$(grep -c 'timeout [0-9]* dmesg' "$ROOT/scripts/probe.sh")" "1"

echo "playback detection"
TINYMIX="$TMP/bin/tinymix-fmt"; unset TINYMIX_STYLE
# The stub answers 'Off' -> normalised 0 for any control it does not know.
PLAYBACK_CTL='ADDA_DL_CH1 DL_24CH_CH1'; PLAYBACK_VALUE=1
check "mixer says not playing"  "$(playback_active && echo yes || echo no)" "no"
PLAYBACK_VALUE=0
check "mixer says playing"      "$(playback_active && echo yes || echo no)" "yes"
check "detector names the control" \
  "$(playback_detector | grep -c "ADDA_DL_CH1")" "1"
# A control that does not exist must not pin playback to "never".
PLAYBACK_CTL='No Such Control'; PLAYBACK_VALUE=1
check "missing control falls back to procfs" \
  "$(playback_detector)" "procfs substream scan"
PLAYBACK_CTL=; PLAYBACK_VALUE=1
check "no control configured -> procfs" \
  "$(playback_detector)" "procfs substream scan"
unset TINYMIX TINYMIX_STYLE

echo "guard control"
TINYMIX="$TMP/bin/tinymix-fmt"; unset TINYMIX_STYLE
GUARD_CTL=; GUARD_VALUE=
check "no guard configured -> always ok" "$(guard_ok && echo yes || echo no)" "yes"
GUARD_CTL='RCV Mux'; GUARD_VALUE='Voice Playback'
check "guard matches -> ok"      "$(guard_ok && echo yes || echo no)" "yes"
GUARD_VALUE='Open'
check "guard differs -> blocked" "$(guard_ok && echo yes || echo no)" "no"
GUARD_CTL='No Such Control'; GUARD_VALUE='Enable'
check "missing guard control does not block" "$(guard_ok && echo yes || echo no)" "yes"
GUARD_CTL='RCV Mux'; GUARD_VALUE='Open'
check "guard blocks before bypass" "$(guard_ok && echo yes || echo no)" "no"
touch "$DATADIR/guard_bypass"
check "bypass overrides a failing guard" "$(guard_ok && echo yes || echo no)" "yes"
rm -f "$DATADIR/guard_bypass"
check "bypass removed -> blocked again" "$(guard_ok && echo yes || echo no)" "no"
GUARD_CTL=; GUARD_VALUE=; unset TINYMIX TINYMIX_STYLE

echo "mixer snapshot diff"
cat > "$TMP/snap.a" <<'SNAP'
664	BOOL	1	Ext_Speaker_Amp Switch	Off
670	ENUM	1	HPL Mux	>Open, Audio Playback,
672	ENUM	1	RCV Mux	>Open, Voice Playback,
560	INT	1	Handset Volume	4
SNAP
cat > "$TMP/snap.b" <<'SNAP'
664	BOOL	1	Ext_Speaker_Amp Switch	On
670	ENUM	1	HPL Mux	>Open, Audio Playback,
672	ENUM	1	RCV Mux	Open, >Voice Playback,
560	INT	1	Handset Volume	4
SNAP
OUT=$(diff_snapshots "$TMP/snap.a" "$TMP/snap.b")
check "reports the changed switch"  "$(echo "$OUT" | grep -c 'Ext_Speaker_Amp Switch')" "2"
check "reports the changed mux"     "$(echo "$OUT" | grep -c 'RCV Mux')" "2"
check "ignores unchanged controls"  "$(echo "$OUT" | grep -c 'Handset Volume')" "0"
check "ignores unchanged mux"       "$(echo "$OUT" | grep -c 'HPL Mux')" "0"
OUT=$(diff_snapshots "$TMP/snap.a" "$TMP/snap.a")
check "identical snapshots are quiet" "$(echo "$OUT" | grep -c 'no control changed')" "1"

echo "portability lint"
# Android's grep is toybox: it treats \| in a basic regex as a literal, so
# every pattern written that way matches nothing and reports it as a clean
# zero. This cost a full probe cycle - three "0 hits" summary lines that were
# the greps failing, not the hardware missing. Alternation must use -E.
BRE=$(grep -n 'grep' "$ROOT"/scripts/* "$ROOT"/customize.sh "$ROOT"/service.sh \
        "$ROOT"/post-fs-data.sh "$ROOT"/uninstall.sh 2>/dev/null \
        | grep -c '\\|' )
check "no BRE alternation in any grep" "$BRE" "0"

echo "tinymix CLI detection"
# Stubs standing in for the two calling conventions. The new-style help text
# is copied from tinyalsa 2.x (tab-indented, which is what made the first
# detection attempt fail); the old one from tinyalsa 1.x.
mkdir -p "$TMP/bin"
cat > "$TMP/bin/tinymix-new" <<'STUB'
#!/bin/sh
case "$1" in
  --help|-h)
    printf 'usage: tinymix [options] <command>\noptions:\n\t-h, --help : help\ncommands:\n\tget NAME|ID              : prints the values of a control\n\tset NAME|ID VALUE(S) ... : sets the value of a control\n'
    exit 0 ;;
  get)
    [ -z "${2:-}" ] && { echo "no control specified" >&2; exit 1; }
    echo "CALLED:get:$2" >> "$STUBLOG"; echo 7; exit 0 ;;
  set)
    echo "CALLED:set:$2:$3" >> "$STUBLOG"; exit 0 ;;
esac
exit 1
STUB
cat > "$TMP/bin/tinymix-old" <<'STUB'
#!/bin/sh
case "$1" in
  --help|-h) echo "Usage: tinymix [-D card] [-a] [ctrl id/name [value(s)]]"; exit 0 ;;
esac
if [ $# -eq 2 ]; then echo "CALLED:set:$1:$2" >> "$STUBLOG"; exit 0; fi
if [ $# -eq 1 ]; then echo "CALLED:get:$1" >> "$STUBLOG"; echo "Mixer name: stub"; echo 7; exit 0; fi
exit 1
STUB
chmod +x "$TMP/bin/tinymix-new" "$TMP/bin/tinymix-old"

TINYMIX="$TMP/bin/tinymix-new"; unset TINYMIX_STYLE
check "tinyalsa 2.x detected as new" "$(tinymix_style)" "new"
TINYMIX="$TMP/bin/tinymix-old"; unset TINYMIX_STYLE
check "tinyalsa 1.x detected as old" "$(tinymix_style)" "old"

# The style must translate into the right argv, or writes silently do nothing.
: > "$STUBLOG"
TINYMIX="$TMP/bin/tinymix-new"; unset TINYMIX_STYLE; MIXER_CARD=
check "new-style get value" "$(ctl_get 'Receiver Switch')" "7"
ctl_set 'Receiver Switch' 1
check "new-style set argv" "$(grep -c '^CALLED:set:Receiver Switch:1$' "$STUBLOG")" "1"

: > "$STUBLOG"
TINYMIX="$TMP/bin/tinymix-old"; unset TINYMIX_STYLE
check "old-style get strips header" "$(ctl_get 'Receiver Switch')" "7"
ctl_set 'Receiver Switch' 1
check "old-style set argv" "$(grep -c '^CALLED:set:Receiver Switch:1$' "$STUBLOG")" "1"
# A binary that cannot execute at all (wrong arch) must not be mistaken for
# the 1.x CLI - that would make every write a silent no-op.
cat > "$TMP/bin/tinymix-broken" <<'STUB'
#!/bin/sh
exit 126
STUB
chmod +x "$TMP/bin/tinymix-broken"
TINYMIX="$TMP/bin/tinymix-broken"; unset TINYMIX_STYLE
check "unrunnable binary reported unknown" "$(tinymix_style)" "unknown"
unset TINYMIX_STYLE
ctl_set 'Receiver Switch' 1 2>/dev/null
check "unknown style refuses to write" "$?" "1"
unset TINYMIX TINYMIX_STYLE

echo "xml validation"
cat > "$TMP/good.xml" <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<audioPolicyConfiguration version="7.0">
  <modules>
    <module name="primary" halVersion="3.0">
      <mixPorts>
        <mixPort name="primary output" role="source" flags="AUDIO_OUTPUT_FLAG_PRIMARY">
          <profile name="" format="AUDIO_FORMAT_PCM_16_BIT" samplingRates="44100 48000" channelMasks="AUDIO_CHANNEL_OUT_STEREO"/>
        </mixPort>
      </mixPorts>
      <devicePorts>
        <devicePort tagName="Speaker" type="AUDIO_DEVICE_OUT_SPEAKER" role="sink">
          <profile name="" format="AUDIO_FORMAT_PCM_16_BIT" samplingRates="44100 48000" channelMasks="AUDIO_CHANNEL_OUT_MONO"/>
        </devicePort>
        <devicePort tagName="Earpiece" type="AUDIO_DEVICE_OUT_EARPIECE" role="sink">
          <profile name="" format="AUDIO_FORMAT_PCM_16_BIT" samplingRates="44100 48000" channelMasks="AUDIO_CHANNEL_OUT_MONO"/>
        </devicePort>
      </devicePorts>
      <routes>
        <route type="mix" sink="Speaker" sources="primary output"/>
      </routes>
    </module>
  </modules>
</audioPolicyConfiguration>
XML
xml_sane "$TMP/good.xml" >/dev/null 2>&1
check "well-formed policy accepted" "$?" "0"

# The exact failure the Hi-Res module produces: a mixPort inserted at a
# hardcoded line number, landing inside another element and never closed.
sed '7i\        <mixPort name="mmap_no_irq_out" role="source">' "$TMP/good.xml" > "$TMP/bad.xml"
xml_sane "$TMP/bad.xml" >/dev/null 2>&1
check "unbalanced mixPort rejected" "$?" "1"

head -n 12 "$TMP/good.xml" > "$TMP/trunc.xml"
xml_sane "$TMP/trunc.xml" >/dev/null 2>&1
check "truncated policy rejected" "$?" "1"

echo "speaker port rewrite"
# Reuse the real patch_one from xml_patch.sh rather than a copy of the awk.
XML_PATCH_LIB=1 . "$ROOT/scripts/xml_patch.sh"
patch_one "$TMP/good.xml" "$TMP/patched.xml"
check "patch_one succeeded" "$?" "0"
check "speaker port widened to stereo" \
  "$(sed -n '/tagName="Speaker"/,/<\/devicePort>/p' "$TMP/patched.xml" | grep -c AUDIO_CHANNEL_OUT_STEREO)" "1"
check "earpiece port left alone" \
  "$(sed -n '/tagName="Earpiece"/,/<\/devicePort>/p' "$TMP/patched.xml" | grep -c AUDIO_CHANNEL_OUT_MONO)" "1"
check "devicePorts container preserved" \
  "$(grep -c '<devicePorts>' "$TMP/patched.xml")" "1"
check "mixPort left alone" "$(grep -c 'name="primary output"' "$TMP/patched.xml")" "1"
xml_sane "$TMP/patched.xml" >/dev/null 2>&1
check "patched policy still valid" "$?" "0"
check "line count unchanged" \
  "$(wc -l < "$TMP/patched.xml")" "$(wc -l < "$TMP/good.xml")"

# A speaker port written as a single self-closing element must also work.
cat > "$TMP/selfclose.xml" <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<audioPolicyConfiguration version="7.0">
  <modules>
    <module name="primary" halVersion="3.0">
      <devicePorts>
        <devicePort tagName="Speaker" type="AUDIO_DEVICE_OUT_SPEAKER" role="sink" channelMasks="AUDIO_CHANNEL_OUT_MONO"/>
        <devicePort tagName="Earpiece" type="AUDIO_DEVICE_OUT_EARPIECE" role="sink" channelMasks="AUDIO_CHANNEL_OUT_MONO"/>
      </devicePorts>
    </module>
  </modules>
</audioPolicyConfiguration>
XML
patch_one "$TMP/selfclose.xml" "$TMP/selfclose-out.xml"
check "self-closing speaker port patched" "$?" "0"
check "self-closing speaker now stereo" \
  "$(grep -c 'tagName="Speaker".*AUDIO_CHANNEL_OUT_STEREO' "$TMP/selfclose-out.xml")" "1"
check "self-closing earpiece untouched" \
  "$(grep -c 'tagName="Earpiece".*AUDIO_CHANNEL_OUT_MONO' "$TMP/selfclose-out.xml")" "1"
check "self-closing line count unchanged" \
  "$(wc -l < "$TMP/selfclose-out.xml")" "$(wc -l < "$TMP/selfclose.xml")"

# A policy with no speaker devicePort must be refused, not silently copied.
grep -v 'AUDIO_DEVICE_OUT_SPEAKER' "$TMP/good.xml" > "$TMP/nospk.xml"
patch_one "$TMP/nospk.xml" "$TMP/nospk-out.xml" 2>/dev/null
check "no speaker port -> refused" "$?" "3"
check "no output file left behind" "$([ -f "$TMP/nospk-out.xml" ] && echo yes || echo no)" "no"

echo "speaker channels"
# The aurisys rewrite: one library, in one scenario, plus the marker.
cat > "$TMP/aur.xml" <<'XML'
<?xml version="1.0" encoding="UTF-8" ?>
<aurisys_config>
    <aurisys_scenarios>
        <aurisys_scenario aurisys_scenario="AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA">
            <downlink_library_name_list digital_gain_lib_name="">
                <library name="smartpa_awinic"/>
            </downlink_library_name_list>
        </aurisys_scenario>
        <aurisys_scenario aurisys_scenario="AURISYS_SCENARIO_DSP_CALL_FINAL">
            <downlink_library_name_list digital_gain_lib_name="">
                <library name="smartpa_awinic"/>
            </downlink_library_name_list>
        </aurisys_scenario>
    </aurisys_scenarios>
</aurisys_config>
XML
_patch_aurisys "$TMP/aur.xml" "$TMP/aur-out.xml"
check "playback scenario -> aurisys_demo" \
  "$(sed -n '/aurisys_scenario="AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA"/,/<\/aurisys_scenario>/p' "$TMP/aur-out.xml" | grep -c '<library name="aurisys_demo"/>')" "1"
check "call scenario keeps smartpa_awinic" \
  "$(sed -n '/DSP_CALL_FINAL/,/<\/aurisys_scenario>/p' "$TMP/aur-out.xml" | grep -c 'smartpa_awinic')" "1"
check "marker added once" "$(grep -c "$AUR_MARK" "$TMP/aur-out.xml")" "1"
check "nothing else changed" "$(($(wc -l < "$TMP/aur-out.xml") - $(wc -l < "$TMP/aur.xml")))" "1"
AUR=$TMP/aur-out.xml
check "stereo detected from the marker" "$(stereo_active && echo yes || echo no)" "yes"
AUR=$TMP/aur.xml
check "stock reads as mono" "$(stereo_active && echo yes || echo no)" "no"

# Amp slot: read-modify-write of bits 11:10 only, through a fake 'reg' node
# that behaves like the driver's (show: all registers, store: "reg val").
mkdir -p "$TMP/amp"
: > "$TMP/amp/dbg_prof"
AMP_DIR=$TMP/amp
printf 'reg:0x05=0x0000\nreg:0x06=0x34e8\nreg:0x07=0x0040\n' > "$TMP/amp/reg"
check "stock slot reads left" "$(amp_chsel)" "left"
# The real node takes "0x06 0x38e8"; the fake file just records the write.
amp_set_chsel right
check "right writes bits 11:10 = 10" "$(cat "$TMP/amp/reg")" "0x06 0x38e8"
printf 'reg:0x06=0x38e8\n' > "$TMP/amp/reg"
check "right reads back" "$(amp_chsel)" "right"
amp_set_chsel mono
check "mono writes bits 11:10 = 11" "$(cat "$TMP/amp/reg")" "0x06 0x3ce8"
printf 'reg:0x06=0x3ce8\n' > "$TMP/amp/reg"
amp_set_chsel mono
check "no write when already there" "$(cat "$TMP/amp/reg")" "reg:0x06=0x3ce8"
check "bad slot refused" "$(amp_set_chsel sideways; echo $?)" "1"

STEREO_ATTEN_DB=6;  check "6 dB = 48 steps" "$(amp_atten_steps)" "48"
STEREO_ATTEN_DB=99; check "capped at 30 dB" "$(amp_atten_steps)" "240"
STEREO_ATTEN_DB=x;  check "junk -> 6 dB"    "$(amp_atten_steps)" "48"

echo "single daemon"
# Three started in the same instant, as service.sh was measured doing on the
# CMF Phone 1: exactly one may hold the lock.
mkdir -p "$TMP/fake/scripts"
cat > "$TMP/fake/scripts/stereo-daemon.sh" <<FAKE
#!/bin/sh
MODDIR=$ROOT DATADIR=$DATADIR
. $ROOT/scripts/common.sh
trap 'daemon_unlock; exit 0' TERM
if daemon_lock; then echo got >> $TMP/locks; while :; do sleep 1; done; fi
echo lost >> $TMP/locks
FAKE
: > "$TMP/locks"
for _i in 1 2 3; do sh "$TMP/fake/scripts/stereo-daemon.sh" & done
sleep 2
check "one of three gets the lock" "$(grep -c got "$TMP/locks")" "1"
check "the other two step aside" "$(grep -c lost "$TMP/locks")" "2"
check "found by command line" "$(daemon_pids | wc -l | tr -d ' ')" "1"
check "pid file names it" "$(daemon_pid)" "$(cat "$PIDFILE")"
# A shell whose command merely mentions the daemon is not the daemon.
sh -c "sleep 3 # scripts/stereo-daemon.sh" &
_decoy=$!
check "a mention is not a daemon" "$(_is_daemon $_decoy && echo yes || echo no)" "no"
stop_daemons
check "stop_daemons stops it" "$(daemon_pids | wc -l | tr -d ' ')" "0"
check "lock released" "$([ -d "$LOCKDIR" ] && echo yes || echo no)" "no"
check "decoy left alone" "$(kill -0 $_decoy 2>/dev/null && echo alive || echo gone)" "alive"
# A lock naming a dead pid (a crash, or the previous boot) is taken over.
mkdir -p "$LOCKDIR"; echo 999999 > "$LOCKDIR/pid"; : > "$TMP/locks"
sh "$TMP/fake/scripts/stereo-daemon.sh" &
sleep 1
check "stale lock taken over" "$(grep -c got "$TMP/locks")" "1"
stop_daemons
wait 2>/dev/null

echo "fast stop"
# The daemon naps through `wait`, so TERM is handled at once, not after the
# sleep in progress ends.
cat > "$TMP/fake/scripts/stereo-daemon.sh" <<FAKE
#!/bin/sh
MODDIR=$ROOT DATADIR=$DATADIR
. $ROOT/scripts/common.sh
trap 'kill "\$NAP_PID" 2>/dev/null; daemon_unlock; exit 0' TERM
daemon_lock || exit 0
while :; do nap 30; done
FAKE
sh "$TMP/fake/scripts/stereo-daemon.sh" &
_w=0; until daemon_pid >/dev/null || [ $_w -ge 30 ]; do tick; _w=$((_w + 1)); done
_t0=$(date +%s)
stop_daemons
_t1=$(date +%s)
check "a napping daemon stops within a second" "$([ $((_t1 - _t0)) -le 1 ] && echo yes || echo no)" "yes"
check "and is gone" "$(daemon_pids | wc -l | tr -d ' ')" "0"
check "its sleep is gone too" "$(pgrep -f 'sleep 30' >/dev/null && echo left || echo none)" "none"
wait 2>/dev/null

echo "tinymix probed once"
# Detection in the parent shell must carry into the subshells that do the
# reads and writes; it used to be redone on every call.
cat > "$TMP/bin/tinymix-count" <<'STUB'
#!/bin/sh
echo "$*" >> "$STUBLOG"
case $1 in
  --help) echo "usage: tinymix get NAME"; exit 0 ;;
  get) echo 3; exit 0 ;;
  set) exit 0 ;;
esac
exit 1
STUB
chmod +x "$TMP/bin/tinymix-count"
: > "$STUBLOG"
TINYMIX="$TMP/bin/tinymix-count"; unset TINYMIX_STYLE; MIXER_CARD=
tinymix_ready
_a=$(ctl_get 'A'); _b=$(ctl_get 'B'); ctl_set 'A' 1; echo x | while read -r _; do ctl_get 'C' >/dev/null; done
check "one style probe for many calls" "$(grep -c '^--help' "$STUBLOG")" "1"
check "reads still work" "$_a$_b" "33"
unset TINYMIX TINYMIX_STYLE

echo "live switching"
# Real bind mounts over fake vendor files; getprop/setprop/dumpsys stand in for
# init's audio HAL service. Needs root (mount): skipped when not available.
L=$TMP/live; mkdir -p "$L/vendor/lib64/hw" "$L/vendor/etc" "$L/ov/hw" "$L/ov/etc" "$L/bin"
echo STOCK-HAL > "$L/vendor/lib64/hw/audio.primary.mt6878.so"
echo STOCK-HAL > "$L/vendor/lib64/hw/audio.primary.mediatek.so"
printf '<aurisys_config>\n</aurisys_config>\n' > "$L/vendor/etc/aurisys_config_rv.xml"
echo STEREO-HAL > "$L/ov/hw/audio.primary.mt6878.so"
echo STEREO-HAL > "$L/ov/hw/audio.primary.mediatek.so"
printf '<aurisys_config>\n<!-- cmf_stereo: stereo -->\n</aurisys_config>\n' > "$L/ov/etc/aurisys_config_rv.xml"
if mount --bind "$L/ov/hw/audio.primary.mt6878.so" "$L/vendor/lib64/hw/audio.primary.mt6878.so" 2>/dev/null; then
  umount "$L/vendor/lib64/hw/audio.primary.mt6878.so"
  echo 100 > "$L/pid"; echo 0 > "$L/restarts"; echo 0 > "$L/callstate"; echo good > "$L/hal"
  cat > "$L/bin/getprop" <<STUB
#!/bin/sh
case \$1 in
  init.svc_debug_pid.vendor.audio-hal) cat "$L/pid" ;;
  init.svc.vendor.audio-hal) echo running ;;
esac
STUB
  # A good HAL comes back as a new process; a broken one never gets a new pid.
  cat > "$L/bin/setprop" <<STUB
#!/bin/sh
[ "\$1" = ctl.restart ] || exit 0
echo \$((\$(cat "$L/restarts") + 1)) > "$L/restarts"
[ "\$(cat "$L/hal")" = good ] && echo \$((\$(cat "$L/pid") + 1)) > "$L/pid"
exit 0
STUB
  printf '#!/bin/sh\necho "mCallState=$(cat %s/callstate)"\n' "$L" > "$L/bin/dumpsys"
  chmod +x "$L/bin/"*
  _OPATH=$PATH; PATH=$L/bin:$PATH
  _OHAL_DIR=$HAL_DIR; _OAUR=$AUR; _OOV_HAL=$OV_HAL; _OOV_ETC=$OV_ETC
  _OHS=$HAL_STOCK; _OHX=$HAL_STEREO; _OAS=$AUR_STOCK; _OAX=$AUR_STEREO; _OLR=$LIVE_ROOT
  HAL_DIR=$L/vendor/lib64/hw; AUR=$L/vendor/etc/aurisys_config_rv.xml
  OV_HAL=$L/ov/hw; OV_ETC=$L/ov/etc; LIVE_ROOT=
  HAL_STOCK=$(_sha "$HAL_DIR/audio.primary.mt6878.so"); AUR_STOCK=$(_sha "$AUR")
  HAL_STEREO=$(_sha "$OV_HAL/audio.primary.mt6878.so"); AUR_STEREO=$(_sha "$OV_ETC/aurisys_config_rv.xml")
  tick() { :; }

  check "stock saved while mono" "$(save_stock && _sha "$STOCKDIR/audio.primary.mediatek.so")" "$HAL_STOCK"
  live_switch stereo >/dev/null; _rc=$?
  check "mono -> stereo live" "$_rc $(stereo_active && echo stereo)" "0 stereo"
  check "both HAL names read as stereo" "$(cat "$HAL_DIR/audio.primary.mt6878.so" "$HAL_DIR/audio.primary.mediatek.so" | tr '\n' ' ')" "STEREO-HAL STEREO-HAL "
  check "HAL restarted once" "$(cat "$L/restarts")" "1"
  check "already stereo: nothing restarted" "$(live_switch stereo >/dev/null; cat "$L/restarts")" "1"
  # Back to mono: our mounts come off; the HAL must restart even though
  # nothing new is mounted (it still runs the stereo binary).
  live_switch mono >/dev/null; _rc=$?
  check "stereo -> mono live" "$_rc $(stereo_active && echo stereo || echo mono)" "0 mono"
  check "HAL restarted for mono" "$(cat "$L/restarts")" "2"
  check "no mounts left" "$([ -f "$LIVEFILE" ] && wc -l < "$LIVEFILE" | tr -d ' ' || echo 0)" "0"

  echo 1 > "$L/callstate"
  check "refused during a call" "$(live_switch stereo)" "a call is active"
  check "nothing mounted for it" "$(stereo_active && echo stereo || echo mono)" "mono"
  echo 0 > "$L/callstate"

  echo bad > "$L/hal"
  check "HAL that does not come back: refused" "$(live_switch stereo)" "the audio HAL did not come back on the stereo files"
  check "and undone" "$(stereo_active && echo stereo || echo mono) $([ -s "$LIVEFILE" ] && echo mounts || echo clean)" "mono clean"
  echo good > "$L/hal"

  # Booted stereo (the stock files are not visible): mono needs a saved copy.
  rm -rf "$STOCKDIR"
  mount --bind "$OV_ETC/aurisys_config_rv.xml" "$AUR"
  check "mono without a stock copy: refused" "$(live_switch mono)" "no verified mono copy of audio.primary.mt6878.so"
  umount "$AUR"

  live_unmount
  PATH=$_OPATH; HAL_DIR=$_OHAL_DIR; AUR=$_OAUR; OV_HAL=$_OOV_HAL; OV_ETC=$_OOV_ETC
  HAL_STOCK=$_OHS; HAL_STEREO=$_OHX; AUR_STOCK=$_OAS; AUR_STEREO=$_OAX; LIVE_ROOT=$_OLR
  tick() { sleep 0.1 2>/dev/null || sleep 1; }
else
  echo "  skip - bind mounts need root"
fi

echo
echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
