use x86_64::VirtAddr;
use spin::Mutex;
use crate::memory::frame_allocator::BitmapFrameAllocator;
use crate::memory::paging::mapper::Mapper;
use crate::memory::paging::flags::PageTableFlags;

/// MemoryManager acts as the primary orchestrator between the Frame Allocator and Mapper.
/// It ensures clean abstractions for memory allocation, mapping, and permission updates.
pub struct MemoryManager {
    frame_allocator: &'static Mutex<BitmapFrameAllocator>,
    // The current PML4 used by the kernel, accessed via HHDM
    pml4: VirtAddr,
}

impl MemoryManager {
    pub const fn new(pml4: VirtAddr, frame_allocator: &'static Mutex<BitmapFrameAllocator>) -> Self {
        Self { pml4, frame_allocator }
    }

    /// Allocate physical frames and map them to a virtual range.
    pub unsafe fn map_range(&self, start: VirtAddr, size: usize, flags: PageTableFlags) {
        let mut frame_allocator_guard = self.frame_allocator.lock();
        let pml4 = &mut *self.pml4.as_mut_ptr::<crate::memory::paging::page_table::PageTable>();

        let start_page = (start.as_u64() / 4096) * 4096;
        let end_page = ((start.as_u64() + size as u64 + 4095) / 4096) * 4096;

        for addr in (start_page..end_page).step_by(4096) {
            // We need to re-borrow frame_allocator inside the loop or use a more complex mapper setup
            // For simplicity in the orchestrator, we allocate first, then map.
            let frame = frame_allocator_guard.allocate_frame().expect("OOM during range mapping");
            let mut mapper = Mapper::new(pml4, &mut *frame_allocator_guard, crate::memory::layout::PHYS_OFFSET);
            mapper.map_4k(VirtAddr::new(addr), frame, flags);
        }
    }

    /// Update permissions for an existing virtual page.
    pub unsafe fn set_permissions(&self, virt: VirtAddr, flags: PageTableFlags) {
        let mut frame_allocator_guard = self.frame_allocator.lock();
        let pml4 = &mut *self.pml4.as_mut_ptr::<crate::memory::paging::page_table::PageTable>();
        let mut mapper = Mapper::new(pml4, &mut *frame_allocator_guard, crate::memory::layout::PHYS_OFFSET);

        mapper.update_flags(virt, flags);
    }

    /// Expand the heap by allocating and mapping new pages.
    pub unsafe fn expand_heap(&self, current_end: VirtAddr, additional_size: usize) {
        self.map_range(
            current_end,
            additional_size,
            PageTableFlags::PRESENT | PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE
        );
    }
}

pub static MEMORY_MANAGER: Mutex<Option<MemoryManager>> = Mutex::new(None);

pub fn init(pml4: VirtAddr, frame_allocator: &'static Mutex<BitmapFrameAllocator>) {
    *MEMORY_MANAGER.lock() = Some(MemoryManager::new(pml4, frame_allocator));
}
