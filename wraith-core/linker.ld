ENTRY(_start)

SECTIONS
{
    . = 1M;

    .text :
    {
        *(.text .text.*)
    }

    .rodata :
    {
        *(.rodata .rodata.*)
    }

    .data :
    {
        *(.data .data.*)
    }

    .bss :
    {
        *(.bss .bss.*)
    }

    /* Define boundaries for tagged regions if needed by allocator later */
    . = ALIGN(4K);
    _secure_heap_start = .;
    . += 2M;
    _secure_heap_end = .;

    _shielded_state_start = .;
    . += 1M;
    _shielded_state_end = .;
}
