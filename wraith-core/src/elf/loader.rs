use crate::elf::types::*;
use crate::elf::error::ElfError;
use crate::elf::parser::ElfParser;
use crate::memory::manager::MEMORY_MANAGER;
use crate::memory::paging::flags::PageTableFlags;
use crate::process::memory_space::MemorySpace;
use x86_64::{VirtAddr, PhysAddr};

pub struct ElfLoader<'a> {
    parser: ElfParser<'a>,
}

impl<'a> ElfLoader<'a> {
    pub fn new(data: &'a [u8]) -> Self {
        Self {
            parser: ElfParser::new(data),
        }
    }

    /// Load the ELF into a new memory space.
    pub unsafe fn load(&self) -> Result<(MemorySpace, u64), ElfError> {
        let header = self.parser.parse_header()?;
        let phs = self.parser.program_headers(&header)?;

        let mut mm_lock = MEMORY_MANAGER.lock();
        let mm = mm_lock.as_mut().ok_or(ElfError::MappingFailed)?;

        // 1. Create a fresh address space
        let mut space = mm.create_user_address_space();

        for ph in phs {
            match ph.p_type {
                PT_LOAD => {
                    self.load_segment(mm, &mut space, ph)?;
                }
                PT_DYNAMIC => return Err(ElfError::DynamicBinaryNotSupported),
                _ => {}
            }
        }

        Ok((space, header.e_entry))
    }

    /// Map a loadable segment and copy its data.
    unsafe fn load_segment(&self, mm: &crate::memory::manager::MemoryManager, space: &mut MemorySpace, ph: &Elf64Phdr) -> Result<(), ElfError> {
        let virt_start = VirtAddr::new(ph.p_vaddr);
        let mem_size = ph.p_memsz as usize;
        let file_size = ph.p_filesz as usize;

        // Map the region with appropriate permissions
        let mut flags = PageTableFlags::empty();
        if ph.p_flags & PF_R != 0 { flags |= PageTableFlags::PRESENT; }
        if ph.p_flags & PF_W != 0 { flags |= PageTableFlags::WRITABLE; }
        if ph.p_flags & PF_X == 0 { flags |= PageTableFlags::NO_EXECUTE; }

        // We map it as WRITABLE initially to allow the kernel to copy the data
        let phys_start = mm.map_user_region_get_phys(space, virt_start, mem_size, PageTableFlags::WRITABLE);

        // Copy segment data from ELF image using HHDM to access physical frames
        let segment_data = &self.parser.data[ph.p_offset as usize..(ph.p_offset as usize + file_size)];
        let dest_ptr = crate::memory::paging::mapper::phys_to_virt_with_offset(phys_start, crate::memory::layout::PHYS_OFFSET).as_mut_ptr::<u8>();

        core::ptr::copy_nonoverlapping(segment_data.as_ptr(), dest_ptr, file_size);

        // Zero the BSS region
        if mem_size > file_size {
            core::ptr::write_bytes(dest_ptr.add(file_size), 0, mem_size - file_size);
        }

        // Apply final permissions
        mm.set_permissions_in_space(space, virt_start, mem_size, flags | PageTableFlags::USER_ACCESSIBLE);

        Ok(())
    }
}

/// Helper extension for MemoryManager to handle isolated space updates.
impl crate::memory::manager::MemoryManager {
    pub unsafe fn set_permissions_in_space(&self, space: &mut MemorySpace, start: VirtAddr, size: usize, flags: PageTableFlags) {
        let pml4_virt = crate::memory::paging::mapper::phys_to_virt_with_offset(space.pml4_phys, crate::memory::layout::PHYS_OFFSET);
        let pml4 = &mut *pml4_virt.as_mut_ptr::<crate::memory::paging::page_table::PageTable>();
        let mut frame_allocator = self.frame_allocator.lock();
        let mut mapper = crate::memory::paging::mapper::Mapper::new(pml4, &mut *frame_allocator, crate::memory::layout::PHYS_OFFSET);

        let start_page = (start.as_u64() / 4096) * 4096;
        let end_page = ((start.as_u64() + size as u64 + 4095) / 4096) * 4096;

        for addr in (start_page..end_page).step_by(4096) {
            mapper.update_flags(VirtAddr::new(addr), flags);
        }
    }

    pub unsafe fn map_user_region_get_phys(&self, space: &mut MemorySpace, start: VirtAddr, size: usize, flags: PageTableFlags) -> PhysAddr {
        let pml4_virt = crate::memory::paging::mapper::phys_to_virt_with_offset(space.pml4_phys, crate::memory::layout::PHYS_OFFSET);
        let pml4 = &mut *pml4_virt.as_mut_ptr::<crate::memory::paging::page_table::PageTable>();

        let start_page = (start.as_u64() / 4096) * 4096;
        let end_page = ((start.as_u64() + size as u64 + 4095) / 4096) * 4096;
        let user_flags = flags | PageTableFlags::USER_ACCESSIBLE | PageTableFlags::PRESENT;

        let mut frame_allocator_guard = self.frame_allocator.lock();
        let mut first_phys = None;

        for addr in (start_page..end_page).step_by(4096) {
            let frame = frame_allocator_guard.allocate_frame().expect("OOM during user mapping");
            if first_phys.is_none() { first_phys = Some(frame); }
            let mut mapper = crate::memory::paging::mapper::Mapper::new(pml4, &mut *frame_allocator_guard, crate::memory::layout::PHYS_OFFSET);
            mapper.map_4k(VirtAddr::new(addr), frame, user_flags);
        }

        space.add_region(start, size, user_flags);
        first_phys.unwrap()
    }
}
