use crate::fs::file::File;
use spin::Mutex;

/// Common interface for any filesystem implementation.
pub trait FileSystem: Send + Sync {
    /// Open a file by its path.
    fn open(&self, path: &str) -> Option<File>;
    /// Read data from an open file.
    fn read(&self, file: &mut File, buf: &mut [u8]) -> usize;
}

/// Global Virtual File System (VFS) orchestrator.
pub static VFS: Mutex<Option<&'static dyn FileSystem>> = Mutex::new(None);

/// High-level API to open a file.
pub fn open(path: &str) -> Option<File> {
    if let Some(fs) = *VFS.lock() {
        fs.open(path)
    } else {
        None
    }
}

/// High-level API to read from a file.
pub fn read(file: &mut File, buf: &mut [u8]) -> usize {
    if let Some(fs) = *VFS.lock() {
        fs.read(file, buf)
    } else {
        0
    }
}
