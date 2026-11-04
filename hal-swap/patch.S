// CMF true stereo: orientation swap.
//
// Replaces AudioALSAPlaybackHandlerBase::doStereoToMonoConversionIfNeed
// (this, void* buffer, size_t bytes) at 0x27b820, which stereo mode already
// turns into a plain return. It now swaps left and right in place when:
//   - the stream goes to the speaker alone (devices vector at
//     [[this+0x20]+0x1d8] is exactly { AUDIO_DEVICE_OUT_SPEAKER = 0x2 }:
//     the same check MediaTek's fold made; headphones are never swapped),
//   - it is not the primary output (output flags at [[this+0x20]+0xc], the
//     value MediaTek's own write() log prints, without AUDIO_OUTPUT_FLAG_
//     PRIMARY = 0x2). Nothing's Dirac sits on the primary output and already
//     swaps it with the rotation (measured: our swap on top cancelled it;
//     with ours off, Dirac alone moved the sound); every other output (deep
//     buffer, fast) has no Dirac and is swapped here,
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
        ldr     w11, [x8, #0xc]
        tbnz    w11, #1, 9f
        adr     x0, key
        mov     w1, wzr
        bl      PGI
        cmp     w0, #270
        b.ne    9f
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
        .balign 4
        .globl patch_end
patch_end:
