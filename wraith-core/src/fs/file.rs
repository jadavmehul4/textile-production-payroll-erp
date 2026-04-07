use crate::fs::inode::Inode;

/// A stateful file handle representing an open file.
pub struct File {
    pub inode: Inode,
    pub offset: usize,
}

impl File {
    pub fn new(inode: Inode) -> Self {
        Self {
            inode,
            offset: 0,
        }
    }

    /// Read data from the file starting at the current offset.
    /// Actual reading logic is handled by the VFS implementation.
    pub fn read(&mut self, _buf: &mut [u8]) -> usize {
        0
    }

    /// Move the file offset.
    pub fn seek(&mut self, new_offset: usize) {
        if new_offset <= self.inode.size {
            self.offset = new_offset;
        }
    }

    /// Close the file handle.
    pub fn close(self) {
    }
}
