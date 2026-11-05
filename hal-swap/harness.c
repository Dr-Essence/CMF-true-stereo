typedef unsigned long size_t; typedef unsigned int u32; typedef unsigned short u16;
extern int swapfn(void *self, void *buf, size_t bytes);
extern long call_rotcave(const char *v);
extern char PG37D[];
static void cp(char *d, const char *s) { while ((*d++ = *s++)); }
extern unsigned long SLOT[2];
static int dlopen_calls, dlsym_calls, lib_calls, lib_ok; static void *lib_self, *lib_buf; static size_t lib_bytes; static char libname[64], symn[32];
static int fake_process(void *s, void *b, size_t n) { lib_calls++; lib_self = s; lib_buf = b; lib_bytes = n; return 7; }
void *DLOPEN(const char *p, int f) { dlopen_calls++; cp(libname, p); return lib_ok ? (void *)1 : 0; }
void *DLSYM(void *h, const char *s) { dlsym_calls++; cp(symn, s); return h ? (void *)fake_process : 0; }
static int prop_val, swap_val, pgi_calls, fails;
static char skey[64];
static char kbuf[64], vbuf[16];
static int eq(const char *a, const char *b) { while (*a && *a == *b) a++, b++; return *a == *b; }
int PGI(const char *key, int def) { pgi_calls++;
  if (eq(key, "vendor.audiohal.cmf_swap")) { cp(skey, key); return swap_val; }
  cp(kbuf, key); return prop_val; }
int PSET(const char *k, const char *v) { cp(kbuf, k); cp(vbuf, v); return 0; }
struct attr { u32 fmt; u32 pad1[2]; u32 flags; char pad[0x1d8 - 16]; u32 *vb, *ve; };
struct handler { char pad[0x20]; struct attr *a; };
static void wr(const char *s) { long n = 0; while (s[n]) n++;
  register long x0 asm("x0") = 1; register const char *x1 asm("x1") = s; register long x2 asm("x2") = n; register long x8 asm("x8") = 64;
  asm volatile("svc #0" : "+r"(x0) : "r"(x1), "r"(x2), "r"(x8) : "memory"); }
