# History: findings, tests and fixes

Everything the README's Status section has said, release by release, kept here so the Status
can show only the current state. Newest first within each list. The release notes for each
version are in [docs/releases](docs/releases).

## As of v1.0.4

**Current release: v1.0.4** (CMF Phone 1, Nothing OS B4.1, Android 16). Stereo works and is
in daily use on the test phone. Mono and Stereo switch without a reboot, and Magisk offers new
releases as updates. Left and right follow the phone's orientation. Android swaps the channels
itself at rotation 270 before the HAL (measured with the HAL's own recordings), except for an
app whose track has its own audio effect (VLC: its recording showed the left-only beep still
on the left at 270). v1.0.2 swaps exactly those in the HAL: the daemon reads
`dumpsys media.audio_flinger` while something plays at rotation 270 and names the outputs that
carry such a track in `vendor.audiohal.cmf_swap`; the HAL swaps only those, only at 270.

**Verified on the phone**
- v1.0.4 stereo protection: `stereoctl protect` reports it running after the first sound
  (the HAL loaded the library), and every setting was tried and works. Seen: speaker level 5
  (16 dB attenuation), boost 0, bass strong, earpiece on -> ceilings speaker off, bass -4 dBFS
  (-20 dB below the amp's full output), earpiece -2.5 dBFS, as designed.
- What "While playing" (MODE=playback) can watch, measured with the DSP's task switches
  logged each second: idle, nothing; a game, `dsp_fast_runtime_en`; a music player,
  `dsp_music_runtime_en` with `dsp_primary_runtime_en` (`dsp_deepbuf_runtime_en` for a moment);
  stopped, nothing; `dsp_playback_runtime_en` and `aw_dev_0_switch` stay on throughout.
- v1.0.2: VLC and the CMF L/R Test app's MOVIE + EFFECT button follow the rotation (the
  left-only file plays on the side of the earpiece or speaker it should), and USB Audio Player
  Pro in bit-perfect mode, and the CMF L/R Test app's AAUDIO (low latency, exclusive, as a
  game asks), AAUDIO SHARED and FLOAT buttons. On the speaker AAudio cannot get the direct
  MMAP path (`mmap_no_irq_out` lists only the earpiece and wired headsets), so low-latency
  games play through Android's mixer, which swaps them.
- Compressed offload (MP3 decoded by the DSP): Android refuses it on this phone
  (`AudioManager.isOffloadedPlaybackSupported` false for MP3 on the speaker), so music
  players do not use that path here. Likely reason, not yet proven: the audio policy refuses
  offload while a non-offloadable effect is on, and Nothing's Dirac (flags 0x280, no offload
  support) is on for the output mix. One check would settle it: Dirac off, COMPRESSED again.
- v1.0.1: the CMF L/R Test app's four buttons (MUSIC, MOVIE, GAME, SPEECH) and InShot follow
  the rotation; VLC does not (it plays the same side whichever way the phone is turned).
- v0.9.9 orientation swap by Dirac's tuning: the left-only file in USB Audio Player Pro
  (Android driver; Dirac MUSIC) and VLC (Dirac MOVIE), earpiece on either side: both right.
- v0.9.9 Action button: switching Mono and Stereo from Magisk works; the audio service kept
  running (v0.9.8 crashed it on the switch to Stereo). One try left UAPP crashing once; it
  did not happen again.
- VLC added to Nothing's Game mode (game dashboard): still right with the earpiece on either
  side, but Dirac's tuning stayed MOVIE (`persist.vendor.newdirac.cur.config`), so this did
  not test Dirac's GAME tuning: that comes only from the game list built into
  `com.nothing.audioeffect` (125 apps, mostly Tencent titles), not from Game mode.
- v0.9.9 orientation swap in apps and games: YouTube (on Nothing's video list, Dirac MOVIE:
  the module swaps) follows the rotation, and a game (The Amazing Spider-Man 2, 64-bit port,
  on no list: Dirac MUSIC) switches sides when turned (checked by ear in the game only).
- Magisk's Update button: with v0.9.6 installed, Magisk showed **Update** for this module
  once v0.9.7 was out and `update.json` named it (before that it rightly showed none).
- Updating from that button to v0.9.7 and rebooting: the module is now listed as v0.9.7 by
  Dr.Essence.
- v0.9.5 orientation swap: the left-only test file in VLC (deep-buffer output) and in USB Audio
  Player Pro (primary output, where Nothing's Dirac does the swap): earpiece on your left, the
  earpiece plays; on your right, the speaker plays. (Then UAPP played on the primary output
  in Dirac's MUSIC tuning; v0.9.9 replaced the output rule, see Fixed.)
- v0.9.8 Action button, live card text and Update button: Action switched Mono, the card
  showed v0.9.8 by Dr.Essence. Action's switch back to Stereo crashed the audio service
  (fixed in v0.9.9).
- v0.9.4 live switching: Mono -> Stereo -> Mono -> Stereo with `stereoctl channels`, no reboot,
  each checked with the left-only test file (speaker silent in Stereo, both play in Mono).
  The first two builds refused it safely (no stock copy; then mounting over the deleted
  files Magisk had mounted), which is what the final design fixed.
- v0.9.4 kernel log: boot messages intact, one `aw882xx_volume_put` at boot instead of a
  `volume_get` line every cycle.
- Stereo: a left-only test file leaves the speaker silent on its right slot and plays on the
  earpiece, with Nothing's Dirac tuning on and off.
- Mono and stereo switching through `stereoctl channels` and the app, with a reboot.
- Restarting the audio HAL by hand (`setprop ctl.restart vendor.audio-hal`) while playing:
  the HAL came back, players paused, calls worked.
- One daemon per boot (three were starting before v0.9.1).
- Earpiece at +8 dB (`Handset Volume 0`) while playing; the old 31 is corrected on install.
- Hi-res playback (USB Audio Player Pro, Direct 192 kHz) still works in stereo.

**Not tested on a phone yet**
- **v1.0.4 stereo protection** (`stereoctl protect`, both apps): the stereo HAL loads the
  module's library (`/vendor/lib64/hw/libcmfstereo.so`, `protect/cmfstereo.c`) and runs, on
  every speaker buffer after the rotation swap: the speaker's bass guard (the band below
  100 Hz held at -8 / -14 / -20 dB below the amp's full output, only when louder; default
  medium), a speaker peak limiter that keeps the peaks at Awinic's measured -5 dB when the
  speaker boost (0-6 dB less fixed attenuation, default 0) is used, and an earpiece limiter at
  -2.5 dBFS (on by default). Needs on the phone: that the HAL loads it (`stereoctl protect`
  says running after the first sound), Stereo sounding the same at boost 0 apart from the
  loudest deep bass, and a listen at boost 6. Tested here: the library's 20 host tests
  (bit-exact when nothing is set, the swap as before, limiters never above their ceilings,
  quiet bass unchanged within 0.3 dB from 30 Hz to 5 kHz, limiter distortion at most 1.2 %
  at 50 Hz and under 0.1 % above 1 kHz, 12 streams, null inputs); the NDK build (needs only
  libc, libm, libdl; rebuilds byte for byte); the HAL patch in the ARM64 emulator (24 cases:
  loaded once, called with the HAL's arguments, a failed load not retried and the swap alone
  run instead); every earlier stereo HAL (v0.9.0-v1.0.3) converting to the v1.0.4 file and
  undoing to stock on the real file; settings, boost rules, amp handling and the crash-loop
  guard in 190 checks under sh, dash, mksh and busybox. After a live switch from a mono boot
  the library is not in place until a reboot: stereo then plays as v1.0.3, boost ignored.
- **v1.0.3** "While playing" with a game and with a music player: the earpiece should now
  engage for both (before, only for music players). Tested here: the detector on stub
  controls under sh, dash, mksh and busybox (a game turning on only `dsp_fast` counts as
  playing; all off, not playing; none readable, the procfs fallback), and the config line
  the installer writes, sourced by mksh.
- **v1.0.2**: an app with its own effect in another category (music, game) and an app with no
  effect after VLC (UAPP) in both orientations; only VLC and MOVIE + EFFECT were tried. Not
  yet checked: compressed offload with Dirac off (the one case where Android might grant
  it; the module does not swap compressed audio). Each needs
  the left-only file played that way, earpiece on your right. Tested here: the HAL patch in an
  ARM64 emulator (18 cases), the bytes and branch against the assembled code, every earlier
  stereo HAL (v0.9.0-v1.0.1) converting to v1.0.2 and undoing to the exact stock hash on the
  real stock file, the detector on two real `dumpsys media.audio_flinger` captures, 156 checks
  under sh, dash, mksh and busybox.
- v0.9.8 Action button: Magisk's **Action** on the module's card switches Mono <-> Stereo
  through `stereoctl channels` and prints its output. Checked: the script parses under
  dash, mksh and busybox and is packaged; not yet pressed on the phone.
- v0.9.8 live description: the card's first words say `[Stereo]`, `[Mono]`, `[Off]`, a switch
  waiting for a reboot, a daemon that is not running, or `[Stereo unavailable]` after a
  Nothing OS update. Covered by the tests (state text, one line, file left alone when nothing
  changed); needs a look on the phone after a switch and after a reboot.
- v0.9.8 Nothing OS update guard: before Magisk mounts, a staged stereo overlay is removed
  (mono) if the vendor audio files are not the analysed build, instead of mounting a HAL
  patched from the old build over the new one; the card and `stereoctl status` then say
  stereo is unavailable. Tested on fake vendor files (different HAL, different DSP config,
  missing HAL); seen on the phone only with the next Nothing OS update.
- v0.9.9: a failed live switch ending on the stock files (tested on bind mounts over a
  Magisk-style skeleton; no failure has happened on the phone since).
- Live switching from the app's Mono/Stereo buttons.
- v0.9.3: on/off speed and the lighter daemon. Passes the test suite under mksh (Android's
  shell), dash and busybox; needs a check on the phone: `time su -c stereoctl off`, then
  `time su -c stereoctl on`, and the earpiece still engaging when audio starts.
- The boot watchdog removing the stereo overlay after two failed boots (no failed boot has
  happened to trigger it).
- Re-staging stereo during a module update, and the refusal on a different Nothing OS build
  (needs the next OTA).
- How the speaker holds up to long, loud stereo listening without Awinic's protection.

**Pending**
- If an app with its own effect and an ordinary app play on the same output at the same time,
  one of them is reversed at rotation 270 (the HAL sees only the mixed stream). Not seen yet.
- Earpiece boost, measured: there is no hidden attenuation to win back. The HAL's own
  recordings (CMF L/R Test FULL CHECK) show the beep at the same level from Android's output
  to the HAL (-8.7 dBFS, the test file's own level at full volume) and through the audio DSP
  (-56.9 in the DSP's 8.24 fixed-point dump, the same -8.7 dBFS), then `ADDA_DL_GAIN` -0.3 dB
  and the receiver amp at its top step (+8 dB). A louder earpiece therefore needs either more
  average power or a different spread of frequencies; the option without any EQ is a leveller
  whose peaks never exceed today's full-scale peaks (more for quiet, dynamic recordings, little
  for already loud masters).
- Driver study, stereo part (CMF L/R Test DRIVER STUDY, measured with the HAL's raw 24-bit
  microphone capture, levels taken from the HAL's copy of what reached it):
  - Dirac (MUSIC) shapes the tones before the drivers: about +2 dB at 150 Hz, +5 to +6 dB at
    200-500 Hz, -2 to -4 dB at 3-5 kHz, a limiter holding peaks at about -0.2 dBFS, and a
    second harmonic at -16 dB on 100 Hz (bass enhancement). Above 150 Hz what reaches the
    drivers is clean (under 0.1 % distortion).
  - Earpiece: under about 5-10 % distortion up to about -3 dBFS from 150 Hz up; in the top
    1.5 dB it clips (odd harmonics jump to 25-35 % at 150, 200 Hz and 2 kHz).
  - Speaker (Awinic off, stereo): distortion grows steadily with level from about -12 dBFS,
    mostly odd harmonics, to about 27 % at -3 dBFS at 1.2-2 kHz (both microphones agree on the
    trend).
  - Pending: the Mono part (Awinic on) for the same tones, to compare.
- Speaker limiter, earpiece boost and EQ (asked for; design stage). Where it can run: the
  HAL's playback path calls `doStereoToMonoConversionIfNeed` (our swap) for every speaker
  stream, including USB Audio Player Pro's direct hi-res output, before the DSP, which runs
  MediaTek's pass-through `aurisys_demo` in stereo. An Android audio effect from the app would
  miss direct outputs, so a limiter meant to protect the speaker has to sit in the HAL path.
  Needs, before any build: whether the host-side Aurisys step after it
  (`aurisys_process_dl_only` in `AudioALSAPlaybackHandlerDsp::write`) adds gain, and the
  user's bass tests (Mono vs Stereo, STEREO_ATTEN_DB 6 vs 12).
- Balance: already there as the app's two levels (earpiece level, speaker level in stereo).
- Hardware checked (I2C devices, driver bindings, mixer, HAL): one Awinic amp at `6-0034`
  (mono output, speaker only); the earpiece is on the codec's left DAC, which takes only
  channel 1; the codec's earpiece amp is at its top step (+8 dB) and the digital path has
  about 0.3 dB left. Ideas under consideration: an earpiece boost (high-pass, compressor and
  limiter on the earpiece channel through Android's DynamicsProcessing, in the app), and a
  mono speaker fallback when the phone is turned with the earpiece on the right (a true
  left/right swap would need the channels swapped in the stream: a bigger project).
- Which stereo speaker level sounds as loud as stock (Mono, with Awinic's protection): needs a
  by-ear comparison on the phone, level by level, with the same track.
- A short clip of the earpiece and speaker splitting a game's or film's audio, for the README
  and the release page.
- Check the vendor file hashes after the next Nothing OS update and add the new build.
- `ADDA_DL_MAX_VOL` was tried for a louder earpiece: no clear difference, left out.

**Fixed recently**
- v1.0.4: in stereo the speaker got up to about 10 dB more deep bass (100 Hz) than Awinic
  lets through in mono, with no protection but the fixed attenuation, and the earpiece clipped
  in its top 1.5 dB (DRIVER STUDY). The bass guard and the earpiece limiter hold both, and a
  crash-loop guard puts the phone back on the stock files (mono) if the audio HAL restarts 3
  times within a minute in stereo.
- v1.0.3: in "While playing" (the default, and the only mode the clean app has) games and
  most apps that are not music players played on the speaker only: playback was detected
  from `dsp_music_runtime_en`, the DSP's music task alone, and a game plays through its fast
  task. Playback now counts when any DSP playback task is on (music, fast, primary, deep
  buffer, VoIP, offload); `PLAYBACK_CTL` takes several controls separated by `|`. Updates
  rewrite the setting, so installed phones get it without touching anything.
- v1.0.2: VLC did not follow the rotation in v1.0.1. Measured: the CMF L/R Test app's MOVIE
  button with a Dynamics Processing effect on its own session (what VLC does) reached the HAL
  unswapped at rotation 270 (the beep stayed left), the same button without it swapped. The
  HAL now swaps only the outputs carrying such a track (see the top of Status).
- v1.0.1: v1.0.0 played reversed in both orientations. Measured with the HAL's own recordings
  (`vendor.streamout.pcm.dump`, CMF L/R Test FULL CHECK): a left-only beep reaches the HAL on
  the right channel at rotation 270 and on the left at 90, in all four Dirac tunings, and from
  USB Audio Player Pro: Android already swaps it. The module's swap undid that; the
  `libaudioflinger.so` patch was loaded (checked in audioserver's own mappings) and changed
  nothing. Both are gone: stereo is again the v0.9.0-v0.9.4 HAL patch.
- v1.0.0 (wrong, replaced by v1.0.1): it patched the speaker swap in `libaudioflinger.so`, on
  the reading that Android's mixer caused the doubled swap; the HAL recordings later showed
  the swap still happening with that patch loaded.
- v0.9.9: the Action button's switch to Stereo crashed the audio service until a reboot.
  Magisk starts `action.sh` as `./action.sh`, so the module folder was "."; the stereo file
  was then mounted from `./system/...` resolved at init's root, i.e. `/vendor/...` itself:
  Magisk's empty placeholder (Magisk 31 builds `/vendor/lib64/hw` as a tmpfs skeleton).
  The failed switch then took the module's mounts off and restarted the HAL on those empty
  files; audioserver crash-looped (`stoi: no conversion`) and `system_server` and
  `audioserver` used a lot of CPU. Now the folder is always absolute, and a failed switch
  mounts the checked stock copies and restarts the HAL only once all three files read back
  as stock; otherwise it leaves the running HAL alone and asks for a reboot.
- v0.9.9: USB Audio Player Pro played reversed with the earpiece on the right once it played
  on the deep-buffer output. Measured: Nothing's audio service gives each app a Dirac
  tuning (VLC is on its video list -> MOVIE; apps on no list, like UAPP -> MUSIC), and only
  MUSIC swaps left and right with the rotation itself. The swap now follows
  `persist.vendor.newdirac.cur.config` / `.enable.value` instead of skipping the primary
  output.
- v0.9.8: after a Nothing OS update the old stereo overlay (patched from the previous build)
  would still have been mounted over the new vendor files; only two failed boots removed it.
- v0.9.7: the module was still listed in Magisk as by Tiimoo-debug; it now says Dr.Essence.
- v0.9.6: Magisk showed an out-of-date module description (Stereo "needs a reboot").
- v0.9.5: turned with the earpiece on your right, left and right came out reversed.
- v0.9.4: switching Mono and Stereo needed a reboot; it now restarts only the audio HAL.
  From a stereo boot, the stock files are rebuilt from the stereo ones (original bytes back,
  then hash-checked), so mono can be switched to live without ever having booted mono.
- v0.9.4: the daemon read the amp's volume every cycle, and the Awinic driver logs each read,
  so dmesg filled with `aw882xx_volume_get` lines (about 20 a minute) and lost the boot
  messages.
- v0.9.3: every mixer read started tinymix three times and every write five (its style check
  was cached inside a subshell and thrown away), on every 2 s daemon cycle. It is now detected
  once per process.
- v0.9.3: on/off waited on fixed sleeps: up to 2 s for the daemon to notice the stop, 1 s
  polling for it to exit, and a flat 2 s after restarting it. The daemon now stops the moment
  it is told to and both waits poll in tenths of a second.
- v0.9.3: finding the daemon started two programs for every process on the phone (several
  hundred), at least twice per on/off. It now checks only shells and the daemon itself.
  Measured in a test container with a running daemon: `on` 0.05 s, `off` 0.18 s.
- v0.9.3: `stereoctl status brief` for the app, without reading every control back.
- v0.9.2: earpiece gain was 31 (the codec's mute value), not the maximum.
- v0.9.1: three daemons fought over the mixer; `status` reported "not running".
- v0.9.0: true stereo: the HAL and Awinic DSP mono folds switched off in stereo mode.
