// Host tests for cmfstereo.c: fake properties, a fake HAL handler, real signals.
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
int cmf_process(void *self, void *buf, size_t bytes);
static char P[16][2][96]; static int NP;
int __system_property_get(const char *k, char *v) {
  for (int i = 0; i < NP; i++) if (!strcmp(P[i][0], k)) { strcpy(v, P[i][1]); return strlen(v); }
  v[0] = 0; return 0;
}
int __system_property_set(const char *k, const char *v) {
  for (int i = 0; i < NP; i++) if (!strcmp(P[i][0], k)) { strcpy(P[i][1], v); return 0; }
  strcpy(P[NP][0], k); strcpy(P[NP][1], v); NP++; return 0;
}
static void setp(const char *k, const char *v) { __system_property_set(k, v); }
struct attr { uint32_t fmt, a, b, flags; uint8_t pad[0x1d8 - 16]; uint32_t *vb, *ve; };
struct handler { uint8_t pad[0x20]; struct attr *a; };
static int fails;
static void check(const char *n, int ok) { printf("  %s - %s\n", ok ? "ok  " : "FAIL", n); if (!ok) fails++; }
#define N 48000
static int32_t b32[N * 2]; static int16_t b16[N * 2];
static double peak(int ch, int from) { double m = 0; for (int i = from; i < N; i++) { double v = fabs(b32[2 * i + ch] / 2147483648.0); if (v > m) m = v; } return 20 * log10(m + 1e-12); }
static void sine(int ch, double f, double db, int clear) {
  if (clear) memset(b32, 0, sizeof b32);
  for (int i = 0; i < N; i++) b32[2 * i + ch] = (int32_t)(pow(10, db / 20) * sin(2 * M_PI * f * i / 48000) * 2147483647.0);
}
static void run(struct handler *h) { for (int k = 0; k < N; k += 960) cmf_process(h, b32 + 2 * k, 960 * 8); }
int main(void) {
  uint32_t spk[1] = {2}, ear[1] = {1};
  struct attr at; memset(&at, 0, sizeof at); struct handler h; h.a = &at;
  at.fmt = 3; at.flags = 8; at.vb = spk; at.ve = spk + 1;

  // Nothing configured: samples untouched, bit for bit.
  for (int i = 0; i < N * 2; i++) b32[i] = rand() * 2 - RAND_MAX;
  static int32_t ref[N * 2]; memcpy(ref, b32, sizeof b32);
  run(&h);
  check("no settings: bit-exact", !memcmp(ref, b32, sizeof b32));
  usleep(100000);   // the running mark is set from its own thread
  check("tells the module it runs (cmf_prot=1)", ({ char v[96]; __system_property_get("vendor.audiohal.cmf_prot", v); !strcmp(v, "1"); }));

  // The rotation swap, as before, and bit-exact.
  setp("vendor.audiohal.cmf_rotation", "270"); setp("vendor.audiohal.cmf_swap", "8");
  memcpy(b32, ref, sizeof b32); run(&h);
  int ok = 1; for (int i = 0; i < N; i++) ok &= b32[2 * i] == ref[2 * i + 1] && b32[2 * i + 1] == ref[2 * i];
  check("270 + flagged output: swapped bit-exact (32-bit)", ok);
  for (int i = 0; i < 8; i++) b16[i] = i + 1;
  cmf_process(&h, b16, 16);
  { struct attr a16 = at; a16.fmt = 1; struct handler h16 = { .a = &a16 }; for (int i = 0; i < 8; i++) b16[i] = i + 1; cmf_process(&h16, b16, 16);
    check("16-bit swapped", b16[0] == 2 && b16[1] == 1 && b16[6] == 8 && b16[7] == 7); }
  setp("vendor.audiohal.cmf_swap", "2"); memcpy(b32, ref, sizeof b32); run(&h);
  check("output not flagged: untouched", !memcmp(ref, b32, sizeof b32));
  setp("vendor.audiohal.cmf_swap", "8"); setp("vendor.audiohal.cmf_rotation", "90"); memcpy(b32, ref, sizeof b32); run(&h);
  check("rotation 90: untouched", !memcmp(ref, b32, sizeof b32));
  setp("vendor.audiohal.cmf_rotation", "270");
  at.vb = ear; at.ve = ear + 1; memcpy(b32, ref, sizeof b32); run(&h);
  check("earpiece-only route: untouched", !memcmp(ref, b32, sizeof b32));
  at.vb = spk; at.ve = spk + 1; at.fmt = 5; memcpy(b32, ref, sizeof b32); run(&h);
  check("float stream: untouched", !memcmp(ref, b32, sizeof b32));
  at.fmt = 3; setp("vendor.audiohal.cmf_rotation", "0");

  // Speaker peak limiter (right channel) at -5 dBFS.
  struct handler h2; h2.a = &at;   // a second stream: its own state
  setp("vendor.audiohal.cmf_spk_ceil", "-500");
  sine(1, 1000, 0, 1); run(&h2);
  check("speaker 1 kHz at 0 dBFS: peaks held at -5 dBFS", peak(1, 0) <= -4.99);
  sine(1, 1000, -20, 1); run(&h2); run(&h2);
  check("speaker 1 kHz at -20 dBFS: unchanged", fabs(peak(1, N / 2) - -20) < 0.02);
  check("earpiece untouched by the speaker limiter", peak(0, 0) < -200);

  // Bass limiter at -14 dBFS (band below 100 Hz), on its own.
  setp("vendor.audiohal.cmf_spk_ceil", "0"); setp("vendor.audiohal.cmf_bass_ceil", "-1400");
  sine(1, 50, -30, 1); run(&h2); run(&h2);
  check("quiet 50 Hz (-30 dBFS): level unchanged", fabs(peak(1, N / 2) - -30) < 0.3);
  sine(1, 50, -3, 1); run(&h2); run(&h2);
  { double p = peak(1, N / 2); printf("        loud 50 Hz at -3 dBFS -> %.1f dBFS\n", p);
    check("loud 50 Hz (-3 dBFS): held near the bass ceiling", p < -12.5 && p > -15.5); }
  sine(1, 1000, -3, 1); run(&h2); run(&h2);
  check("1 kHz at -3 dBFS: the bass limiter leaves it alone", fabs(peak(1, N / 2) - -3) < 0.2);
  sine(1, 300, -3, 1); run(&h2); run(&h2);
  check("300 Hz at -3 dBFS: left alone too", fabs(peak(1, N / 2) - -3) < 0.3);
  const double fr[] = {30, 60, 100, 150, 300, 1000, 5000};
  int flat = 1;
  for (int k = 0; k < 7; k++) { sine(1, fr[k], -40, 1); run(&h2); run(&h2); double p = peak(1, N / 2); if (fabs(p + 40) > 0.3) { flat = 0; printf("        %g Hz: %.2f\n", fr[k], p); } }
  check("quiet signal: flat from 30 Hz to 5 kHz (+-0.3 dB)", flat);

  // Earpiece limiter (left) at -2.5 dBFS.
  setp("vendor.audiohal.cmf_bass_ceil", "0"); setp("vendor.audiohal.cmf_ear_ceil", "-250");
  sine(0, 2000, 0, 1); run(&h2);
  check("earpiece 2 kHz at 0 dBFS: held at -2.5 dBFS", peak(0, 0) <= -2.49);
  sine(0, 200, -6, 1); run(&h2); run(&h2);
  check("earpiece 200 Hz at -6 dBFS: unchanged, bass kept", fabs(peak(0, N / 2) - -6) < 0.02);

  // Many streams: never crashes, keeps working.
  struct handler hs[12]; for (int i = 0; i < 12; i++) { hs[i].a = &at; sine(0, 2000, 0, 1); run(&hs[i]); }
  check("12 streams (more than its 8 slots): still limits", peak(0, 0) <= -2.49);
  cmf_process(NULL, b32, 8); cmf_process(&h, NULL, 8);
  { struct handler hn = { .a = NULL }; cmf_process(&hn, b32, 8); }
  check("null handler / buffer / attributes: no crash", 1);
  printf(fails ? "FAILED\n" : "all passed\n");
  return fails;
}
