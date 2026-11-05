#!/system/bin/sh
# Shared helpers for the CMF Phone 1 stereo module.
# Sourced by post-fs-data.sh, service.sh, stereoctl and probe.sh.

MODID=cmf_stereo
MODDIR=${MODDIR:-/data/adb/modules/$MODID}
# Overridable so the scripts can be exercised off-device.
DATADIR=${DATADIR:-/data/adb/cmf-stereo}
# Always absolute. Magisk runs action.sh as ./action.sh from the module's
# folder, so ${0%/*} is "."; a relative path is wrong as soon as a command
# runs elsewhere. nsenter puts the live-switch mount at init's root, where
# ./system/vendor/... is /system/vendor -> /vendor: the stereo HAL was then
# "mounted" from Magisk's empty placeholder of the very file it was meant to
# replace (measured on the phone, v0.9.8).
case $MODDIR in /*) ;; *) MODDIR=$(cd "$MODDIR" 2>/dev/null && pwd) || MODDIR=/data/adb/modules/$MODID ;; esac
case $DATADIR in /*) ;; *) DATADIR=$(cd "$DATADIR" 2>/dev/null && pwd) || DATADIR=/data/adb/cmf-stereo ;; esac

CONF=$DATADIR/stereo.conf
ACTIONS=$DATADIR/actions.conf
STATEDIR=$DATADIR/state
LOGFILE=$DATADIR/stereo.log
PIDFILE=$DATADIR/daemon.pid
KILLSWITCH=$DATADIR/disabled

# Defaults, overridden by stereo.conf.
ENABLED=1
MODE=playback
WATCH_INTERVAL=2
LOG_LEVEL=info
LOG_MAX_KB=512
MIXER_CARD=
GUARD_CTL=
GUARD_VALUE=
PLAYBACK_CTL=
PLAYBACK_VALUE=1
CHANNELS=mono
STEREO_ATTEN_DB=6
SPEAKER_BOOST=0
BASS_PROTECT=medium
EARPIECE_LIMIT=on
EARPIECE_LEVELLER=off

mkdir -p "$DATADIR" "$STATEDIR" 2>/dev/null

[ -f "$CONF" ] && . "$CONF"

##############################################################################
# logging
##############################################################################

log() {
  # log <level> <message...>
  _lvl=$1; shift
  case $LOG_LEVEL in
    debug) ;;
    info)  [ "$_lvl" = debug ] && return 0 ;;
    warn)  case $_lvl in debug|info) return 0 ;; esac ;;
    *)     [ "$_lvl" = debug ] && return 0 ;;
  esac
  echo "$(date '+%Y-%m-%d %H:%M:%S') [$_lvl] $*" >> "$LOGFILE"
}

rotate_log() {
  [ -f "$LOGFILE" ] || return 0
  _kb=$(( $(stat -c %s "$LOGFILE" 2>/dev/null || echo 0) / 1024 ))
  [ "$_kb" -gt "${LOG_MAX_KB:-512}" ] && mv -f "$LOGFILE" "$LOGFILE.1"
  return 0
}

##############################################################################
# tinymix discovery + calling convention
##############################################################################

# Not every vendor ships tinymix. We look in the usual places, including a
# copy the user dropped into the module's bin/ directory.
find_tinymix() {
  [ -n "${TINYMIX:-}" ] && [ -x "$TINYMIX" ] && return 0
  for _c in \
    "$MODDIR/bin/tinymix" \
    /data/adb/cmf-stereo/bin/tinymix \
    /vendor/bin/tinymix \
    /system/bin/tinymix \
    /system/vendor/bin/tinymix \
    /odm/bin/tinymix \
    /data/local/tmp/tinymix
  do
    [ -x "$_c" ] && { TINYMIX=$_c; return 0; }
  done
  # Anything a another module put on PATH.
  _c=$(command -v tinymix 2>/dev/null)
  [ -n "$_c" ] && { TINYMIX=$_c; return 0; }
  TINYMIX=
  return 1
}

# tinyalsa 2.x uses "tinymix get/set NAME", older builds use "tinymix NAME [val]".
#
# Detection goes through --help, which 2.x answers even with no sound card
# present. Do not match on the error text from a bare "tinymix get": 2.x
# answers that with "no control specified", which reads nothing like a usage
# message, and guessing "old" from it makes every later write a silent no-op.
_tinymix_detect() {
  _help=$("$TINYMIX" --help 2>&1)
  _get=$("$TINYMIX" get 2>&1)
  if echo "$_help" | grep -qE 'get[[:space:]]+(NAME|<|\[)'; then
    echo new
  elif echo "$_get" | grep -qi 'no control specified'; then
    echo new
  elif [ -z "$_help" ] && [ -z "$_get" ]; then
    # Says nothing to either probe: wrong architecture, or not executable.
    # Reporting a style here would turn every later write into a silent no-op.
    echo unknown
  else
    echo old
  fi
}

# Finds tinymix and detects its style once, caching both in this shell.
#
# Call it in the top-level shell (the daemon and stereoctl do) before any
# mixer work. The mixer helpers run inside $(...) and pipelines, which are
# subshells: a cache filled in there is thrown away when they return, which
# is how every single read used to start tinymix three times and every write
# five. Filled in the parent, the subshells inherit it.
#
# "unknown" is reported but not kept, so a binary that could not run once is
# tried again on the next call, as before.
tinymix_ready() {
  find_tinymix || return 1
  [ -n "${TINYMIX_STYLE:-}" ] && return 0
  _st=$(_tinymix_detect)
  [ "$_st" = unknown ] && return 1
  TINYMIX_STYLE=$_st
}

tinymix_style() {
  if tinymix_ready; then echo "$TINYMIX_STYLE"; else echo unknown; fi
}

_card_args() {
  [ -n "$MIXER_CARD" ] && echo "-D $MIXER_CARD"
}

# Turn what tinymix prints into something tinymix will accept back.
#
#   enum : "Open, Mute, > Voice Playback, Test Mode," -> "Voice Playback"
#   int  : "31 (range 0->18)"                         -> "31"
#   bool : "On" / "Off"                               -> "1" / "0"
#
# Without this, revert feeds a whole enum list or a range suffix back to
# tinymix, which refuses it - and a failed revert leaves the earpiece driven.
# Note the int case must be tested first: a range like "0->18" contains the
# same ">" that marks the selected enum entry.
ctl_normalize() {
  case $1 in
    *'(range'*)  echo "$1" | sed 's/[[:space:]]*(range.*//; s/^[[:space:]]*//; s/[[:space:]]*$//' ;;
    *'>'*)       echo "$1" | sed 's/.*>[[:space:]]*//; s/,.*//; s/^[[:space:]]*//; s/[[:space:]]*$//' ;;
    On|ON|on)    echo 1 ;;
    Off|OFF|off) echo 0 ;;
    *)           echo "$1" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' ;;
  esac
}

