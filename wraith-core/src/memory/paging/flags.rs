use bitflags::bitflags;

bitflags! {
    /// 64-bit page table entry flags.
    /// These are standardized flags for x86_64 4-level paging.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
    pub struct PageTableFlags: u64 {
        /// Bit 0: Entry is present in memory.
        const PRESENT = 1;
        /// Bit 1: Entry is writable (1) or read-only (0).
        const WRITABLE = 1 << 1;
        /// Bit 2: Accessible from user mode (Ring 3).
        const USER_ACCESSIBLE = 1 << 2;
        /// Bit 3: Write-through caching (PWT).
        const WRITE_THROUGH = 1 << 3;
        /// Bit 4: Disable caching (PCD).
        const NO_CACHE = 1 << 4;
        /// Bit 5: Entry has been accessed by CPU.
        const ACCESSED = 1 << 5;
        /// Bit 6: Entry has been written to (only for Level 1 or HUGE).
        const DIRTY = 1 << 6;
        /// Bit 7: Entry maps a 2MB or 1GB page instead of a page table.
        const HUGE_PAGE = 1 << 7;
        /// Bit 8: Global page (not flushed from TLB on CR3 switch).
        const GLOBAL = 1 << 8;
        /// Bit 63: No-Execute (NX) bit (requires IA32_EFER.NXE).
        const NO_EXECUTE = 1 << 63;
    }
}
