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
    /// This identifies a suitable hole for the bitmap dynamically.
    pub unsafe fn init(memory_map: &'static MemoryMap) -> Self {
        let total_memory: u64 = memory_map.iter()
            .map(|r| r.range.end_addr())
            .max()
            .unwrap_or(0);

        let total_frames = (total_memory / 4096) as usize;
        let bitmap_size = (total_frames + 7) / 8;

        // Find a usable region to place the bitmap (below the kernel or elsewhere safe)
        let bitmap_base = Self::find_bitmap_hole(memory_map, bitmap_size)
            .expect("Could not find a safe memory region for frame allocator bitmap");

        // Zero the bitmap
        core::ptr::write_bytes(bitmap_base, 0, bitmap_size);

        let mut allocator = Self {
            memory_map,
            bitmap_base,
            total_frames,
            next_free_frame: 0,
        };

        // Mark all unusable memory as used in the bitmap
        allocator.mark_unusable_regions();

        // Mark the bitmap region itself as used
        let bitmap_start_idx = (bitmap_base as usize / 4096);
        let bitmap_end_idx = ((bitmap_base as usize + bitmap_size + 4095) / 4096);
        for i in bitmap_start_idx..bitmap_end_idx {
            allocator.set_bit(i, true);
        }

        allocator
    }

    /// Find a hole in physical memory that is large enough for the bitmap.
    /// Avoids 0x0..0x100000 (BIOS/VGA) and kernel region.
    fn find_bitmap_hole(memory_map: &MemoryMap, size: usize) -> Option<*mut u8> {
        for region in memory_map.iter() {
            if region.region_type == MemoryRegionType::Usable {
                let start = region.range.start_addr();
                let end = region.range.end_addr();

                // Skip low memory (first 1MB)
                let search_start = start.max(0x100000);

                // Also ensure we don't overlap the kernel (assume kernel is < 8MB for now)
                // In a production kernel, we would use linker symbols to find kernel physical range.
                let search_start = search_start.max(0x800000);

                if end > search_start && (end - search_start) >= size as u64 {
                    return Some(search_start as *mut u8);
                }
            }
        }
        None
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
