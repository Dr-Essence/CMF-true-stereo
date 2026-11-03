# Security policy

## Supported versions

Only the latest release of **CMF-true-stereo** gets fixes. Please update and check the
problem still happens before reporting.

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately through GitHub instead: on this repository open the
**Security** tab and choose **Report a vulnerability**. Only the maintainer
sees the report.

Include what you can of:

- the version, your phone model and Android / Nothing OS build;
- what happens, and the steps or input that trigger it;
- logs (`logcat`, the module's own log) or a proof of concept.

## What counts as a security problem here

This module runs as root and changes how the phone's audio stack is set up, so
these are in scope:

- anything that lets another app, file or user get root code run through the
  module's scripts (`stereoctl`, the daemon, the installer), for example via
  its config or state files in `/data/adb/cmf-stereo`;
- the module writing to, deleting or mounting over anything outside what it
  documents (its own folder, its config, the stereo overlay it builds);
- stereo staging accepting or producing a vendor file other than the verified
  ones, or the hash checks being bypassable;
- a way to cause a bootloop the boot watchdog does not recover from;
- anything that can drive the speaker or earpiece past safe levels without the
  user asking for it.

Ordinary bugs, crashes that need no special input, and feature requests
belong in regular issues.

## What to expect

You will get an acknowledgement as soon as the report has been read. Confirmed
problems are fixed in the next release, and you will be credited in its notes
unless you would rather not be. Please allow a fix to ship before disclosing
the details publicly.