# Raw text as tinymix prints it - useful for showing a user their options.
ctl_get_raw() {
  tinymix_ready || return 1
  _out=$(
    if [ "$TINYMIX_STYLE" = new ]; then
      # shellcheck disable=SC2046
      "$TINYMIX" $(_card_args) get "$1" 2>/dev/null
    else
      # shellcheck disable=SC2046
      "$TINYMIX" $(_card_args) "$1" 2>/dev/null
    fi
  )
  # Old tinymix echoes a header line before the value; keep the last non-empty
  # line. Do not strip a leading ">": it marks the selected enum entry.
  echo "$_out" | grep -v '^[[:space:]]*$' | tail -n 1 \
    | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}

ctl_get() {
  _raw=$(ctl_get_raw "$1") || return 1
  [ -n "$_raw" ] || return 1
  ctl_normalize "$_raw"
}

ctl_set() {
  # ctl_set <control name> <value>
  tinymix_ready || return 1
  if [ "$TINYMIX_STYLE" = new ]; then
    # shellcheck disable=SC2046
    "$TINYMIX" $(_card_args) set "$1" "$2" >/dev/null 2>&1
  else
    # shellcheck disable=SC2046
    "$TINYMIX" $(_card_args) "$1" "$2" >/dev/null 2>&1
  fi
}

##############################################################################
# telling the apps
#
# CMF Stereo (both editions) shows the module's state in Nothing Settings
# from what it last read, so Settings never needs a root call to show it. A
# change made outside the apps (stereoctl, Magisk's Action button, the
# daemon's own switch back to mono) is announced here: each installed app's
# provider is asked to read the state again, and Settings updates at once.
# In the background and silent: an app that is not installed changes nothing.
##############################################################################
CMF_APPS="com.tiimoo.cmfstereo com.tiimoo.cmfstereo.clean"
notify_apps() {
  command -v content >/dev/null 2>&1 || return 0
  for _p in $CMF_APPS; do
    ( content call --uri "content://$_p.settingstile" --method stateChanged >/dev/null 2>&1 & )
  done
  return 0
}

