# Content of the CMF True Stereo user manual (module v1.0.9-beta).
# Every fact here comes from the module's own repository: README.md, CHANGELOG.md,
# docs/releases/*.md, module.prop, config/*.conf, customize.sh, post-fs-data.sh,
# service.sh, action.sh, uninstall.sh and scripts/*. Section titles are plain text
# (the layout script escapes them); section bodies are HTML.

TITLE = "CMF True Stereo"
SUBTITLE = "Real left and right stereo for the CMF Phone 1"
VERSION = "v1.0.9-beta"

CHAPTERS = [

# ---------------------------------------------------------------------------
# 1. Welcome
# ---------------------------------------------------------------------------
{"title": "Welcome",
 "intro": "<p>What CMF True Stereo is, what it needs, and the few things to know before you play anything loud.</p>",
 "sections": [

{"title": "What CMF True Stereo is",
 "html": """
<p>CMF True Stereo is a root module for the <strong>CMF Phone 1</strong>. It makes the phone play media from its <strong>earpiece as well as its bottom speaker</strong>.</p>
<p>In <strong>Stereo</strong> the two become a real left and right pair. Left and right follow the screen, however you turn the phone. Games, films and music finally have sides.</p>
<p>You do not need a custom kernel. You only need root, through Magisk, KernelSU or APatch.</p>
<ul>
<li>It never writes to the vendor partition.</li>
<li>It only patches files it has checked are the exact ones it was built for.</li>
<li>It undoes its stereo change by itself after two failed boots.</li>
</ul>
<div class="tech">
<p><strong>Names.</strong> The project is called <em>CMF-true-stereo</em> (it was once called <em>cmf-fake-stereo</em>, when it only did what Mono does today). In your root manager the module is listed as <code>CMF Phone 1 Dual Speaker (mono / stereo)</code>, by Dr.Essence, with the module id <code>cmf_stereo</code>. The command-line tool is <code>stereoctl</code>.</p>
</div>
"""},

{"title": "The two modes at a glance",
 "html": """
<table>
<tr><th>Mode</th><th>What you hear</th><th>Speaker protection</th></tr>
<tr><td><strong>Mono</strong> (default)</td><td>Both the earpiece and the speaker play the full mix. Louder, fuller and taller than the bottom speaker alone.</td><td>Awinic's own speaker protection, as on a stock phone.</td></tr>
<tr><td><strong>Stereo</strong></td><td>The earpiece and the speaker play left and right, following how you hold the phone.</td><td>Awinic's protection is off for media (calls keep it). The module's own protection stands in.</td></tr>
</table>
<p>You can switch between them at any time, and the change happens at once, without a reboot. Chapter 4 explains both modes in full.</p>
"""},

{"title": "What you need",
 "html": """
<ul>
<li>A <strong>CMF Phone 1 (A015)</strong>.</li>
<li><strong>Root</strong> through Magisk, KernelSU or APatch.</li>
<li>For the <strong>Action button</strong> on the module's card: Magisk 28 or newer, KernelSU or APatch.</li>
<li>Optional: the companion app <strong>CMF Stereo</strong> (or CMF Stereo Pro), if you would rather not use a terminal.</li>
<li>Optional: a terminal with root, such as Termux with <code>su</code>, or <code>adb shell</code> then <code>su</code>.</li>
</ul>
<div class="tech">
<p>The installer expects Android 12 or newer (API 31). On older Android it prints <code>! Android 12 or newer expected; continuing anyway.</code> and carries on.</p>
</div>
"""},

{"title": "The phone and build it was tested on",
 "html": """
<p>Everything in this manual was measured on one CMF Phone 1 (A015), EEA region:</p>
<table>
<tr><th>Part</th><th>Version</th></tr>
<tr><td>Nothing OS</td><td>4.1, <code>Tetris-B4.1-260615-1652-EEA</code> (<code>ro.build.display.id</code> B4.1-260615-1652, product TetrisEEA)</td></tr>
<tr><td>Android</td><td>16 (<code>BP2A.250605.031.A3</code>), security patch 2026-06-01</td></tr>
<tr><td>Vendor</td><td><code>UP1A.231005.007</code> (the Android 14 vendor image, where the audio HAL is)</td></tr>
<tr><td>Chip</td><td>MediaTek MT6878 (code name Tetris)</td></tr>
</table>
<p><strong>Other regions</strong> (Global, India) are untested. The module checks the audio files by hash and only patches the exact ones it was built for. On a build whose files differ, it refuses Stereo and stays in Mono.</p>
"""},

{"title": "Safety first",
 "html": """
<div class="warn">
<p><strong>Read this before you use Stereo.</strong></p>
<ul>
<li><strong>Stereo turns off Awinic's speaker protection for media.</strong> Calls always keep it. In its place the module holds the speaker <strong>6 dB below the amp's full output</strong> at its loudest (app speaker level 10), and 2 dB more for each level down. Its deepest bass is held back when it gets loud, and the earpiece is kept from clipping.</li>
<li>These are <strong>fixed limits</strong>. There is <strong>no temperature model</strong> of the speaker in Stereo, as Awinic has in Mono.</li>
<li><strong>Use Mono for long, loud listening.</strong> In Stereo, lower the speaker level and back off at the first distortion.</li>
<li><strong>The earpiece is a receiver.</strong> It is a small driver with a fraction of the speaker's movement and power handling, and it has no protection circuit of its own. In Stereo the module's earpiece limiter (on by default) keeps it below where it crackles. In Mono the earpiece plays without that limiter.</li>
<li>Distortion or rattle means <strong>back off</strong>. That kind of damage does not come back.</li>
</ul>
</div>
<p>If the phone fails to boot twice in a row with Stereo on, the module removes Stereo by itself and falls back to Mono. Chapter 8 lists every safety net.</p>
"""},

{"title": "What it does",
 "html": """
<ul>
<li><strong>Real stereo</strong> in Stereo mode: the earpiece and the bottom speaker play left and right, following the screen.</li>
<li><strong>Mono</strong> mode: both speakers play the full mix, with Awinic's speaker protection on the speaker.</li>
<li>Plays media through the earpiece alongside the speaker, automatically.</li>
<li>Drives the earpiece at the receiver amp's maximum, +8 dB, the same value the audio HAL itself uses.</li>
<li>Works only while audio is playing (by default), so the earpiece is not held energised all day.</li>
<li>Steps aside for headphones and Bluetooth.</li>
<li>Puts back every control it touches when it stops, is turned off, or is uninstalled.</li>
<li>Lets you switch modes with <code>stereoctl channels mono|stereo</code>, the app, or the Action button on the module's card.</li>
<li>Shows on the module's card what is running: <code>[Stereo]</code>, <code>[Mono]</code>, <code>[Off]</code>, or <code>[Stereo unavailable]</code> after a Nothing OS update.</li>
</ul>
"""},

{"title": "What it does not do",
 "html": """
<ul>
<li><strong>No Awinic protection on media in Stereo.</strong> Awinic's processing on the audio DSP is the part that folds the sound to mono, so Stereo replaces it with the module's own, simpler protection. Awinic's live model of the speaker, built from the amp's current and voltage sense, is not copied.</li>
<li><strong>No extra volume from the main speaker.</strong> The speaker's own path is untouched; in Stereo it is in fact held a little lower.</li>
<li><strong>Nothing on other phones out of the box.</strong> On any other device it installs inert, and ships a probe to work out that device's routing.</li>
<li><strong>No custom kernel</strong>, and no write to the vendor partition.</li>
<li><strong>No vendor file is shipped.</strong> Stereo is built from your own phone's files, after checking them.</li>
</ul>
"""},

{"title": "The companion app, CMF Stereo",
 "html": """
<p>The module works fully on its own. The app is an optional, friendly front end. It comes in two editions that can be installed side by side:</p>
<table>
<tr><th></th><th>CMF Stereo</th><th>CMF Stereo Pro</th></tr>
<tr><td>For</td><td>everyday listening</td><td>tuning and diagnosing</td></tr>
<tr><td>Controls</td><td>on/off, Mono/Stereo, earpiece and speaker level 1&ndash;10, speaker boost, deep bass guard, earpiece leveller and limiter</td><td>the same in raw values, plus solo, doctor, mode, mixer tools, diff, probe, logs and the config files</td></tr>
<tr><td>Look</td><td>Nothing style, NDot type in green</td><td>Material dark</td></tr>
</table>
<p>Both offer a Quick Settings tile. With LSPosed, each can also add a <strong>Stereo speakers</strong> row in Nothing's Settings &gt; Sound and a full Stereo page inside Settings.</p>
<p>Everything the apps do is a call to the module's own <code>stereoctl</code>, or an edit to the files in <code>/data/adb/cmf-stereo/</code>. The module stays the source of truth, and the terminal keeps working exactly as before.</p>
<div class="note"><p>The app needs root, superuser permission for itself, and the module flashed and rebooted first. Its own manual is in its repository, <em>CMF-true-stereo-manager</em>.</p></div>
"""},

{"title": "This version and its beta status",
 "html": """
<p>This manual describes <strong>v1.0.9-beta</strong> (internal version 1090). Versions are marked <em>beta</em> from this release on, because the module is still in testing. Nothing in the module changed since v1.0.8; the new number lets your root manager offer it as an update.</p>
<p>Stereo works and is in daily use on the test phone. Some features have been tested only on fake files, not on a phone yet; section 12.13 lists them.</p>
"""},

{"title": "How to read this manual",
 "html": """
<p>Each section starts in plain language. Precise technical detail follows in boxes like these:</p>
<div class="note"><p><strong>Tip.</strong> Something useful, not essential.</p></div>
<div class="warn"><p><strong>Safety warning.</strong> Read these. They protect your speaker, your earpiece and your ears.</p></div>
<div class="tech"><p><strong>Technical detail.</strong> Exact file names, values and mechanisms, for those who want them.</p></div>
<p>Commands are shown like <code>stereoctl status</code>. Run them in a root shell (see section 6.1). Example output marked <code>&lt;pid&gt;</code> or similar stands for a value that differs on your phone.</p>
"""},

]},

# ---------------------------------------------------------------------------
# 2. Installing
# ---------------------------------------------------------------------------
{"title": "Installing",
 "intro": "<p>Flash, reboot, play something. This chapter walks through each step, shows what the installer tells you, and covers updates, other phones and removal.</p>",
 "sections": [

{"title": "Install in three steps",
 "html": """
<ol>
<li>Flash the zip in <strong>Magisk</strong>, <strong>KernelSU</strong> or <strong>APatch</strong>, and reboot.</li>
<li>Choose Stereo if you want it: open <strong>CMF Stereo</strong> and pick <strong>Stereo</strong>, or tap <strong>Action</strong> on the module's card, or run <code>su -c stereoctl channels stereo</code> in a terminal. It switches at once: the sound stops for a moment, then press play again.</li>
<li>Turn the phone sideways either way. Left and right follow the screen.</li>
</ol>
<p>On a CMF Phone 1 that is the whole setup: the verified routing is preconfigured. After the first reboot the phone is in <strong>Mono</strong>, the default.</p>
"""},

{"title": "Getting the zip and checking it",
 "html": """
<p>Download the module from the project's releases page (<em>CMF-true-stereo</em>, latest release). If you build it yourself, <code>./build.sh</code> in the repository makes the flashable zip.</p>
<p>Every release lists the <strong>SHA-256 checksum</strong> of each file, in the release description and in <code>SHA256SUMS.txt</code>. Compare it with your download to be sure it is the genuine file.</p>
<pre>sha256sum CMF-true-stereo-v1.0.9-beta.zip</pre>
<div class="note"><p>Every release also carries two test files, <code>LEFT_ONLY_3min.wav</code> and <code>LEFT10s_RIGHT10s.wav</code>. Keep them: section 3.9 shows how to use them.</p></div>
<div class="tech"><p>The exact zip file name on the release page may differ from the example above; use the name of the file you downloaded.</p></div>
"""},

{"title": "Installing with Magisk",
 "html": """
<ol>
<li>Open Magisk and go to its <strong>Modules</strong> page.</li>
<li>Install the module zip from storage.</li>
<li>Read the installer's output (section 2.5), then <strong>reboot</strong>.</li>
</ol>
<p>After the reboot the module's card shows its state in its first words, for example <code>[Mono] Both speakers play the full mix.</code> The <strong>Action</strong> button on the card needs Magisk 28 or newer.</p>
<p>From v0.9.6 on, Magisk shows an <strong>Update</strong> button on the card when a new release is out, and installs it straight from the release page.</p>
"""},

{"title": "Installing with KernelSU or APatch",
 "html": """
<p>Flash the same zip from the Modules page of KernelSU or APatch, then reboot. Everything in this manual works the same way:</p>
<ul>
<li>the module's card shows the live state;</li>
<li>the <strong>Action</strong> button switches between Mono and Stereo;</li>
<li>updates are offered on the card;</li>
<li>the <code>disable</code> file for manual recovery is honoured (section 8.9).</li>
</ul>
"""},

{"title": "What the installer does and prints",
 "html": """
<p>The installer deliberately does nothing to the audio stack. It lays down the tools and the settings, and tells you what to do next. On a CMF Phone 1 you will see lines like these:</p>
<pre>  CMF Phone 1 - stereo speaker
  ----------------------------
  device   : &lt;model&gt; (&lt;device&gt;)
  platform : &lt;platform&gt; / &lt;manufacturer&gt;
  android  : &lt;version&gt; (API &lt;n&gt;)

  installed default stereo.conf
  guard: earpiece follows the speaker amp
  playback detected on every DSP playback task (music, fast, primary, ...)
  installed the CMF Phone 1 routing profile
  channels : mono (stock). 'stereoctl channels stereo' for L/R

  tinymix  : bundled (this device ships none)
             static aarch64 build of upstream tinyalsa;
             provenance in bin/README.md
  actions  : 3 configured

  Next steps
  ----------
  1. reboot
  2. play something
  3. stereoctl status   (should show the routing applied)

  Earpiece gain: Handset Volume 0 = +8 dB (loudest),
  18 = -10 dB. Raise the number in actions.conf for a
  quieter earpiece; back off at the first buzz.</pre>
<div class="tech">
<p>Step by step, the installer:</p>
<ol>
<li>checks the device: it looks for <code>Tetris</code>, <code>A015</code> or <code>CMF</code> in <code>ro.product.device</code> and <code>ro.product.model</code>;</li>
<li>creates <code>/data/adb/cmf-stereo/</code> with <code>state/</code> and <code>bin/</code>, and installs <code>stereo.conf</code> there (or keeps yours, section 2.11);</li>
<li>on a CMF Phone 1, sets the guard (<code>GUARD_CTL='aw_dev_0_switch'</code>, <code>GUARD_VALUE='Enable'</code>) and the playback detector (the six DSP task switches, section 7.10);</li>
<li>installs the CMF Phone 1 routing profile as <code>actions.conf</code>, unless you already have one with real content;</li>
<li>resets the boot watchdog counter (<code>boot_pending</code> = 0) and sets file permissions;</li>
<li>if your settings say <code>CHANNELS=stereo</code>, stages Stereo again from your phone's files (it refuses, and sets Mono, if they do not check out);</li>
<li>reports which <code>tinymix</code> will be used and how many actions are configured.</li>
</ol>
</div>
"""},

{"title": "The first boot",
 "html": """
<p>After the reboot the module waits for Android to finish starting, then a further <strong>10 seconds</strong> (<code>STARTUP_DELAY</code>), before it touches anything. This lets the audio system settle.</p>
<p>From then on a small background service (the <em>daemon</em>) watches for sound. When something plays on the speaker, it switches the earpiece on; when everything stops, it switches it off again.</p>
<div class="tech">
<p>At boot, <code>post-fs-data.sh</code> runs first (before Magisk mounts anything): the boot watchdog and the unknown-build guard. Then <code>service.sh</code> waits for <code>sys.boot_completed</code> (up to 180 s), marks the boot healthy, keeps a hash-checked copy of the stock audio files, notes whether this is the analysed build, updates the card's text, and starts <code>scripts/stereo-daemon.sh</code>. Section 11.11 has the details.</p>
</div>
"""},

{"title": "Checking that it works",
 "html": """
<p>Play some music, then open a root shell and run:</p>
<pre>su
stereoctl status     # all three controls should show want= matching now=
stereoctl solo       # speaker off, earpiece only - proves it is really the earpiece
stereoctl unsolo     # back to normal</pre>
<p>In <code>status</code>, look at the <code>current values:</code> list at the end. Each of the three routing controls should show the same value after <code>want=</code> and <code>now=</code>.</p>
<p><code>solo</code> turns the speaker off so you can hear the earpiece on its own. Always finish with <code>unsolo</code>.</p>
<div class="note"><p>If the earpiece stays silent, run <code>stereoctl doctor</code> with music playing. It walks every layer that can cause silence and names the one responsible (section 9.2).</p></div>
"""},

{"title": "Installing the app",
 "html": """
<p>Install <strong>CMF Stereo</strong> or <strong>CMF Stereo Pro</strong> (or both) from the app's releases page, <em>CMF-true-stereo-manager</em>, after the module is flashed and the phone rebooted. Grant it superuser permission when your root manager asks.</p>
<ul>
<li>The app can also be kept up to date through Komi Store, an app store for apps released on GitHub.</li>
<li>For the Stereo speakers page inside Nothing Settings you need LSPosed, with the app on internal storage. Enable one edition in LSPosed (scope: Settings), not both, then force-stop Settings.</li>
<li>The Quick Settings tile needs no LSPosed.</li>
</ul>
<div class="note"><p>App versions matter for some settings: the protection settings need app v1.0.56 or newer (module v1.0.4+), the earpiece leveller app v1.0.60 or newer (module v1.0.5+), and the Settings page that follows every change at once app v1.0.65 or newer (module v1.0.6+).</p></div>
"""},

{"title": "Installing on another phone",
 "html": """
<p>On a phone that is not a CMF Phone 1 the module installs and <strong>changes nothing</strong>. The installer says so:</p>
<pre>  ! This does not look like a CMF Phone 1.
    Nothing is applied automatically, so it is safe to keep
    going - the probe works on any device.
...
  installed empty actions.conf (run 'stereoctl probe')
...
  Until actions.conf has routing in it, this module changes
  nothing about how your phone sounds.</pre>
<p>What you can do there is <strong>probe</strong> the audio hardware and share the report, so the routing for that device can be worked out:</p>
<pre>su
stereoctl probe
stereoctl report</pre>
<p>Section 8.6 explains why it ships empty, and sections 6.20 and 6.21 explain the two commands.</p>
<div class="warn"><p>Do not fill <code>actions.conf</code> with guessed control names. A wrong mixer write is, from least to most regret: nothing, silence, a crash of the audio HAL, or an earpiece driven past what a receiver is built for. When you find a working route, start its gain low and raise it one step at a time.</p></div>
"""},

{"title": "Updating the module",
 "html": """
<p>When a new release is out, your root manager shows an <strong>Update</strong> button on the module's card. Tap it, let it install, and <strong>reboot</strong>. You can also flash the new zip by hand over the old one.</p>
<ul>
<li>Your settings in <code>/data/adb/cmf-stereo/</code> are kept.</li>
<li>A phone that was in Stereo is staged in Stereo again during the update.</li>
<li>Settings added by the new version are added to your file automatically.</li>
</ul>
<div class="tech">
<p>Updates are found through <code>updateJson</code> in <code>module.prop</code>, which points to <code>update.json</code> in the project repository. Your root manager compares its <code>versionCode</code> with the installed one (1090 for v1.0.9-beta).</p>
<p>The Stereo overlay lives inside the module folder, which an update replaces. That is why the installer stages Stereo again: it re-checks and re-patches your phone's own files. If they do not check out, it sets <code>CHANNELS=mono</code> and prints why: <code>channels : mono - stereo could not be staged:</code> followed by the reason.</p>
</div>
"""},

{"title": "Updating from older versions",
 "html": """
<p>The installer takes care of a few things left over from older versions:</p>
<ul>
<li><strong>New settings.</strong> If your <code>stereo.conf</code> lacks a setting the new version knows, the default is added under a line <code># --- added by v&lt;version&gt; ---</code>, and the installer prints <code>kept stereo.conf, added N new setting(s)</code>. Otherwise it prints <code>keeping existing stereo.conf</code>.</li>
<li><strong>Your routing.</strong> An <code>actions.conf</code> with real content is never overwritten (<code>keeping your actions.conf (N actions)</code>): that is your tuning.</li>
<li><strong>The old earpiece gain mistake.</strong> Versions before v0.9.2 shipped <code>Handset Volume</code> 31, believing it was the loudest; on this codec it is the mute value (&minus;40 dB). Any value above 18 is corrected to 0 and the installer prints <code>earpiece gain corrected: 31 was -40 dB (mute), now 0 = +8 dB</code>.</li>
<li><strong>The guard and the playback detector</strong> are set again on every install on a CMF Phone 1, so phones updated from v1.0.2 or earlier get the v1.0.3 detection that also covers games.</li>
<li><strong>The pre-release test module.</strong> If <code>cmf_stereo_halpatch_test</code> is installed, it is marked for removal at the next reboot.</li>
</ul>
"""},

{"title": "Uninstalling",
 "html": """
<p>Remove the module in your root manager and reboot.</p>
<ul>
<li>The uninstall script stops the daemon and puts back every control it touched.</li>
<li>It gives the speaker amp its own gain back.</li>
<li>The Stereo overlay goes with the module, so the phone is back on its stock audio files.</li>
<li><code>/data/adb/cmf-stereo/</code> is <strong>left in place</strong>, so a reinstall does not lose your routing and settings. Delete that folder by hand for a clean slate.</li>
</ul>
<pre>su
rm -rf /data/adb/cmf-stereo</pre>
<div class="warn"><p>Only run that <code>rm</code> after the module is removed. It deletes your settings, your routing and the saved original values for good.</p></div>
<div class="note"><p>Uninstall the apps separately if you no longer want them; without the module they have nothing to control.</p></div>
"""},

]},

# ---------------------------------------------------------------------------
# 3. Everyday use
# ---------------------------------------------------------------------------
{"title": "Everyday use",
 "intro": "<p>Where the controls are, what the module's card tells you, and how the module behaves day to day: with headphones, during calls, and when you turn the phone.</p>",
 "sections": [

{"title": "Where the controls are",
 "html": """
<p>You can control the module from five places. They all do the same thing underneath, and they stay in step.</p>
<table>
<tr><th>Place</th><th>What you can do</th></tr>
<tr><td>CMF Stereo / CMF Stereo Pro app</td><td>on/off, Mono/Stereo, levels, protection settings (Pro: much more)</td></tr>
<tr><td>Quick Settings tile (from the app)</td><td>Mono / Stereo</td></tr>
<tr><td>Stereo speakers page in Nothing Settings (app with LSPosed)</td><td>the app's settings, inside Settings &gt; Sound</td></tr>
<tr><td>Action button on the module's card</td><td>switch Mono &harr; Stereo</td></tr>
<tr><td>Terminal: <code>stereoctl</code></td><td>everything, including diagnostics</td></tr>
</table>
"""},

{"title": "The module's card",
 "html": """
<p>Magisk, KernelSU and APatch show the module's description on its card. The module keeps the first words of that description current, so a glance tells you what is running:</p>
<table>
<tr><th>Card starts with</th><th>Meaning</th></tr>
<tr><td><code>[Stereo] Left and right follow the screen.</code></td><td>Stereo is running.</td></tr>
<tr><td><code>[Mono] Both speakers play the full mix.</code></td><td>Mono is running.</td></tr>
<tr><td><code>[Off] Earpiece not used. Turn on in the app or with stereoctl on.</code></td><td>The module is turned off (section 3.4).</td></tr>
<tr><td><code>[Stereo unavailable] This Nothing OS build is not supported yet: mono (stock audio) until a module update adds it.</code></td><td>Your vendor audio files are not the analysed build, usually after a Nothing OS update (section 4.11).</td></tr>
<tr><td><code>[Inactive] Not a CMF Phone 1 audio stack: nothing is changed.</code></td><td>The audio files the module looks for are not there.</td></tr>
</table>
<p>Two notes can follow: <code>Switches to stereo after a reboot.</code> (or mono) when a change is waiting for a reboot, and <code>Not running: restart it in the app.</code> when the daemon is not running.</p>
<div class="note"><p>Root managers read the description when the Modules page opens. Pull down on Magisk's Modules page to refresh it.</p></div>
"""},

{"title": "The Action button",
 "html": """
<p>Tap <strong>Action</strong> on the module's card to switch to the other mode: from Mono to Stereo, or from Stereo to Mono. The button shows what happens, for example:</p>
<pre>CMF true stereo: switching to stereo

stereo applied now (audio restarted - press play again)
...</pre>
<p>The rest of the output is the same as <code>stereoctl channels stereo</code> or <code>stereoctl channels mono</code> (section 6.6).</p>
<div class="tech"><p><code>action.sh</code> checks whether the Stereo overlay is staged: if it is, it asks for <code>mono</code>; if not, for <code>stereo</code>. It then runs <code>stereoctl channels</code> with that mode. It needs Magisk 28 or newer, KernelSU or APatch.</p></div>
"""},

{"title": "Turning the module on and off",
 "html": """
<p>You can turn the earpiece off without uninstalling anything: in the app, or with:</p>
<pre>stereoctl off     # disarm: earpiece not used, every control put back
stereoctl on      # arm again</pre>
<p><strong>Off survives a reboot.</strong> The module stays off until you turn it on again.</p>
<div class="warn">
<p><strong>Turning it off while in Stereo.</strong> <code>stereoctl off</code> stops the daemon, but the Stereo files stay in place. With the daemon off, the speaker amp goes back to its stock left slot on the next stream, so the speaker would play the left channel alone. If you want the module off, <strong>switch to Mono first</strong> (<code>stereoctl channels mono</code>; it switches at once).</p>
</div>
<div class="tech"><p><code>off</code> creates the kill switch <code>/data/adb/cmf-stereo/disabled</code>, stops every daemon, restores the saved originals, and in Stereo sets the amp to its mono (L+R)/2 slot for now. <code>on</code> removes the kill switch and restarts the daemon. <code>ENABLED=0</code> in <code>stereo.conf</code> has the same effect as the kill switch.</p></div>
"""},

{"title": "While playing, or always on",
 "html": """
<p>By default the module uses the earpiece <strong>only while audio is playing</strong> (the app calls this <em>While playing</em>). The earpiece is not built to run continuously, and this saves power too.</p>
<p>The other choice, <em>Always on</em>, keeps the routing applied all the time. It is louder in theory only, harder on the earpiece, and costs idle power. The clean CMF Stereo app offers only <em>While playing</em>; CMF Stereo Pro and <code>stereo.conf</code> offer both.</p>
<div class="tech"><p>This is the <code>MODE</code> setting: <code>playback</code> (default) or <code>always</code> (section 7.5). "Playing" is detected from the audio DSP's task switches, so games, music players and every other app count (v1.0.3 and later).</p></div>
"""},

{"title": "Headphones and Bluetooth",
 "html": """
<p>When headphones or Bluetooth audio take over, the earpiece steps aside by itself. You never have the earpiece playing to nobody while you wear headphones.</p>
<p>The left/right swap for turning the phone also applies only to the speakers; headphones are never swapped.</p>
<div class="tech"><p>The audio HAL switches off the speaker amp (<code>aw_dev_0_switch</code>) when headphones or Bluetooth take over. The module's <em>guard</em> reads that switch once per cycle and applies the routing only while it reads <code>Enable</code> (section 7.9). A second, optional check (<code>REQUIRE_SPEAKER_ROUTE</code>, off by default) reads <code>dumpsys audio</code> instead.</p></div>
"""},

{"title": "Phone calls",
 "html": """
<p>Calls are left alone.</p>
<ul>
<li>In both modes, calls keep Awinic's speaker protection.</li>
<li>A switch between Mono and Stereo is refused while a call is active. It is applied after the next reboot instead, or you can try again after the call.</li>
<li>When the module restarts the audio service for a switch, calls are unaffected (measured on the phone).</li>
</ul>
<div class="tech"><p>Stereo changes only the DSP scenario <code>AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA</code>; <code>DSP_CALL_FINAL</code> keeps <code>smartpa_awinic</code>. The live switch checks <code>dumpsys telephony.registry</code> for an active call state before it does anything.</p></div>
"""},

{"title": "Turning the phone: left and right follow the screen",
 "html": """
<p>In Stereo, left and right follow how you hold the phone:</p>
<ul>
<li>In portrait, and sideways with the <strong>earpiece on your left</strong>, the earpiece plays the left channel and the speaker the right.</li>
<li>Turned the other way, with the <strong>earpiece on your right</strong>, they swap: the earpiece plays the right channel and the speaker the left. The stereo image stays the right way round.</li>
</ul>
<p>There is nothing to set up and no per-app list. Keep auto-rotate on. For an app with its own audio effect (such as VLC), the swap can take up to about 2 seconds after you press play or turn the phone.</p>
<div class="tech"><p>Android itself swaps left and right before the audio HAL when the screen is at rotation 270, except for a track whose session has its own effect chain (VLC's Dynamics Processing). The daemon finds such tracks and names their outputs to the HAL, which swaps exactly those, only at rotation 270. Section 11.8 explains it in full.</p></div>
"""},

{"title": "Testing with the test files",
 "html": """
<p>Every release carries two test files. Play them with any music app (VLC, USB Audio Player Pro, Files and so on), with auto-rotate on.</p>
<table>
<tr><th>File</th><th>What it contains</th><th>What you should hear</th></tr>
<tr><td><code>LEFT_ONLY_3min.wav</code></td><td>Sound in the left channel only.</td><td><strong>Stereo</strong>, earpiece on your left: only the earpiece plays. Turn the phone (earpiece on your right): only the speaker plays. <strong>Mono</strong>: both play.</td></tr>
<tr><td><code>LEFT10s_RIGHT10s.wav</code></td><td>A voice says "left", then 10 s of sound from the left only; then "right" and 10 s from the right only. Six rounds.</td><td>In Stereo, each side's sound comes from the driver that is on that side.</td></tr>
</table>
<div class="tech"><p>Both files are made by <code>tools/make-test-audio.py</code> in the repository.</p></div>
"""},

{"title": "Apps that were checked",
 "html": """
<p>Left and right were checked to follow the rotation on the test phone with:</p>
<ul>
<li>ordinary apps and music players, including USB Audio Player Pro (bit-perfect mode too);</li>
<li>InShot, YouTube and games;</li>
<li>VLC (it uses its own audio effect, so the module swaps it; v1.0.2 and later);</li>
<li>every button of the CMF L/R Test app: MUSIC, MOVIE, MOVIE + EFFECT, GAME, SPEECH, AAUDIO, AAUDIO SHARED and FLOAT.</li>
</ul>
<p>"While playing" engages the earpiece for games and music players alike (v1.0.3). Hi-res playback (USB Audio Player Pro, Direct 192 kHz) still works in Stereo.</p>
"""},

{"title": "Nothing Settings and the apps stay in step",
 "html": """
<p>When something changes outside the apps, the module tells them, so the app, its Quick Settings tile and the Stereo speakers page in Nothing Settings update at once. This happens after:</p>
<ul>
<li>a <code>stereoctl</code> command that changes something;</li>
<li>the Action button;</li>
<li>the module's own switch back to Mono (its crash-loop safety net);</li>
<li>once each time the daemon starts, after boot.</li>
</ul>
<p>If an app is not installed, nothing happens; it is silent and runs in the background.</p>
<div class="tech"><p>The module calls <code>content call --uri content://&lt;app&gt;.settingstile --method stateChanged</code> for <code>com.tiimoo.cmfstereo</code> and <code>com.tiimoo.cmfstereo.clean</code>. Commands that notify: <code>on</code>, <code>off</code>, <code>reset</code>, <code>solo</code>, <code>unsolo</code>, <code>restart</code>, and <code>guard</code>, <code>protect</code> and <code>channels</code> when given a value. This is tested with a stand-in <code>content</code> command; it has not yet been seen working on a phone.</p></div>
"""},

{"title": "Battery and background work",
 "html": """
<p>The daemon checks every <strong>2 seconds</strong> whether something is playing, and keeps the routing in place while it is. When nothing plays, it does very little.</p>
<p>If you notice battery drain, you can raise the interval to 5 seconds (<code>WATCH_INTERVAL</code>, section 7.6). The audio system resets mixer controls on every route change, so the interval cannot be very large.</p>
<div class="tech"><p>Work kept small on purpose: one mixer read per cycle for the guard (no <code>dumpsys</code>); <code>tinymix</code>'s calling style detected once per process; the amp's attenuation checked when playback starts and every 10th cycle (the Awinic driver writes a kernel log line for each read); <code>dumpsys media.audio_flinger</code> read only while playing at rotation 270.</p></div>
"""},

]},

# ---------------------------------------------------------------------------
# 4. Mono and stereo
# ---------------------------------------------------------------------------
{"title": "Mono and stereo",
 "intro": "<p>The two channel modes in detail: what each sounds like, how to switch, what happens during a switch, and exactly what Stereo changes on your phone.</p>",
 "sections": [

{"title": "Mono",
 "html": """
<p><strong>Mono is the default, and it is stock audio.</strong> Both the earpiece and the bottom speaker play the same full mix. The result is louder, fuller and taller than the single bottom-firing speaker.</p>
<ul>
<li>The phone's audio files are untouched.</li>
<li>The speaker keeps Awinic's speaker protection.</li>
<li>The earpiece plays without the module's earpiece limiter (that limiter runs only in Stereo).</li>
</ul>
<p>This was the whole module once, when it was called cmf-fake-stereo.</p>
"""},

{"title": "Stereo",
 "html": """
<p><strong>Stereo is real left and right.</strong> The earpiece and the speaker each play one channel, following the screen (section 3.8).</p>
<p>It costs Awinic's speaker-protection processing on media. In its place, the module's own protection runs: a fixed amp attenuation, a deep bass guard and an earpiece limiter, measured against what Awinic does, with an optional speaker boost and earpiece leveller. Chapter 5 covers each one.</p>
<div class="warn"><p>Stereo has no temperature model of the speaker. For long, loud listening, use Mono.</p></div>
"""},

{"title": "Which mode to choose",
 "html": """
<table>
<tr><th>You want</th><th>Choose</th></tr>
<tr><td>Games, films and music with real sides</td><td>Stereo</td></tr>
<tr><td>Long, loud listening</td><td>Mono</td></tr>
<tr><td>The fullest Awinic speaker protection</td><td>Mono</td></tr>
<tr><td>The module off, with no change to the speaker</td><td>Mono, then <code>stereoctl off</code></td></tr>
</table>
<p>You can change your mind at any time; switching takes about a second.</p>
"""},

{"title": "Switching between Mono and Stereo",
 "html": """
<p>Use any of these. Each switches at once, without a reboot:</p>
<ul>
<li>the <strong>Mono / Stereo</strong> choice in CMF Stereo or CMF Stereo Pro;</li>
<li>the apps' <strong>Quick Settings tile</strong>, or their Stereo speakers page in Nothing Settings;</li>
<li>the <strong>Action</strong> button on the module's card;</li>
<li>the terminal:</li>
</ul>
<pre>stereoctl channels            # what is running, and what is staged
stereoctl channels stereo     # switch to stereo now
stereoctl channels mono       # back to stock now</pre>
<p>Your choice is remembered (<code>CHANNELS</code> in <code>stereo.conf</code>) and used at every boot.</p>
<div class="note"><p>Change the mode with these, not by editing <code>CHANNELS</code> by hand: Stereo needs its files prepared and checked first, which only the switch does.</p></div>
"""},

{"title": "What you hear during a switch",
 "html": """
<p>The module restarts only the phone's audio service, not the phone:</p>
<ul>
<li>about <strong>a second of silence</strong>;</li>
<li>players <strong>pause</strong>: press play again;</li>
<li><strong>calls</strong> are unaffected.</li>
</ul>
<p>The output says <code>stereo applied now (audio restarted - press play again)</code> (or <code>mono applied now ...</code>). If you ask for the mode that is already running, it says <code>stereo (already running)</code> and changes nothing.</p>
"""},

{"title": "When a switch waits for a reboot",
 "html": """
<p>The module only switches live when every check passes. If one does not, it undoes what it did and the change waits for the next reboot. You then see, for example:</p>
<pre>stereo staged. Reboot to apply (a call is active).</pre>
<p>Reasons you may see in the brackets:</p>
<table>
<tr><th>Reason</th><th>What to do</th></tr>
<tr><td><code>a call is active</code></td><td>Try again after the call, or reboot.</td></tr>
<tr><td><code>a mount over the audio files is not ours - not touching it</code></td><td>Another module mounts over the same files. Reboot; see section 9.9 about other modules.</td></tr>
<tr><td><code>no verified stereo copy of ...</code></td><td>The prepared files did not check out. Reboot, or switch again.</td></tr>
<tr><td><code>... does not read back as the stereo file</code> / <code>cannot mount over ...</code></td><td>A file did not land as expected. Reboot.</td></tr>
<tr><td><code>the audio HAL did not come back on the stereo files</code></td><td>The module went back to the stock files. Reboot.</td></tr>
</table>
<p>While a change waits, <code>stereoctl channels</code> shows <code>staged:  stereo   (reboot to apply)</code> and the card adds <code>Switches to stereo after a reboot.</code></p>
"""},

{"title": "What a live switch checks",
 "html": """
<p>A live switch is careful by design. In short: it only removes its own changes, puts on exactly what the wanted mode needs, checks every file where the audio service reads it, and makes sure the audio service is still running a few seconds later.</p>
<div class="tech">
<ul>
<li>Magisk bind-mounts each of the module's files over its vendor path at boot, in init's mount namespace, which the audio HAL shares (measured).</li>
<li>A live switch takes off <strong>only its own</strong> mounts. If any mount from anywhere else sits on those paths, the switch is refused.</li>
<li>It then mounts what the wanted mode needs: the staged files for Stereo, nothing for Mono, or, where Magisk left an empty placeholder rather than the stock file, a copy of the phone's own stock files.</li>
<li>That stock copy is made when the phone booted Mono, or rebuilt from the Stereo files by putting the original bytes back, and kept only if it hashes to the stock build.</li>
<li>Every file is read back through <code>/proc/1/root</code> and must hash to the expected build.</li>
<li>The audio HAL is restarted with <code>setprop ctl.restart vendor.audio-hal</code>. The new process must be running, and still be the same process <strong>3 seconds later</strong>.</li>
<li>If anything fails, the mounts are undone and the HAL is restarted only once all three files read back as stock. If they cannot be put back, the running HAL is left alone and a reboot puts everything right.</li>
</ul>
</div>
"""},

{"title": "What Stereo changes, and nothing else",
 "html": """
<p>Stereo changes five things. Everything else on the phone stays as it is.</p>
<ol>
<li><strong>The audio HAL's fold to mono</strong> is switched off. In its place the HAL loads the module's protection library and runs it on every buffer, and the audio DSP is told the speaker is stereo.</li>
<li><strong>The audio DSP's fold to mono</strong>: Awinic's speaker protection for media is replaced by MediaTek's pass-through, which the phone's own configuration file already declares. Calls keep Awinic.</li>
<li><strong>The amp's slot</strong>: while the earpiece plays, the speaker amp plays the right slot; whenever the earpiece is not playing, the amp plays a mono mix, so the speaker never plays one channel alone.</li>
<li><strong>Attenuation</strong>: the amp is held 6 dB down by default (the speaker level).</li>
<li><strong>Protection</strong>: the module's library guards the speaker's deep bass and limits the earpiece (chapter 5).</li>
</ol>
<div class="tech">
<p>1. <code>AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed</code> in <code>audio.primary.mt6878.so</code> (and <code>audio.primary.mediatek.so</code>) is patched (<code>hal-swap/patch.S</code>) to load <code>libcmfstereo.so</code> and call it; the DSP task gets <code>hw_info</code> bit <code>0x4</code> (two branches). Four places in all; the stock bytes every earlier version changed are written back first, and the result must hash to the tested build.</p>
<p>2. <code>AURISYS_SCENARIO_DSP_PLAYBACK_SMARTPA</code> in <code>aurisys_config_rv.xml</code> runs <code>aurisys_demo</code> instead of <code>smartpa_awinic</code>. The phone's own file already declares <code>aurisys_demo</code> for that scenario (2 channels in and out, IV reference).</p>
<p>3&ndash;4. The daemon writes the amp's I2S slot register and holds <code>aw_dev_0_volume</code> (sections 4.9 and 5.3). Mono gives the amp its previous value back.</p>
</div>
"""},

{"title": "The first second of a stream",
 "html": """
<p>In Stereo, the very first second or two of a new stream can come from the speaker as the stock left slot, before the module puts the amp on its right slot. This is expected.</p>
<div class="tech"><p>The Awinic driver rewrites its slot register from its profile on every stream start. The daemon re-asserts the slot on its next cycle (every <code>WATCH_INTERVAL</code> seconds, 2 by default). Register <code>0x06</code> bits 11:10: <code>01</code> left (stock <code>0x34e8</code>), <code>10</code> right (<code>0x38e8</code>), <code>11</code> mono (L+R)/2. When nothing plays, the daemon does not touch the amp at all, so its I2C bus is not woken.</p></div>
"""},

{"title": "No vendor file ships in this module",
 "html": """
<p>The module carries no file from Nothing or MediaTek. To prepare Stereo (<em>staging</em>), it copies your phone's own audio files, checks they are exactly the analysed build, patches them, and checks the result against the tested one, before putting it in the module's own overlay folder with the original SELinux labels.</p>
<p>Anything else &mdash; another firmware, a different file &mdash; is refused, and the phone stays on Mono.</p>
<div class="tech"><p>Staged files: <code>/vendor/lib64/hw/audio.primary.mt6878.so</code>, <code>/vendor/lib64/hw/audio.primary.mediatek.so</code>, <code>/vendor/etc/aurisys_config_rv.xml</code>, plus the module's own <code>libcmfstereo.so</code> (checked against its own hash). They go into <code>system/vendor/...</code> inside the module folder; the vendor partition is never written.</p></div>
"""},

{"title": "Stereo after a Nothing OS update",
 "html": """
<p>A Nothing OS update can replace the audio files Stereo was built from. The module checks for this at every boot, before anything is mounted. If the files differ:</p>
<ul>
<li>the Stereo overlay is removed and the phone boots on stock <strong>Mono</strong>;</li>
<li>the card says <code>[Stereo unavailable]</code>, and <code>stereoctl status</code> shows <code>build:     updated</code>;</li>
<li>Stereo stays refused until a module release supports the new build.</li>
</ul>
<p>The CMF Phone 1 is expected to get security updates only, but those can still replace the audio files. When the new build has been checked, a module update adds it.</p>
<div class="note"><p>This guard has been tested on fake vendor files only; it will first be seen on a phone with the next Nothing OS update.</p></div>
"""},

{"title": "Known limits in Stereo",
 "html": """
<ul>
<li><strong>Two apps at once.</strong> If an app with its own audio effect (VLC) and an ordinary app play on the same output at the same time, with the earpiece on your right, one of them comes out reversed. The audio HAL sees only the mix.</li>
<li><strong>Compressed offload</strong> (the DSP decoding MP3 itself) is refused by Android on this phone, so apps never use it here. The module does not swap compressed audio.</li>
<li><strong>Protection after a live switch from a Mono boot</strong> starts only after a reboot (section 5.8).</li>
<li><strong>The first second of a stream</strong> may play on the stock left slot (section 4.9).</li>
<li><strong>The earpiece will not match the speaker.</strong> It is a receiver; balance the two by turning the speaker down (section 5.10).</li>
</ul>
<div class="tech"><p>Offload: <code>AudioManager.isOffloadedPlaybackSupported</code> is false for MP3 on the speaker. The likely reason, not yet proven, is that the audio policy refuses offload while a non-offloadable effect is on, and Nothing's Dirac is on for the output mix.</p></div>
"""},

]},

# ---------------------------------------------------------------------------
# 5. Protection and levels
# ---------------------------------------------------------------------------
{"title": "Protection and levels",
 "intro": "<p>Stereo replaces Awinic's speaker protection with the module's own. This chapter explains each part, every setting, how loud each driver can go, and the risks, plainly.</p>",
 "sections": [

{"title": "Why Stereo needs its own protection",
 "html": """
<p>In Mono, Awinic's software on the audio DSP protects the speaker. It works from a live model of the speaker, keeping it within its movement and temperature limits. But that same software mixes left and right into one, which is exactly what Stereo has to avoid. So Stereo turns it off for media, and the module protects the speaker and earpiece itself.</p>
<p>The module's protection was built from measurements of what Awinic does (CMF L/R Test, DRIVER STUDY). Measured in Stereo without it, the speaker got up to about <strong>10 dB more deep bass</strong> than Awinic lets through, and the earpiece <strong>clipped</strong> in its loudest 1.5 dB. The protection holds both.</p>
<p>It runs inside the audio HAL, for every app, before the sound reaches the DSP.</p>
"""},

{"title": "Risks, plainly",
 "html": """
<div class="warn">
<p><strong>The speaker in Stereo.</strong> In Mono, Awinic keeps the speaker within its movement and temperature limits from a live model of it. In Stereo, media gets:</p>
<ul>
<li>the amp's own hardware over-temperature and over-current cut-outs;</li>
<li>the speaker's peaks held <strong>6 dB below the amp's full output</strong> at speaker level 10, 2 dB more per level down;</li>
<li>its deepest bass held back when it gets loud (the deep bass guard).</li>
</ul>
<p>Both were measured against Awinic's, but they are <strong>fixed limits</strong>: there is <strong>no temperature model</strong>. Speaker boost makes it louder; a limiter then holds its peaks at Awinic's own level, about 5 dB below full output. For long, loud listening use <strong>Mono</strong>. In Stereo, lower the speaker level and back off at the first distortion.</p>
</div>
<div class="warn">
<p><strong>The earpiece.</strong> In Stereo the earpiece limiter (on by default) holds it at &minus;2.5 dBFS, below where it starts to crackle, and the leveller never lifts its peaks above that. In Mono the earpiece plays without protection. It has no protection circuit of its own: back off at the first buzz or rattle.</p>
</div>
<p>How the speaker holds up to long, loud Stereo listening has not been tested yet.</p>
"""},

{"title": "The speaker level and the 6 dB margin",
 "html": """
<p>In Stereo the speaker amp is held a fixed amount below its full output. This margin is part of what stands in for Awinic's protection.</p>
<table>
<tr><th>App speaker level</th><th>Amp held down by</th></tr>
<tr><td>10 (loudest)</td><td>6 dB (default)</td></tr>
<tr><td>9</td><td>8 dB</td></tr>
<tr><td>8</td><td>10 dB</td></tr>
<tr><td>7</td><td>12 dB</td></tr>
<tr><td>6</td><td>14 dB</td></tr>
<tr><td>5</td><td>16 dB</td></tr>
<tr><td>4</td><td>18 dB</td></tr>
<tr><td>3</td><td>20 dB</td></tr>
<tr><td>2</td><td>22 dB</td></tr>
<tr><td>1</td><td>24 dB</td></tr>
</table>
<p>CMF Stereo never goes below the 6 dB margin. Raise the attenuation if you play loud.</p>
<div class="warn"><p>CMF Stereo Pro and <code>stereo.conf</code> accept values under 6 dB (the setting's range is 0&ndash;30). Pro asks before going under 6 dB. Below that margin the speaker has less headroom than the module was designed around; with the protection library not running (after a live switch from a Mono boot, until a reboot), only the amp's own cut-outs protect it.</p></div>
<div class="tech"><p>Setting: <code>STEREO_ATTEN_DB</code> (default 6, range 0&ndash;30). It is applied through the amp's own volume control, <code>aw_dev_0_volume</code>, an attenuation in 1/8 dB steps (0&ndash;720 = 0&ndash;90 dB, per the aw882xx driver), less the speaker boost while the protection runs. A larger attenuation set by someone else (you, or the driver's own monitor) is kept. Mono gives the amp its previous value back.</p></div>
"""},

{"title": "Speaker boost",
 "html": """
<p>Speaker boost makes the speaker louder in Stereo by taking up to 6 dB off the fixed attenuation. A limiter then keeps the speaker's loudest moments where Awinic keeps them in Mono, about 5 dB below the amp's full output.</p>
<table>
<tr><th>Values</th><th>Default</th><th>Set with</th></tr>
<tr><td>0 to 6 (dB)</td><td>0</td><td>the apps, or <code>stereoctl protect boost N</code></td></tr>
</table>
<ul>
<li>At 0 the speaker sounds as before.</li>
<li>It works only while the protection runs. If the protection is not running, the boost is ignored and the full attenuation is kept.</li>
</ul>
<pre>stereoctl protect boost 3</pre>
<div class="warn"><p>Boost raises the average level, and so the heat in the speaker. The peak limiter does not model temperature. Boost 6 has been tried only briefly so far. For long listening, keep boost low or use Mono.</p></div>
<div class="tech"><p>Amp attenuation = <code>STEREO_ATTEN_DB</code> &minus; <code>SPEAKER_BOOST</code> (never below 0). The speaker's peak ceiling is (attenuation &minus; 5) dB of full scale when that is negative, so that peaks never exceed &minus;5 dB below the amp's full output; at an attenuation of 5 dB or more the ceiling is off (0), because the attenuation alone already holds them there.</p></div>
"""},

{"title": "Deep bass guard",
 "html": """
<p>The deep bass guard holds back only the speaker's deepest bass, below 100 Hz, and <strong>only when it gets loud</strong>. Quiet bass is untouched, unlike Awinic, which always cuts it.</p>
<table>
<tr><th>Value</th><th>Deep bass held at, below the amp's full output</th></tr>
<tr><td><code>off</code></td><td>not held</td></tr>
<tr><td><code>light</code></td><td>&minus;8 dB</td></tr>
<tr><td><code>medium</code> (default)</td><td>&minus;14 dB</td></tr>
<tr><td><code>strong</code></td><td>&minus;20 dB</td></tr>
</table>
<pre>stereoctl protect bass medium</pre>
<p>For comparison, Awinic in Mono cuts 100 Hz by 16 dB at every level.</p>
<div class="warn"><p>Turning the guard <code>off</code> removes the one protection aimed at the speaker's excursion in Stereo. Leave it on unless you know why you are turning it off.</p></div>
<div class="tech"><p>A 4th-order Linkwitz-Riley split at 100 Hz on the speaker channel; the band below is limited only when it exceeds its ceiling. The ceiling handed to the library is (level + attenuation) dB of the samples' full scale, so it follows the speaker level: for example speaker level 5 (16 dB) with <code>strong</code> gives &minus;4 dBFS on the signal, &minus;20 dB below the amp's full output (verified on the phone).</p></div>
"""},

{"title": "Earpiece limiter",
 "html": """
<p>The earpiece limiter stops the earpiece clipping at its very loudest. It holds the earpiece at <strong>&minus;2.5 dBFS</strong>; above that, the earpiece crackles. Its bass is kept.</p>
<table>
<tr><th>Values</th><th>Default</th><th>Set with</th></tr>
<tr><td><code>on</code>, <code>off</code></td><td><code>on</code></td><td>the apps, or <code>stereoctl protect earpiece on|off</code></td></tr>
</table>
<pre>stereoctl protect earpiece on</pre>
<div class="warn"><p>Keep it on. Measured on the phone, the earpiece clips in its top 1.5 dB of full scale: odd harmonics jump to 25&ndash;35 % at 150 Hz, 200 Hz and 2 kHz. The limiter runs only in Stereo.</p></div>
"""},

{"title": "Earpiece leveller",
 "html": """
<p>The leveller is optional. It brings up the earpiece's <strong>quiet and medium parts</strong>, so the earpiece side keeps up with the speaker. You will notice it most with films, classical music and older recordings; loud modern pop is already levelled in the studio and changes little.</p>
<table>
<tr><th>Value</th><th>Quietest parts raised by at most</th></tr>
<tr><td><code>off</code> (default)</td><td>&mdash;</td></tr>
<tr><td><code>light</code></td><td>4 dB</td></tr>
<tr><td><code>medium</code></td><td>8 dB</td></tr>
<tr><td><code>strong</code></td><td>12 dB</td></tr>
</table>
<ul>
<li>Loud parts, bass and every frequency stay as they are.</li>
<li>The earpiece's peaks never go above what it already gets at full volume.</li>
<li>Silence stays silent: the hiss between tracks is not raised.</li>
</ul>
<pre>stereoctl protect leveller medium</pre>
<p>On the phone, the leveller made a clear difference on the earpiece side, with no distortion heard.</p>
<div class="tech"><p>It raises loudness towards &minus;18 dBFS, making up 35 / 55 / 75 % of the gap (light / medium / strong) up to the 4 / 8 / 12 dB limit, and leaves anything below &minus;60 dBFS alone. Peaks stay at the earpiece's ceiling: &minus;2.5 dBFS with the limiter on, &minus;0.1 dBFS with it off.</p></div>
"""},

{"title": "When the protection runs",
 "html": """
<p>The protection runs only in <strong>Stereo</strong>. Check it with:</p>
<pre>stereoctl protect</pre>
<p>The first line tells you:</p>
<table>
<tr><th>It says</th><th>Meaning</th></tr>
<tr><td><code>protection:  running</code></td><td>The audio HAL loaded the library and it is working.</td></tr>
<tr><td><code>protection:  not running yet (...)</code></td><td>Stereo is on, but the library has not started: it starts with the first sound on the speaker.</td></tr>
<tr><td><code>protection:  off (mono)</code></td><td>Mono is running; the protection is not used.</td></tr>
</table>
<div class="warn"><p><strong>After a live switch from a Mono boot</strong>, the protection starts only after the next reboot, because the library is not in place until then. Until you reboot, Stereo plays with the fixed attenuation alone and the boost is ignored. Reboot once after you first switch to Stereo.</p></div>
<div class="tech"><p>The library marks itself with <code>vendor.audiohal.cmf_prot=1</code> on its first speaker buffer; the module also checks that the file the HAL loads hashes to the tested build. Settings reach the library within one daemon cycle (and at once if Stereo runs when you change them).</p></div>
"""},

{"title": "The earpiece level",
 "html": """
<p>By default the earpiece plays at the receiver amp's maximum, <strong>+8 dB</strong>, the same value the audio HAL uses when it drives the earpiece itself.</p>
<p>In CMF Stereo, <strong>earpiece level 10</strong> is that maximum, and each step down is 2 dB quieter, to level 1 at &minus;10 dB. In CMF Stereo Pro you set it in dB.</p>
<p>By hand, change the number in <code>actions.conf</code>:</p>
<pre>ctl|Handset Volume|0</pre>
<p>Raise the number (towards 18) to make the earpiece quieter.</p>
<div class="tech">
<p><code>Handset Volume</code> is the receiver amp's gain on the MT6369 codec. Read from the codec driver (<code>snd-soc-mt6369.ko</code>), the range is 0&ndash;18 and the register runs the opposite way to the dB scale ALSA advertises:</p>
<table>
<tr><th>Value</th><th>Gain</th></tr>
<tr><td>0</td><td>+8 dB (loudest)</td></tr>
<tr><td>8</td><td>0 dB</td></tr>
<tr><td>18</td><td>&minus;10 dB</td></tr>
<tr><td>31</td><td>&minus;40 dB (the codec's mute value)</td></tr>
</table>
<p>Measured: the earpiece's whole path is already at full level; there is no hidden attenuation to win back. <code>ADDA_DL_GAIN</code>, the digital gain before the DAC, is left alone: the HAL parks it at 63311 of 65535 (&minus;0.3 dB), and <code>ADDA_DL</code> is shared with the headphone path. <code>ADDA_DL_MAX_VOL</code> was tried for a louder earpiece: no clear difference, left out.</p>
</div>
"""},

{"title": "Balancing the earpiece and the speaker",
 "html": """
<p>The earpiece is a receiver; it will never match the speaker. To balance the two:</p>
<ul>
<li>turn the <strong>speaker</strong> down (the apps' speaker level, or <code>STEREO_ATTEN_DB</code>);</li>
<li>use the <strong>earpiece leveller</strong> to bring up the earpiece's quiet parts without raising its peaks.</li>
</ul>
<div class="warn"><p>Do not try to balance by pushing the earpiece harder. It is already at its maximum, and it has no protection circuit of its own.</p></div>
"""},

{"title": "Awinic compared with the module",
 "html": """
<p>Measured with CMF L/R Test DRIVER STUDY: tones from 100 Hz to 8 kHz at &minus;30 to &minus;3 dBFS, with the HAL's and the DSP's own recordings of what reached them and the HAL's raw 24-bit two-microphone capture.</p>
<table>
<tr><th></th><th>Awinic (Mono, stock)</th><th>The module in Stereo</th></tr>
<tr><td>Speaker peaks</td><td>about &minus;5 dB below the amp's full output</td><td>about &minus;6 dB (fixed attenuation); with boost, a limiter keeps them at &minus;5 dB</td></tr>
<tr><td>100 Hz</td><td>cut by 16 dB at every level</td><td>untouched while quiet; held at &minus;8 / &minus;14 / &minus;20 dB below full output when loud (light / medium / strong)</td></tr>
<tr><td>150 Hz &ndash; 3 kHz</td><td>about +3.5 dB EQ</td><td>unchanged</td></tr>
<tr><td>Earpiece</td><td>(not Awinic's) clips in its top 1.5 dB of full scale</td><td>limited at &minus;2.5 dBFS; optional leveller raises quiet passages, peaks unchanged</td></tr>
</table>
<p>The limiters add at most 1.2 % distortion while working (at 50 Hz), under 0.1 % above 1 kHz. Nothing changes while a signal is below its ceiling.</p>
"""},

{"title": "Choosing your settings",
 "html": """
<p>The defaults are a sensible start: speaker level 10 (6 dB), boost 0, bass guard medium, earpiece limiter on, leveller off. From there, the module's own advice is:</p>
<ul>
<li><strong>Loud, long listening:</strong> switch to Mono.</li>
<li><strong>Playing loud in Stereo:</strong> raise the attenuation (lower the speaker level).</li>
<li><strong>At the first distortion:</strong> back off: lower the speaker level, reduce boost.</li>
<li><strong>Earpiece too quiet next to the speaker:</strong> turn the speaker down, or try the leveller.</li>
<li><strong>Earpiece buzzes or rattles:</strong> keep the limiter on and make the earpiece quieter (a higher <code>Handset Volume</code> number).</li>
</ul>
<div class="note"><p>Which Stereo speaker level sounds as loud as stock Mono has not been measured yet; compare by ear with the same track.</p></div>
"""},

]},

# ---------------------------------------------------------------------------
# 6. The command line
# ---------------------------------------------------------------------------
{"title": "The command line: stereoctl",
 "intro": "<p>Every feature of the module is reachable from one command, <code>stereoctl</code>. This chapter lists every command, what it does, what it prints, and an example.</p>",
 "sections": [

{"title": "Opening a root shell",
 "html": """
<p>Run <code>stereoctl</code> as root, from Termux or from a computer with <code>adb</code>:</p>
<pre># in Termux, or after: adb shell
su
stereoctl status</pre>
<p>Or run one command at a time:</p>
<pre>su -c stereoctl channels stereo</pre>
<p><code>stereoctl</code> with no command is the same as <code>stereoctl status</code>. <code>stereoctl help</code> (or <code>-h</code>, <code>--help</code>) prints the list of commands.</p>
<div class="tech"><p><code>/system/bin/stereoctl</code> is a small shim from the module that runs <code>/data/adb/modules/cmf_stereo/scripts/stereoctl</code>. An unknown command prints <code>unknown command: ...</code> and the list.</p></div>
"""},

{"title": "All commands at a glance",
 "html": """
<table>
<tr><th>Command</th><th>What it does</th></tr>
<tr><td><code>status [brief]</code></td><td>module, daemon and control state</td></tr>
<tr><td><code>doctor</code></td><td>diagnose why the earpiece is silent</td></tr>
<tr><td><code>channels [mono|stereo]</code></td><td>show or choose the speaker channels (applied at once)</td></tr>
<tr><td><code>protect</code></td><td>Stereo protection settings, and whether it runs</td></tr>
<tr><td><code>protect boost 0-6</code></td><td>speaker boost</td></tr>
<tr><td><code>protect bass off|light|medium|strong</code></td><td>deep bass guard</td></tr>
<tr><td><code>protect earpiece on|off</code></td><td>earpiece limiter (&minus;2.5 dBFS)</td></tr>
<tr><td><code>protect leveller off|light|medium|strong</code></td><td>earpiece leveller</td></tr>
<tr><td><code>on</code> | <code>off</code></td><td>arm / disarm (off survives a reboot)</td></tr>
<tr><td><code>solo</code> | <code>unsolo</code></td><td>speaker off, earpiece only / back to normal</td></tr>
<tr><td><code>guard on|off</code></td><td>re-enable / bypass the speaker-follows guard</td></tr>
<tr><td><code>apply</code> | <code>revert</code></td><td>one-shot apply / restore of the routing</td></tr>
<tr><td><code>restart</code></td><td>restart the daemon</td></tr>
<tr><td><code>reset</code></td><td>clear saved state and start clean</td></tr>
<tr><td><code>log [n]</code></td><td>show the end of the log</td></tr>
<tr><td><code>edit</code></td><td>print the config file paths</td></tr>
<tr><td><code>probe [dir]</code></td><td>dump the audio hardware</td></tr>
<tr><td><code>report</code></td><td>fold the newest probe into one shareable .txt</td></tr>
<tr><td><code>scan [pattern]</code></td><td>search the mixer for candidate controls</td></tr>
<tr><td><code>ctl NAME [VALUE]</code></td><td>read or write one mixer control</td></tr>
<tr><td><code>dump</code></td><td>every mixer control and its value</td></tr>
<tr><td><code>diff [seconds]</code></td><td>snapshot the mixer, wait, show what changed</td></tr>
<tr><td><code>xml-patch</code> | <code>xml-revert</code></td><td>install / remove the stereo speaker-port overlay (reboot)</td></tr>
</table>
"""},

{"title": "status",
 "html": """
<p>Shows the module, the daemon, and the live value of every control the module manages. It is the first thing to run when something seems wrong.</p>
<pre>stereoctl status</pre>
<pre>module:    /data/adb/modules/cmf_stereo
config:    /data/adb/cmf-stereo/stereo.conf
actions:   /data/adb/cmf-stereo/actions.conf (3 configured)
armed:     yes
mode:      playback (interval 2s)
daemon:    running (pid &lt;pid&gt;)
tinymix:   &lt;path&gt; (&lt;style&gt; style)
playback:  active
boot:      0 strike(s) since last successful boot
channels:  stereo
build:     known
amp slot:  right   attenuation: &lt;steps&gt;/8 dB (holds 6 dB)
xml overlay: 0 file(s)

current values:
  ctl    Handset Volume              want=0          now=0
  ctl    ADDA_DL_CH1 DL_24CH_CH1     want=1          now=1
  ctl    RCV Mux                     want=Voice Playback now=Voice Playback</pre>
<table>
<tr><th>Line</th><th>What to look for</th></tr>
<tr><td><code>armed</code></td><td><code>no (disabled)</code> means the module is off: <code>stereoctl on</code>.</td></tr>
<tr><td><code>daemon</code></td><td><code>not running</code>: <code>stereoctl restart</code>.</td></tr>
<tr><td><code>tinymix</code></td><td><code>NOT FOUND</code> or <code>UNUSABLE</code>: mixer actions cannot run (section 9.13).</td></tr>
<tr><td><code>playback</code></td><td><code>idle</code> when nothing plays; the routing then is not applied (with <code>MODE=playback</code>).</td></tr>
<tr><td><code>boot</code></td><td>Failed boots counted by the watchdog; 0 is normal.</td></tr>
<tr><td><code>channels</code></td><td>What runs; a waiting change shows as <code>mono (switches to stereo after reboot)</code>.</td></tr>
<tr><td><code>build</code></td><td><code>known</code> (supported), <code>updated</code> (Nothing OS update, Stereo unavailable), <code>absent</code> (not a CMF Phone 1 audio stack).</td></tr>
<tr><td><code>amp slot</code></td><td>Stereo only: <code>right</code> while the earpiece plays, <code>mono</code> otherwise; the attenuation the amp holds.</td></tr>
<tr><td><code>current values</code></td><td>With audio playing, <code>want=</code> should match <code>now=</code> for each control.</td></tr>
</table>
"""},

{"title": "status brief",
 "html": """
<p>The same as <code>status</code>, but it stops after the <code>build</code> and <code>amp slot</code> lines and does not read every control back. The apps use it to refresh quickly after each tap.</p>
<pre>stereoctl status brief</pre>
"""},

{"title": "doctor",
 "html": """
<p>Diagnoses why the earpiece is silent. It walks every layer that can silence the earpiece, in the order they apply, and names the one responsible. <strong>Start some music first</strong>, then run:</p>
<pre>stereoctl doctor</pre>
<p>It checks six things:</p>
<ol>
<li><strong>module armed</strong> &mdash; the kill switch is not set;</li>
<li><strong>daemon</strong> &mdash; exactly one daemon is running;</li>
<li><strong>tinymix</strong> &mdash; the mixer tool works;</li>
<li><strong>playback</strong> &mdash; audio is detected as playing, and by which detector;</li>
<li><strong>guard</strong> &mdash; the speaker amp switch allows the routing;</li>
<li><strong>applying now</strong> &mdash; it applies the routing and reads each control back: <code>ok</code> or <code>FAILED</code>.</li>
</ol>
<p>Each problem comes with its fix, for example <code>NO - kill switch set (it survives reboots). Fix: stereoctl on</code>. Section 9.3 explains every message.</p>
<div class="note"><p>If nothing is playing, doctor skips step 6 on purpose: applying would switch the earpiece on outside normal use and make it look as if doctor fixed something.</p></div>
"""},

{"title": "channels",
 "html": """
<p>Shows or chooses the speaker channels. A change is applied at once by restarting the audio HAL; if that cannot be done safely, after a reboot.</p>
<pre>stereoctl channels</pre>
<pre>running: mono
staged:  mono</pre>
<pre>stereoctl channels stereo</pre>
<pre>stereo applied now (audio restarted - press play again)

  left and right play on the earpiece and the speaker, following the screen.
  Awinic's speaker protection is off for media in this mode; the
  amp is held 6 dB down instead (STEREO_ATTEN_DB), and the
  module's own protection holds the deep bass and the earpiece
  ('stereoctl protect'; after a live switch from a mono boot it starts
  with the next reboot).
  Back off at the first sign of distortion, and use
  'stereoctl channels mono' for loud listening.

  Turned the other way (earpiece on your right), left and right
  swap with the screen, so the image stays the right way round.</pre>
<pre>stereoctl channels mono</pre>
<pre>mono applied now (audio restarted - press play again)</pre>
<p>Other results: <code>stereo (already running)</code>, <code>stereo staged. Reboot to apply (&lt;reason&gt;).</code> (section 4.6), and <code>stereo NOT staged: &lt;reason&gt;</code> when your phone's files cannot be prepared (section 9.5).</p>
<div class="tech"><p>Stereo: saves a checked stock copy, stages the overlay, sets <code>CHANNELS=stereo</code>, then switches live. Mono: from a Stereo boot rebuilds the stock files first, removes the overlay, sets <code>CHANNELS=mono</code>, switches live, and gives the amp its own gain and left slot back. With a mode given, it also updates the card and tells the apps.</p></div>
"""},

{"title": "protect",
 "html": """
<p>Shows the Stereo protection settings and whether the protection runs.</p>
<pre>stereoctl protect</pre>
<pre>protection:  running
boost:       0 dB  (amp attenuation now 6 dB)
bass:        medium
earpiece:    on
leveller:    off
ceilings:    speaker 0, bass -800, earpiece -250 (1/100 dB of full scale, 0 = off), leveller 0</pre>
<p>The example shows the default settings with the protection running. The <code>ceilings</code> line is what the module hands the library, in hundredths of a dB of full scale; 0 switches a stage off. With the defaults the speaker's own peak limiter is off (the 6 dB attenuation already holds the peaks), the bass guard is at &minus;8 dBFS on the signal (&minus;14 dB below the amp's full output), and the earpiece at &minus;2.5 dBFS.</p>
<p>Each <code>protect</code> sub-command below saves its value in <code>stereo.conf</code> and then prints this same summary.</p>
"""},

{"title": "protect boost",
 "html": """
<p>Sets the speaker boost, 0 to 6 dB less amp attenuation, only while the protection runs. The speaker's peaks stay at Awinic's level, about &minus;5 dB.</p>
<pre>stereoctl protect boost 2</pre>
<p>Any value outside 0&ndash;6 prints <code>usage: stereoctl protect boost 0-6</code> and changes nothing. See section 5.4 for the warning.</p>
"""},

{"title": "protect bass",
 "html": """
<p>Sets the deep bass guard: <code>off</code>, <code>light</code>, <code>medium</code> or <code>strong</code>. It holds the speaker's bass below 100 Hz only when it gets loud, at &minus;8 / &minus;14 / &minus;20 dB below the amp's full output.</p>
<pre>stereoctl protect bass strong</pre>
"""},

{"title": "protect earpiece",
 "html": """
<p>Turns the earpiece limiter <code>on</code> or <code>off</code>. On, it holds the earpiece below &minus;2.5 dBFS, where it would otherwise clip.</p>
<pre>stereoctl protect earpiece on</pre>
"""},

{"title": "protect leveller",
 "html": """
<p>Sets the earpiece leveller: <code>off</code>, <code>light</code>, <code>medium</code> or <code>strong</code>. It raises the earpiece's quiet and medium passages by at most 4 / 8 / 12 dB, with no frequency changed and peaks never higher.</p>
<pre>stereoctl protect leveller light</pre>
"""},

{"title": "on and off",
 "html": """
<p><code>off</code> disarms the module: it stops the daemon and puts every control back. It survives a reboot.</p>
<pre>stereoctl off</pre>
<pre>daemon stopped
disarmed and reverted - controls are yours until 'stereoctl on'
note: this survives a reboot. 'stereoctl on' to re-arm.</pre>
<p>In Stereo it adds a note: the Stereo overlay is still mounted, the amp will return to its left slot on the next stream, and you should run <code>stereoctl channels mono</code> for stock audio.</p>
<p><code>on</code> arms it again and restarts the daemon:</p>
<pre>stereoctl on</pre>
<pre>armed
daemon restarted (pid &lt;pid&gt;)</pre>
"""},

{"title": "solo and unsolo",
 "html": """
<p><code>solo</code> turns the speaker amp off so you hear the earpiece alone. Use it to audition the earpiece, or to prove it is really playing. <code>unsolo</code> puts the speaker back.</p>
<pre>stereoctl solo</pre>
<pre>speaker off (aw_dev_0_switch was Enable), guard bypassed
earpiece only - run 'stereoctl unsolo' when done</pre>
<pre>stereoctl unsolo</pre>
<pre>speaker restored to Enable, guard active</pre>
<div class="note"><p>Solo bypasses the guard first. Otherwise turning the speaker amp off would also silence the earpiece, because the guard reads that as "headphones took over".</p></div>
<div class="warn"><p>In solo the earpiece plays everything on its own. Keep the volume moderate and always finish with <code>unsolo</code>.</p></div>
"""},

{"title": "guard",
 "html": """
<p>The guard makes the earpiece follow the speaker: it plays only while the speaker amp is on. You can bypass it or turn it back on:</p>
<pre>stereoctl guard          # show: guard: aw_dev_0_switch = Enable  (or: guard: bypassed)
stereoctl guard off      # guard bypassed
stereoctl guard on       # guard active</pre>
<div class="warn"><p>With the guard bypassed, the earpiece can play while headphones or Bluetooth are in use. Turn it back on when you are done.</p></div>
"""},

{"title": "apply and revert",
 "html": """
<p>One-shot commands for testing. <code>apply</code> writes every action in <code>actions.conf</code> once; <code>revert</code> puts back the saved originals.</p>
<pre>stereoctl apply      # prints: applied
stereoctl revert     # prints: reverted</pre>
<div class="note"><p>While the daemon runs it keeps doing its own applying and reverting every cycle, so a one-shot change may be undone within seconds. For hand testing, turn the module <code>off</code> first.</p></div>
"""},

{"title": "restart",
 "html": """
<p>Stops every running daemon and starts one fresh, with no start-up delay. Use it after editing <code>stereo.conf</code>, or when the daemon is not running.</p>
<pre>stereoctl restart</pre>
<pre>daemon restarted (pid &lt;pid&gt;)</pre>
<p>If it fails: <code>daemon did not start - check: stereoctl log</code>.</p>
"""},

{"title": "reset",
 "html": """
<p>Clears the remembered state and starts clean: the saved original values, the guard bypass, the solo state and the kill switch. Then it restarts the daemon.</p>
<pre>stereoctl reset</pre>
<pre>cleared: saved originals, guard bypass, solo state, kill switch
daemon restarted (pid &lt;pid&gt;)</pre>
<div class="note"><p>Use it when a revert keeps restoring a wrong value: saved originals survive a reinstall, and a bad one makes every revert restore it. Note that reset also clears the kill switch, so a module you had turned off is on again.</p></div>
"""},

{"title": "log",
 "html": """
<p>Shows the end of the module's log, 50 lines by default, or as many as you ask for.</p>
<pre>stereoctl log
stereoctl log 200</pre>
<p>Lines look like this:</p>
<pre>&lt;date&gt; &lt;time&gt; [info] daemon started (mode=playback interval=2s actions=3 channels=stereo)
&lt;date&gt; &lt;time&gt; [info] stereo engaged
&lt;date&gt; &lt;time&gt; [info] playback stopped - reverted</pre>
<p>If there is none yet: <code>no log yet</code>.</p>
<div class="tech"><p>The log is <code>/data/adb/cmf-stereo/stereo.log</code>. It is moved to <code>stereo.log.1</code> when it passes <code>LOG_MAX_KB</code> (512 KB by default), when the daemon starts. How much it writes is set by <code>LOG_LEVEL</code>.</p></div>
"""},

{"title": "edit",
 "html": """
<p>Prints the paths of the two config files, so you can open them in an editor.</p>
<pre>stereoctl edit</pre>
<pre>/data/adb/cmf-stereo/stereo.conf
/data/adb/cmf-stereo/actions.conf</pre>
"""},

{"title": "probe",
 "html": """
<p>Dumps the phone's audio hardware into a folder on your storage, for working out the routing on a new device. <strong>It changes nothing</strong> on the phone.</p>
<pre>stereoctl probe              # writes to /sdcard
stereoctl probe /some/dir    # or to another folder</pre>
<p>It shows its progress in eleven steps, then a summary:</p>
<pre>Probing audio hardware -&gt; /sdcard/cmf-stereo-probe-&lt;timestamp&gt;
  [1/11] device identity
  [2/11] ALSA topology
  [3/11] mixer controls
  ...
  [11/11] safety baseline

Done. Report: /sdcard/cmf-stereo-probe-&lt;timestamp&gt;
      Tarball: /sdcard/cmf-stereo-probe-&lt;timestamp&gt;.tar.gz</pre>
<p>The folder holds the device identity, the ALSA topology, every mixer control, candidate control names, the smart-amp drivers, the HAL config files, the speaker device port, the HAL implementation, the current routing, MediaTek's AudioParam tree and a safety baseline of the earpiece gains. Section 12.8 lists every file.</p>
"""},

{"title": "report",
 "html": """
<p>Folds the newest probe into <strong>one plain text file</strong>, because chat and mail clients often refuse <code>.tar.gz</code> files.</p>
<pre>stereoctl report</pre>
<pre>wrote /sdcard/cmf-stereo-report.txt (&lt;size&gt;, &lt;n&gt; lines)
source: /sdcard/cmf-stereo-probe-&lt;timestamp&gt;</pre>
<p>If no probe exists yet: <code>no probe report found - run: stereoctl probe</code>.</p>
<div class="tech"><p>It includes <code>SUMMARY.txt</code>, <code>00-device.txt</code>, <code>01-alsa.txt</code>, <code>02-mixer.txt</code>, <code>03-candidates.txt</code>, <code>04-amplifier.txt</code>, <code>06-speaker-port.txt</code>, <code>07-hal.txt</code>, <code>10-safety.txt</code>, <code>09-audio-param/index.txt</code> and the audio policy XML files. The command also accepts a probe folder as its argument instead of the newest one.</p></div>
"""},

{"title": "scan",
 "html": """
<p>Searches the mixer for candidate controls by name. With no pattern it looks for receiver, earpiece, speaker, mux and amp names.</p>
<pre>stereoctl scan
stereoctl scan 'ADDA_DL'</pre>
<div class="tech"><p>The pattern is a case-insensitive extended regular expression; the default in the code is <code>receiver|earpiece|rcv|handset|spk|speaker|mux|amp</code>.</p></div>
"""},

{"title": "ctl",
 "html": """
<p>Reads or writes a single mixer control. This is the one to experiment with: find a candidate with <code>scan</code>, flip it while music plays, and listen to the earpiece.</p>
<pre>stereoctl ctl 'Handset Volume'</pre>
<pre>Handset Volume = 0
  (&lt;raw line, with the range or the enum options&gt;)</pre>
<pre>stereoctl ctl 'Handset Volume' 4</pre>
<pre>Handset Volume: 0 -&gt; 4</pre>
<p>Errors: <code>no such control: NAME</code>, <code>failed to set 'NAME'</code>, or <code>usage: stereoctl ctl NAME [VALUE]</code> with no name.</p>
<div class="warn"><p>A wrong write can mean silence, a crash of the audio HAL, or an overdriven earpiece. Change gains one step at a time, and turn the module <code>off</code> first if you test by hand, or the daemon will undo your change within seconds.</p></div>
"""},

{"title": "dump",
 "html": """
<p>Prints every mixer control and its value.</p>
<pre>stereoctl dump &gt; /sdcard/mixer.txt</pre>
"""},

{"title": "diff",
 "html": """
<p>Takes a snapshot of the mixer, waits, takes another, and shows what changed. Start or stop playback, or plug in headphones, during the wait: this is how you find which controls really carry media.</p>
<pre>stereoctl diff 20</pre>
<pre>snapshot taken (&lt;n&gt; controls).
now change what you want to observe - start music, stop it, plug in
headphones - you have 20s.

controls that changed:
  - &lt;control before&gt;
  + &lt;control after&gt;</pre>
<p>The default wait is 20 seconds. If nothing changed: <code>(no control changed)</code>.</p>
"""},

{"title": "xml-patch and xml-revert",
 "html": """
<p>An optional tool for <strong>other devices</strong>. If a phone's audio policy declares its speaker as mono, Android mixes to one channel before the audio HAL sees the sound. <code>xml-patch</code> widens only the speaker's port to stereo, in an overlay copy; <code>xml-revert</code> removes it. Both take effect after a reboot.</p>
<pre>stereoctl xml-patch
stereoctl xml-revert</pre>
<p><strong>On the CMF Phone 1 it does nothing:</strong> its policy already declares a stereo speaker port, so you will see:</p>
<pre>  skip (already stereo): &lt;file&gt;

Nothing patched - the policy does not declare a mono speaker port,
so this step is not what is holding stereo back on this device.</pre>
<div class="tech"><p>Only the speaker <code>&lt;devicePort&gt;</code> block is rewritten (<code>AUDIO_CHANNEL_OUT_MONO</code> to <code>AUDIO_CHANNEL_OUT_STEREO</code>); everything else stays byte-identical. The result must pass the structural check (section 8.7) or it is rejected. The overlay is guarded by the boot watchdog. Alone it does not create stereo; it only stops the framework folding to one channel.</p></div>
"""},

]},

# ---------------------------------------------------------------------------
# 7. Configuration files
# ---------------------------------------------------------------------------
{"title": "Configuration files",
 "intro": "<p>All settings live in two text files that survive module updates. This chapter describes every setting: its values, its default, what it does and when to change it.</p>",
 "sections": [

{"title": "Where the files live",
 "html": """
<p>Everything is in <code>/data/adb/cmf-stereo/</code>, which survives module updates and uninstalls.</p>
<table>
<tr><th>File</th><th>What it holds</th></tr>
<tr><td><code>stereo.conf</code></td><td>behaviour: mode, channels, attenuation, protection, poll interval, log level</td></tr>
<tr><td><code>actions.conf</code></td><td>the routing itself, one action per line</td></tr>
<tr><td><code>stereo.log</code></td><td>what the daemon did</td></tr>
<tr><td><code>state/</code></td><td>saved original values, used to revert</td></tr>
</table>
<p>Section 12.10 lists every other file the module keeps there.</p>
"""},

{"title": "Editing the settings safely",
 "html": """
<ul>
<li>Prefer the apps or <code>stereoctl</code>: <code>stereoctl channels</code> for the mode and <code>stereoctl protect</code> for the protection. They write the file for you and apply the change.</li>
<li>To edit by hand, open the file as root with any text editor (<code>stereoctl edit</code> prints the paths), save it, then run <code>stereoctl restart</code>.</li>
<li><code>MODE</code> and <code>ENABLED</code> are re-read every cycle; they need no restart.</li>
<li>Each line is <code>NAME=value</code>. Lines starting with <code>#</code> are comments.</li>
</ul>
<div class="warn"><p>Do not set <code>CHANNELS=stereo</code> by hand: Stereo needs its files staged and checked, which only <code>stereoctl channels stereo</code>, the apps or the Action button do.</p></div>
<div class="tech"><p>The file is read by the shell (it is sourced), so keep values simple: no spaces around <code>=</code>, and quote values that contain <code>|</code>, as the installer does for <code>PLAYBACK_CTL</code>.</p></div>
"""},

{"title": "All settings at a glance",
 "html": """
<table>
<tr><th>Setting</th><th>Values</th><th>Default</th></tr>
<tr><td><code>ENABLED</code></td><td>1, 0</td><td>1</td></tr>
<tr><td><code>MODE</code></td><td>playback, always</td><td>playback</td></tr>
<tr><td><code>WATCH_INTERVAL</code></td><td>seconds</td><td>2</td></tr>
<tr><td><code>STARTUP_DELAY</code></td><td>seconds</td><td>10</td></tr>
<tr><td><code>REQUIRE_SPEAKER_ROUTE</code></td><td>0, 1</td><td>0</td></tr>
<tr><td><code>GUARD_CTL</code> / <code>GUARD_VALUE</code></td><td>mixer control / value</td><td>empty (CMF Phone 1: <code>aw_dev_0_switch</code> / <code>Enable</code>)</td></tr>
<tr><td><code>PLAYBACK_CTL</code> / <code>PLAYBACK_VALUE</code></td><td>controls separated by <code>|</code> / value</td><td>empty / 1 (CMF Phone 1: six DSP task switches / 1)</td></tr>
<tr><td><code>MIXER_CARD</code></td><td>ALSA card number</td><td>empty (card 0)</td></tr>
<tr><td><code>CHANNELS</code></td><td>mono, stereo</td><td>mono</td></tr>
<tr><td><code>STEREO_ATTEN_DB</code></td><td>0&ndash;30 (dB)</td><td>6</td></tr>
<tr><td><code>SPEAKER_BOOST</code></td><td>0&ndash;6 (dB)</td><td>0</td></tr>
<tr><td><code>BASS_PROTECT</code></td><td>off, light, medium, strong</td><td>medium</td></tr>
<tr><td><code>EARPIECE_LIMIT</code></td><td>on, off</td><td>on</td></tr>
<tr><td><code>EARPIECE_LEVELLER</code></td><td>off, light, medium, strong</td><td>off</td></tr>
<tr><td><code>LOG_LEVEL</code></td><td>debug, info, warn</td><td>info</td></tr>
<tr><td><code>LOG_MAX_KB</code></td><td>kilobytes</td><td>512</td></tr>
</table>
"""},

{"title": "ENABLED",
 "html": """
<p>The master switch. <code>1</code> (default): the module works. <code>0</code>: it does nothing at all.</p>
<p><strong>When to change it:</strong> rarely; <code>stereoctl off</code> and the apps' on/off do the same through a separate kill-switch file. Re-read every cycle.</p>
<div class="warn"><p>As with <code>stereoctl off</code>: in Stereo, switch to Mono first, or the speaker may play the left channel alone once the amp returns to its stock slot.</p></div>
"""},

{"title": "MODE",
 "html": """
<table>
<tr><th>Value</th><th>Meaning</th></tr>
<tr><td><code>playback</code> (default)</td><td>Drive the earpiece only while audio is actually playing. Recommended: the earpiece is not built to run continuously.</td></tr>
<tr><td><code>always</code></td><td>Keep the routing applied at all times (still only while the guard allows it).</td></tr>
</table>
<p><strong>When to change it:</strong> almost never. <code>always</code> is louder in theory only, harder on the earpiece, and costs idle power. Re-read every cycle.</p>
"""},

{"title": "WATCH_INTERVAL",
 "html": """
<p>How often, in seconds, the daemon re-asserts the routing. Default <strong>2</strong>.</p>
<p>The audio HAL resets mixer controls on every route change, so this cannot be very large. 2 is a good balance; <strong>raise it to 5 if you notice battery drain</strong>.</p>
<div class="note"><p>A longer interval also means the earpiece joins in a little later after you press play, the amp's right slot comes a little later at the start of a stream, and the crash-loop guard looks less often.</p></div>
"""},

{"title": "STARTUP_DELAY",
 "html": """
<p>Seconds to wait after boot before touching anything. Default <strong>10</strong>. It gives the audio HAL time to settle after Android has started.</p>
<p><strong>When to change it:</strong> normally never. <code>stereoctl restart</code> ignores it and starts at once.</p>
"""},

{"title": "REQUIRE_SPEAKER_ROUTE",
 "html": """
<p>Skip the earpiece when headphones or Bluetooth audio are connected, by checking Android's audio state. Default <strong>0</strong> (off).</p>
<p>It costs one <code>dumpsys</code> call per cycle, so it is off by default: the routing usually falls away on its own when the output changes, and on the CMF Phone 1 the guard (next section) already does this job with a single mixer read.</p>
<p><strong>When to change it:</strong> on another device without a usable guard, if the earpiece keeps playing with headphones in.</p>
<div class="tech"><p>Set to 1, it reads the first 200 lines of <code>dumpsys audio</code> and skips the earpiece if they mention <code>BLUETOOTH_A2DP</code>, <code>WIRED_HEADPHONE</code>, <code>WIRED_HEADSET</code> or <code>USB_HEADSET</code>. If the dump is empty, it does not block.</p></div>
"""},

{"title": "GUARD_CTL and GUARD_VALUE",
 "html": """
<p>Apply the routing only while the mixer control <code>GUARD_CTL</code> reads <code>GUARD_VALUE</code>. Leave <code>GUARD_CTL</code> empty to switch the check off.</p>
<p>On the CMF Phone 1 the installer sets:</p>
<pre>GUARD_CTL='aw_dev_0_switch'
GUARD_VALUE='Enable'</pre>
<p>That is the speaker amp's switch, which the HAL turns off when headphones or Bluetooth take over. So the earpiece follows the speaker rather than playing to nobody.</p>
<p><strong>When to change it:</strong> not on the CMF Phone 1 (the installer sets it again on every install). Use <code>stereoctl guard off</code> or <code>solo</code> for a temporary bypass.</p>
<div class="tech"><p>One mixer read per cycle, no <code>dumpsys</code>. If the control cannot be read at all, the guard does not block.</p></div>
"""},

{"title": "PLAYBACK_CTL and PLAYBACK_VALUE",
 "html": """
<p>How the module tells that audio is playing. <code>PLAYBACK_CTL</code> names one or more mixer controls, separated by <code>|</code>; audio is playing when any one of them reads <code>PLAYBACK_VALUE</code> (default <code>1</code>).</p>
<p>On the CMF Phone 1 the installer sets all six DSP playback task switches:</p>
<pre>PLAYBACK_CTL='dsp_music_runtime_en|dsp_fast_runtime_en|dsp_primary_runtime_en|dsp_deepbuf_runtime_en|dsp_voipdl_runtime_en|dsp_offload_runtime_en'
PLAYBACK_VALUE='1'</pre>
<p>Empty means: scan <code>/proc/asound</code> for a running stream. That scan <strong>misses DSP playback entirely</strong>, so on devices where media bypasses the normal path, name a control the HAL flips when media starts. Find one with <code>stereoctl diff</code>.</p>
<p><strong>When to change it:</strong> not on the CMF Phone 1 (set again on every install).</p>
<div class="tech"><p>Measured on the phone, logging the switches each second: a game turns on <code>dsp_fast_runtime_en</code>; a music player <code>dsp_music_runtime_en</code> with <code>dsp_primary_runtime_en</code> (<code>dsp_deepbuf_runtime_en</code> for a moment); nothing stays on when playback stops. <code>dsp_playback_runtime_en</code> stays on even when idle, so it is not used. Watching <code>dsp_music</code> alone (up to v1.0.2) left games on the speaker only. If none of the named controls can be read (renamed by a vendor update, say), the module falls back to the procfs scan rather than reporting "never playing" for ever.</p></div>
"""},

{"title": "MIXER_CARD",
 "html": """
<p>The ALSA sound card to talk to. Empty (default) means <code>tinymix</code>'s default, card 0, which is right on essentially every phone.</p>
<p><strong>When to change it:</strong> only if a probe shows several sound cards and the routing is on another one.</p>
"""},

{"title": "CHANNELS",
 "html": """
<table>
<tr><th>Value</th><th>Meaning</th></tr>
<tr><td><code>mono</code> (default)</td><td>Stock. Both drivers play the full mix; Awinic speaker protection.</td></tr>
<tr><td><code>stereo</code></td><td>Left and right on the earpiece and the speaker, following the screen. Awinic's DSP speaker protection is off for media (calls keep it); the attenuation and the module's protection stand in.</td></tr>
</table>
<p><strong>Change it with <code>stereoctl channels mono|stereo</code></strong>, the apps or the Action button, not by hand: Stereo needs its files staged. The module itself sets it back to <code>mono</code> when a safety net removes Stereo.</p>
<div class="note"><p>The comment above this setting in <code>stereo.conf</code> still says that both modes need a reboot and that the earpiece plays the left channel and the speaker the right. Both are out of date: switching has been live since v0.9.4, and left and right follow the screen since v0.9.5.</p></div>
"""},

{"title": "STEREO_ATTEN_DB",
 "html": """
<p>In Stereo, hold the speaker amp this many dB down. Range 0&ndash;30, default <strong>6</strong>. This is the apps' <em>speaker level</em>: 10 = 6 dB, 2 dB more per level down (section 5.3).</p>
<p>Together with the protection, it is part of the margin that stands in for Awinic's protection, on top of the amp's own over-temperature and over-current cut-outs.</p>
<p><strong>When to change it:</strong> raise it if you play loud, or to balance the speaker against the earpiece.</p>
<div class="warn"><p>Values under 6 dB give up part of the safety margin the module was designed with. The clean app never goes there.</p></div>
"""},

{"title": "The protection settings",
 "html": """
<table>
<tr><th>Setting</th><th>Values</th><th>Default</th><th>What it does</th></tr>
<tr><td><code>SPEAKER_BOOST</code></td><td>0&ndash;6</td><td>0</td><td>dB less amp attenuation, only while the protection runs; the speaker's peaks still never exceed what Awinic allows in Mono (&minus;5 dB).</td></tr>
<tr><td><code>BASS_PROTECT</code></td><td>off, light, medium, strong</td><td>medium</td><td>Holds the speaker's band below 100 Hz at &minus;8 / &minus;14 / &minus;20 dB below the amp's full output, only when louder.</td></tr>
<tr><td><code>EARPIECE_LIMIT</code></td><td>on, off</td><td>on</td><td>Holds the earpiece at &minus;2.5 dBFS (it clips above).</td></tr>
<tr><td><code>EARPIECE_LEVELLER</code></td><td>off, light, medium, strong</td><td>off</td><td>Raises the earpiece's quiet and medium passages by at most 4 / 8 / 12 dB; no frequency changed, peaks never above today's, near-silence left alone.</td></tr>
</table>
<p>Change them with <code>stereoctl protect</code> or the apps. Chapter 5 explains each one and when to change it.</p>
"""},

{"title": "LOG_LEVEL and LOG_MAX_KB",
 "html": """
<table>
<tr><th>Setting</th><th>Values</th><th>Default</th></tr>
<tr><td><code>LOG_LEVEL</code></td><td><code>debug</code> (everything), <code>info</code> (normal events), <code>warn</code> (problems only)</td><td><code>info</code></td></tr>
<tr><td><code>LOG_MAX_KB</code></td><td>size in kilobytes before the log is rotated</td><td>512</td></tr>
</table>
<p><strong>When to change it:</strong> set <code>debug</code> while chasing a problem, <code>warn</code> to keep the log small.</p>
"""},

{"title": "actions.conf: the routing",
 "html": """
<p><code>actions.conf</code> holds the routing, one action per line, applied from top to bottom. Blank lines and lines starting with <code>#</code> are ignored.</p>
<pre>ctl|&lt;mixer control name&gt;|&lt;value&gt;     set an ALSA mixer control
sysfs|&lt;path&gt;|&lt;value&gt;                 write to a sysfs node
prop|&lt;property&gt;|&lt;value&gt;              set a system property</pre>
<p>Before changing anything, the module saves the original value of everything it touches under <code>/data/adb/cmf-stereo/state/</code>, and restores it when playback stops, the module is turned off, or it is uninstalled.</p>
<div class="warn"><p>On another device this file ships <strong>empty by design</strong>: the control names must come from a real probe. A wrong write is at best silence and at worst a damaged earpiece. When you first find a working route, set its gain <strong>low</strong> and raise it one step at a time. Distortion or a rattle means back off at once.</p></div>
<div class="tech"><p>A <code>ctl</code> line whose control does not exist is skipped with a warning in the log. A <code>sysfs</code> write denied by SELinux is logged. A <code>prop</code> is set with <code>resetprop</code> where available, otherwise <code>setprop</code>. An unknown kind is logged and skipped.</p></div>
"""},

{"title": "The CMF Phone 1 routing profile",
 "html": """
<p>On a CMF Phone 1, <code>actions.conf</code> holds three lines, verified on Nothing OS B4.1-260615-1652, Android 16:</p>
<pre>ctl|Handset Volume|0
ctl|ADDA_DL_CH1 DL_24CH_CH1|1
ctl|RCV Mux|Voice Playback</pre>
<ol>
<li><strong>Handset Volume 0</strong>: the earpiece gain, +8 dB, set <em>before</em> it is driven.</li>
<li><strong>ADDA_DL_CH1 DL_24CH_CH1</strong>: feed the internal DAC from the same stream that already goes to the speaker.</li>
<li><strong>RCV Mux = Voice Playback</strong>: route that DAC to the earpiece.</li>
</ol>
<p>Order matters: the feed is connected before the mux is opened, so the receiver is never pointed at an undefined path. These three lines are the same in Mono and Stereo; the earpiece always takes channel 1 of the stream, the left channel.</p>
<div class="note"><p>To make the earpiece quieter, raise the first number towards 18, one step at a time. Back off at the first buzz or rattle.</p></div>
"""},

]},

# ---------------------------------------------------------------------------
# 8. Safety and recovery
# ---------------------------------------------------------------------------
{"title": "Safety and recovery",
 "intro": "<p>The module is built so that a mistake costs a reboot, not a trip to recovery. This chapter describes each safety net, what triggers it, and how to recover by hand if you ever need to.</p>",
 "sections": [

{"title": "The safety nets at a glance",
 "html": """
<table>
<tr><th>Safety net</th><th>Protects against</th><th>What it does</th></tr>
<tr><td>Boot watchdog</td><td>a boot that fails with the module's overlay in place</td><td>after two failed boots, removes the overlay; Stereo goes back to Mono</td></tr>
<tr><td>Crash-loop guard</td><td>the audio service dying again and again in Stereo</td><td>3 restarts within a minute: back to the stock files (Mono) at once</td></tr>
<tr><td>Hash checks</td><td>patching or mounting the wrong files</td><td>only the exact analysed build is patched; every result is checked</td></tr>
<tr><td>Unknown-build guard</td><td>a Nothing OS update</td><td>stock Mono until a module update supports the new build</td></tr>
<tr><td>Live switch checks</td><td>a switch going wrong</td><td>every file read back; audio service must stay up; otherwise stock files</td></tr>
<tr><td>Ships empty elsewhere</td><td>wrong mixer writes on another phone</td><td>changes nothing until real routing is filled in</td></tr>
<tr><td>XML validation</td><td>a broken audio policy</td><td>a patched policy is installed only if it passes a structural check</td></tr>
<tr><td>Restore on stop</td><td>leftover changes</td><td>every touched control put back on stop, off or uninstall</td></tr>
</table>
<p>The boot watchdog, the crash-loop guard and a failed live switch ending on the stock files are covered by tests on fake files. None has been needed on the phone yet.</p>
"""},

{"title": "Boot watchdog",
 "html": """
<p>If two boots in a row fail to finish while the Stereo overlay (or the audio policy overlay) is in place, the module removes that overlay before it can be mounted again. Stereo goes back to stock Mono (<code>CHANNELS=mono</code>). A bad boot costs one extra reboot instead of a trip to recovery.</p>
<p>After the next good boot, the log notes it: <code>the stereo overlay was auto-removed after failed boots; channels are back to mono</code>.</p>
<div class="tech">
<p>Each boot with something active (an overlay, or any routing action) adds a strike to <code>/data/adb/cmf-stereo/boot_pending</code> in <code>post-fs-data.sh</code>. <code>service.sh</code> clears it once <code>sys.boot_completed</code> is 1 (it waits up to 180 s). At two strikes, <code>post-fs-data.sh</code> removes the overlay files before Magisk mounts them, sets <code>CHANNELS=mono</code> and leaves a marker (<code>stereo_auto_removed</code> or <code>xml_overlay_auto_removed</code>) that <code>service.sh</code> logs and deletes. <code>stereoctl status</code> shows the count on its <code>boot:</code> line.</p>
</div>
"""},

{"title": "Crash-loop guard",
 "html": """
<p>In Stereo the audio service runs the module's own code. If it kept crashing, Android would simply restart it and the phone would still boot, so the boot watchdog would never notice. The crash-loop guard covers that case: if the audio HAL restarts <strong>3 times within a minute</strong> in Stereo, the daemon puts the stock files back (Mono) at once and tells the apps.</p>
<p>The log then says: <code>the audio HAL restarted 3 times within a minute in stereo - back to mono (stock files)</code>. You can switch back to Stereo yourself once you know why.</p>
<div class="tech"><p>The daemon records the HAL's process id (<code>init.svc_debug_pid.vendor.audio-hal</code>) each cycle in <code>state/hal_pids</code> and keeps only the last 60 s; four different ids (the first seen plus three restarts) trigger it. A mode switch restarts the HAL once, which counts as one. If the live switch to Mono fails, the log says Mono comes after a reboot.</p></div>
"""},

{"title": "Hash checks on every file",
 "html": """
<p>The module never patches or mounts an audio file it has not identified exactly. Each file's SHA-256 fingerprint must match the analysed build before it is patched, and the patched result must match the tested one before it is used.</p>
<ul>
<li>A different file &mdash; another firmware, another region's build, a file changed by another module &mdash; is refused, and the phone stays on Mono.</li>
<li>Files from older Stereo versions (v0.9.0 to v1.0.3) are recognised and converted to the current one.</li>
<li>The module's own protection library is checked against its own hash. Without a matching library, Stereo still plays (the patch falls back to the rotation swap alone) and the speaker keeps its fixed attenuation.</li>
</ul>
<div class="tech"><p>The expected hashes are in <code>scripts/channels.sh</code> (section 12.6). <code>hal-swap/run.sh</code> checks the bytes <code>channels.sh</code> writes against the assembled patch, in an ARM64 emulator.</p></div>
"""},

{"title": "The unknown-build guard",
 "html": """
<p>At every boot, before anything is mounted, the module checks the phone's own vendor audio files against the analysed build. If they differ (after a Nothing OS update, say), the Stereo overlay is removed and the phone boots on stock Mono. Mounting the old patched files over a new build would run an old audio HAL against new firmware and configs.</p>
<p>The card then says <code>[Stereo unavailable]</code> and <code>stereoctl status</code> shows <code>build:     updated</code>, until a module release supports the new build. The log says: <code>this Nothing OS build is not supported yet - stereo is unavailable, mono runs</code>.</p>
"""},

{"title": "Ships empty on other devices",
 "html": """
<p>Mixer control names differ from device to device. A wrong write is, in ascending order of regret: nothing, silence, a crash of the audio HAL, or an earpiece driven past what a receiver is built for. The earpiece has a fraction of the speaker's movement and power handling, and no protection circuit that assumes you will use it for music.</p>
<p>So on any phone that is not a CMF Phone 1, the module installs with an empty <code>actions.conf</code> and changes nothing. The daemon starts, finds no actions, logs <code>no actions configured - nothing to do (run 'stereoctl probe' first)</code> and exits. Probe first, then fill in real names.</p>
<div class="warn"><p>When you find a working route on another device, start its gain low and raise it a step at a time. Distortion or rattle means back off &mdash; that damage does not come back.</p></div>
"""},

{"title": "XML validation",
 "html": """
<p>No patched audio policy is installed unless it passes a structural check. Android has no <code>xmllint</code>, and a malformed audio policy takes <code>audioserver</code> down hard enough to loop the boot.</p>
<div class="tech"><p>Checked: balanced <code>&lt;module&gt;</code>, <code>&lt;modules&gt;</code>, <code>&lt;mixPort&gt;</code>, <code>&lt;mixPorts&gt;</code>, <code>&lt;devicePort&gt;</code>, <code>&lt;devicePorts&gt;</code>, <code>&lt;route&gt;</code>, <code>&lt;routes&gt;</code> and root elements (self-closing ones count as open and close), the closing root tag present, and no stray trailing backslash from a bad insertion. This applies to <code>stereoctl xml-patch</code>, which the CMF Phone 1 does not need.</p></div>
"""},

{"title": "Everything put back",
 "html": """
<p>Before the module changes a control, it saves its original value once. It puts that value back:</p>
<ul>
<li>when playback stops (in <code>MODE=playback</code>);</li>
<li>when you turn the module off;</li>
<li>when the daemon stops;</li>
<li>when you uninstall the module.</li>
</ul>
<p>The speaker amp's own gain is given back when you go to Mono or uninstall.</p>
<div class="tech"><p>Saved originals are in <code>/data/adb/cmf-stereo/state/</code>, one file per control. They survive a reinstall; <code>stereoctl reset</code> clears them if one is ever wrong.</p></div>
"""},

{"title": "Manual recovery",
 "html": """
<p>If you ever need to switch the module off without booting normally:</p>
<pre>adb wait-for-device shell           # or hold vol-down for safe mode
su
touch /data/adb/modules/cmf_stereo/disable
reboot</pre>
<p>Both Magisk and KernelSU honour the <code>disable</code> file, and the boot script never touches audio when the actions list is empty.</p>
<div class="note"><p>Thanks to the boot watchdog you should rarely need this: two failed boots with Stereo on already put the phone back on Mono by themselves.</p></div>
"""},

{"title": "Reporting a security problem",
 "html": """
<p>The module runs as root. If you find a security problem, <strong>do not open a public issue</strong>. Report it privately on the project's GitHub page: open the <strong>Security</strong> tab and choose <strong>Report a vulnerability</strong>. Only the maintainer sees it.</p>
<p>In scope: anything that lets another app, file or user run root code through the module's scripts (including via its config or state files); the module writing, deleting or mounting outside what it documents; staging accepting or producing a vendor file other than the verified ones, or the hash checks being bypassable; a bootloop the watchdog does not recover from; anything that can drive the speaker or earpiece past safe levels without you asking for it.</p>
<p>Include the version, your phone model and build, what happens and how, and logs. Only the latest release gets fixes.</p>
"""},

]},

# ---------------------------------------------------------------------------
# 9. Troubleshooting
# ---------------------------------------------------------------------------
{"title": "Troubleshooting",
 "intro": "<p>Start with the first section: three quick looks settle most problems. Then find your symptom below.</p>",
 "sections": [

{"title": "First steps for any problem",
 "html": """
<ol>
<li><strong>Look at the module's card.</strong> Its first words say what runs (section 3.2).</li>
<li><strong>Run <code>stereoctl status</code></strong> with music playing (section 6.3).</li>
<li><strong>Read the log:</strong> <code>stereoctl log 100</code>. Lines marked <code>[warn]</code> usually name the problem.</li>
<li><strong>Make sure you are on the latest release.</strong> Only the latest gets fixes.</li>
<li><strong>Think about other modules</strong> that change audio (section 9.9).</li>
</ol>
"""},

{"title": "The earpiece is silent",
 "html": """
<p>Start music, then run:</p>
<pre>stereoctl doctor</pre>
<p>It walks every layer that can silence the earpiece and names the one responsible, with its fix. Fix the items it marks, then run it again. The next section explains each message.</p>
<p>Also check:</p>
<ul>
<li>headphones or Bluetooth are not connected (the earpiece steps aside for them);</li>
<li>the media volume is up;</li>
<li><code>stereoctl solo</code>, to hear the earpiece alone, then <code>stereoctl unsolo</code>.</li>
</ul>
"""},

{"title": "Reading doctor's messages",
 "html": """
<table>
<tr><th>Step</th><th>Message</th><th>Fix</th></tr>
<tr><td>1. module armed</td><td><code>NO - kill switch set (it survives reboots).</code></td><td><code>stereoctl on</code></td></tr>
<tr><td>2. daemon</td><td><code>NOT running.</code></td><td><code>stereoctl restart</code></td></tr>
<tr><td>2. daemon</td><td><code>N RUNNING - they fight over the mixer.</code></td><td><code>stereoctl restart</code></td></tr>
<tr><td>3. tinymix</td><td><code>UNUSABLE - mixer writes cannot happen</code></td><td>see section 9.13</td></tr>
<tr><td>4. playback</td><td><code>IDLE - with MODE=playback nothing is applied until audio plays.</code></td><td>start music and run doctor again</td></tr>
<tr><td>5. guard</td><td><code>BLOCKING: aw_dev_0_switch = ..., needs Enable</code></td><td>the speaker amp is off (headphones, or turned off by hand): <code>stereoctl solo</code>, or re-enable the amp</td></tr>
<tr><td>6. applying now</td><td><code>FAILED  &lt;control&gt; want X, reads Y</code></td><td>the control did not take its value; check the name in <code>actions.conf</code></td></tr>
</table>
<p>If everything applied and it is still silent, doctor says: <code>Everything applied. If it is still silent, the path is powered but inaudible - check Handset Volume and the media volume.</code></p>
<div class="tech"><p>Step 4 also prints which detector answered: <code>mixer controls: ...</code> (the DSP task switches) or <code>procfs substream scan</code> (the fallback, which misses DSP playback). Step 5 says <code>bypassed (solo mode)</code> or <code>none configured</code> when it does not apply.</p></div>
"""},

{"title": "No stereo: both drivers play the same",
 "html": """
<ol>
<li>Check what runs: <code>stereoctl channels</code>. If it says <code>running: mono</code>, switch: <code>stereoctl channels stereo</code>.</li>
<li>If it says <code>staged:  stereo   (reboot to apply)</code>, reboot.</li>
<li>If the card says <code>[Stereo unavailable]</code> or <code>status</code> shows <code>build: updated</code>, your build is not supported yet (section 4.11).</li>
<li>If Stereo was on and is now Mono by itself, a safety net switched it (section 9.12).</li>
<li>Test with <code>LEFT_ONLY_3min.wav</code>: in Stereo, earpiece on your left, only the earpiece should play.</li>
<li>Many recordings have little difference between left and right. The test files show clearly whether Stereo works.</li>
</ol>
"""},

{"title": "Stereo refuses to start",
 "html": """
<p>If <code>stereoctl channels stereo</code> prints <code>stereo NOT staged:</code> followed by a reason, your phone's files could not be prepared. Your phone stays on Mono, unchanged.</p>
<table>
<tr><th>Reason</th><th>Meaning</th></tr>
<tr><td><code>... missing - not a CMF Phone 1 audio stack</code></td><td>The audio files the module patches are not there.</td></tr>
<tr><td><code>... is not the analysed build (&lt;hash&gt;) - refusing to patch an unknown binary</code></td><td>Your audio HAL differs from the analysed one: another Nothing OS build or region, or a file changed by another module.</td></tr>
<tr><td><code>/vendor/etc/aurisys_config_rv.xml is not the analysed file - refusing</code></td><td>The same, for the DSP configuration file.</td></tr>
<tr><td><code>patched ... does not match the tested binary</code> / <code>... does not match the expected result</code></td><td>The patch did not produce the tested file; nothing is used.</td></tr>
<tr><td><code>cannot copy ...</code> / <code>patching ... failed</code></td><td>A copy or write failed (storage full, permissions).</td></tr>
</table>
<p>If you are on a build other than the tested one (section 1.4), Stereo has to wait until that build is checked and added in a module release.</p>
"""},

{"title": "Left and right are reversed",
 "html": """
<ul>
<li>Make sure <strong>auto-rotate is on</strong>; left and right follow the screen's rotation.</li>
<li>For apps with their own audio effect (VLC), wait about <strong>2 seconds</strong> after pressing play or turning the phone.</li>
<li>If two apps play at once, one of them with its own effect, one can come out reversed with the earpiece on your right. This is a known limit (section 4.12).</li>
<li>Check with <code>LEFT10s_RIGHT10s.wav</code>: the voice says which side should play.</li>
</ul>
"""},

{"title": "Distortion, crackle or rattle",
 "html": """
<div class="warn"><p><strong>Back off at once.</strong> Damage to a driver does not come back.</p></div>
<p><strong>From the speaker</strong> (in Stereo):</p>
<ul>
<li>lower the speaker level (raise <code>STEREO_ATTEN_DB</code>);</li>
<li>reduce or remove the speaker boost;</li>
<li>make sure the deep bass guard is on; try <code>strong</code>;</li>
<li>for loud listening, switch to <strong>Mono</strong>.</li>
</ul>
<p><strong>From the earpiece:</strong></p>
<ul>
<li>in Stereo, make sure the earpiece limiter is on (<code>stereoctl protect earpiece on</code>);</li>
<li>make the earpiece quieter: raise the <code>Handset Volume</code> number in <code>actions.conf</code> (or lower the app's earpiece level);</li>
<li>remember that in Mono the earpiece limiter does not run.</li>
</ul>
<div class="tech"><p>Measured in Stereo without Awinic: the speaker's distortion grows steadily with level from about &minus;12 dBFS, mostly odd harmonics, to about 27 % at &minus;3 dBFS at 1.2&ndash;2 kHz; the earpiece stays under about 5&ndash;10 % up to about &minus;3 dBFS from 150 Hz up, and clips in its top 1.5 dB.</p></div>
"""},

{"title": "The sound stops, drops out or pauses",
 "html": """
<ul>
<li><strong>Right after a switch</strong> between Mono and Stereo: this is expected. The audio service restarted; press play again.</li>
<li><strong>Stereo turned into Mono by itself</strong>: the crash-loop guard found the audio service restarting again and again. Check <code>stereoctl log</code> (section 9.12).</li>
<li><strong>The earpiece comes and goes</strong> with <code>MODE=playback</code>: that is the module following playback. If it misses some apps, make sure you are on v1.0.3 or newer (games were not detected before).</li>
<li><strong>The earpiece joins a moment after you press play</strong>: up to one cycle (2 s by default).</li>
<li><strong>Another module</strong> may be fighting over audio (next section).</li>
</ul>
"""},

{"title": "Full volume not reached: check other modules",
 "html": """
<p>Other modules that change audio can interfere with this one or with the phone's volume. <strong>A real case from the test phone:</strong> NothingTweaks' <strong>Customise Volume Steps</strong>, set to 24 steps, made the highest volume step silent, and the middle of the bar was the loudest; it looked like this module's fault even with the module off. With the custom steps turned off, full volume was correct again.</p>
<p>If something sounds wrong that this manual does not explain:</p>
<ol>
<li>list your modules, especially any that touch audio, volume, Dirac or effects;</li>
<li>disable them one at a time and reboot after each;</li>
<li>test again with the test files and full media volume.</li>
</ol>
<div class="warn"><p><strong>Do not run the Hi-Res Audio module at the same time</strong>: the two touch the same files. A module that mounts over the same audio files also makes a live switch refuse with <code>a mount over the audio files is not ours - not touching it</code>.</p></div>
"""},

{"title": "The earpiece is weak or uneven",
 "html": """
<ul>
<li>Check <code>Handset Volume</code> in <code>actions.conf</code>: <strong>0 is the loudest</strong> (+8 dB). 31 is the codec's mute value, not the top. The installer corrects old values above 18, but check if you edited the file by hand.</li>
<li>If the log keeps showing <code>Handset Volume: 0 -&gt; 31</code>, the file has the old value: the daemon pulls the earpiece down every cycle while the HAL puts it back. Set it to 0.</li>
<li>The earpiece will never match the speaker. Balance by turning the speaker down, or try the earpiece leveller (Stereo).</li>
</ul>
"""},

{"title": "The card says Not running, or the daemon misbehaves",
 "html": """
<p>If the card ends with <code>Not running: restart it in the app.</code>, or <code>status</code> says <code>daemon:    not running</code>:</p>
<pre>stereoctl restart</pre>
<p>If it does not start, read <code>stereoctl log</code>. Possible reasons:</p>
<ul>
<li><code>no actions configured - nothing to do (run 'stereoctl probe' first)</code>: <code>actions.conf</code> is empty (normal on other phones);</li>
<li><code>another daemon is already running (pid ...) - exiting</code>: one is already running; that is fine;</li>
<li><code>tinymix not found but ctl actions are configured; they will be skipped</code>: see section 9.13.</li>
</ul>
<p>If <code>doctor</code> reports several daemons, <code>stereoctl restart</code> stops them all and starts one.</p>
"""},

{"title": "Back in Mono by itself",
 "html": """
<p>If you chose Stereo and find Mono running, one of the safety nets switched it. The log tells you which:</p>
<table>
<tr><th>Log line</th><th>Cause</th></tr>
<tr><td><code>boot watchdog: 2 failed boots with the stereo overlay - back to mono</code></td><td>Two boots failed with Stereo on.</td></tr>
<tr><td><code>the audio HAL restarted 3 times within a minute in stereo - back to mono (stock files)</code></td><td>The audio service crash-looped in Stereo.</td></tr>
<tr><td><code>the vendor audio files are not the analysed build (...; a Nothing OS update?) - stereo overlay removed, mono</code></td><td>Your audio files changed.</td></tr>
</table>
<p>In the first two cases you can try <code>stereoctl channels stereo</code> again, but if it happens again, stay on Mono and report it with your log.</p>
"""},

{"title": "tinymix problems",
 "html": """
<p>The module needs <code>tinymix</code> to read and write mixer controls. The CMF Phone 1 ships none, so the module bundles one. If <code>status</code> says <code>NOT FOUND</code> or <code>UNUSABLE (wrong arch, or not executable)</code>:</p>
<ul>
<li>reinstall the module, so its bundled <code>bin/tinymix</code> gets its permissions again;</li>
<li>or build tinymix yourself, or use Termux's <code>tinyalsa</code> package, and place it at <code>/data/adb/cmf-stereo/bin/tinymix</code> with <code>chmod 0755</code>.</li>
</ul>
<p>Section 12.7 describes the bundled binary and the search order.</p>
"""},

{"title": "What to send when asking for help",
 "html": """
<ul>
<li>the module version, your phone model and the Nothing OS build (compare it with the tested build in section 1.4);</li>
<li>the output of <code>stereoctl status</code> and <code>stereoctl doctor</code>, with music playing;</li>
<li>the output of <code>stereoctl channels</code> and <code>stereoctl protect</code>;</li>
<li><code>stereoctl log 200</code>;</li>
<li>the other modules you have installed;</li>
<li>on another device: <code>stereoctl probe</code>, then <code>stereoctl report</code>, and send <code>/sdcard/cmf-stereo-report.txt</code>.</li>
</ul>
"""},

]},

# ---------------------------------------------------------------------------
# 10. Questions and answers
# ---------------------------------------------------------------------------
{"title": "Questions and answers",
 "intro": "<p>Short answers to the questions people ask most, with a pointer to the full explanation.</p>",
 "sections": [

{"title": "Compatibility",
 "html": """
<p><strong>Does it work on other phones?</strong> It works on the CMF Phone 1 (A015). On any other phone it installs and does nothing; you can probe the hardware there (section 2.9).</p>
<p><strong>Does it work on Global or India builds?</strong> Untested. The module checks the audio files by hash; if they differ from the tested EEA build, it refuses Stereo and stays in Mono.</p>
<p><strong>Does it need a custom kernel?</strong> No. The routing, the amp driver, the audio HAL and the DSP libraries are all vendor code; root is enough.</p>
<p><strong>Magisk, KernelSU or APatch?</strong> All three. The Action button needs Magisk 28 or newer.</p>
<p><strong>Can I use it with the Hi-Res Audio module?</strong> No, not at the same time: they touch the same files.</p>
"""},

{"title": "Sound",
 "html": """
<p><strong>Will the speaker get louder?</strong> No. The main speaker's own path is untouched; in Stereo it is held a little lower for safety. Mono is louder overall because both drivers play.</p>
<p><strong>Why does the earpiece sound quieter than the speaker?</strong> It is a receiver, made for voice. It already plays at its maximum. Turn the speaker down to balance, or try the leveller.</p>
<p><strong>Does it change Dirac, Nothing's sound tuning?</strong> No. Dirac keeps running on the output mix in both modes.</p>
<p><strong>Does hi-res playback still work?</strong> Yes, checked in Stereo with USB Audio Player Pro (Direct 192 kHz).</p>
<p><strong>Are headphones affected?</strong> No. The earpiece steps aside, and the rotation swap applies only to the speakers.</p>
"""},

{"title": "Safety",
 "html": """
<p><strong>Can Stereo damage my speaker?</strong> Stereo turns off Awinic's speaker protection for media. The module's protection stands in with fixed limits measured against Awinic's, but without a temperature model. For long, loud listening use Mono; in Stereo lower the speaker level and back off at the first distortion.</p>
<p><strong>Can it damage my earpiece?</strong> The earpiece has no protection circuit. In Stereo the earpiece limiter keeps it below where it crackles; in Mono it plays without it. Back off at the first buzz.</p>
<p><strong>Does it write to the vendor partition?</strong> Never. Its files are mounted over the vendor paths by your root manager, and removed with the module.</p>
<p><strong>What if the phone does not boot?</strong> After two failed boots the module removes Stereo by itself. Manual recovery is in section 8.9.</p>
<p><strong>Are calls affected?</strong> No. Calls keep Awinic's protection, and a mode switch waits during a call.</p>
"""},

{"title": "Everyday questions",
 "html": """
<p><strong>Do I need to reboot to switch modes?</strong> No, since v0.9.4. The sound stops for about a second; press play again.</p>
<p><strong>Do I need the app?</strong> No. The module works on its own; the app, the Action button and <code>stereoctl</code> are three ways to control it.</p>
<p><strong>Does it drain the battery?</strong> Very little: one check every 2 seconds. Raise <code>WATCH_INTERVAL</code> to 5 if you notice drain.</p>
<p><strong>Why does the first second of a song sometimes come from one side?</strong> The amp driver resets its slot at every stream start; the module corrects it on its next cycle (section 4.9).</p>
<p><strong>What happens after a Nothing OS update?</strong> The phone boots on stock Mono, the card says Stereo unavailable, until a module update supports the new build.</p>
<p><strong>Are my settings kept when I update?</strong> Yes. They live in <code>/data/adb/cmf-stereo/</code>, which updates do not touch.</p>
"""},

]},

# ---------------------------------------------------------------------------
# 11. How it works
# ---------------------------------------------------------------------------
{"title": "How it works",
 "intro": "<p>First the idea in plain words, then each mechanism in technical detail: the routing, the two places the phone folds to mono, the daemon, the rotation swap, playback detection, the live switch and the boot scripts.</p>",
 "sections": [

{"title": "In plain words",
 "html": """
<p>Your phone has two drivers: the bottom speaker for media, and the earpiece for calls. Normally media never reaches the earpiece at all.</p>
<p>The module does three things:</p>
<ol>
<li><strong>It connects the earpiece</strong> to the same sound the speaker plays, by setting three switches in the phone's audio mixer. That alone gives you Mono: both drivers play everything.</li>
<li><strong>For Stereo, it stops the phone mixing left and right together.</strong> Two places in the phone's audio software do that, because the phone was designed with one speaker. The module switches both off, and the earpiece and the speaker each get their own channel.</li>
<li><strong>It protects the drivers</strong> in Stereo, since one of those two places was also Awinic's speaker protection.</li>
</ol>
<p>A small background service keeps those mixer switches set while you listen, because the phone's audio software resets them every time a sound starts.</p>
"""},

{"title": "Three layers, smallest hammer first",
 "html": """
<p><strong>1. Mixer actions (<code>actions.conf</code>).</strong> The real work. An ALSA mixer control enables the receiver's output stage; on MediaTek there is usually also a routing control that decides which DL (downlink) stream feeds it. Setting those while the speaker plays puts the earpiece to work next to the speaker.</p>
<p><strong>2. Audio policy overlay (<code>stereoctl xml-patch</code>, optional).</strong> If the policy declares the speaker as <code>AUDIO_CHANNEL_OUT_MONO</code>, the framework downmixes to one channel before the HAL sees it, and no mixer work brings the second channel back. The patch widens only the speaker <code>&lt;devicePort&gt;</code> to stereo, in an overlay copy. Opt-in, validated, reversible &mdash; and not needed on the CMF Phone 1.</p>
<p><strong>3. What the CMF Phone 1 actually needed</strong>: the internal DAC fed from the speaker's stream (next sections), and, for Stereo, the two mono folds switched off.</p>
"""},

{"title": "How the earpiece was brought in",
 "html": """
<p>Media on this phone never touches the internal codec. Playback runs:</p>
<pre>DL_24CH_CH1/CH2 --&gt; I2SOUT4_CH1/CH2 --&gt; Awinic aw_dev_0 smart PA --&gt; speaker
                                  &lt;-- I2SIN4 --&gt; UL3   (IV-sense feedback)</pre>
<p>The earpiece hangs off the internal codec's DAC (<code>ADDA_DL</code>), and that DAC normally has <strong>no source connected at all</strong>: every one of its roughly 20 input switches sits Off. So pointing <code>RCV Mux</code> at the receiver routes it to a silent wire &mdash; exactly what happened on the first attempt.</p>
<p>The switch that matters is <code>ADDA_DL_CH1 DL_24CH_CH1</code>: it feeds the internal DAC from the same <code>DL_24CH</code> stream already going to the speaker amp. Turn it on, then open <code>RCV Mux</code>, and the earpiece plays.</p>
<p>There is only one Awinic device (<code>aw_dev_0</code>), so there is no second amp channel to press into service; the internal codec was the only way in. That alone gives both drivers the same full mix: Mono.</p>
"""},

{"title": "The two places the phone folds to mono",
 "html": """
<p>Real Stereo needed one more step: switching off the two places the phone folds the speaker to mono.</p>
<ol>
<li><strong>The MediaTek audio HAL.</strong> <code>AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed</code> writes (L+R)/2 to both channels whenever the phone is configured for one speaker. Patching it out alone: still mono.</li>
<li><strong>Awinic's speaker protection on the audio DSP</strong> (Aurisys <code>smartpa_awinic</code>). It has one speaker model, so it mixes L+R and protects that. With it replaced by MediaTek's pass-through <code>aurisys_demo</code> as well, the amp's right slot went silent with a left-only file, and the left slot still played: the channels were separate at last.</li>
</ol>
<p>Earlier versions of the README said both drivers were hard-wired to channel 1, then that a custom kernel would be needed, then that the DSP firmware was the limit. All three were wrong; each stage was then measured (section 12.1).</p>
<div class="tech"><p>Setting <code>MTK_AUDIO_NUMBER_OF_SPEAKER</code> to 2 was rejected: it also switches the HAL to a <code>dual_speaker_output</code> path that does not exist in this phone's <code>audio_device.xml</code>, and puts Awinic's protection into two-amp mode with one amp fitted.</p></div>
"""},

{"title": "From the app to the two drivers",
 "html": """
<p>The path of a sound in Stereo:</p>
<pre>app -&gt; Android's mixer (AudioFlinger)            swaps L/R itself at rotation 270,
                                                 except a track with its own effect
    -&gt; Dirac (Nothing's tuning, session 0)
    -&gt; audio HAL, AudioALSAPlaybackHandlerBase   patched: hal-swap/patch.S loads
       ::doStereoToMonoConversionIfNeed          protect/libcmfstereo.so and calls it
         rotation swap (VLC-type outputs)        &lt;- vendor.audiohal.cmf_swap (daemon)
         speaker: bass guard, peak limiter       &lt;- vendor.audiohal.cmf_*_ceil (daemon)
         earpiece: leveller, limiter
    -&gt; audio DSP, aurisys_demo (pass-through)    aurisys_config_rv.xml patched
    -&gt; DL_24CH ch1 -&gt; codec DAC -&gt; earpiece      routing: config/actions.cmf1.conf
       DL_24CH ch2 -&gt; Awinic amp (right slot) -&gt; speaker   amp slot/attenuation: daemon</pre>
<p>Measured end to end with the HAL's and the DSP's own recordings: nothing after the patched function changes the level, so the library's ceilings are exact.</p>
"""},

{"title": "The protection library",
 "html": """
<p>The module's protection is a small library of its own, <code>libcmfstereo.so</code>, which the patched audio HAL loads once and calls for every buffer it plays, just before the DSP.</p>
<div class="tech">
<p>For a speaker-only stream (devices exactly <code>AUDIO_DEVICE_OUT_SPEAKER</code>), 16- or 32-bit, two interleaved channels, it runs:</p>
<ol>
<li>the rotation swap: left and right swapped at rotation 270 for the outputs <code>vendor.audiohal.cmf_swap</code> names;</li>
<li>speaker (right): the bass limiter (band below 100 Hz, only above its ceiling), then a peak limiter at its ceiling;</li>
<li>earpiece (left): the leveller if on, then a peak limiter at its ceiling.</li>
</ol>
<p>Ceilings come from properties in hundredths of a dB of full scale; a ceiling at or above 0 dBFS, or unset, switches that stage off and leaves the samples exactly as they were. It never blocks, never allocates, and touches only the buffer it is given. If the library cannot be loaded, the patch does not retry and runs the rotation swap alone. Source: <code>protect/cmfstereo.c</code>, with host tests and a reproducible NDK build (<code>protect/build.sh</code>) that rebuilds byte for byte and needs only libc, libm and libdl.</p>
</div>
"""},

{"title": "The background daemon",
 "html": """
<p>The audio HAL rewrites mixer controls on every route change (a stream starting, a device switch, a call), so a one-shot write does not survive. A small daemon re-asserts the values every couple of seconds and, by default, only while audio is playing.</p>
<div class="tech">
<p>Each cycle (<code>WATCH_INTERVAL</code>, 2 s), <code>scripts/stereo-daemon.sh</code>:</p>
<ol>
<li>re-reads <code>stereo.conf</code>, so edits take effect without a reboot;</li>
<li>if disabled, reverts once and waits (in Stereo, keeps the amp on its mono slot while playing);</li>
<li>decides whether the routing is wanted: playing (or <code>MODE=always</code>), speaker route allowed, guard satisfied;</li>
<li>applies the actions (a no-op for controls already right), or reverts them when playback stops;</li>
<li>in Stereo: checks the crash-loop guard; hands the library its ceilings; holds the amp attenuation (when playback starts, every 10th cycle, or when the wanted value changes); at rotation 270 while playing, updates the outputs to swap (when playback starts, when the phone turns, and every 3rd cycle); sets the amp to its right slot while the earpiece plays, or its mono slot while playing without it.</li>
</ol>
<p>Only one daemon runs: it takes an atomic lock at start, and others exit. On stop it reverts the actions, puts the amp on its mono slot in Stereo, and updates the card.</p>
</div>
"""},

{"title": "How turning the phone is handled",
 "html": """
<p>Android itself swaps left and right before the audio HAL when the phone is turned with the earpiece on your right (rotation 270). The module lets it, and only fills the one gap Android leaves.</p>
<div class="tech">
<p>Measured with the HAL's own recordings (<code>vendor.streamout.pcm.dump</code>): a left-only beep reached the HAL on the right at rotation 270 and on the left at 90, in all four Dirac tunings and from USB Audio Player Pro &mdash; except for a track whose session has its own effect chain (VLC's Dynamics Processing, the test app's MOVIE + EFFECT), which reached the HAL unswapped.</p>
<p>The daemon reads <code>dumpsys media.audio_flinger</code> only while playing at rotation 270, finds the tracks with their own effect chain (session 0, the output mix with Dirac, is not counted), and writes the OR of their mixer threads' output flags to <code>vendor.audiohal.cmf_swap</code>. The patched HAL keeps Android's <code>rotation</code> parameter in <code>vendor.audiohal.cmf_rotation</code> (the stock HAL drops it) and swaps a speaker stream only when the rotation is 270 and its output is named.</p>
<p>v0.9.5 to v1.0.0 swapped by output, by Dirac tuning, then by patching Android's mixer; each rule held only for the apps it was tested with. v1.0.1 returned to letting Android swap, and v1.0.2 added the swap for own-effect tracks.</p>
</div>
"""},

{"title": "How playback is detected",
 "html": """
<p>To use the earpiece only while something plays, the module has to know when that is. On this phone the obvious way (looking for a running stream in <code>/proc/asound</code>) never sees media, because media plays through the audio DSP.</p>
<div class="tech"><p>So the module reads the DSP's own task switches, <code>dsp_&lt;task&gt;_runtime_en</code>, for every playback task: music, fast, primary, deep buffer, VoIP and offload. Audio counts as playing when any of them reads 1. If none can be read, it falls back to the procfs scan. Before v1.0.3 only the music task was watched, so games (which use the fast task) played on the speaker only.</p></div>
"""},

{"title": "How a live switch works",
 "html": """
<p>Instead of rebooting, the module restarts only the audio HAL on the wanted files. Measured on the CMF Phone 1: the HAL comes back within seconds, <code>audioserver</code> reconnects on its own, calls keep working, and players pause.</p>
<div class="tech">
<ol>
<li>If the files the system shows already match the wanted mode: <code>unchanged</code>, nothing done.</li>
<li>Refuse during a call.</li>
<li>For Stereo, check every staged file's hash before touching anything.</li>
<li>Take off the module's own mounts on the three paths (lazily, topmost first); refuse if any mount that is not the module's remains.</li>
<li>Mount what the mode needs (via <code>nsenter</code> into init's mount namespace when run from an app), and read each file back through <code>/proc/1/root</code>.</li>
<li><code>setprop ctl.restart vendor.audio-hal</code>; wait for a new process (up to 8 s), then make sure it is still the same process 3 s later.</li>
<li>On any failure: undo, mount the checked stock copies over whatever is not stock, and restart the HAL only if all three files read back as stock.</li>
</ol>
<p>Why the care: Magisk 31 builds <code>/vendor/lib64/hw</code> as a tmpfs skeleton whose replaced files are empty placeholders under the module's mounts. In v0.9.8, restarting the HAL on those empty files had it and <code>audioserver</code> crash-looping until a reboot (fixed in v0.9.9).</p>
</div>
"""},

{"title": "What the boot and button scripts do",
 "html": """
<table>
<tr><th>Script</th><th>When it runs</th><th>What it does</th></tr>
<tr><td><code>customize.sh</code></td><td>install and update</td><td>device check, config kept across updates, Stereo re-staged (section 2.5)</td></tr>
<tr><td><code>post-fs-data.sh</code></td><td>early boot, before mounts</td><td>boot watchdog for both overlays; unknown-build guard; clears the old daemon lock; counts a boot strike if anything is active</td></tr>
<tr><td><code>service.sh</code></td><td>late boot</td><td>waits for boot to complete, clears the strike, logs auto-removals, saves the hash-checked stock copies, notes the build state, updates the card, starts the daemon</td></tr>
<tr><td><code>action.sh</code></td><td>the Action button</td><td>Mono &harr; Stereo through <code>stereoctl channels</code></td></tr>
<tr><td><code>uninstall.sh</code></td><td>module removed</td><td>stops the daemon, restores every touched control, gives the amp its gain back; keeps <code>/data/adb/cmf-stereo/</code></td></tr>
</table>
"""},

]},

# ---------------------------------------------------------------------------
# 12. Technical reference
# ---------------------------------------------------------------------------
{"title": "Technical reference",
 "intro": "<p>The measurements behind the module, every control, property and file it uses, the bundled <code>tinymix</code>, the probe's output, the development checks and the version history.</p>",
 "sections": [

{"title": "Findings: where the speaker is folded to mono",
 "html": """
<p>Each stage was measured with a test file that has sound on the left channel only and silence on the right, with the amp switched to its right slot: silence there means the right channel really is separate.</p>
<table>
<tr><th>Stage</th><th>Separate L/R?</th><th>Evidence</th></tr>
<tr><td>Android framework</td><td>Yes</td><td><code>dumpsys media.audio_flinger</code>: speaker output is 2-channel FL/FR, <em>Master mono</em> off. The policy's speaker port is already stereo, so <code>stereoctl xml-patch</code> finds nothing to change.</td></tr>
<tr><td>Dirac (Nothing's speaker tuning)</td><td>Not the fold</td><td>Session-0 insert effect, 2-in/2-out presets. Removing it alone changed nothing.</td></tr>
<tr><td>MediaTek audio HAL (<code>audio.primary.mt6878.so</code>)</td><td><strong>Folds to mono</strong></td><td><code>doStereoToMonoConversionIfNeed</code> writes (L+R)/2 to both channels whenever <code>MTK_AUDIO_NUMBER_OF_SPEAKER</code> is 1. Patching it out alone: still mono.</td></tr>
<tr><td>Aurisys on the audio DSP, <code>smartpa_awinic</code></td><td><strong>Folds to mono</strong></td><td>One speaker model (<code>AW_DSP.bin</code>: five presets, each one 11,244-byte block for one speaker, all with 0.5/0.5 weights). With <code>aurisys_demo</code> as well, the right slot went silent and the left still played.</td></tr>
<tr><td>AFE routing</td><td>Yes</td><td><code>I2SOUT4_CH2 &lt;- DL_24CH_CH2</code> is live during playback.</td></tr>
<tr><td>Awinic amp (<code>aw882xx</code>)</td><td>Yes</td><td>I2S slot select is register <code>0x06</code> bits 11:10 (<code>01</code> left, <code>10</code> right, <code>11</code> mono (L+R)/2), writable through the driver's <code>reg</code> attribute. Stock is left (<code>0x34e8</code>); on the right slot, cutting <code>I2SOUT4_CH2</code> silences the speaker.</td></tr>
<tr><td>Earpiece</td><td>Left channel</td><td><code>RCV &lt;- ADDA_DL_CH1 &lt;- DL_24CH_CH1</code>; <code>ADDA_DL_CH1</code> has no CH2 source.</td></tr>
</table>
"""},

{"title": "Findings: protection and the drivers",
 "html": """
<p>Measured with CMF L/R Test DRIVER STUDY (tones 100 Hz to 8 kHz at &minus;30 to &minus;3 dBFS; the HAL's and the DSP's recordings, and the HAL's raw 24-bit two-microphone capture). The Awinic-against-module table is in section 5.11. Also measured:</p>
<ul>
<li>the speaker's resonance at about 1 kHz (from Awinic's current and voltage sense);</li>
<li>Dirac (MUSIC) before either driver: about +2 dB at 150 Hz, +5 to +6 dB at 200&ndash;500 Hz, &minus;2 to &minus;4 dB at 3&ndash;5 kHz, a limiter at about &minus;0.2 dBFS, and a second harmonic at &minus;16 dB on 100 Hz (bass enhancement); above 150 Hz what reaches the drivers is clean (under 0.1 % distortion);</li>
<li>the earpiece's whole path is at full level already: the beep was &minus;8.7 dBFS from Android's output to the HAL and through the DSP, then <code>ADDA_DL_GAIN</code> &minus;0.3 dB and the receiver amp at its top step (+8 dB);</li>
<li>earpiece distortion under about 5&ndash;10 % up to about &minus;3 dBFS from 150 Hz up, clipping in its top 1.5 dB;</li>
<li>speaker (Awinic off) distortion growing from about &minus;12 dBFS to about 27 % at &minus;3 dBFS at 1.2&ndash;2 kHz;</li>
<li>the limiters add at most 1.2 % distortion while working (50 Hz), under 0.1 % above 1 kHz.</li>
</ul>
<p>Still pending: the Mono part of the study (Awinic on) for the same tones.</p>
"""},

{"title": "Mixer controls and hardware",
 "html": """
<table>
<tr><th>Control</th><th>Role</th><th>Module's use</th></tr>
<tr><td><code>Handset Volume</code></td><td>receiver amp gain, MT6369 codec (0 = +8 dB &hellip; 18 = &minus;10 dB, 31 = mute)</td><td>set to 0 while playing</td></tr>
<tr><td><code>ADDA_DL_CH1 DL_24CH_CH1</code></td><td>feeds the codec DAC from the speaker's stream</td><td>set to 1 while playing</td></tr>
<tr><td><code>RCV Mux</code></td><td>routes the DAC to the earpiece</td><td><code>Voice Playback</code> while playing</td></tr>
<tr><td><code>aw_dev_0_switch</code></td><td>speaker amp on/off (HAL turns it off for headphones and Bluetooth)</td><td>the guard; solo turns it off</td></tr>
<tr><td><code>aw_dev_0_volume</code></td><td>speaker amp attenuation, 1/8 dB steps (0&ndash;720 = 0&ndash;90 dB)</td><td>held at the Stereo attenuation</td></tr>
<tr><td><code>dsp_*_runtime_en</code></td><td>audio DSP task switches</td><td>playback detection</td></tr>
<tr><td><code>ADDA_DL_GAIN</code></td><td>digital gain before the DAC (HAL: 63311/65535, &minus;0.3 dB)</td><td>left alone (shared with headphones)</td></tr>
</table>
<div class="tech"><p>Amp slot: register <code>0x06</code> through the driver's <code>reg</code> attribute, found under <code>/sys/bus/i2c/devices/*</code> by its <code>dbg_prof</code> and <code>reg</code> nodes; written as <code>0x06 0x&lt;value&gt;</code>. One Awinic amp, at I2C <code>6-0034</code>.</p></div>
"""},

{"title": "System properties used",
 "html": """
<table>
<tr><th>Property</th><th>Set by</th><th>Meaning</th></tr>
<tr><td><code>vendor.audiohal.cmf_rotation</code></td><td>patched HAL</td><td>Android's last <code>rotation</code> parameter</td></tr>
<tr><td><code>vendor.audiohal.cmf_swap</code></td><td>daemon</td><td>output flags of the outputs the HAL swaps at rotation 270</td></tr>
<tr><td><code>vendor.audiohal.cmf_spk_ceil</code></td><td>daemon</td><td>speaker peak ceiling, 1/100 dB of full scale (0 = off)</td></tr>
<tr><td><code>vendor.audiohal.cmf_bass_ceil</code></td><td>daemon</td><td>bass guard ceiling (0 = off)</td></tr>
<tr><td><code>vendor.audiohal.cmf_ear_ceil</code></td><td>daemon</td><td>earpiece limiter ceiling (&minus;250 on, 0 off)</td></tr>
<tr><td><code>vendor.audiohal.cmf_ear_level</code></td><td>daemon</td><td>leveller strength 0&ndash;3</td></tr>
<tr><td><code>vendor.audiohal.cmf_prot</code></td><td>library</td><td>1 once the library has processed its first speaker buffer</td></tr>
<tr><td><code>ctl.restart vendor.audio-hal</code></td><td>live switch</td><td>restarts the audio HAL</td></tr>
<tr><td><code>init.svc.vendor.audio-hal</code>, <code>init.svc_debug_pid.vendor.audio-hal</code></td><td>Android</td><td>HAL state and process id, read by the live switch and the crash-loop guard</td></tr>
</table>
"""},

{"title": "The HAL patch",
 "html": """
<p>Four places in a stock <code>audio.primary.mt6878.so</code> / <code>audio.primary.mediatek.so</code> are patched:</p>
<table>
<tr><th>Offset</th><th>Function</th><th>Change</th></tr>
<tr><td><code>0x27b820</code></td><td><code>doStereoToMonoConversionIfNeed</code></td><td>no fold to mono; loads the protection library once and calls it for every buffer; without it, the rotation swap alone (<code>hal-swap/patch.S</code>, 432 bytes)</td></tr>
<tr><td><code>0x2587c0</code></td><td><code>setParameters</code>, <code>rotation</code> key</td><td>branch to the rotation store, which keeps the value in <code>vendor.audiohal.cmf_rotation</code></td></tr>
<tr><td><code>0x27f2d4</code></td><td><code>InitArsiTaskConfig</code></td><td><code>b.ne</code> &rarr; <code>nop</code> (always set <code>hw_info</code> 0x4)</td></tr>
<tr><td><code>0x1e0a00</code></td><td><code>SetArsiTaskConfig</code></td><td>the same, in the DSP stream manager</td></tr>
</table>
<p>The stock bytes of the first two places are written first, so any earlier Stereo HAL patches to the same file, and the reverse gives back the stock file from any of them (verified to the stock hash). The patch is assembled and tested in an ARM64 emulator (<code>hal-swap/run.sh</code>).</p>
"""},

{"title": "Files Stereo replaces, and their hashes",
 "html": """
<table>
<tr><th>File</th><th>Stock SHA-256</th><th>Stereo SHA-256</th></tr>
<tr><td><code>/vendor/lib64/hw/audio.primary.mt6878.so</code>, <code>audio.primary.mediatek.so</code></td><td><code>28db2e24e9d4c4f88a67a7631ab581fa064bb03a47a87314b7599a2cb757a324</code></td><td><code>a6362995ca0a3987e58e149c070573b4fd8ae4aecb66c196f9fdbfbf97a803ea</code></td></tr>
<tr><td><code>/vendor/etc/aurisys_config_rv.xml</code></td><td><code>f5818d29d40ce6a5e18765af96ab72a00db8c816e5a0c308c8003eff6e65f2cc</code></td><td><code>f0f7512085d86e8707131a4e6b3f413d25115c88419c69193493957da4d30ced</code></td></tr>
<tr><td><code>libcmfstereo.so</code> (module's own)</td><td>&mdash;</td><td><code>bddc81fe27aa92df289446299dc30c6b2356b14fa0b9ed9178041924629f64cc</code></td></tr>
</table>
<p>Stereo HAL files from v0.9.0&ndash;v1.0.3 and the pre-release test module's DSP configuration are also recognised and converted. The patched <code>aurisys_config_rv.xml</code> carries a marker comment, <code>cmf_stereo: stereo</code>, which is how the module tells that Stereo is what the system is running.</p>
"""},

{"title": "tinymix",
 "html": """
<p>Mixer controls cannot be read or written without a <code>tinymix</code> binary, and the CMF Phone 1 ships none. The module bundles one: a statically linked <code>aarch64</code> build of upstream tinyalsa, hardware backend only, no <code>dlopen</code>.</p>
<pre>upstream: https://github.com/tinyalsa/tinyalsa
commit:   9fab97ca07184371ecad81154d1dadb09d0fa7cf
license:  BSD-3-Clause

git clone https://github.com/tinyalsa/tinyalsa &amp;&amp; cd tinyalsa
git checkout 9fab97ca07184371ecad81154d1dadb09d0fa7cf
aarch64-linux-gnu-gcc -static -O2 -Wall -Iinclude \\
    src/mixer.c src/mixer_hw.c src/limits.c utils/tinymix.c -o tinymix
aarch64-linux-gnu-strip tinymix</pre>
<p>If you would rather not trust a shipped binary, build it yourself and drop it at <code>/data/adb/cmf-stereo/bin/tinymix</code> (<code>chmod 0755</code>). Termux's <code>tinyalsa</code> package works too.</p>
<div class="tech"><p>Both the tinyalsa 1.x <code>tinymix NAME VALUE</code> and the 2.x <code>tinymix set NAME VALUE</code> calling styles are handled, detected through <code>--help</code> rather than guessed from an error message, once per process. Search order in the code: the module's <code>bin/</code>, <code>/data/adb/cmf-stereo/bin</code>, <code>/vendor/bin</code>, <code>/system/bin</code>, <code>/system/vendor/bin</code>, <code>/odm/bin</code>, <code>/data/local/tmp</code>, then <code>$PATH</code>. The project README gives a different order, with <code>/data/adb/cmf-stereo/bin</code> first and a vendor-supplied <code>tinymix</code> winning over the bundled one; in this version's code the module's own <code>bin/tinymix</code> is checked first, so a copy you place in <code>/data/adb/cmf-stereo/bin</code> is used only when the module's own is missing or not executable.</p></div>
"""},

{"title": "The probe's output files",
 "html": """
<p><code>stereoctl probe</code> writes <code>/sdcard/cmf-stereo-probe-&lt;timestamp&gt;/</code> (and a <code>.tar.gz</code> of it). Nothing on the device is modified.</p>
<table>
<tr><th>File</th><th>Contents</th></tr>
<tr><td><code>00-device.txt</code></td><td>build properties and audio-related properties</td></tr>
<tr><td><code>01-alsa.txt</code></td><td>sound cards, devices, PCMs, the <code>/proc/asound</code> tree, hw_params and status</td></tr>
<tr><td><code>02-mixer.txt</code></td><td>every mixer control (or <code>NO TINYMIX FOUND.</code>)</td></tr>
<tr><td><code>03-candidates.txt</code></td><td>controls whose names look like receiver, speaker, output stage or routing</td></tr>
<tr><td><code>04-amplifier.txt</code></td><td>smart-amp sysfs entries, I2C device names, loaded modules, codec kernel log</td></tr>
<tr><td><code>05-hal-configs/</code></td><td>copies of audio policy, device, mixer path, effects and platform files</td></tr>
<tr><td><code>06-speaker-port.txt</code></td><td>the speaker and earpiece <code>devicePort</code> blocks</td></tr>
<tr><td><code>07-hal.txt</code></td><td>HAL libraries, services, audio processes, sound effects, manifest entries</td></tr>
<tr><td><code>08-routing.txt</code></td><td>the head of <code>dumpsys audio</code> and <code>dumpsys media.audio_flinger</code></td></tr>
<tr><td><code>09-audio-param/</code></td><td>MediaTek AudioParam XMLs, 2nd-loudspeaker hits, aaudio/mmap properties</td></tr>
<tr><td><code>10-safety.txt</code></td><td>receiver gain controls and their values, audio protection nodes</td></tr>
<tr><td><code>SUMMARY.txt</code></td><td>device, tinymix, counts of controls and hits, the file list</td></tr>
</table>
"""},

{"title": "The module's files",
 "html": """
<table>
<tr><th>Path</th><th>What</th></tr>
<tr><td><code>customize.sh</code></td><td>install: device check, config kept across updates, Stereo re-staged</td></tr>
<tr><td><code>post-fs-data.sh</code></td><td>before mounts: boot watchdog, unknown-build guard</td></tr>
<tr><td><code>service.sh</code></td><td>after boot: stock copies saved, the daemon started</td></tr>
<tr><td><code>action.sh</code></td><td>the Action button: Mono &harr; Stereo</td></tr>
<tr><td><code>uninstall.sh</code></td><td>stop, restore, give the amp its gain back</td></tr>
<tr><td><code>scripts/common.sh</code></td><td>config, logging, tinymix access, playback detection, the routing actions, the card's text</td></tr>
<tr><td><code>scripts/channels.sh</code></td><td>Stereo: hashes and patches, staging, live switching, the amp, protection settings, crash-loop guard</td></tr>
<tr><td><code>scripts/stereo-daemon.sh</code></td><td>keeps routing, amp slot, attenuation, rotation swap and protection applied while playing</td></tr>
<tr><td><code>scripts/stereoctl</code></td><td>the command-line tool the apps and you call</td></tr>
<tr><td><code>scripts/probe.sh</code></td><td>the hardware dump</td></tr>
<tr><td><code>scripts/xml_patch.sh</code></td><td>the audio-policy overlay (opt-in, not for this device)</td></tr>
<tr><td><code>system/bin/stereoctl</code></td><td>the shim that puts <code>stereoctl</code> on the path</td></tr>
<tr><td><code>protect/libcmfstereo.so</code></td><td>the protection library</td></tr>
<tr><td><code>config/</code></td><td>default settings and the verified CMF Phone 1 routing</td></tr>
<tr><td><code>bin/tinymix</code></td><td>static aarch64 tinyalsa build</td></tr>
<tr><td><code>system/vendor/...</code></td><td>the Stereo overlay, present only when staged</td></tr>
</table>
<p>The module lives in <code>/data/adb/modules/cmf_stereo/</code>.</p>
"""},

{"title": "The data folder's files",
 "html": """
<p>Everything the module keeps in <code>/data/adb/cmf-stereo/</code>:</p>
<table>
<tr><th>File</th><th>Purpose</th></tr>
<tr><td><code>stereo.conf</code>, <code>actions.conf</code></td><td>your settings and routing</td></tr>
<tr><td><code>stereo.log</code>, <code>stereo.log.1</code></td><td>the log and its previous rotation</td></tr>
<tr><td><code>state/</code></td><td>saved original values; also <code>amp_ours</code> (the attenuation the module set) and <code>hal_pids</code> (crash-loop guard)</td></tr>
<tr><td><code>stock/</code></td><td>hash-checked copies of the stock audio files, for switching to Mono live</td></tr>
<tr><td><code>build_state</code></td><td><code>known</code>, <code>updated</code> or <code>absent</code></td></tr>
<tr><td><code>disabled</code></td><td>the kill switch (<code>stereoctl off</code>)</td></tr>
<tr><td><code>guard_bypass</code>, <code>solo_prev</code></td><td>guard bypassed; the speaker switch's value before solo</td></tr>
<tr><td><code>boot_pending</code></td><td>boot watchdog strikes</td></tr>
<tr><td><code>daemon.pid</code>, <code>daemon.lock/</code></td><td>the running daemon</td></tr>
<tr><td><code>snap.before</code>, <code>snap.after</code></td><td>the two snapshots of <code>stereoctl diff</code></td></tr>
<tr><td><code>bin/</code></td><td>your own <code>tinymix</code>, if you add one</td></tr>
</table>
"""},

{"title": "MediaTek's second-loudspeaker machinery",
 "html": """
<p>MediaTek's "2nd loudspeaker" machinery <strong>is</strong> present on this build, in <code>/vendor/etc/audio_param/</code>:</p>
<pre>2nd Loudspeaker Compensation Filter (2nd-ACF)
2nd Loudspeaker High/Low Pass Filter Order
bes_loudness_Sep_LR_Filter
bes_loudness_L_*  /  bes_loudness_R_*   (separate L and R filter sets)</pre>
<p>An earlier revision of the README claimed it was absent; that came from broken search patterns that reported a clean zero for a pattern that never matched. On the CMF Phone 1 every <code>bes_loudness_R_*</code> value and <code>bes_loudness_Sep_LR_Filter</code> read <code>0x0</code>: MediaTek's stock template, untuned. 2nd-ACF is a filter feature: it applies a different EQ to a second driver's channel; it does not create a route to one. Whether it is wired to a second driver on this hardware is unresolved. The module's Stereo does not use it.</p>
"""},

{"title": "Development checks",
 "html": """
<pre>sh tests/run-tests.sh      # 198 checks; run under sh, dash, mksh and busybox sh
sh hal-swap/run.sh         # the HAL patch in qemu-aarch64 (needs clang, ld.lld, qemu)
sh protect/build.sh        # the library rebuilds byte for byte (needs the NDK)
./build.sh                 # the flashable zip</pre>
<p>Every vendor file is patched only after its hash proves it is the analysed build, and the result is hashed again; <code>hal-swap/run.sh</code> checks the bytes <code>channels.sh</code> writes against the assembled patch.</p>
"""},

{"title": "Test status of this version",
 "html": """
<p><strong>Verified on the phone:</strong> the earpiece leveller (v1.0.5); Stereo with a left-only file, Dirac on and off; Mono; live switching from <code>stereoctl channels</code>, both apps and the Action button; Magisk's Update button; left and right following the rotation in the apps of section 3.10; "While playing" for games and music players; every protection setting; the earpiece at +8 dB; hi-res playback in Stereo.</p>
<p><strong>Not tested on a phone yet:</strong></p>
<ul>
<li>the apps following changes made outside them (v1.0.6), tested with a stand-in;</li>
<li>boost 6 over a longer listen;</li>
<li>the protection after a live switch from a Mono boot (by design it starts after a reboot);</li>
<li>the safety nets that need a failure: crash-loop guard, boot watchdog, a failed live switch ending on the stock files (covered by tests on fake files);</li>
<li>the next Nothing OS update: the unknown-build guard and re-staging during a module update;</li>
<li>how the speaker holds up to long, loud Stereo listening.</li>
</ul>
<p><strong>Pending:</strong> adding the next Nothing OS build after checking its file hashes; a short clip of the two drivers splitting a game's or film's audio.</p>
"""},

{"title": "Version history",
 "html": """
<table>
<tr><th>Version</th><th>Date</th><th>Change</th></tr>
<tr><td>v1.0.9-beta</td><td>8 Nov 2026</td><td>marked beta; module unchanged since v1.0.8 (version code 1090)</td></tr>
<tr><td>v1.0.8</td><td>7 Nov 2026</td><td>every text says left and right follow how you hold the phone</td></tr>
<tr><td>v1.0.7</td><td>6 Nov</td><td><code>stereoctl off</code> no longer asks for a reboot in Mono; exact tested build in the README</td></tr>
<tr><td>v1.0.6</td><td>5 Nov</td><td>Nothing Settings and the tile follow every change at once</td></tr>
<tr><td>v1.0.5</td><td>5 Nov</td><td>optional earpiece leveller</td></tr>
<tr><td>v1.0.4</td><td>5 Nov</td><td>the module's own Stereo protection; crash-loop guard</td></tr>
<tr><td>v1.0.3</td><td>5 Nov</td><td>both speakers in games and every other app</td></tr>
<tr><td>v1.0.2</td><td>5 Nov</td><td>apps with their own audio effect (VLC) follow the screen</td></tr>
<tr><td>v1.0.1</td><td>5 Nov</td><td>left and right right again (v1.0.0 played them reversed)</td></tr>
<tr><td>v1.0.0</td><td>5 Nov</td><td>one swap for every app; played reversed, replaced</td></tr>
<tr><td>v0.9.9</td><td>5 Nov</td><td>fixed Stereo from the Action button crashing the audio service; reversed channels in some apps</td></tr>
<tr><td>v0.9.8</td><td>5 Nov</td><td>Action button, live status on the card, stock sound after a Nothing OS update</td></tr>
<tr><td>v0.9.7</td><td>5 Nov</td><td>listed as by Dr.Essence; first release offered as an update</td></tr>
<tr><td>v0.9.6</td><td>4 Nov</td><td>updates through the root manager; SHA-256 checksums</td></tr>
<tr><td>v0.9.5</td><td>4 Nov</td><td>left and right follow which way the phone is turned</td></tr>
<tr><td>v0.9.4</td><td>4 Nov</td><td>Mono and Stereo switch without a reboot; quieter kernel log</td></tr>
<tr><td>v0.9.3</td><td>4 Nov</td><td>instant on/off; lighter in the background; <code>status brief</code></td></tr>
<tr><td>v0.9.2</td><td>3 Nov</td><td>first true stereo; earpiece gain fixed (31 was mute)</td></tr>
<tr><td>v0.8.2, v0.7.1</td><td>Sep 2026</td><td>the earlier version: the same mono mix on both drivers</td></tr>
</table>
<p>The full history of findings, tests and fixes is in <code>CHANGELOG.md</code>.</p>
"""},

]},

# ---------------------------------------------------------------------------
# 13. Credits and licence
# ---------------------------------------------------------------------------
{"title": "Credits and licence",
 "intro": "<p>Who made this, whose work it started from, and the terms you may use it under.</p>",
 "sections": [

{"title": "Author",
 "html": """
<p><strong>Dr.Essence</strong>: author and maintainer. Ideas, design decisions, and every test on a real phone (logs, recordings, measurements) that the work rests on.</p>
<p>Code written with Claude Code, against a real CMF Phone 1: every routing claim came from measurements on the device, not from documentation.</p>
"""},

{"title": "The Hi-Res Audio module",
 "html": """
<p>This module owes a real debt to <strong>Hi-Res Audio</strong> by Adinata (@Adivenxnataly). It is the reason the project knew where to look. Before it, "use the earpiece as a second speaker on a MediaTek phone" was a vague idea with no entry point. That module pointed at MediaTek's <code>2nd Loudspeaker</code> / <code>bes_loudness</code> machinery and at the earpiece <code>&lt;devicePort&gt;</code> channel mask; working out why those levers do not pan out on the CMF Phone 1 led to the routing that does.</p>
<p>It aims at a different goal &mdash; high-resolution output, not dual speakers &mdash; so it is worth trying on its own terms. What this module took from it: edit the element you mean to change, validate the result, and keep a way back. Hence the block-aware rewrite, the XML structural check, and the boot watchdog.</p>
<div class="warn"><p>Do not run both modules at the same time: they touch the same files.</p></div>
"""},

{"title": "A bug reported upstream",
 "html": """
<p>Tested against Hi-Res Audio <code>v2.0 with aaudio_mmap</code>, versionCode 20000, commit <code>78706f5</code> (2025-06-12), it bootlooped a CMF Phone 1. The cause is a one-character typo in its <code>customize.sh</code>:</p>
<pre>name="Apply Same Filter Setting with 2nd Loudspeaker\\/&gt;</pre>
<p>The attribute value is never closed. The fix:</p>
<pre>name="Apply Same Filter Setting with 2nd Loudspeaker\\"\\/&gt;</pre>
<p>Without it, <code>Playback_ParamTreeView.xml</code> gets <code>&lt;Field ... name="Apply Same Filter Setting with 2nd Loudspeaker/&gt;</code>; MediaTek's AudioParamParser cannot parse that, so the audio HAL aborts on every boot. The <code>sed</code> fires on any device carrying a <code>bes_loudness_L_lpf_order</code> field.</p>
<p>Also worth knowing on a phone like this: it forces <code>aaudio.mmap_policy=3</code> / <code>aaudio.mmap_exclusive_policy=3</code> plus <code>killall audioserver</code>, which needs a HAL with an MMAP PCM path, and it sets the speaker channel mask to <code>AUDIO_CHANNEL_OUT_SURROUND</code>, which not every speaker port accepts. An earlier claim in this project's README that its <code>&lt;mixPort&gt;</code> insertions land mid-element was wrong and is retracted: it computes the correct insertion point and otherwise skips.</p>
"""},

{"title": "Why its stereo approach does not work here",
 "html": """
<p>Not a criticism: the approach is sound on hardware with a second loudspeaker. Two things stop it on the CMF Phone 1:</p>
<ul>
<li><code>Playback_ParamTreeView.xml</code> is the <strong>view definition</strong> for MediaTek's tuning tool. The runtime coefficients live in <code>PlaybackACF_AudioParam.xml</code>. Editing the view changes which fields a tuning tool displays, not what the DSP does.</li>
<li>Every <code>bes_loudness_R_*</code> value and <code>bes_loudness_Sep_LR_Filter</code> read <code>0x0</code>, MediaTek's untuned template, because this phone has no second loudspeaker. And 2nd-ACF is a filter, not a route.</li>
</ul>
"""},

{"title": "Others who did this before",
 "html": """
<p>Thanks to the people who worked out this mod on other hardware and wrote it up: the OnePlus 6 stereo speaker mod, Xiaomi Merlin (merlin_DualSpeaker_mod), LeEco Le Max 2 (Dual-Speaker-x2) and whyred (Magisk dual speaker mod). Their write-ups of duplicated-mono "dual speaker" mods are what this project set out to go beyond: Mono mode is that; Stereo mode is real left and right.</p>
"""},

{"title": "Licence",
 "html": """
<p>The module is &copy; 2026 Dr.Essence under <strong>CC BY-NC-SA 4.0</strong>. You may use, copy, change and share it, as long as you:</p>
<ul>
<li>credit Dr.Essence;</li>
<li>do not use it commercially, including selling it or anything built from it;</li>
<li>share changed versions under the same licence.</li>
</ul>
<p>Releases up to v0.9.6 were published under 0BSD; copies obtained under it keep those terms.</p>
<p><code>bin/tinymix</code> is a statically linked <code>aarch64</code> build of tinyalsa, under BSD-3-Clause. Its licence, upstream commit and exact build command are in <code>bin/README.md</code>, so you can reproduce it rather than trust the shipped binary.</p>
"""},

]},

]
