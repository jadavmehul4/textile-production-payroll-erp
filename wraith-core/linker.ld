ENTRY(_start)

SECTIONS
{
    /* Load the kernel at 1MB physical */
    . = 1M;

    /* But link it to the High-Half Virtual Base (provided by user) */
    _kernel_phys_base = .;
    _kernel_virt_base = 0xffffffff80000000;

    .text _kernel_virt_base : AT(_kernel_phys_base)
    {
        _text_start = .;
        *(.text .text.*)
        . = ALIGN(4K);
        _text_end = .;
    }

    .rodata : ALIGN(4K)
    {
        _rodata_start = .;
        *(.rodata .rodata.*)
        . = ALIGN(4K);
        _rodata_end = .;
    }

    .data : ALIGN(4K)
    {
        _data_start = .;
        *(.data .data.*)
        . = ALIGN(4K);
        _data_end = .;
    }

    .bss : ALIGN(4K)
    {
        _bss_start = .;
        *(.bss .bss.*)
        . = ALIGN(4K);
        _bss_end = .;
    }

    _kernel_end = .;

    /* Define boundaries for tagged regions */
    . = ALIGN(4K);
    _secure_heap_start = .;
    . += 2M;
    _secure_heap_end = .;

    _shielded_state_start = .;
    . += 1M;
    _shielded_state_end = .;
}
