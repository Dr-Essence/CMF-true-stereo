<p align="center"><img src="https://raw.githubusercontent.com/Dr-Essence/CMF-true-stereo/main/docs/banner.png" alt="CMF true stereo - earpiece left, speaker right" width="100%"></p>

# CMF-true-stereo

**Real left/right stereo on the CMF Phone 1.** The earpiece becomes the left
speaker, the bottom speaker the right — no custom kernel, just root.

<p align="center">
  <a href="https://github.com/Dr-Essence/CMF-true-stereo/releases/latest"><b>Download the module</b></a> ·
  <a href="https://github.com/Dr-Essence/CMF-true-stereo-manager/releases/latest"><b>Get the app</b></a> ·
  <a href="#mono-and-stereo">How stereo works</a>
</p>

|  | |
|---|---|
| 🔊 **Stereo** | Earpiece = left, speaker = right. Games, films and music finally have sides. |
| 📢 **Mono** | Default. Both speakers play the full mix: louder and fuller than the bottom speaker alone. |
| 📱 **App** | *CMF Stereo*, a clean Nothing-style app: on/off, Mono/Stereo, two 1–10 levels. |
| 🛟 **Safe** | Patches nothing it has not verified, never touches the vendor partition, and undoes itself after two failed boots. |

### Install in three steps

1. Flash the zip in **Magisk / KernelSU / APatch** and reboot.
2. Open **CMF Stereo** and pick **Stereo**, or tap **Action** on the module's card in Magisk,
   or in a terminal: `su -c stereoctl channels stereo`.
   It switches at once (the sound stops for a moment; press play again).
3. Turn the phone sideways either way: left and right follow the screen.

Works on the **CMF Phone 1 (A015)**. On any other phone it installs and does
nothing.

> **Before you use stereo**
> - Stereo turns off Awinic's speaker protection for media (calls always keep
>   it). The module's own protection stands in: the speaker is held **6 dB
>   below the amp's full output** at its loudest (app speaker level 10, 2 dB
>   more per level down), its deepest bass is held back when it gets loud, and
>   the earpiece is kept from clipping. Use **Mono** for loud listening.
> - If the phone fails to boot twice in a row with stereo on, the module
>   removes stereo on its own and falls back to Mono.
>
> Details in [Mono and stereo](#mono-and-stereo).

## Status

**Current release: v1.0.6** (CMF Phone 1, Nothing OS B4.1, Android 16). Stereo works and is in
daily use on the test phone, with the module's own protection running in the audio HAL (deep
bass guard, earpiece limiter, optional speaker boost and earpiece leveller). Mono and Stereo switch without a reboot,
and Magisk offers new releases as updates. Left and right follow the phone's orientation for
every way apps play sound on this phone. "While playing" engages the earpiece for games and
music alike. The full history of findings, tests and fixes is in [CHANGELOG.md](CHANGELOG.md).

**Verified on the phone**
- v1.0.5 earpiece leveller: a clear difference on the earpiece side, with no distortion heard.
- Stereo: a left-only file plays on the earpiece only, the speaker's right slot silent, with
  Dirac on and off. Mono: both play the full mix.
- Switching Mono and Stereo at once (audio HAL restart, no reboot) from `stereoctl channels`,
  both apps and Magisk's Action button; Magisk's Update button.
- Left and right follow the rotation: ordinary apps and music players (USB Audio Player Pro,
  bit-perfect too), InShot, YouTube, games, VLC (its own audio effect: swapped by the HAL,
  v1.0.2), and the CMF L/R Test's MUSIC, MOVIE, MOVIE + EFFECT, GAME, SPEECH, AAUDIO, AAUDIO
  SHARED and FLOAT buttons.
- "While playing" (v1.0.3): games (`dsp_fast`) and music players (`dsp_music`, `dsp_primary`)
  both engage the earpiece.
