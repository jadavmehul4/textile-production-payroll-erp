pub mod flags;
pub mod page_table;
pub mod mapper;

use x86_64::{PhysAddr, VirtAddr};
use crate::memory::frame_allocator::BitmapFrameAllocator;
use self::page_table::PageTable;
use self::mapper::Mapper;
use self::flags::PageTableFlags;

// Linker symbols
extern "C" {
    static _text_start: usize;
    static _text_end: usize;
    static _rodata_start: usize;
    static _rodata_end: usize;
    static _data_start: usize;
    static _data_end: usize;
    static _bss_start: usize;
    static _bss_end: usize;
    static _kernel_phys_base: usize;
}

/// Initialize the 4-level paging system.
/// Accepts the physical memory offset provided by the bootloader for bootstrapping.
pub unsafe fn init(frame_allocator: &mut BitmapFrameAllocator, current_offset: u64) {
    // 1. Enable No-Execute (NX) bit in IA32_EFER MSR
    enable_nx_bit();

    // 2. Allocate and initialize the new PML4 table
    let pml4_frame = frame_allocator.allocate_frame()
        .expect("Failed to allocate PML4 frame");

    // Access the newly allocated frame using the current offset
    let pml4_virt = self::mapper::phys_to_virt_with_offset(pml4_frame, current_offset);
    let pml4 = &mut *pml4_virt.as_mut_ptr::<PageTable>();
    pml4.zero();

    // Identify total physical memory before creating mapper
    let total_phys_memory = frame_allocator.total_frames() as u64 * 4096;

    let mut mapper = Mapper::new(pml4, frame_allocator, current_offset);

    // 3. Identity map critical regions (first 1MB) for continuity during switch
    for i in 0..256 {
        let addr = i * 4096;
        mapper.map_4k(
            VirtAddr::new(addr),
            PhysAddr::new(addr),
            PageTableFlags::PRESENT | PageTableFlags::WRITABLE
        );
    }

    // 4. Map Kernel Sections into HIGH HALF (0xffffffff80000000)
    let phys_base = &_kernel_phys_base as *const usize as u64;

    // TEXT → RX
    map_section_high(&mut mapper, &_text_start, &_text_end, phys_base, PageTableFlags::PRESENT);

    // RODATA → R
    map_section_high(&mut mapper, &_rodata_start, &_rodata_end, phys_base, PageTableFlags::PRESENT | PageTableFlags::NO_EXECUTE);

    // DATA/BSS → RW
    map_section_high(&mut mapper, &_data_start, &_bss_end, phys_base, PageTableFlags::PRESENT | PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE);

    // 5. Map MMIO regions at dedicated high addresses
    mapper.map_4k(
        VirtAddr::new(crate::memory::layout::MMIO_BASE),
        PhysAddr::new(0xb8000),
        PageTableFlags::PRESENT | PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE
    );

    // 6. Map the full physical memory to the NEW HHDM region (PHYS_OFFSET)
    let gigabyte = 1024 * 1024 * 1024;
    let map_limit = total_phys_memory.max(gigabyte); // Map at least 1GB

    for addr in (0..map_limit).step_by(2 * 1024 * 1024) {
        mapper.map_2m(
            VirtAddr::new(addr + self::mapper::PHYS_OFFSET),
            PhysAddr::new(addr),
            PageTableFlags::PRESENT | PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE
        );
    }

    // 7. Map the current stack region in the new tables
    let mut rsp: u64;
    core::arch::asm!("mov {}, rsp", out(reg) rsp);
    let stack_page_start = rsp & !0xFFF;

    if stack_page_start >= current_offset {
        let phys_stack_start = stack_page_start - current_offset;
        for i in 0..16 { // Map 64KB stack
            let addr_virt = stack_page_start - (i * 4096);
            let addr_phys = phys_stack_start - (i * 4096);
            mapper.map_4k(
                VirtAddr::new(addr_virt),
                PhysAddr::new(addr_phys),
                PageTableFlags::PRESENT | PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE
            );
        }
        GUARD_PAGE_START = stack_page_start - (17 * 4096);
    }

    // 8. Switch to the new page tables by loading CR3
    load_cr3(pml4_frame);
}

/// Helper to map a high-half linker section with specific flags.
unsafe fn map_section_high(mapper: &mut Mapper, start: &usize, end: &usize, phys_base: u64, flags: PageTableFlags) {
    let start_virt = start as *const usize as u64;
    let end_virt = end as *const usize as u64;
    let virt_base = 0xffffffff80000000;

    for virt_addr in (start_virt..end_virt).step_by(4096) {
        let phys_addr = phys_base + (virt_addr - virt_base);
        mapper.map_4k(VirtAddr::new(virt_addr), PhysAddr::new(phys_addr), flags);
    }
}

static mut GUARD_PAGE_START: u64 = 0;

pub fn is_guard_page_violation(addr: u64) -> bool {
    unsafe { addr >= GUARD_PAGE_START && addr < GUARD_PAGE_START + 4096 }
}

/// Enable the No-Execute (NX) bit using the IA32_EFER MSR.
unsafe fn enable_nx_bit() {
    core::arch::asm!(
        "mov ecx, 0xC0000080", // EFER MSR
        "rdmsr",
        "or eax, 1 << 11",    // Bit 11: NXE (No-Execute Enable)
        "wrmsr",
    );
}

/// Load a new PML4 address into the CR3 register.
unsafe fn load_cr3(pml4_phys: PhysAddr) {
    core::arch::asm!(
        "mov cr3, {0}",
        in(reg) pml4_phys.as_u64(),
    );
}
