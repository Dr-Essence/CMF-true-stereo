// CMF true stereo: orientation swap.
//
// Replaces AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed
// (this, void* buffer, size_t bytes) at 0x27b820, which stereo mode already
// turns into a plain return. It now swaps left and right in place when:
//   - the stream goes to the speaker alone (devices vector at
//     [[this+0x20]+0x1d8] is exactly { AUDIO_DEVICE_OUT_SPEAKER = 0x2 }:
//     the same check MediaTek's fold made; headphones are never swapped),
//   - Nothing's Dirac is not already swapping it: Dirac follows the music
//     stream to whichever output plays it, and in its MUSIC tuning it swaps
//     left and right with the rotation itself; in MOVIE (and the other
//     tunings) it does not. Measured on the phone, same output for both:
//     UAPP (not on Nothing's app lists -> MUSIC) came out right only with
//     this swap off, VLC (on its video list -> MOVIE) only with it on.
//     Dirac keeps its tuning in persist.vendor.newdirac.cur.config and its
//     switch in persist.vendor.newdirac.enable.value ("1.000000" on), so
//     the swap is skipped while those read MUSIC and 1. If the tuning
//     cannot be read at all, the earlier rule stands. (v0.9.5-v0.9.8 went
//     by the output instead - skipping the primary one - which was right
//     only while MUSIC apps happened to play there.)
//   - the format at [[this+0x20]] is PCM_16_BIT (1) or PCM_32_BIT (3), the
//     two MediaTek's fold handled,
//   - vendor.audiohal.cmf_rotation reads 270 (earpiece on the right,
//     measured on the phone).
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
        // Dirac on and in MUSIC: it swaps this stream itself.
        sub     sp, sp, #96             // PROP_VALUE_MAX (92), rounded up
        adr     x0, kcfg
        mov     x1, sp
        adr     x2, unread              // "?" when it cannot be read
        bl      PG
        ldrb    w9, [sp]
        cmp     w9, #'?'
        b.ne    6f
        // Unreadable (no Dirac, or not allowed): the earlier rule, which
        // held while MUSIC apps played on the primary output.
        add     sp, sp, #96
        ldr     x8, [x19, #0x20]
        ldr     w11, [x8, #0xc]
        tbnz    w11, #1, 9f
        b       7f
6:      ldr     x9, [sp]
        and     x9, x9, #0xffffffffffff // "MUSIC" and its NUL
        ldr     x10, music
        cmp     x9, x10
        b.ne    5f
        adr     x0, kon
        mov     x1, sp
        adr     x2, key + 28
        bl      PG
        ldrb    w9, [sp]
        cmp     w9, #'1'
        b.ne    5f
        add     sp, sp, #96
        b       9f
5:      add     sp, sp, #96
7:
        ldr     x8, [x19, #0x20]
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
kcfg:   .asciz  "persist.vendor.newdirac.cur.config"
kon:    .asciz  "persist.vendor.newdirac.enable.value"
unread: .asciz  "?"
        .balign 8
music:  .ascii  "MUSIC\0\0\0"
        .balign 4
        .globl patch_end
patch_end:
