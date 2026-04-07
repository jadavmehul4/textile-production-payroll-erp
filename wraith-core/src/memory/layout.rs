/// Virtual Memory Layout for Wraith Core (Ultra Pro Max)

/// Dedicated High Region for Memory Mapped I/O
pub const MMIO_BASE: u64 = 0xffff_f000_0000_0000;

/// Base address for the Kernel Heap
pub const HEAP_START: u64 = 0xffff_9000_0000_0000;
pub const HEAP_INITIAL_SIZE: usize = 1024 * 1024; // 1 MiB

/// High-Half Direct Mapping (HHDM) of full physical memory
pub const PHYS_OFFSET: u64 = 0xffff_8000_0000_0000;

/// Base virtual address for the Kernel (requested: 0xffffffff80000000)
pub const KERNEL_VIRT_BASE: u64 = 0xffff_ffff_8000_0000;
pub const KERNEL_PHYS_BASE: u64 = 0x0000_0000_0010_0000; // 1 MiB