##############################################################################
# playback detection
##############################################################################

# True while audio is playing.
#
# Two detectors, because procfs alone is not enough. Media routed through the
# DSP offload path never appears as a RUNNING substream in
# /proc/asound - so on such a device MODE=playback would never engage while
# MODE=always worked, which is exactly the symptom seen on the CMF Phone 1.
#
# PLAYBACK_CTL names the mixer controls the HAL flips when audio starts (found
# with 'stereoctl diff'), separated by '|': audio is playing when any of them
# reads PLAYBACK_VALUE. They are authoritative when at least one is readable;
# the procfs scan stays as the fallback for devices without them.
#
# On the CMF Phone 1 each kind of output has its own DSP task switch
# (dsp_<task>_runtime_en). Measured on the phone: a game turns on only
# dsp_fast, a music player dsp_music with dsp_primary (dsp_deepbuf for a
# moment), and nothing stays on when it stops; dsp_playback is on all the
# time, so it says nothing. Watching dsp_music alone left games on the
# speaker only in MODE=playback.
playback_active() {
  if [ -n "${PLAYBACK_CTL:-}" ]; then
    _seen=0
    _rest=$PLAYBACK_CTL
    while [ -n "$_rest" ]; do
      _c=${_rest%%"|"*}
      case $_rest in *'|'*) _rest=${_rest#*"|"} ;; *) _rest= ;; esac
      [ -n "$_c" ] || continue
      _pb=$(ctl_get "$_c" 2>/dev/null)
      [ -n "$_pb" ] || continue
      _seen=1
      [ "$_pb" = "${PLAYBACK_VALUE:-1}" ] && return 0
    done
    [ $_seen -eq 1 ] && return 1
    # No control readable (renamed by a vendor update?): fall through rather
    # than silently reporting "never playing" forever.
  fi

  for _s in /proc/asound/card*/pcm*p/sub*/status; do
    [ -f "$_s" ] || continue
    grep -q '^state: RUNNING' "$_s" 2>/dev/null && return 0
  done
  return 1
}

# Which detector answered, for diagnostics.
playback_detector() {
  _ok=
  _rest=${PLAYBACK_CTL:-}
  while [ -n "$_rest" ]; do
    _c=${_rest%%"|"*}
    case $_rest in *'|'*) _rest=${_rest#*"|"} ;; *) _rest= ;; esac
    [ -n "$_c" ] && [ -n "$(ctl_get "$_c" 2>/dev/null)" ] && _ok="$_ok${_ok:+, }$_c"
  done
  if [ -n "$_ok" ]; then echo "mixer controls: $_ok"; else echo "procfs substream scan"; fi
}

# Best-effort check that audio is going out of the speaker rather than
# headphones/BT. If we cannot tell, we say yes and let the actions decide.
speaker_route_active() {
  [ "${REQUIRE_SPEAKER_ROUTE:-0}" = 1 ] || return 0
  _dump=$(dumpsys audio 2>/dev/null | head -n 200)
  [ -z "$_dump" ] && return 0
  echo "$_dump" | grep -qiE 'BLUETOOTH_A2DP|WIRED_HEADPHONE|WIRED_HEADSET|USB_HEADSET' && return 1
  return 0
}

# Only drive the earpiece while a named control holds a given value. On the
# CMF Phone 1 the guard is the speaker amp's own switch: the HAL disables it
# when headphones or Bluetooth take over, so this costs one mixer read per
# cycle instead of a dumpsys, and it means the earpiece never plays into an
# empty room while you are wearing headphones.
guard_ok() {
  # Bypass exists because the guard defeats the obvious way to audition the
  # earpiece: disabling the speaker amp is exactly what the guard reads as
  # "headphones took over".
  [ -f "$DATADIR/guard_bypass" ] && return 0
  [ -n "${GUARD_CTL:-}" ] || return 0
  _g=$(ctl_get "$GUARD_CTL" 2>/dev/null)
  [ -n "$_g" ] || return 0     # control missing: do not block on it
  [ "$_g" = "$GUARD_VALUE" ]
}

