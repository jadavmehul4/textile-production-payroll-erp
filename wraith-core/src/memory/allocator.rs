use core::alloc::{GlobalAlloc, Layout};
use core::ptr;

/// Memory region tags for secure allocation.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MemoryTag {
    SECURE,   // High-security sensitive data (XORed, MMU protected)
    VOLATILE, // Standard heap
    SHIELDED, // Dedicated Hardware Shield state
}

/// A simple bump allocator for bare-metal use.
pub struct BumpAllocator {
    heap_start: usize,
    heap_end: usize,
    next: usize,
    allocations: usize,
}

impl BumpAllocator {
    pub const fn new() -> Self {
        BumpAllocator {
            heap_start: 0,
            heap_end: 0,
            next: 0,
            allocations: 0,
        }
    }

    pub unsafe fn init(&mut self, heap_start: usize, heap_size: usize) {
        self.heap_start = heap_start;
        self.heap_end = heap_start + heap_size;
        self.next = heap_start;
    }
}

pub struct Locked<A> {
    inner: spin::Mutex<A>,
}

impl<A> Locked<A> {
    pub const fn new(inner: A) -> Self {
        Locked {
            inner: spin::Mutex::new(inner),
        }
    }

    pub fn lock(&self) -> spin::MutexGuard<'_, A> {
        self.inner.lock()
    }
}

unsafe impl GlobalAlloc for Locked<BumpAllocator> {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let mut bump = self.lock();

        let alloc_start = (bump.next + layout.align() - 1) & !(layout.align() - 1);
        let alloc_end = match alloc_start.checked_add(layout.size()) {
            Some(end) => end,
            None => return ptr::null_mut(),
        };

        if alloc_end > bump.heap_end {
            ptr::null_mut()
        } else {
            bump.next = alloc_end;
            bump.allocations += 1;
            alloc_start as *mut u8
        }
    }

    unsafe fn dealloc(&self, _ptr: *mut u8, _layout: Layout) {
        let mut bump = self.lock();
        if bump.allocations > 0 {
            bump.allocations -= 1;
        }
        if bump.allocations == 0 {
            bump.next = bump.heap_start;
        }
    }
}

#[global_allocator]
pub static ALLOCATOR: Locked<BumpAllocator> = Locked::new(BumpAllocator::new());
