use x86_64::{PhysAddr, VirtAddr};
use crate::memory::paging::page_table::PageTable;
use crate::memory::paging::flags::PageTableFlags;
use crate::memory::frame_allocator::BitmapFrameAllocator;

/// Fixed high virtual base for High-Half Direct Mapping (HHDM).
/// This is our desired offset for the new page tables.
pub const PHYS_OFFSET: u64 = 0xffff_8000_0000_0000;

/// Convert a physical address to a virtual address using a specific offset.
pub fn phys_to_virt_with_offset(phys: PhysAddr, offset: u64) -> VirtAddr {
    VirtAddr::new(phys.as_u64() + offset)
}

/// A paging mapper for 4KB and 2MB pages.
pub struct Mapper<'a> {
    p4: &'a mut PageTable,
    frame_allocator: &'a mut BitmapFrameAllocator,
    current_offset: u64, // The offset currently usable by the CPU to access physical memory
}

impl<'a> Mapper<'a> {
    pub fn new(p4: &'a mut PageTable, frame_allocator: &'a mut BitmapFrameAllocator, current_offset: u64) -> Self {
        Self { p4, frame_allocator, current_offset }
    }

    /// Map a 4KB virtual page to a physical frame.
    pub unsafe fn map_4k(&mut self, virt: VirtAddr, phys: PhysAddr, flags: PageTableFlags) {
        let p3_ptr = Self::create_next_table_static(self.p4, virt.p4_index(), self.frame_allocator, self.current_offset);
        let p2_ptr = Self::create_next_table_static(&mut *p3_ptr, virt.p3_index(), self.frame_allocator, self.current_offset);
        let p1_ptr = Self::create_next_table_static(&mut *p2_ptr, virt.p2_index(), self.frame_allocator, self.current_offset);

        let p1 = &mut *p1_ptr;
        let entry = &mut p1[usize::from(virt.p1_index())];

        entry.set_addr(phys.as_u64());
        entry.set_flags(flags | PageTableFlags::PRESENT);
    }

    /// Update flags for an existing page.
    pub unsafe fn update_flags(&mut self, virt: VirtAddr, flags: PageTableFlags) {
        let p3_ptr = Self::get_next_table_static(self.p4, virt.p4_index(), self.current_offset);
        if p3_ptr.is_none() { return; }

        let p2_ptr = Self::get_next_table_static(&mut *p3_ptr.unwrap(), virt.p3_index(), self.current_offset);
        if p2_ptr.is_none() { return; }

        let p1_ptr = Self::get_next_table_static(&mut *p2_ptr.unwrap(), virt.p2_index(), self.current_offset);
        if p1_ptr.is_none() { return; }

        let p1 = &mut *p1_ptr.unwrap();
        let entry = &mut p1[usize::from(virt.p1_index())];

        entry.set_flags(flags | PageTableFlags::PRESENT);

        // Flush TLB for the updated page
        self::flush_tlb(virt);
    }

    /// Map a 2MB virtual page to a physical frame.
    pub unsafe fn map_2m(&mut self, virt: VirtAddr, phys: PhysAddr, flags: PageTableFlags) {
        let p3_ptr = Self::create_next_table_static(self.p4, virt.p4_index(), self.frame_allocator, self.current_offset);
        let p2_ptr = Self::create_next_table_static(&mut *p3_ptr, virt.p3_index(), self.frame_allocator, self.current_offset);

        let p2 = &mut *p2_ptr;
        let entry = &mut p2[usize::from(virt.p2_index())];

        entry.set_addr(phys.as_u64());
        entry.set_flags(flags | PageTableFlags::PRESENT | PageTableFlags::HUGE_PAGE);
    }

    /// Helper to navigate and create page tables dynamically.
    unsafe fn create_next_table_static(table: &mut PageTable, index: x86_64::structures::paging::PageTableIndex, frame_allocator: &mut BitmapFrameAllocator, current_offset: u64) -> *mut PageTable {
        let entry = &mut table[usize::from(index)];

        if entry.is_unused() {
            let frame = frame_allocator.allocate_frame()
                .expect("Out of physical memory for page tables");

            let virt = phys_to_virt_with_offset(frame, current_offset);
            let next_table = virt.as_mut_ptr::<PageTable>();
            (*next_table).zero();

            entry.set_addr(frame.as_u64());
            entry.set_flags(PageTableFlags::PRESENT | PageTableFlags::WRITABLE);
        }

        phys_to_virt_with_offset(PhysAddr::new(entry.addr()), current_offset).as_mut_ptr()
    }

    /// Helper to navigate existing page tables.
    unsafe fn get_next_table_static(table: &mut PageTable, index: x86_64::structures::paging::PageTableIndex, current_offset: u64) -> Option<*mut PageTable> {
        let entry = &mut table[usize::from(index)];
        if entry.is_unused() { return None; }
        Some(phys_to_virt_with_offset(PhysAddr::new(entry.addr()), current_offset).as_mut_ptr())
    }
}

/// Flush the TLB for a single page.
pub unsafe fn flush_tlb(virt: VirtAddr) {
    core::arch::asm!(
        "invlpg [{}]",
        in(reg) virt.as_u64(),
    );
}

/// Full TLB flush by reloading CR3.
pub unsafe fn full_tlb_flush() {
    core::arch::asm!(
        "mov rax, cr3",
        "mov cr3, rax",
        out("rax") _,
    );
}
