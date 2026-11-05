// CMF true stereo: orientation swap and protection, in the HAL's playback path.
//
// Replaces AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed
// (this, void* buffer, size_t bytes) at 0x27b820 (508 bytes), which stereo mode
// already turns into a plain return. On its first call it loads the module's
// protection library (/vendor/lib64/hw/libcmfstereo.so, protect/cmfstereo.c)
// and from then on calls its cmf_process(this, buffer, bytes): the rotation
// swap, the speaker and bass limiters and the earpiece limiter. The library's
// address (and a "failed" mark) is kept at 0x384ff0, in the HAL's last
// writable page past the end of its .bss (data ends at 0x3849b8, the page at
// 0x385000): mapped, zeroed, used by nothing else.
//
// If the library cannot be loaded, the function falls back to the swap alone,
// the v1.0.2 code below: left and right swapped in place when
//   - the stream goes to the speaker alone (devices vector at
//     [[this+0x20]+0x1d8] is exactly { AUDIO_DEVICE_OUT_SPEAKER = 0x2 }),
//   - vendor.audiohal.cmf_rotation reads 270 (earpiece on the right),
//   - the stream's output flags ([[this+0x20]+0xc]) share a bit with
//     vendor.audiohal.cmf_swap (outputs carrying a track with its own effect
//     chain, which Android leaves unswapped; written by the module's daemon),
//   - the format at [[this+0x20]] is PCM_16_BIT (1) or PCM_32_BIT (3).
// Always returns 0, as before.
//
// rotcave is reached from setParameters at 0x2587c0 (the "rotation" key was
// found; the stock HAL only drops it): it stores the value with
// property_set, re-runs the instruction it replaced and goes back.
        .text
        .globl swapfn
swapfn:
        stp     x29, x30, [sp, #-48]!
        mov     x29, sp
        stp     x19, x20, [sp, #16]
        str     x21, [sp, #32]
        mov     x19, x0
        mov     x20, x1
        mov     x21, x2
        adrp    x9, SLOTPAGE
        add     x9, x9, :lo12:SLOT
        ldr     x10, [x9]
        cbnz    x10, 7f
        ldr     w11, [x9, #8]
        cbnz    w11, 8f
        adr     x0, libpath
        mov     w1, #2                  // RTLD_NOW
        bl      DLOPEN
        cbz     x0, 6f
        adr     x1, symname
        bl      DLSYM
        cbz     x0, 6f
        adrp    x9, SLOTPAGE
        add     x9, x9, :lo12:SLOT
        str     x0, [x9]
        mov     x10, x0
7:      mov     x0, x19
        mov     x1, x20
        mov     x2, x21
        blr     x10
        b       9f
6:      adrp    x9, SLOTPAGE
        add     x9, x9, :lo12:SLOT
        mov     w11, #1
        str     w11, [x9, #8]
8:
        ldr     x8, [x19, #0x20]
        cbz     x8, 9f
        ldp     x9, x10, [x8, #0x1d8]
        sub     x11, x10, x9
        cmp     x11, #4
        b.ne    9f
        ldr     w11, [x9]
        cmp     w11, #2
        b.ne    9f
        adr     x0, key
        mov     w1, wzr
        bl      PGI
        cmp     w0, #270
        b.ne    9f
        adr     x0, swapkey
        mov     w1, wzr
        bl      PGI
        ldr     x8, [x19, #0x20]
        ldr     w9, [x8, #0xc]
        tst     w0, w9
        b.eq    9f
        ldr     w8, [x8]
        cmp     w8, #3
        b.eq    3f
        cmp     w8, #1
        b.ne    9f
        lsr     x9, x21, #2
        cbz     x9, 9f
1:      ldr     w10, [x20]
        ror     w10, w10, #16
        str     w10, [x20], #4
        subs    x9, x9, #1
        b.ne    1b
        b       9f
3:      lsr     x9, x21, #3
        cbz     x9, 9f
4:      ldp     w10, w11, [x20]
        stp     w11, w10, [x20], #8
        subs    x9, x9, #1
        b.ne    4b
9:      mov     w0, wzr
        ldr     x21, [sp, #32]
        ldp     x19, x20, [sp, #16]
        ldp     x29, x30, [sp], #48
        ret

        .globl rotcave
rotcave:
        ldr     x1, [sp, #0x3c0]
        adr     x0, key
        bl      PSET
        adrp    x1, PG37D
        b       RET2587C4

key:    .asciz  "vendor.audiohal.cmf_rotation"
swapkey: .asciz "vendor.audiohal.cmf_swap"
libpath: .asciz "/vendor/lib64/hw/libcmfstereo.so"
symname: .asciz "cmf_process"
        .balign 4
        .globl patch_end
patch_end:
