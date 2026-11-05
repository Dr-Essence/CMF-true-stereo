// CMF true stereo: orientation swap for streams Android leaves unswapped.
//
// Replaces AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed
// (this, void* buffer, size_t bytes) at 0x27b820, which stereo mode already
// turns into a plain return. Android swaps left and right itself at rotation
// 270 (HAL recordings: a left-only beep reaches the HAL on the right), except
// for a track whose session has its own effect chain (VLC's Dynamics
// Processing, the test app's MOVIE + EFFECT: the beep stays on the left).
// The module's daemon finds those (dumpsys media.audio_flinger) and writes the
// output flags of their mixer threads to vendor.audiohal.cmf_swap. This
// function swaps in place only when:
//   - the stream goes to the speaker alone (devices vector at
//     [[this+0x20]+0x1d8] is exactly { AUDIO_DEVICE_OUT_SPEAKER = 0x2 }:
//     the same check MediaTek's fold made; headphones are never swapped),
//   - vendor.audiohal.cmf_rotation reads 270 (earpiece on the right),
//   - the stream's output flags ([[this+0x20]+0xc], the value MediaTek's
//     write() log prints) share a bit with vendor.audiohal.cmf_swap,
//   - the format at [[this+0x20]] is PCM_16_BIT (1) or PCM_32_BIT (3), the
//     two MediaTek's fold handled.
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
        .balign 4
        .globl patch_end
patch_end:
