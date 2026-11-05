        .text
        .globl _start
_start: bl      main
        mov     x8, #93
        svc     #0
// long call_rotcave(const char *value): builds the setParameters frame shape
// (String8 value at sp+0x3c0), jumps into rotcave, and returns the x1 that
// rotcave computed with its replayed adrp, once it branches to RET2587C4.
        .globl call_rotcave
call_rotcave:
        stp     x29, x30, [sp, #-16]!
        sub     sp, sp, #0x400
        str     x0, [sp, #0x3c0]
        b       rotcave
        .globl RET2587C4
RET2587C4:
        mov     x0, x1
        add     sp, sp, #0x400
        ldp     x29, x30, [sp], #16
        ret
        .data
        .balign 4096
        .globl PG37D
PG37D:  .quad 0
// The library slot (address, then the "failed" mark), as at 0x384ff0 in the HAL.
        .balign 4096
        .globl SLOTPAGE
        .globl SLOT
SLOTPAGE:
SLOT:   .quad 0, 0
