#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ElfError {
    InvalidMagic,
    UnsupportedClass,
    UnsupportedDataEncoding,
    UnsupportedMachine,
    CorruptedHeader,
    CorruptedProgramHeader,
    DynamicBinaryNotSupported,
    MemoryAllocationFailed,
    MappingFailed,
}

impl core::fmt::Display for ElfError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            Self::InvalidMagic => write!(f, "Invalid ELF Magic"),
            Self::UnsupportedClass => write!(f, "Only 64-bit ELF supported"),
            Self::UnsupportedDataEncoding => write!(f, "Only Little-Endian supported"),
            Self::UnsupportedMachine => write!(f, "Only x86_64 supported"),
            Self::CorruptedHeader => write!(f, "Corrupted ELF Header"),
            Self::CorruptedProgramHeader => write!(f, "Corrupted Program Header"),
            Self::DynamicBinaryNotSupported => write!(f, "Dynamic binaries not supported"),
            Self::MemoryAllocationFailed => write!(f, "Memory allocation failed"),
            Self::MappingFailed => write!(f, "Mapping failed"),
        }
    }
}
