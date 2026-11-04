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
