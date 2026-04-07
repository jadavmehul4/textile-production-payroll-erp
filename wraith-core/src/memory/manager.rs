use x86_64::{VirtAddr, PhysAddr};
use spin::Mutex;
use crate::memory::frame_allocator::BitmapFrameAllocator;
use crate::memory::paging::mapper::Mapper;
use crate::memory::paging::flags::PageTableFlags;
use crate::process::memory_space::MemorySpace;

/// MemoryManager acts as the primary orchestrator between the Frame Allocator and Mapper.
pub struct MemoryManager {
    frame_allocator: &'static Mutex<BitmapFrameAllocator>,
    // The master kernel PML4 (physical address)
    kernel_pml4: PhysAddr,
}

impl MemoryManager {
    pub const fn new(kernel_pml4: PhysAddr, frame_allocator: &'static Mutex<BitmapFrameAllocator>) -> Self {
        Self { kernel_pml4, frame_allocator }
    }

    /// Create a new isolated address space for a user process.
    pub unsafe fn create_user_address_space(&self) -> MemorySpace {
        let mut frame_allocator = self.frame_allocator.lock();

        // 1. Allocate a new PML4 table
        let pml4_frame = frame_allocator.allocate_frame().expect("OOM: Failed to allocate process PML4");
        let pml4_virt = crate::memory::paging::mapper::phys_to_virt_with_offset(pml4_frame, crate::memory::layout::PHYS_OFFSET);
        let pml4 = &mut *pml4_virt.as_mut_ptr::<crate::memory::paging::page_table::PageTable>();
        pml4.zero();

        // 2. Copy Kernel Mappings (top half: 256-511)
        let kernel_pml4_virt = crate::memory::paging::mapper::phys_to_virt_with_offset(self.kernel_pml4, crate::memory::layout::PHYS_OFFSET);
        let kernel_pml4 = &*kernel_pml4_virt.as_ptr::<crate::memory::paging::page_table::PageTable>();

        for i in 256..512 {
            pml4[i] = kernel_pml4[i];
        }

        MemorySpace::new(pml4_frame)
    }

    /// Map a user-accessible region within a specific memory space.
    pub unsafe fn map_user_region(&self, space: &mut MemorySpace, start: VirtAddr, size: usize, flags: PageTableFlags) {
        let pml4_virt = crate::memory::paging::mapper::phys_to_virt_with_offset(space.pml4_phys, crate::memory::layout::PHYS_OFFSET);
        let pml4 = &mut *pml4_virt.as_mut_ptr::<crate::memory::paging::page_table::PageTable>();

        let start_page = (start.as_u64() / 4096) * 4096;
        let end_page = ((start.as_u64() + size as u64 + 4095) / 4096) * 4096;
        let user_flags = flags | PageTableFlags::USER_ACCESSIBLE | PageTableFlags::PRESENT;

        for addr in (start_page..end_page).step_by(4096) {
            let mut frame_allocator = self.frame_allocator.lock();
            let frame = frame_allocator.allocate_frame().expect("OOM during user mapping");
            let mut mapper = Mapper::new(pml4, &mut *frame_allocator, crate::memory::layout::PHYS_OFFSET);
            mapper.map_4k(VirtAddr::new(addr), frame, user_flags);
        }

        space.add_region(start, size, user_flags);
    }

    /// Allocate physical frames and map them to a virtual range (Kernel/Global).
    pub unsafe fn map_range(&self, start: VirtAddr, size: usize, flags: PageTableFlags) {
        let pml4_virt = crate::memory::paging::mapper::phys_to_virt_with_offset(self.kernel_pml4, crate::memory::layout::PHYS_OFFSET);
        let pml4 = &mut *pml4_virt.as_mut_ptr::<crate::memory::paging::page_table::PageTable>();

        let start_page = (start.as_u64() / 4096) * 4096;
        let end_page = ((start.as_u64() + size as u64 + 4095) / 4096) * 4096;

        for addr in (start_page..end_page).step_by(4096) {
            let mut frame_allocator = self.frame_allocator.lock();
            let frame = frame_allocator.allocate_frame().expect("OOM during range mapping");
            let mut mapper = Mapper::new(pml4, &mut *frame_allocator, crate::memory::layout::PHYS_OFFSET);
            mapper.map_4k(VirtAddr::new(addr), frame, flags);
        }
    }

    /// Validate that a user-provided pointer is within canonical user address space.
    pub fn validate_user_ptr(&self, ptr: u64, size: u64) -> bool {
        let user_base = 0x0000_0000_0040_0000;
        let user_limit = 0x0000_7FFF_FFFF_FFFF;
        if ptr < user_base || (ptr + size) > user_limit {
            return false;
        }
        true
    }

    /// Expand the heap by allocating and mapping new pages (Kernel/Global).
    pub unsafe fn expand_heap(&self, current_end: VirtAddr, additional_size: usize) {
        self.map_range(
            current_end,
            additional_size,
            PageTableFlags::PRESENT | PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE
        );
    }
}

pub static MEMORY_MANAGER: Mutex<Option<MemoryManager>> = Mutex::new(None);

pub fn init(kernel_pml4: PhysAddr, frame_allocator: &'static Mutex<BitmapFrameAllocator>) {
    *MEMORY_MANAGER.lock() = Some(MemoryManager::new(kernel_pml4, frame_allocator));
}
