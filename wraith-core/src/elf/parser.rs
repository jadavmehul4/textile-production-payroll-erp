use crate::elf::types::*;
use crate::elf::error::ElfError;

pub struct ElfParser<'a> {
    pub data: &'a [u8],
}

impl<'a> ElfParser<'a> {
    pub fn new(data: &'a [u8]) -> Self {
        Self { data }
    }

    /// Validate the ELF header and return it if correct.
    pub fn parse_header(&self) -> Result<Elf64Header, ElfError> {
        if self.data.len() < core::mem::size_of::<Elf64Header>() {
            return Err(ElfError::CorruptedHeader);
        }

        let header = unsafe { *(self.data.as_ptr() as *const Elf64Header) };

        if header.e_ident[0..4] != ELF_MAGIC {
            return Err(ElfError::InvalidMagic);
        }
        if header.e_ident[4] != ELF_CLASS_64 {
            return Err(ElfError::UnsupportedClass);
        }
        if header.e_ident[5] != ELF_DATA_2LSB {
            return Err(ElfError::UnsupportedDataEncoding);
        }
        if header.e_machine != EM_X86_64 {
            return Err(ElfError::UnsupportedMachine);
        }

        Ok(header)
    }

    /// Extract program headers from the ELF data.
    pub fn program_headers(&self, header: &Elf64Header) -> Result<&[Elf64Phdr], ElfError> {
        let offset = header.e_phoff as usize;
        let num = header.e_phnum as usize;
        let size = header.e_phentsize as usize;

        if offset + (num * size) > self.data.len() {
            return Err(ElfError::CorruptedProgramHeader);
        }

        let ph_ptr = unsafe { self.data.as_ptr().add(offset) as *const Elf64Phdr };
        Ok(unsafe { core::slice::from_raw_parts(ph_ptr, num) })
    }
}
