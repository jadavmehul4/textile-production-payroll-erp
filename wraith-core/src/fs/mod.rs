pub mod inode;
pub mod file;
pub mod vfs;
pub mod initramfs;

use crate::fs::initramfs::InitRamFs;
use crate::fs::vfs::VFS;
use alloc::boxed::Box;

/// Initial static file list for InitRamFs.
static FILES: &[(&str, &[u8])] = &[
    ("/test.txt", b"Hello Wraith OS"),
];

/// Initialize the Virtual File System with an initial ramdisk.
pub fn init_fs() {
    let ramfs = InitRamFs::new(FILES);
    // Leak the RAMFS to satisfy 'static lifetime for dyn FileSystem
    let static_ramfs: &'static InitRamFs = Box::leak(Box::new(ramfs));
    *VFS.lock() = Some(static_ramfs);
}
