/// Type of file in the filesystem.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FileType {
    File,
    Directory,
}

/// Metadata for a file or directory.
#[derive(Debug, Clone, Copy)]
pub struct Inode {
    pub id: u64,
    pub file_type: FileType,
    pub size: usize,
}

impl Inode {
    pub const fn new(id: u64, file_type: FileType, size: usize) -> Self {
        Self { id, file_type, size }
    }
}
