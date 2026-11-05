// CMF true stereo: the speaker and earpiece protection, and the rotation swap.
//
// Loaded by the patched AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed
// (hal-swap/patch.S), which calls cmf_process(this, buffer, bytes) for every
// buffer the HAL plays, just before the audio DSP. Everything between here and
// the amplifiers is level-neutral (measured with the HAL's and the DSP's own
// recordings), so the ceilings below are exact.
//
// For a speaker-only stream (devices vector exactly { AUDIO_DEVICE_OUT_SPEAKER }),
// 16- or 32-bit, two interleaved channels:
//   1. the rotation swap, as before: left and right swapped at rotation 270
//      for the outputs vendor.audiohal.cmf_swap names (streams Android leaves
//      unswapped);
//   2. speaker (right): a bass limiter (only the band below 100 Hz, only when
//      it is louder than its ceiling: quiet bass is untouched), then a peak
//      limiter at its ceiling;
//   3. earpiece (left): a peak limiter at its ceiling (measured: it clips in the
//      top 1.5 dB).
// Ceilings come from properties in hundredths of a dB of full scale; a ceiling
// at or above 0 dBFS (or unset) switches that stage off and leaves the samples
// exactly as they were.
//
// Never blocks, never allocates, touches only the buffer it is given.
#include <math.h>
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/system_properties.h>

#define RATE 48000.0f
#define SLOTS 8

typedef struct { float b0, b1, b2, a1, a2; } coef_t;
typedef struct { float z1, z2; } bq_t;

typedef struct {
  void *volatile owner;            // the HAL handler this state belongs to
  bq_t lp[2], hp[2];               // 4th-order Linkwitz-Riley split, speaker
  float bass_env, bass_gain;
  float spk_env, ear_env;
} state_t;

static state_t g_state[SLOTS];
static coef_t g_lp, g_hp;
static float g_rel_bass, g_rel_peak, g_att_gain;
static int g_ready;

static float qprop(const char *k, float def) {
  char v[PROP_VALUE_MAX];
  if (__system_property_get(k, v) <= 0) return def;
  return (float)atof(v);
}

static int iprop(const char *k, int def) {
  char v[PROP_VALUE_MAX];
  if (__system_property_get(k, v) <= 0) return def;
  return atoi(v);
}

// Butterworth biquad (Q = 1/sqrt 2), RBJ cookbook.
static void butter(coef_t *c, float fc, int high) {
  float w = 2.0f * (float)M_PI * fc / RATE, cw = cosf(w), al = sinf(w) / (2.0f * 0.70710678f);
  float a0 = 1.0f + al;
  if (high) { c->b0 = (1 + cw) / 2; c->b1 = -(1 + cw); c->b2 = (1 + cw) / 2; }
  else      { c->b0 = (1 - cw) / 2; c->b1 = 1 - cw;    c->b2 = (1 - cw) / 2; }
  c->b0 /= a0; c->b1 /= a0; c->b2 /= a0;
  c->a1 = -2 * cw / a0; c->a2 = (1 - al) / a0;
}

static inline float bq(const coef_t *c, bq_t *s, float x) {
  float y = c->b0 * x + s->z1;
  s->z1 = c->b1 * x - c->a1 * y + s->z2;
  s->z2 = c->b2 * x - c->a2 * y;
  return y;
}

// Setting a property is a round trip to init: done on a thread of its own so
// the audio thread never waits on it.
static void *mark_running(void *unused) {
  (void)unused;
  __system_property_set("vendor.audiohal.cmf_prot", "1");
  return NULL;
}

static void init(void) {
  butter(&g_lp, 100.0f, 0);
  butter(&g_hp, 100.0f, 1);
  g_rel_bass = expf(-1.0f / (0.300f * RATE));   // bass limiter lets go over 300 ms
  g_rel_peak = expf(-1.0f / (0.100f * RATE));   // peak limiters over 100 ms
  g_att_gain = expf(-1.0f / (0.005f * RATE));   // bass gain moves down over 5 ms
  g_ready = 1;
  // Tells the module the protection is running (it only lowers the speaker's
  // fixed attenuation once this reads 1).
  pthread_t t;
  if (pthread_create(&t, NULL, mark_running, NULL) == 0) pthread_detach(t);
}

static state_t *slot(void *owner) {
  for (int i = 0; i < SLOTS; i++) if (g_state[i].owner == owner) return &g_state[i];
  for (int i = 0; i < SLOTS; i++) {
    if (__sync_bool_compare_and_swap(&g_state[i].owner, NULL, owner)) {
      state_t *s = &g_state[i];
      memset(s->lp, 0, sizeof s->lp); memset(s->hp, 0, sizeof s->hp);
      s->bass_env = s->spk_env = s->ear_env = 0; s->bass_gain = 1;
      return s;
    }
  }
  // Table full (more than 8 streams have played since the HAL started): reuse
  // a slot. A filter state shared by two streams only colours the transient.
  return &g_state[((uintptr_t)owner >> 4) % SLOTS];
}

