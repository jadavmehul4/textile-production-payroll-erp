use bootloader::bootinfo::{MemoryMap, MemoryRegionType};
use x86_64::PhysAddr;

/// A physical frame allocator that uses a bitmap to track memory status.
pub struct BitmapFrameAllocator {
    memory_map: &'static MemoryMap,
    bitmap_base: *mut u8,
    total_frames: usize,
    next_free_frame: usize,
}

unsafe impl Send for BitmapFrameAllocator {}

impl BitmapFrameAllocator {
    /// Initialize a new bitmap-based frame allocator.
    /// This requires a pointer to a pre-allocated bitmap region in memory.
    pub unsafe fn init(memory_map: &'static MemoryMap, bitmap_base: *mut u8) -> Self {
        let total_memory: u64 = memory_map.iter()
            .map(|r| r.range.end_addr())
            .max()
            .unwrap_or(0);

        let total_frames = (total_memory / 4096) as usize;

        // Zero the bitmap (assuming it's in a safe, mapped region)
        let bitmap_size = (total_frames + 7) / 8;
        core::ptr::write_bytes(bitmap_base, 0, bitmap_size);

        let mut allocator = Self {
            memory_map,
            bitmap_base,
            total_frames,
            next_free_frame: 0,
        };

        // Mark all unusable memory as used in the bitmap
        allocator.mark_unusable_regions();

        allocator
    }

    fn mark_unusable_regions(&mut self) {
        for region in self.memory_map.iter() {
            if region.region_type != MemoryRegionType::Usable {
                let start = (region.range.start_addr() / 4096) as usize;
                let end = ((region.range.end_addr() + 4095) / 4096) as usize; // Align up
                for i in start..end {
                    self.set_bit(i, true);
                }
            }
        }
    }

    fn set_bit(&mut self, frame_idx: usize, value: bool) {
        if frame_idx >= self.total_frames { return; }
        let byte_idx = frame_idx / 8;
        let bit_idx = frame_idx % 8;
        unsafe {
            let byte_ptr = self.bitmap_base.add(byte_idx);
            let byte = core::ptr::read(byte_ptr);
            if value {
                core::ptr::write(byte_ptr, byte | (1 << bit_idx));
            } else {
                core::ptr::write(byte_ptr, byte & !(1 << bit_idx));
            }
        }
    }

    fn get_bit(&self, frame_idx: usize) -> bool {
        if frame_idx >= self.total_frames { return true; }
        let byte_idx = frame_idx / 8;
        let bit_idx = frame_idx % 8;
        unsafe {
            let byte = core::ptr::read(self.bitmap_base.add(byte_idx));
            (byte & (1 << bit_idx)) != 0
        }
    }

    /// Allocate a physical frame.
    pub fn allocate_frame(&mut self) -> Option<PhysAddr> {
        let start_search = self.next_free_frame;
        for i in start_search..self.total_frames {
            if !self.get_bit(i) {
                self.set_bit(i, true);
                self.next_free_frame = i + 1;
                return Some(PhysAddr::new((i as u64) * 4096));
            }
        }

        // Wrap around search
        for i in 0..start_search {
            if !self.get_bit(i) {
                self.set_bit(i, true);
                self.next_free_frame = i + 1;
                return Some(PhysAddr::new((i as u64) * 4096));
            }
        }

        None
    }

    /// Deallocate a physical frame.
    pub fn deallocate_frame(&mut self, addr: PhysAddr) {
        let frame_idx = (addr.as_u64() / 4096) as usize;
        self.set_bit(frame_idx, false);
        if frame_idx < self.next_free_frame {
            self.next_free_frame = frame_idx;
        }
    }
}