##############################################################################
# action engine
#
# actions.conf holds one action per line:
#   ctl|<mixer control name>|<value>
#   sysfs|<path>|<value>
#   prop|<property>|<value>
# Blank lines and lines starting with '#' are ignored.
##############################################################################

_state_key() {
  echo "$1_$2" | tr -c 'A-Za-z0-9._-' '_'
}

action_lines() {
  [ -f "$ACTIONS" ] || return 0
  grep -v '^[[:space:]]*#' "$ACTIONS" | grep -v '^[[:space:]]*$'
}

action_count() {
  action_lines | wc -l | tr -d ' '
}

# Remember the pre-module value once, so revert puts the device back.
_save_original() {
  # _save_original <kind> <target> <current value>
  _f=$STATEDIR/$(_state_key "$1" "$2")
  [ -f "$_f" ] && return 0
  printf '%s' "$3" > "$_f"
}

_original() {
  _f=$STATEDIR/$(_state_key "$1" "$2")
  [ -f "$_f" ] && cat "$_f"
}

apply_actions() {
  action_lines | while IFS='|' read -r kind target value rest; do
    kind=$(echo "$kind" | tr -d ' ')
    target=$(echo "$target" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    value=$(echo "$value" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    [ -n "$kind" ] && [ -n "$target" ] || continue
    case $kind in
      ctl)
        _cur=$(ctl_get "$target")
        if [ -z "$_cur" ]; then
          log warn "mixer control not found: $target"
          continue
        fi
        _save_original ctl "$target" "$_cur"
        [ "$_cur" = "$value" ] && continue
        if ctl_set "$target" "$value"; then
          log info "ctl '$target': $_cur -> $value"
        else
          log warn "ctl '$target': failed to set $value"
        fi
        ;;
      sysfs)
        if [ ! -e "$target" ]; then
          log warn "sysfs node missing: $target"
          continue
        fi
        _cur=$(cat "$target" 2>/dev/null)
        _save_original sysfs "$target" "$_cur"
        [ "$_cur" = "$value" ] && continue
        if echo "$value" > "$target" 2>/dev/null; then
          log info "sysfs '$target': $_cur -> $value"
        else
          log warn "sysfs '$target': write denied (SELinux or read-only)"
        fi
        ;;
      prop)
        _cur=$(getprop "$target")
        _save_original prop "$target" "$_cur"
        [ "$_cur" = "$value" ] && continue
        if command -v resetprop >/dev/null 2>&1; then
          resetprop -n "$target" "$value" && log info "prop '$target': $_cur -> $value"
        else
          setprop "$target" "$value" && log info "prop '$target': $_cur -> $value"
        fi
        ;;
      *)
        log warn "unknown action kind: $kind"
        ;;
    esac
  done
}

revert_actions() {
  action_lines | while IFS='|' read -r kind target value rest; do
    kind=$(echo "$kind" | tr -d ' ')
    target=$(echo "$target" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    [ -n "$kind" ] && [ -n "$target" ] || continue
    _orig=$(_original "$kind" "$target")
    [ -n "$_orig" ] || continue
    case $kind in
      ctl)   ctl_set "$target" "$_orig" && log info "ctl '$target' restored to $_orig" ;;
      sysfs) echo "$_orig" > "$target" 2>/dev/null && log info "sysfs '$target' restored to $_orig" ;;
      prop)
        if command -v resetprop >/dev/null 2>&1; then
          resetprop -n "$target" "$_orig"
        else
          setprop "$target" "$_orig"
        fi
        ;;
    esac
  done
}

module_active() {
  [ -f "$KILLSWITCH" ] && return 1
  [ "${ENABLED:-1}" = 1 ]
}

# The daemon is found by its command line, not only through the pid file.
# On the CMF Phone 1 service.sh was measured starting three daemons in the
# same second at every boot; the pid file named one of them, so status read
# "not running" while three were fighting over the mixer, and restart added
# a fourth.
#
# Match the script argument itself (argv[1] of "sh .../stereo-daemon.sh"), not
# the name anywhere in the command line: a shell running a command that merely
# mentions stereo-daemon.sh must never be taken for the daemon and killed.
_is_daemon() {
  case $(tr '\0' '\n' 2>/dev/null < "/proc/$1/cmdline" | sed -n 2p) in
    */scripts/stereo-daemon.sh) return 0 ;;
  esac
  return 1
}