- Protection (v1.0.4): `stereoctl protect` reports it running after the first sound, and
  every setting was tried and works (ceilings as designed, e.g. speaker level 5, bass strong:
  -4 dBFS on the signal, -20 dB below the amp's full output).
- Earpiece at the receiver amp's top step (+8 dB); hi-res playback still works in stereo.

**Not tested on a phone yet**
- **v1.0.6** telling the apps: after a change made outside CMF Stereo (`stereoctl`,
  Magisk's Action button, the daemon's switch back to mono, and once when the daemon starts)
  the module asks each installed app to read the state again (`content call ...
  --method stateChanged`), so Nothing Settings' Stereo speakers page and Sound row follow at
  once. Tested here: both apps' providers called (a stand-in `content`), 198 checks in four
  shells.
- Boost 6 over a longer listen (it was tried briefly with the other settings).
- The protection after a live switch from a mono boot: by design it starts only after a
  reboot (the library is not in place until then; stereo plays as v1.0.3, boost ignored).
- The safety nets that need a failure: the crash-loop guard (3 audio HAL restarts within a
  minute in stereo -> mono), the boot watchdog (two failed boots -> mono), a failed live
  switch ending on the stock files. Each is covered by the tests on fake files.
- The next Nothing OS update: the guard that turns stereo off for an unknown build, and
  re-staging during a module update.
- How the speaker holds up to long, loud stereo listening.

**Pending**
- After the next Nothing OS update: check the vendor file hashes and add the new build.
- Earpiece leveller (optional, not built): raises the earpiece's quiet and medium passages,
  peaks never above today's, no frequency changed.
- Known limit: an app with its own audio effect (VLC) and an ordinary app playing on the same
  output at once, earpiece on the right: one of them is reversed (the HAL sees only the mix).
- Compressed offload: Android refuses it on this phone (Dirac is on for the output mix), so
  apps never use it here; not worth testing further.
- A short clip of the two drivers splitting a game's or film's audio, for this page.

**Fixed recently**
- v1.0.4: in stereo the speaker got up to about 10 dB more deep bass than Awinic lets through
  in mono, and the earpiece clipped in its top 1.5 dB (CMF L/R Test DRIVER STUDY). The bass
  guard and the earpiece limiter hold both; a crash-loop guard puts the stock files back if
  the audio HAL keeps restarting in stereo.
- v1.0.3: "While playing" watched only the DSP's music task, so games played on the speaker
  only. It now watches every playback task.
- v1.0.2: VLC did not follow the rotation (Android leaves a track with its own audio effect
  unswapped); the HAL now swaps exactly those outputs.
- Older: [CHANGELOG.md](CHANGELOG.md).

---

## About

A Magisk / KernelSU / APatch module that makes the **CMF Phone 1** play media
out of its **earpiece as well as its bottom speaker** — in true stereo if you
want it.

It has two channel modes:

- **mono** (default, stock audio): both drivers play the same full mix —
  louder, fuller and taller than the single bottom-firing speaker. This was
  the whole module once, back when it was called cmf-fake-stereo.
- **stereo**: real left/right. The **earpiece plays the left channel and the
  speaker the right**. It costs Awinic's speaker-protection processing on
  media; the module's own protection (a fixed amp attenuation, a deep bass
  guard and an earpiece limiter, measured against what Awinic does) stands in. See
  [Mono and stereo](#mono-and-stereo).

Getting stereo took finding the two places the phone folds the speaker to
mono; the [Findings](#findings-what-this-device-actually-does) section shows
the measurements rather than asking you to take my word.

Verified on **A015 / Tetris, MT6878, Nothing OS B4.1, Android 16.**

## What it does

- **Real stereo** in stereo mode: earpiece = left channel, bottom speaker = right
- **Mono** mode: both speakers play the full mix, with full speaker protection
- Plays media through the earpiece alongside the speaker, automatically
- Earpiece at the receiver amp's maximum, +8 dB (`Handset Volume 0`), the same value the HAL uses
- Applies only while audio is playing, so the receiver is not held energised
- Steps aside for headphones and Bluetooth
- Restores every control it touches on stop, disarm or uninstall
- Disarms itself if it ever causes a failed boot
- Switch modes with `stereoctl channels mono|stereo`, the app, or the Action button on
  the module's card in Magisk / KernelSU / APatch; the stereo overlay removes itself after
  two failed boots
- Says on the module's card what is running: `[Stereo]`, `[Mono]`, `[Off]`, or
  `[Stereo unavailable]` after a Nothing OS update

## What it does not do

- **No Awinic protection on media in stereo.** Awinic's DSP processing is the
  part that folds to mono, so stereo replaces it with the module's own, simpler
  protection (see [Mono and stereo](#mono-and-stereo)). Its model of the
  speaker, live from the amp's current and voltage sense, is not copied.
- **No extra volume from the main speaker.** It is untouched.
- **Nothing on other devices out of the box.** It installs inert elsewhere and
  ships a probe to work out that device's routing.

## Quick start

Flash the zip (build it with `./build.sh`, or grab a release), reboot, play
something. That is the whole setup on a CMF Phone 1 — the verified routing is
preconfigured.

To check it is working, with audio playing:

```sh
su
stereoctl status     # all three controls should show want= matching now=
stereoctl solo       # speaker off, earpiece only - proves it is really the earpiece
stereoctl unsolo
```

For real stereo (applied at once):

```sh
su -c stereoctl channels stereo
```

If it is ever silent, `stereoctl doctor` walks every layer that can cause that
and names the one responsible.

## On other devices

It installs with an empty `actions.conf` and changes nothing. Run
`stereoctl probe` to dump the audio hardware — ALSA topology, every mixer
control, smart-amp drivers, HAL configs and MediaTek's AudioParam tree — then
`stereoctl report` to fold it into one shareable text file. The routing for
that device gets written into `actions.conf` from what the probe finds. See
[Why it ships empty elsewhere](#why-it-ships-empty-elsewhere).

---

## How it works

Three layers, smallest hammer first.

**1. Mixer actions (`actions.conf`).** The real work. An ALSA mixer control
somewhere enables the receiver output stage; on MediaTek there is usually also
a routing control that decides which DL (downlink) stream feeds it. Setting
those while the speaker is playing is what puts the earpiece to work next to
the speaker.

The audio HAL rewrites mixer controls on every route change, so a one-shot
write does not survive the next stream start. A small daemon re-asserts the
values every couple of seconds and — by default — only while audio is actually
playing, so the earpiece is not left energised all day.

Everything touched has its original value saved under
`/data/adb/cmf-stereo/state/` and restored on stop, disarm or uninstall.

**2. Audio policy overlay (`stereoctl xml-patch`, optional).** If the policy
declares the speaker as `AUDIO_CHANNEL_OUT_MONO`, the framework downmixes to
one channel before the HAL ever sees it, and no amount of mixer work brings
the second channel back. The patch widens only the speaker `<devicePort>` to
stereo, in an overlay copy — the vendor partition is never written. It is
opt-in, validated before it is installed, and reversible.

**3. What the CMF Phone 1 actually needed.** Worth recording, because it was
not any of the obvious answers and the probe is what found it.

Media on this device never touches the internal codec. Playback runs:

```
DL_24CH_CH1/CH2 ──▶ I2SOUT4_CH1/CH2 ──▶ Awinic aw_dev_0 smart PA ──▶ speaker
                                  ◀── I2SIN4 ──▶ UL3   (IV-sense feedback)
```

The earpiece hangs off the internal codec's DAC (`ADDA_DL`), and that DAC
normally has **no source connected at all** — every one of its ~20 input
switches sits Off. So pointing `RCV Mux` at the receiver routes it to a
silent wire, which is exactly what happened on the first attempt.

The switch that matters is `ADDA_DL_CH1 DL_24CH_CH1`: it feeds the internal
DAC from the same `DL_24CH` stream already going to the speaker amp. Turn it
on, then open `RCV Mux`, and the earpiece plays.

There is only one Awinic device (`aw_dev_0`), so there is no second amp
channel to press into service — the internal codec was the only way in.

That alone gives both drivers the same full mix: **mono mode**. Real stereo
needed one more step — switching off the two places the phone folds the
speaker to mono — which is what `stereoctl channels stereo` adds (see
[Findings](#findings-what-this-device-actually-does) and
[Mono and stereo](#mono-and-stereo)).

## Findings: what this device actually does

### Where the speaker is folded to mono

Earlier revisions of this section said both transducers were hard-wired to
channel 1, then that a custom kernel would be needed, then that the DSP
firmware was the limit. All three were wrong. Each stage was measured with a
test file that has sound on the left channel only and silence on the right,
by switching the amp to its right slot: silence there means the right channel
really is separate.

| Stage | Separate L/R? | Evidence |
|---|---|---|
| Android framework | Yes | `dumpsys media.audio_flinger`: speaker output is 2-channel FL/FR, *Master mono* off. The policy's speaker port is already stereo, so `stereoctl xml-patch` finds nothing to change. |
| Dirac (Nothing's speaker tuning) | Not the fold | Session-0 insert effect, 2-in/2-out presets. Removing it alone changed nothing. |
| MediaTek audio HAL (`audio.primary.mt6878.so`) | **Folds to mono** | `AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed` writes (L+R)/2 to both channels whenever `MTK_AUDIO_NUMBER_OF_SPEAKER` is 1. Patching it out alone: still mono. |
| Aurisys on the audio DSP, `smartpa_awinic` | **Folds to mono** | Awinic's speaker protection has one speaker model (`AW_DSP.bin`: five presets, each one 11,244-byte block for one speaker, all carrying 0.5/0.5 weights). With it replaced by MediaTek's pass-through `aurisys_demo` as well, the right slot went **silent** and the left slot still played. |
| AFE routing | Yes | `I2SOUT4_CH2 <- DL_24CH_CH2` is live during playback. |
| Awinic amp (`aw882xx`) | Yes | I2S slot select is register `0x06` bits 11:10 (`01` left, `10` right, `11` mono (L+R)/2), writable through the driver's `reg` attribute. Stock is left (`0x34e8`); on the right slot, cutting `I2SOUT4_CH2` silences the speaker. |
| Earpiece | Left channel | `RCV <- ADDA_DL_CH1 <- DL_24CH_CH1`; `ADDA_DL_CH1` has no CH2 source. |

A kernel never mattered: the routing, the amp driver, the HAL and the DSP
libraries are all vendor code. Setting `MTK_AUDIO_NUMBER_OF_SPEAKER` to 2 was
rejected: it also switches the HAL to a `dual_speaker_output` path that does
not exist in this phone's `audio_device.xml`, and puts Awinic's protection
into two-amp mode with one amp fitted.

### Protection: what Awinic does, and what stereo does

Measured with CMF L/R Test DRIVER STUDY (tones from 100 Hz to 8 kHz at -30 to -3 dBFS; the
HAL's and the DSP's own recordings of what reached them, and the HAL's raw 24-bit two-microphone
capture):

| | Awinic (mono, stock) | the module in stereo |
|---|---|---|
| Speaker peaks | about -5 dB below the amp's full output | about -6 dB (fixed attenuation); with boost, a limiter keeps them at -5 dB |
| 100 Hz | cut by 16 dB at every level | untouched while quiet; held at -8 / -14 / -20 dB below full output when loud (light / medium / strong) |
| 150 Hz-3 kHz | about +3.5 dB EQ | unchanged |
| Earpiece | (not Awinic's) clips in its top 1.5 dB of full scale | limited at -2.5 dBFS; optional leveller raises quiet passages, peaks unchanged |

Also measured: the speaker's resonance at about 1 kHz (from Awinic's current/voltage sense);
Dirac (MUSIC) adds +5 to +6 dB at 200-500 Hz, a limiter at about -0.2 dBFS and a second
harmonic on 100 Hz before either driver; the earpiece's whole path is at full level already
(no hidden attenuation to win back). The limiters add at most 1.2 % distortion while working
(50 Hz), under 0.1 % above 1 kHz; nothing changes while a signal is below its ceiling.

## Mono and stereo

**Checksums**: every release lists the SHA-256 of its files, in the description and in
`SHA256SUMS.txt`.

**Test files**: every release carries `LEFT_ONLY_3min.wav` (left channel only) and
`LEFT10s_RIGHT10s.wav` (spoken "left" / "right", then 10 s from that side only), built by
`tools/make-test-audio.py`. In Stereo the left-only file plays from the earpiece alone, or the
speaker alone when the phone is turned with the earpiece on your right; in Mono from both.

```sh
stereoctl channels            # what is running, and what is staged
stereoctl channels stereo     # switch to stereo now
stereoctl channels mono       # back to stock now
```

The CMF Stereo Manager app has the same switch, and so does the **Action** button on the
module's card in Magisk (28 or newer), KernelSU and APatch: each press switches to the
other mode and shows `stereoctl channels`' output.

**Switching without a reboot** (v0.9.4). The module restarts the audio HAL
(`setprop ctl.restart vendor.audio-hal`) on the wanted files instead of
rebooting: about a second of silence, players pause, calls are unaffected
(measured on the CMF Phone 1). Magisk bind-mounts each of the module's files over its
vendor path at boot, in init's mount namespace, which the HAL shares (measured).
A live switch takes those mounts of ours off (only ours: a mount from anywhere
else on those paths and the switch is refused) and mounts what the wanted mode
still needs: the staged files for stereo, nothing for mono, or, where Magisk
left a placeholder rather than the stock file, a copy of the phone's own stock
files (copied when it booted mono, or rebuilt from the stereo files by putting
the original bytes back, and kept only when it hashes to the stock build). Every
file is read back through `/proc/1/root` and must hash to the expected build;
the new HAL process must still be running 3 s later. If any check fails, or a
call is active, the mounts are undone and the change waits for a reboot.

**What stereo changes**, and nothing else:

1. **The HAL fold**: `doStereoToMonoConversionIfNeed` no longer folds to mono;
   it loads the module's protection library and calls it for every buffer
   (`hal-swap/patch.S`), and the DSP task is told the speaker is stereo
   (`hw_info` bit `0x4`, two branches). Four places; the stock bytes every
   earlier version changed are written back first, and the result must hash
   to the tested build.
2. **The DSP fold**: `AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA` runs
   `aurisys_demo` instead of `smartpa_awinic`. The phone's own
   `aurisys_config_rv.xml` already declares `aurisys_demo` for that scenario
   (2 channels in/out, IV reference), so this is a configuration the vendor
   file provides. **Calls keep `smartpa_awinic`** (`DSP_CALL_FINAL` is
   untouched).
3. **The amp slot**: while the earpiece plays, the daemon puts the amp on the
   right slot; whenever the earpiece is not playing, on mono (L+R)/2, so the
   speaker never plays one channel alone. The driver resets the slot on every
   stream start, so the first second or two of a stream is the stock left
   slot until the daemon's next cycle.
4. **Attenuation**: the amp is held `STEREO_ATTEN_DB` (default 6 dB) down
   through its own volume control, `aw_dev_0_volume` (1/8 dB steps, per the
   aw882xx driver), less the speaker boost while the protection runs. Mono
   gives the amp its previous value back.
5. **Protection** (`protect/cmfstereo.c`, `stereoctl protect`): see
   [Protection](#protection-what-awinic-does-and-what-stereo-does) below.

**No vendor file ships in this module** (the protection library is the
module's own code). Staging copies this phone's own
`audio.primary.mt6878.so`, `audio.primary.mediatek.so` and
`aurisys_config_rv.xml`, checks their SHA-256 against the analysed build,
patches them, and checks the result against the tested one before putting it
in the module's overlay with the original SELinux labels. Anything else —
another firmware, a different file — is refused and the phone stays on mono.
After a Nothing OS update the hashes will differ and stereo will refuse until
the new build has been checked.

**Risks, plainly:**


- Awinic's processing keeps the speaker within its excursion and temperature
  limits at high volume, from a live model of the speaker. In stereo, media gets
  the amp's hardware over-temperature / over-current cut-outs, the attenuation,
  and the module's fixed protection (peak and deep-bass limits measured against
  Awinic's, no temperature model). Use mono for loud listening, raise
  `STEREO_ATTEN_DB` if you play loud in stereo, and back off at the first
  distortion.
- If the audio HAL restarts 3 times within a minute in stereo, the daemon puts
  the stock files back (mono) at once.
- The earpiece has no protection in either mode (that was already true).
- Two failed boots with the stereo overlay in place remove it and set
  `CHANNELS=mono` — the same watchdog the audio-policy overlay has.
- With the daemon stopped (`stereoctl off`) the amp goes back to its stock
  left slot on the next stream, so in stereo the speaker would play the left
  channel alone. Switch to mono if you want the module off.
- **Orientation**: turned with the earpiece on your right, Android itself swaps left and
  right before the audio HAL (the HAL's own recordings show the channels already swapped at
  rotation 270), except for a track whose session has its own audio effect chain (VLC's
  Dynamics Processing): that one reaches the HAL unswapped. The daemon finds such tracks in
  `dumpsys media.audio_flinger` (only while playing at rotation 270: when playback starts, when
  the phone turns, and every third 2 s cycle) and writes the output flags of their mixer
  threads to `vendor.audiohal.cmf_swap`; the HAL swaps a speaker stream only when the
  rotation (`vendor.audiohal.cmf_rotation`, stored by the HAL from Android's `rotation`
  parameter) is 270 and its output is named there. v0.9.5-v1.0.0 swapped by output, by Dirac
  tuning, then by patching the mixer; each rule held only for the apps it was tested with.

MediaTek's "2nd loudspeaker" machinery **is** present on this build, in
`/vendor/etc/audio_param/`:

```
2nd Loudspeaker Compensation Filter (2nd-ACF)
2nd Loudspeaker High/Low Pass Filter Order
bes_loudness_Sep_LR_Filter
bes_loudness_L_*  /  bes_loudness_R_*   (separate L and R filter sets)
```

An earlier revision of this file claimed it was absent. That was wrong — it
came from the broken BRE greps fixed in the ERE commit, which reported a
clean zero for a pattern that never matched anything. Whether the feature is
merely MediaTek's stock parameter template or actually wired to a second
transducer on this hardware is unresolved.

---

## Commands

```
stereoctl status              module, daemon, and live control values
stereoctl doctor              diagnose why the earpiece is silent
stereoctl reset               clear saved state and start clean
stereoctl probe [dir]         dump the audio hardware
stereoctl report              fold the newest probe into one shareable .txt
stereoctl on | off            arm / disarm (off survives a reboot)
stereoctl solo | unsolo       speaker off, earpiece only - for auditioning
stereoctl guard on | off      re-enable / bypass the speaker-follows guard
stereoctl apply | revert      one-shot apply / restore
stereoctl restart             restart the watcher daemon
stereoctl log [n]             tail the log

stereoctl scan [pattern]      search the mixer for candidate controls
stereoctl ctl NAME [VALUE]    read or write one mixer control
stereoctl dump                every control and its value
stereoctl diff [seconds]      snapshot the mixer, wait, show what changed

stereoctl channels [mono|stereo]  show / choose the speaker channels (applied at once)
stereoctl protect                 stereo protection: settings, and whether it runs
stereoctl protect boost 0-6       speaker boost (dB less fixed attenuation, peaks still
                                  at Awinic's level; only while the protection runs)
stereoctl protect bass off|light|medium|strong
                                  deep bass guard (below 100 Hz, only when loud)
stereoctl protect earpiece on|off earpiece limiter (-2.5 dBFS)
stereoctl protect leveller off|light|medium|strong
                                  earpiece leveller (quiet passages up 4 / 8 / 12 dB at most)

stereoctl xml-patch           install the stereo speaker-port overlay (reboot)
stereoctl xml-revert          remove it (reboot)
```

`stereoctl ctl` is the one to experiment with: find a candidate with `scan`,
flip it while music plays, listen to the earpiece.

---

## Config

Lives in `/data/adb/cmf-stereo/`, survives module updates.

| file | what |
|---|---|
| `stereo.conf` | behaviour: mode, channels, attenuation, protection, poll interval, log level |
| `actions.conf` | the routing itself, one action per line |
| `stereo.log` | what the daemon did |
| `state/` | saved original values, used to revert |

`actions.conf` syntax:

```
ctl|<mixer control name>|<value>     set an ALSA mixer control
sysfs|<path>|<value>                 write to a sysfs node
prop|<property>|<value>              set a system property
```

`MODE=playback` (default) applies the routing only while something is playing.
`MODE=always` keeps it on permanently — louder in theory, harder on the
earpiece, and it costs idle power.

`PLAYBACK_CTL` / `PLAYBACK_VALUE` decide how "audio is playing" is detected:
one or more mixer controls separated by `|`, any of them reading the value
means playing. Empty means scan `/proc/asound` for a RUNNING substream — which
**misses DSP playback entirely**. On the CMF Phone 1 every kind of output has
its own DSP task switch (measured, logged each second: a game turns on
`dsp_fast_runtime_en`, a music player `dsp_music_runtime_en` with
`dsp_primary_runtime_en`; `dsp_playback_runtime_en` stays on even when idle),
so the installer sets all six playback tasks. Controls that cannot be read
fall back to the procfs scan rather than reporting "never playing" forever.

`SPEAKER_BOOST` (0-6, default 0), `BASS_PROTECT` (off / light / medium /
strong, default medium), `EARPIECE_LIMIT` (on / off, default on) and
`EARPIECE_LEVELLER` (off / light / medium / strong, default off) set the stereo
protection; change them with `stereoctl protect` or the apps.

`GUARD_CTL` / `GUARD_VALUE` gate the routing on a mixer control's value. On
the CMF Phone 1 the guard is `aw_dev_0_switch` = `Enable`: the HAL disables
the speaker amp when headphones or Bluetooth take over, so the earpiece
follows the speaker instead of playing to nobody. One mixer read per cycle,
no `dumpsys`.

### Earpiece gain, and how loud it can get

`Handset Volume` is the receiver amp's gain on the MT6369 codec. Read from the
codec driver (`snd-soc-mt6369.ko`): the control's range is 0–18, and the
register runs the opposite way to the dB scale ALSA advertises for it:

| value | gain |
|---|---|
| 0 | **+8 dB** (loudest) |
| 8 | 0 dB |
| 18 | −10 dB |
| 31 | −40 dB (the codec's mute value) |

Evidence: every output reads 31 at rest; the driver's put handler treats 31
as a special case; and the HAL itself sets 0 whenever it drives the receiver.

**Versions before v0.9.2 shipped 31**, believing it was the top. That made
the daemon pull the earpiece down to −40 dB every cycle while the HAL kept
putting it back to +8 dB — the `Handset Volume: 0 -> 31` lines repeating in
the log, and an earpiece that sounded weak and uneven. The installer now
corrects any value above 18 to 0. The two earlier explanations in this README
(that 31 was the ceiling, then that the control barely mattered) were both
wrong; recorded rather than quietly edited, because the mistake is the useful
part.

`ADDA_DL_GAIN`, the digital gain before the DAC, is left alone: the HAL parks
it at 63311 of 65535 (−0.3 dB), and `ADDA_DL` is shared with the headphone
path.

The earpiece is a receiver: it will not match the speaker, and it has no
protection circuit. In stereo, balance the two by turning the **speaker** down
(`STEREO_ATTEN_DB`), not by pushing the earpiece.

## Why it ships empty elsewhere

The mixer control names are device-specific. A wrong write is, in ascending
order of regret: nothing, silence, a HAL crash, or an earpiece driven past
what a receiver is built for. The earpiece has a fraction of the excursion and
power handling of the main speaker and there is no protection circuit assuming
you will use it for music.

So: probe first, then fill in real names. When you find a working route, start
its gain low and raise it a step at a time. Distortion or rattle means back
off — that damage does not come back.

---

## Safety and recovery

**Boot watchdog.** If two consecutive boots fail to reach `sys.boot_completed`
while the policy overlay is active, `post-fs-data.sh` deletes the overlay
before it can be mounted again. A bad policy costs one extra reboot instead of
a trip to recovery.

**XML validation.** No patched policy is installed unless it passes a
structural check — balanced `<module>`, `<mixPort>`, `<devicePort>` and
`<route>` elements, intact root tag, no stray backslashes from a bad
insertion. Android has no `xmllint`, and a malformed audio policy takes
`audioserver` down hard enough to loop the boot.

**Nothing OS updates.** An update replaces the vendor audio files the stereo
overlay was patched from. Before anything is mounted at boot, `post-fs-data.sh`
checks the vendor files against the analysed build; if they differ, the stereo
overlay is removed and the phone boots on stock mono. The module's card and
`stereoctl status` (`build: updated`) then say stereo is unavailable until a
module release supports the new build.

**Manual recovery**, if you ever need it:

```sh
adb wait-for-device shell           # or hold vol-down for safe mode
su
touch /data/adb/modules/cmf_stereo/disable
reboot
```

Both Magisk and KernelSU honour the `disable` file, and `post-fs-data.sh`
never touches audio when the actions list is empty.

---

## Credit: the Hi-Res Audio module

This module owes a real debt to
[**Hi-Res Audio™** by Adinata (@Adivenxnataly)](https://github.com/adivenxnataly/Hi-ResAudio).

It is the reason we knew where to look. Before finding it, "use the earpiece
as a second speaker on a MediaTek phone" was a vague idea with no entry point.
That module is what pointed at MediaTek's `2nd Loudspeaker` / `bes_loudness`
machinery and at the earpiece `<devicePort>` channel mask — and working out
why those particular levers *don't* pan out on the CMF Phone 1 is what led to
the routing that does. Reverse-engineering a vendor audio stack and giving the
result away for free is generous work, and this project started from it.
Thank you.

It also aims at a different goal — high-resolution output, not dual speakers —
so it is worth trying on its own terms if that is what you want.

### One bug worth reporting upstream

Tested against `v2.0 with aaudio_mmap`, versionCode 20000, commit `78706f5`
(2025-06-12). It bootlooped a CMF Phone 1, and the cause is a small typo with
large consequences. In `customize.sh`:

```sh
name="Apply Same Filter Setting with 2nd Loudspeaker\/>
```

The attribute value is never closed — `name="` opens a quote, then text, then
`/>`, with no closing `"`. The fix is one character:

```sh
name="Apply Same Filter Setting with 2nd Loudspeaker\"\/>
```

Without it, this reaches `Playback_ParamTreeView.xml`:

```xml
<Field ... name="Apply Same Filter Setting with 2nd Loudspeaker/>
```

MediaTek's AudioParamParser cannot parse that, so the audio HAL aborts on
every boot. The `sed` fires on any device carrying a `bes_loudness_L_lpf_order`
field.

Two other things to be aware of on a device like this one: it forces
`aaudio.mmap_policy=3` / `aaudio.mmap_exclusive_policy=3` plus
`killall audioserver`, which needs a HAL with an MMAP PCM path; and it sets
the speaker channel mask to `AUDIO_CHANNEL_OUT_SURROUND`, which not every
speaker port accepts.

And a correction to an earlier version of this file, which claimed its
`<mixPort>` insertions land mid-element: **they do not.** It computes the
correct insertion point (`POL + POLD - 1`, the last line of the
`primary output` block) and only writes when that matches a known constant,
so placement is self-consistent, and otherwise it skips. That claim was wrong
and is retracted.

### Why its stereo approach doesn't work on this device

Not a criticism of the approach — it is sound on hardware that has a second
loudspeaker. Two things stop it here (this module's stereo comes from a
different route entirely, see [Mono and stereo](#mono-and-stereo)):

- `Playback_ParamTreeView.xml` is the **view definition** for MediaTek's
  parameter tuning tool (`TreeRoot`, `Feature`, `FieldList`,
  `CategoryPathList`). The runtime coefficients live in
  `PlaybackACF_AudioParam.xml`. Editing the view changes which fields a tuning
  application displays, not what the DSP does.
- On the CMF Phone 1 every `bes_loudness_R_*` value and
  `bes_loudness_Sep_LR_Filter` read `0x0` — MediaTek's stock template,
  untuned, because this phone has no second loudspeaker. And 2nd-ACF is a
  *filter* feature: it applies a different EQ curve to a second transducer's
  channel, it does not create a route to one.

What this module took from it: edit the element you mean to change, validate
the result, and keep a way back. Hence the block-aware `awk`, the XML
structural check, and the boot watchdog.

Do not run both modules at the same time — they touch the same files.

---

## tinymix

Mixer controls cannot be read or written without a `tinymix` binary, and the
CMF Phone 1 ships none. The module bundles one: a statically linked `aarch64`
build of upstream tinyalsa, hardware backend only, no `dlopen`. Provenance,
license and the exact build command are in [`bin/README.md`](bin/README.md).

If you would rather not trust a shipped binary, build it yourself and drop it
at `/data/adb/cmf-stereo/bin/tinymix` (`chmod 0755`) — that path is searched
first. Termux's `tinyalsa` package works too.

Search order: `/data/adb/cmf-stereo/bin`, the module's `bin/`, `/vendor/bin`,
`/system/bin`, `/odm/bin`, `/data/local/tmp`, then `$PATH`. A vendor-supplied
`tinymix` wins over the bundled one. Both the tinyalsa 1.x
`tinymix NAME VALUE` and the 2.x `tinymix set NAME VALUE` calling conventions
are handled, detected via `--help` rather than by guessing from an error
message.

---

## Uninstall

Remove it in your root manager. `uninstall.sh` stops the daemon and restores
every control it touched. `/data/adb/cmf-stereo/` is left in place so a
reinstall does not lose your routing; delete it by hand for a clean slate.

---

## Development

### How a sound gets from an app to the two drivers (stereo)

```
app -> Android's mixer (AudioFlinger)            swaps L/R itself at rotation 270,
                                                 except a track with its own effect
    -> Dirac (Nothing's tuning, session 0)
    -> audio HAL, AudioALSAPlaybackHandlerBase   patched: hal-swap/patch.S loads
       ::doStereoToMonoConversionIfNeed          protect/libcmfstereo.so and calls it
         rotation swap (VLC-type outputs)        <- vendor.audiohal.cmf_swap (daemon)
         speaker: bass guard, peak limiter       <- vendor.audiohal.cmf_*_ceil (daemon)
         earpiece: leveller, limiter
    -> audio DSP, aurisys_demo (pass-through)    aurisys_config_rv.xml patched
    -> DL_24CH ch1 -> codec DAC -> earpiece      routing: config/actions.cmf1.conf
       DL_24CH ch2 -> Awinic amp (right slot) -> speaker   amp slot/attenuation: daemon
```

Measured end to end with the HAL's and the DSP's own recordings: nothing after the patched
function changes the level, so the library's ceilings are exact.

### Files

| path | what |
|---|---|
| `customize.sh` | install: device check, config kept across updates, stereo re-staged |
| `post-fs-data.sh` | before Magisk mounts: boot watchdog, unknown-build guard |
| `service.sh` | after boot: stock copies saved, the daemon started |
| `action.sh` | Magisk's Action button: Mono <-> Stereo |
| `scripts/common.sh` | config, logging, tinymix access, playback detection, the routing actions, the module card's text |
| `scripts/channels.sh` | stereo: vendor file hashes and patches, staging, live switching, the amp, protection settings, crash-loop guard |
| `scripts/stereo-daemon.sh` | keeps routing, amp slot, attenuation, rotation swap and protection applied while playing |
| `scripts/stereoctl` | the CLI the apps and users call |
| `scripts/probe.sh` | hardware dump |
| `scripts/xml_patch.sh` | audio-policy overlay (opt-in, not for this device) |
| `hal-swap/` | the HAL patch in ARM64 assembly, and its emulator harness (`run.sh`) |
| `protect/` | the protection library (`cmfstereo.c`), its host tests and reproducible NDK build (`build.sh`) |
| `config/` | default settings and the verified CMF Phone 1 routing |
| `bin/tinymix` | static aarch64 tinyalsa build, see `bin/README.md` |
| `tests/` | the off-device test suite and its recorded fixtures |
| `tools/make-test-audio.py` | makes the left-only / left-right test files |

### Checks

```sh
sh tests/run-tests.sh      # 194 checks; run under sh, dash, mksh and busybox sh
sh hal-swap/run.sh         # the HAL patch in qemu-aarch64 (needs clang, ld.lld, qemu)
sh protect/build.sh        # the library rebuilds byte for byte (needs the NDK)
./build.sh                 # the flashable zip
```

Every vendor file is patched only after its hash proves it is the analysed build, and the
result is hashed again; `hal-swap/run.sh` checks the bytes `channels.sh` writes against the
assembled patch.

---

## Credits and licence

- **[Dr.Essence](https://github.com/Dr-Essence)**: author and maintainer. Ideas, design decisions, and every test on a real phone (logs, recordings, measurements) that the work here rests on.
- Code written with [Claude Code](https://claude.com/claude-code).

The module is © 2026 Dr.Essence under [CC BY-NC-SA 4.0](LICENSE): use, copy,
change and share it, as long as you credit Dr.Essence, do not use it
commercially (including selling it or anything built from it), and share
changed versions under the same licence. Releases up to v0.9.6 were published
under 0BSD; copies obtained under it keep those terms.

`bin/tinymix` is a statically linked `aarch64` build of
[tinyalsa](https://github.com/tinyalsa/tinyalsa), BSD-3-Clause. Its licence,
upstream commit and exact build command are in
[`bin/README.md`](bin/README.md), so you can reproduce it rather than trust
the shipped binary.

Thanks to **Adinata ([@Adivenxnataly](https://github.com/adivenxnataly))**,
whose [Hi-Res Audio™](https://github.com/adivenxnataly/Hi-ResAudio) module
pointed this project at the right part of MediaTek's audio stack.

Thanks also to the people who worked out this mod on other hardware and wrote
it up —
[OnePlus 6](https://www.xda-developers.com/oneplus-6-stereo-speaker-mod/),
[Xiaomi Merlin](https://github.com/Charlie-117/merlin_DualSpeaker_mod),
[LeEco Le Max 2](https://github.com/J3is/Dual-Speaker-x2),
[whyred](https://xdaforums.com/t/magisk-dual-speaker-mod-for-whyred.3845595/).
Their write-ups of duplicated-mono "dual speaker" mods are what this project
set out to go beyond: mono mode is that, stereo mode is real left/right.

Built with [Claude Code](https://claude.com/claude-code) against a real
CMF Phone 1 — every routing claim here came from measurements on the device,
not from documentation.
