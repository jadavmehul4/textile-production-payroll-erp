use core::ops::{Index, IndexMut};
use crate::memory::paging::flags::PageTableFlags;

/// A 64-bit page table entry.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(transparent)]
pub struct PageTableEntry(u64);

impl PageTableEntry {
    /// Return the raw bits of the entry.
    pub const fn bits(&self) -> u64 {
        self.0
    }

    /// Return the flags as `PageTableFlags`.
    pub const fn flags(&self) -> PageTableFlags {
        PageTableFlags::from_bits_truncate(self.0)
    }

    /// Return the physical address from the entry (bits 12..52).
    pub const fn addr(&self) -> u64 {
        self.0 & 0x000F_FFFF_FFFF_F000
    }

    /// Set the flags for this entry.
    pub fn set_flags(&mut self, flags: PageTableFlags) {
        self.0 = (self.0 & 0x000F_FFFF_FFFF_F000) | flags.bits();
    }

    /// Set the physical address for this entry.
    pub fn set_addr(&mut self, addr: u64) {
        // Address must be 4KB aligned
        debug_assert_eq!(addr % 4096, 0);
        self.0 = (self.0 & !0x000F_FFFF_FFFF_F000) | (addr & 0x000F_FFFF_FFFF_F000);
    }

    /// Clear the entry.
    pub fn clear(&mut self) {
        self.0 = 0;
    }

    /// Check if the entry is unused.
    pub const fn is_unused(&self) -> bool {
        self.0 == 0
    }
}

/// A x86_64 page table containing 512 entries.
#[repr(align(4096))]
pub struct PageTable {
    entries: [PageTableEntry; 512],
}

impl PageTable {
    pub const fn new() -> Self {
        Self {
            entries: [PageTableEntry(0); 512],
        }
    }

    pub fn zero(&mut self) {
        for entry in self.entries.iter_mut() {
            entry.clear();
        }
    }
}

impl Index<usize> for PageTable {
    type Output = PageTableEntry;

    fn index(&self, index: usize) -> &Self::Output {
        &self.entries[index]
    }
}

impl IndexMut<usize> for PageTable {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        &mut self.entries[index]
    }
}