# A phone runs several hundred processes, and _is_daemon starts two programs
# for each one it checks, so it only checks the candidates: processes whose
# name (read with the shell's own `read`, no new process) is a shell, or the
# daemon itself when it was started through its #! line ("stereo-daemon.s",
# the name cut to 15 characters). Checking every pid cost seconds on each
# on/off.
daemon_pids() {
  for _d in /proc/[0-9]*; do
    _p=${_d#/proc/}
    [ "$_p" = "$$" ] && continue
    _c=
    { read -r _c < "$_d/comm"; } 2>/dev/null || continue
    case $_c in
      sh|mksh|ash|dash|bash|busybox|stereo-daemon*) _is_daemon "$_p" && echo "$_p" ;;
    esac
  done
}

daemon_pid() {
  _p=$(cat "$PIDFILE" 2>/dev/null)
  [ -n "$_p" ] && _is_daemon "$_p" && { echo "$_p"; return 0; }
  _p=$(daemon_pids | head -n 1)
  [ -n "$_p" ] && { echo "$_p"; return 0; }
  return 1
}

# One daemon only. mkdir is atomic, so of several started at once exactly one
# gets the lock. A lock left by a dead daemon (or a previous boot) is taken
# over; an empty pid means a daemon is mid-start, so leave it alone.
LOCKDIR=$DATADIR/daemon.lock
daemon_lock() {
  if ! mkdir "$LOCKDIR" 2>/dev/null; then
    _o=$(cat "$LOCKDIR/pid" 2>/dev/null)
    [ -z "$_o" ] && return 1
    _is_daemon "$_o" && return 1
    rm -rf "$LOCKDIR"
    mkdir "$LOCKDIR" 2>/dev/null || return 1
  fi
  echo $$ > "$LOCKDIR/pid"
  echo $$ > "$PIDFILE"
}

# Release only what is ours: a stopping daemon must not delete the pid file
# or lock of the one that replaced it.
daemon_unlock() {
  [ "$(cat "$PIDFILE" 2>/dev/null)" = "$$" ] && rm -f "$PIDFILE"
  [ "$(cat "$LOCKDIR/pid" 2>/dev/null)" = "$$" ] && rm -rf "$LOCKDIR"
}

# A tenth of a second. Toybox and busybox sleep take fractions; a sleep that
# does not falls back to a whole second rather than spinning.
tick() {
  sleep 0.1 2>/dev/null || sleep 1
}

# sleep that a trapped signal cuts short. A shell runs its trap only after the
# foreground command returns, so a plain `sleep 2` held a stop request for up
# to two seconds; `wait` returns as soon as a trapped signal arrives (POSIX).
# The daemon's stop handler kills the leftover sleep through $NAP_PID.
nap() {
  sleep "$1" &
  NAP_PID=$!
  wait "$NAP_PID" 2>/dev/null
  NAP_PID=
}

# Stop every daemon, however many there are, and wait for them to go.
stop_daemons() {
  _ps=$(daemon_pids)
  [ -n "$_ps" ] || { rm -rf "$LOCKDIR" "$PIDFILE"; return 1; }
  # shellcheck disable=SC2086
  kill $_ps 2>/dev/null
  # The daemon handles TERM at once (it naps through `wait`, see nap), so
  # poll in short ticks: a whole second per check was most of the delay
  # when the app switched the module on or off.
  _w=0
  while [ -n "$(daemon_pids)" ] && [ $_w -lt 100 ]; do tick; _w=$((_w + 1)); done
  rm -rf "$LOCKDIR" "$PIDFILE"
  return 0
}

##############################################################################
# Magisk description
#
# Magisk, KernelSU and APatch show module.prop's description on the module's
# card and read it again each time the Modules page opens, so the module keeps
# its first line current: what is playing, and anything that needs the user.
# Rewritten only when it changes.
##############################################################################

MODPROP=${MODPROP:-$MODDIR/module.prop}
DESC_ABOUT='Real left/right stereo on the CMF Phone 1 (A015): earpiece left, bottom speaker right, swapped when the phone is turned. Mono (stock, with Awinic speaker protection) or Stereo, switched at once from the app, stereoctl or the Action button. Patches only this phone'"'"'s verified vendor files; back to mono after two failed boots.'

