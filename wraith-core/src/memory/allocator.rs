use core::alloc::{GlobalAlloc, Layout};
use core::ptr;
use spin::Mutex;
use crate::memory::layout::HEAP_START;

/// A node in the free list.
struct FreeNode {
    size: usize,
    next: Option<&'static mut FreeNode>,
}

impl FreeNode {
    const fn new(size: usize) -> Self {
        Self { size, next: None }
    }

    fn start_addr(&self) -> usize {
        self as *const Self as usize
    }

    fn end_addr(&self) -> usize {
        self.start_addr() + self.size
    }
}

/// A flexible Linked List Allocator for kernel heap management.
pub struct LinkedListAllocator {
    head: FreeNode,
    current_end: usize,
}

impl LinkedListAllocator {
    pub const fn new() -> Self {
        Self {
            head: FreeNode::new(0),
            current_end: HEAP_START as usize,
        }
    }

    /// Initialize the allocator with a given range.
    pub unsafe fn init(&mut self, heap_start: usize, heap_size: usize) {
        self.add_free_region(heap_start, heap_size);
        self.current_end = heap_start + heap_size;
    }

    /// Add a free region to the allocator.
    unsafe fn add_free_region(&mut self, addr: usize, size: usize) {
        // Alignment checks
        let layout = Layout::from_size_align(size, core::mem::align_of::<FreeNode>()).unwrap();
        let (size, _) = Self::size_align(layout);

        let mut node = FreeNode::new(size);
        node.next = self.head.next.take();
        let node_ptr = addr as *mut FreeNode;
        node_ptr.write(node);
        self.head.next = Some(&mut *node_ptr);
    }

    /// Find a free region that fits the given size and alignment.
    fn find_region(&mut self, size: usize, align: usize) -> Option<(&'static mut FreeNode, usize)> {
        let mut current = &mut self.head;

        while let Some(ref mut next) = current.next {
            if let Ok(alloc_start) = Self::alloc_from_region(next, size, align) {
                let old_next = current.next.take().unwrap();
                current.next = old_next.next.take(); // Corrected move
                return Some((old_next, alloc_start));
            } else {
                current = current.next.as_mut().unwrap();
            }
        }
        None
    }

    /// Helper to calculate allocation start within a region.
    fn alloc_from_region(region: &FreeNode, size: usize, align: usize) -> Result<usize, ()> {
        let alloc_start = (region.start_addr() + align - 1) & !(align - 1);
        let alloc_end = alloc_start.checked_add(size).ok_or(())?;

        if alloc_end > region.end_addr() {
            return Err(());
        }

        let excess_size = region.end_addr() - alloc_end;
        if excess_size > 0 && excess_size < core::mem::size_of::<FreeNode>() {
            return Err(());
        }

        Ok(alloc_start)
    }

    /// Adjust the size and alignment of the given layout.
    fn size_align(layout: Layout) -> (usize, usize) {
        let layout = layout
            .align_to(core::mem::align_of::<FreeNode>())
            .expect("Alignment adjustment failed")
            .pad_to_align();
        let size = layout.size().max(core::mem::size_of::<FreeNode>());
        (size, layout.align())
    }
}

pub struct Locked<A> {
    inner: Mutex<A>,
}

impl<A> Locked<A> {
    pub const fn new(inner: A) -> Self {
        Self {
            inner: Mutex::new(inner),
        }
    }

    pub fn lock(&self) -> spin::MutexGuard<'_, A> {
        self.inner.lock()
    }
}

unsafe impl GlobalAlloc for Locked<LinkedListAllocator> {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let (size, align) = LinkedListAllocator::size_align(layout);
        let mut allocator = self.lock();

        if let Some((region, alloc_start)) = allocator.find_region(size, align) {
            let alloc_end = alloc_start + size;
            let excess_size = region.end_addr() - alloc_end;
            if excess_size > 0 {
                allocator.add_free_region(alloc_end, excess_size);
            }
            alloc_start as *mut u8
        } else {
            // Memory expansion logic
            if let Some(ref mm) = *crate::memory::manager::MEMORY_MANAGER.lock() {
                let expand_size = size.max(4096);
                let current_end = allocator.current_end;
                mm.expand_heap(x86_64::VirtAddr::new(current_end as u64), expand_size);
                allocator.current_end += expand_size;
                allocator.add_free_region(current_end, expand_size);

                // Retry allocation
                if let Some((region, alloc_start)) = allocator.find_region(size, align) {
                    let alloc_end = alloc_start + size;
                    let excess_size = region.end_addr() - alloc_end;
                    if excess_size > 0 {
                        allocator.add_free_region(alloc_end, excess_size);
                    }
                    return alloc_start as *mut u8;
                }
            }
            ptr::null_mut()
        }
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        let (size, _) = LinkedListAllocator::size_align(layout);
        self.lock().add_free_region(ptr as usize, size);
    }
}

#[global_allocator]
pub static ALLOCATOR: Locked<LinkedListAllocator> = Locked::new(LinkedListAllocator::new());
