pub mod flags;
pub mod page_table;
pub mod mapper;

use x86_64::{PhysAddr, VirtAddr};
use crate::memory::frame_allocator::BitmapFrameAllocator;
use self::page_table::PageTable;
use self::mapper::Mapper;
use self::flags::PageTableFlags;

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

    let mut mapper = Mapper::new(pml4, frame_allocator, current_offset);

    // 3. Identity map critical early-boot regions (first 1MB)
    // VGA (0xb8000), Serial (0x3F8), and Kernel text/data
    for i in 0..1024 { // Map 4MB to cover common kernel/stack identity mappings
        let addr = i * 4096;
        mapper.map_4k(
            VirtAddr::new(addr),
            PhysAddr::new(addr),
            PageTableFlags::PRESENT | PageTableFlags::WRITABLE
        );
    }

    // 4. Map the full physical memory to the NEW HHDM region (PHYS_OFFSET)
    // Map the first 1GB as 2MB huge pages for the high-half
    for i in 0..512 {
        let addr = i * 2 * 1024 * 1024;
        mapper.map_2m(
            VirtAddr::new(addr + self::mapper::PHYS_OFFSET),
            PhysAddr::new(addr),
            PageTableFlags::PRESENT | PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE
        );
    }

    // 5. Explicitly map the current stack region in the new tables to ensure continuity
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
                PageTableFlags::PRESENT | PageTableFlags::WRITABLE
            );
        }

        // Guard Page: 1 page below the stack
        GUARD_PAGE_START = stack_page_start - (17 * 4096);
    }

    // 6. Switch to the new page tables by loading CR3
    load_cr3(pml4_frame);
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