describe_state() {
  case $(build_state) in
    updated) echo "[Stereo unavailable] This Nothing OS build is not supported yet: mono (stock audio) until a module update adds it." ; return ;;
    absent)  echo "[Inactive] Not a CMF Phone 1 audio stack: nothing is changed." ; return ;;
  esac
  if ! module_active; then
    echo "[Off] Earpiece not used. Turn on in the app or with stereoctl on."
    return
  fi
  if stereo_active; then _d="[Stereo] Earpiece left, speaker right."
  else _d="[Mono] Both speakers play the full mix."; fi
  _stg=mono; stereo_staged && _stg=stereo
  _act=mono; stereo_active && _act=stereo
  [ "$_act" != "$_stg" ] && _d="$_d Switches to $_stg after a reboot."
  [ "${1:-}" = boot ] || daemon_pid >/dev/null || _d="$_d Not running: restart it in the app."
  echo "$_d"
}

# update_description [boot]   (boot: from service.sh, before the daemon is up)
update_description() {
  [ -w "$MODPROP" ] || return 0
  _line="description=$(describe_state "${1:-}") $DESC_ABOUT"
  # Keep the result a single line sed can take: no newline, | or &.
  _line=$(printf '%s' "$_line" | tr -d '\n|&\\')
  grep -qxF "$_line" "$MODPROP" && return 0
  sed -i "s|^description=.*|$_line|" "$MODPROP" 2>/dev/null
}

##############################################################################
# XML sanity
#
# There is no xmllint on Android, and a malformed audio policy takes the audio
# HAL down hard enough to bootloop the phone. So before any patched policy is
# allowed into the overlay it has to survive these structural checks.
##############################################################################

xml_sane() {
  # xml_sane <file> -> 0 if the file looks structurally intact
  _f=$1
  [ -s "$_f" ] || { echo "empty file"; return 1; }

  # Container elements are checked too: <devicePorts> differs from
  # <devicePort> by one character, and losing one is invisible otherwise.
  for _tag in module modules mixPort mixPorts devicePort devicePorts \
              route routes audioPolicyConfiguration; do
    # Self-closing elements (<devicePort ... />) count as open+close.
    _open=$(grep -o "<$_tag[ >]" "$_f" 2>/dev/null | wc -l)
    _close=$(grep -o "</$_tag>" "$_f" 2>/dev/null | wc -l)
    _self=$(grep -o "<$_tag[^>]*/>" "$_f" 2>/dev/null | wc -l)
    if [ "$_open" -ne $((_close + _self)) ]; then
      echo "unbalanced <$_tag>: $_open open, $_close close, $_self self-closing"
      return 1
    fi
  done

  grep -q '</audioPolicyConfiguration>' "$_f" || {
    echo "missing root closing tag (file truncated?)"; return 1; }

  # A stray backslash is the signature of a bad sed/awk insertion.
  grep -q '\\$' "$_f" && { echo "trailing backslash - bad line insertion"; return 1; }

  return 0
}

##############################################################################
# boot watchdog
#
# Counts boots that started with our changes active but never reached
# sys.boot_completed. Two strikes and the module disarms itself, so a bad
# config costs a reboot rather than a trip to recovery.
##############################################################################

BOOTCOUNT=$DATADIR/boot_pending

boot_strikes() {
  [ -f "$BOOTCOUNT" ] && cat "$BOOTCOUNT" 2>/dev/null || echo 0
}

boot_strike_add() {
  echo $(( $(boot_strikes) + 1 )) > "$BOOTCOUNT"
}

boot_strike_clear() {
  echo 0 > "$BOOTCOUNT"
}

##############################################################################
# mixer snapshots
#
# The fastest way to find which controls carry media is to watch what the HAL
# itself changes when playback starts. Guessing at names is how you end up
# writing to a path the media stream never reaches.
##############################################################################

mixer_snapshot() {
  # mixer_snapshot <file>
  tinymix_ready || return 1
  if [ "$TINYMIX_STYLE" = new ]; then
    "$TINYMIX" contents 2>/dev/null > "$1"
  else
    "$TINYMIX" 2>/dev/null > "$1"
  fi
  [ -s "$1" ]
}

# Print controls whose value differs between two snapshots. Keyed on the
# leading control id so a renamed or reordered list cannot produce noise.
diff_snapshots() {
  awk '
    NR == FNR { before[$1] = $0; next }
    ($1 in before) && before[$1] != $0 {
      print "  - " before[$1]
      print "  + " $0
      n++
    }
    END { if (n == 0) print "  (no control changed)" }
  ' "$1" "$2"
}

# Mono / stereo speaker channels and the speaker amp helpers.
. "$MODDIR/scripts/channels.sh"