static inline float lin(float cdb) { return powf(10.0f, cdb / 2000.0f); }

// Peak limiter: instant attack, smooth release, never above c.
static inline float limit(float x, float *env, float rel, float c) {
  float a = fabsf(x);
  *env = a > *env ? a : *env * rel + a * (1 - rel);
  if (*env > c) x *= c / *env;
  return x > c ? c : (x < -c ? -c : x);
}

__attribute__((visibility("default"))) int cmf_process(void *self, void *buf, size_t bytes) {
  if (!self || !buf) return 0;
  uint8_t *attr = *(uint8_t **)((uint8_t *)self + 0x20);
  if (!attr) return 0;
  uint32_t *db = *(uint32_t **)(attr + 0x1d8), *de = *(uint32_t **)(attr + 0x1e0);
  if (!db || de - db != 1 || db[0] != 2) return 0;        // speaker only
  uint32_t fmt = *(uint32_t *)attr, flags = *(uint32_t *)(attr + 0xc);
  if (fmt != 1 && fmt != 3) return 0;                     // 16 / 32-bit PCM
  if (!g_ready) init();

  int swap = iprop("vendor.audiohal.cmf_rotation", 0) == 270 &&
             (iprop("vendor.audiohal.cmf_swap", 0) & (int)flags) != 0;
  float spk = qprop("vendor.audiohal.cmf_spk_ceil", 0), bass = qprop("vendor.audiohal.cmf_bass_ceil", 0);
  float ear = qprop("vendor.audiohal.cmf_ear_ceil", 0);
  int do_spk = spk < 0, do_bass = bass < 0, do_ear = ear < 0;
  if (!swap && !do_spk && !do_bass && !do_ear) return 0;

  size_t frames = bytes / (fmt == 1 ? 4 : 8);
  // The swap moves whole samples, so it stays bit-exact.
  if (swap) {
    if (fmt == 1) {
      uint32_t *p = (uint32_t *)buf;
      for (size_t i = 0; i < frames; i++) p[i] = (p[i] >> 16) | (p[i] << 16);
    } else {
      uint32_t *p = (uint32_t *)buf;
      for (size_t i = 0; i < frames; i++) { uint32_t t = p[2 * i]; p[2 * i] = p[2 * i + 1]; p[2 * i + 1] = t; }
    }
  }
  if (!do_spk && !do_bass && !do_ear) return 0;

  state_t *s = slot(self);
  float cs = lin(spk), cb = lin(bass), ce = lin(ear);
  for (size_t i = 0; i < frames; i++) {
    float l, r;
    if (fmt == 1) { int16_t *p = (int16_t *)buf + 2 * i; l = p[0] / 32768.0f; r = p[1] / 32768.0f; }
    else          { int32_t *p = (int32_t *)buf + 2 * i; l = p[0] / 2147483648.0f; r = p[1] / 2147483648.0f; }
    float r0 = r, l0 = l;
    if (do_bass) {
      float lo = bq(&g_lp, &s->lp[1], bq(&g_lp, &s->lp[0], r));
      float hi = bq(&g_hp, &s->hp[1], bq(&g_hp, &s->hp[0], r));
      float a = fabsf(lo);
      s->bass_env = a > s->bass_env ? a : s->bass_env * g_rel_bass;
      float want = s->bass_env > cb ? cb / s->bass_env : 1.0f;
      s->bass_gain = want < s->bass_gain ? want + (s->bass_gain - want) * g_att_gain
                                         : want + (s->bass_gain - want) * g_rel_bass;
      // The two bands sum back to the input's magnitude (Linkwitz-Riley); with
      // the bass at full gain only its phase below 100 Hz moves.
      r = lo * s->bass_gain + hi;
    }
    if (do_spk) r = limit(r, &s->spk_env, g_rel_peak, cs);
    if (do_ear) l = limit(l, &s->ear_env, g_rel_peak, ce);
    // A channel nothing changed keeps its exact samples.
    if (fmt == 1) {
      int16_t *p = (int16_t *)buf + 2 * i;
      if (l != l0) { float a = l * 32768.0f; p[0] = (int16_t)(a > 32767 ? 32767 : a < -32768 ? -32768 : lrintf(a)); }
      if (r != r0) { float b = r * 32768.0f; p[1] = (int16_t)(b > 32767 ? 32767 : b < -32768 ? -32768 : lrintf(b)); }
    } else {
      int32_t *p = (int32_t *)buf + 2 * i;
      if (l != l0) { double a = l * 2147483648.0; p[0] = (int32_t)(a > 2147483647.0 ? 2147483647 : a < -2147483648.0 ? -2147483647 - 1 : llrint(a)); }
      if (r != r0) { double b = r * 2147483648.0; p[1] = (int32_t)(b > 2147483647.0 ? 2147483647 : b < -2147483648.0 ? -2147483647 - 1 : llrint(b)); }
    }
  }
  return 0;
}
