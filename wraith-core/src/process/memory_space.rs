use x86_64::{VirtAddr, PhysAddr};
use alloc::vec::Vec;
use crate::memory::paging::flags::PageTableFlags;

/// Represents a distinct memory region within an address space.
#[derive(Debug, Clone)]
pub struct MemoryRegion {
    pub start: VirtAddr,
    pub size: usize,
    pub flags: PageTableFlags,
}

/// Represents the isolated virtual address space of a process.
pub struct MemorySpace {
    /// Physical address of the process-specific PML4 table.
    pub pml4_phys: PhysAddr,
    /// List of allocated regions for cleanup tracking.
    pub regions: Vec<MemoryRegion>,
}

impl MemorySpace {
    pub fn new(pml4_phys: PhysAddr) -> Self {
        Self {
            pml4_phys,
            regions: Vec::new(),
        }
    }

    pub fn add_region(&mut self, start: VirtAddr, size: usize, flags: PageTableFlags) {
        self.regions.push(MemoryRegion { start, size, flags });
    }
}