static void check(const char *name, int ok) { wr(ok ? "  ok   - " : "  FAIL - "); wr(name); wr("\n"); if (!ok) fails++; }
int main(void) {
  u32 spk[1] = {2}, two[2] = {2, 4}, ear[1] = {1};
  struct attr at; struct handler h; h.a = &at;
  u16 b16[6]; u32 b32[6]; int r;
  #define SET16 b16[0]=1;b16[1]=2;b16[2]=3;b16[3]=4;b16[4]=5;b16[5]=6;
  #define SET32 b32[0]=0x11111111;b32[1]=0x22222222;b32[2]=0x33333333;b32[3]=0x44444444;b32[4]=0x55555555;b32[5]=0x66666666;

  // The protection library: loaded once, then called with the HAL's arguments.
  at.flags = 0x8; at.fmt = 3; at.vb = spk; at.ve = spk + 1; prop_val = 270; swap_val = 0x8;
  lib_ok = 1; SLOT[0] = SLOT[1] = 0; SET32
  r = swapfn(&h, b32, 16);
  check("library loaded from /vendor/lib64/hw/libcmfstereo.so", eq(libname, "/vendor/lib64/hw/libcmfstereo.so") && eq(symn, "cmf_process"));
  check("library called with this, buffer, bytes; returns 0", lib_calls == 1 && lib_self == &h && lib_buf == b32 && lib_bytes == 16 && r == 0);
  check("with the library, the patch itself swaps nothing", b32[0]==0x11111111 && b32[1]==0x22222222);
  swapfn(&h, b32, 16); swapfn(&h, b32, 16);
  check("loaded once, called every time", dlopen_calls == 1 && dlsym_calls == 1 && lib_calls == 3);
  // No library: marked failed, never retried, the swap alone runs.
  lib_ok = 0; SLOT[0] = SLOT[1] = 0; dlopen_calls = 0; SET32
  swapfn(&h, b32, 16);
  check("library missing: falls back to the swap", b32[0]==0x22222222 && b32[1]==0x11111111);
  SET32 swapfn(&h, b32, 16);
  check("a failed load is not retried", dlopen_calls == 1 && SLOT[1] == 1);
  // VLC-like stream on the deep-buffer output, which the daemon flagged.
  at.flags = 0x8; at.fmt = 1; at.vb = spk; at.ve = spk + 1; prop_val = 270; swap_val = 0x8; SET16
  r = swapfn(&h, b16, 8);
  check("16-bit, speaker, 270, flagged output: swapped", r == 0 && b16[0]==2 && b16[1]==1 && b16[2]==4 && b16[3]==3 && b16[4]==5 && b16[5]==6);
  check("reads vendor.audiohal.cmf_rotation", eq(kbuf, "vendor.audiohal.cmf_rotation"));
  check("reads vendor.audiohal.cmf_swap", eq(skey, "vendor.audiohal.cmf_swap"));
  at.fmt = 3; SET32
  r = swapfn(&h, b32, 16);
  check("32-bit, speaker, 270, flagged output: swapped", r == 0 && b32[0]==0x22222222 && b32[1]==0x11111111 && b32[2]==0x44444444 && b32[3]==0x33333333 && b32[4]==0x55555555);
  // Android swapped these itself: left alone.
  swap_val = 0; SET32
  swapfn(&h, b32, 16);
  check("cmf_swap 0 (unset, no own-effect track): untouched", b32[0]==0x11111111 && b32[1]==0x22222222);
  swap_val = 0x8; at.flags = 0x2; SET32
  swapfn(&h, b32, 16);
  check("primary output, deep buffer flagged: untouched", b32[0]==0x11111111);
  at.flags = 0x4; SET32
  swapfn(&h, b32, 16);
  check("fast output, deep buffer flagged: untouched", b32[0]==0x11111111);
  swap_val = 0x2 | 0x8; at.flags = 0x2; SET32
  swapfn(&h, b32, 16);
  check("primary and deep buffer flagged, primary output: swapped", b32[0]==0x22222222);
  at.flags = 0x8; swap_val = 0x8;
  prop_val = 90; SET32 pgi_calls = 0;
  swapfn(&h, b32, 16);
  check("rotation 90: untouched, cmf_swap not read", b32[0]==0x11111111 && b32[1]==0x22222222 && pgi_calls == 1);
  prop_val = 0; SET32
  swapfn(&h, b32, 16);
  check("rotation 0 (unset): untouched", b32[0]==0x11111111);
  prop_val = 270; at.vb = two; at.ve = two + 2; SET32 pgi_calls = 0;
  swapfn(&h, b32, 16);
  check("speaker + another device: untouched", b32[0]==0x11111111 && pgi_calls == 0);
  at.vb = ear; at.ve = ear + 1; SET32
  swapfn(&h, b32, 16);
  check("earpiece-only route: untouched", b32[0]==0x11111111);
  at.vb = spk; at.ve = spk; SET32
  swapfn(&h, b32, 16);
  check("no devices: untouched", b32[0]==0x11111111);
  at.vb = spk; at.ve = spk + 1; at.fmt = 5; SET32
  swapfn(&h, b32, 16);
  check("float format: untouched", b32[0]==0x11111111);
  at.fmt = 3; SET32
  r = swapfn(&h, b32, 0);
  check("zero bytes: nothing written, returns 0", r == 0 && b32[0]==0x11111111);
  h.a = 0; r = swapfn(&h, b32, 16);
  check("no attributes: returns 0", r == 0 && b32[0]==0x11111111);
  h.a = &at;
  long x1 = call_rotcave("270");
  check("rotation key: stored by property_set", eq(kbuf, "vendor.audiohal.cmf_rotation") && eq(vbuf, "270"));
  check("replayed adrp gives the original page", x1 == (((long)PG37D) & ~0xfffL));
  wr(fails ? "FAILED\n" : "all passed\n");
  return fails;
}
