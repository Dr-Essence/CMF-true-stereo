# Working rules for this repo

- **Never assume.** Find the cause in evidence from the phone (logs, dumps, recordings,
  disassembly) before changing anything; ask for the exact dump that settles a question
  instead of shipping a guess.
- **Test before each build.** Run `sh tests/run-tests.sh` where it exists, check every change
  against the code it touches, and say plainly what was and was not verified.
- **Keep the README's Status section current with every change.** Each commit that changes
  behaviour also updates it: the current version and state, what is pending, which features
  have not been tested on a phone yet, which tests are pending (and what evidence they need),
  and the bugs fixed. A change is not finished while the Status section still describes the
  build before it.
- **Never risk the hardware or the boot.** Speaker and earpiece safety come before loudness;
  anything mounted at boot needs a watchdog and a way back.

# Next release (agreed 2026-11-17)

CMF Stereo is paused apart from bug fixes. The next release carries:
1. **The call bug fix**, once a phone test confirms the cause: while a call is active the
   daemon neither applies nor restores the earpiece controls. Tests before it counts as fixed:
   music playing, then a call answered on the earpiece, with the daemon on (must work) and the
   log showing no restore during the call.
2. **A separate download counter for Magisk updates:** the same zip attached twice,
   `CMF-true-stereo-<ver>.zip` (manual downloads) and `CMF-true-stereo-<ver>-update.zip`
   (linked only from update.json's zipUrl), both in SHA256SUMS.txt. No tracking in the module:
   only GitHub's per-file download counts.
