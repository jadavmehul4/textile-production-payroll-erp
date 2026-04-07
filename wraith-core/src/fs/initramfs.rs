use crate::fs::vfs::FileSystem;
use crate::fs::inode::{Inode, FileType};
use crate::fs::file::File;

/// A simple, read-only in-memory filesystem (InitRamFs).
pub struct InitRamFs {
    /// List of file entries (path, content).
    pub files: &'static [(&'static str, &'static [u8])],
}

impl InitRamFs {
    pub const fn new(files: &'static [(&'static str, &'static [u8])]) -> Self {
        Self { files }
    }
}

impl FileSystem for InitRamFs {
    fn open(&self, path: &str) -> Option<File> {
        for (i, (file_path, content)) in self.files.iter().enumerate() {
            if *file_path == path {
                let inode = Inode::new(i as u64, FileType::File, content.len());
                return Some(File::new(inode));
            }
        }
        None
    }

    fn read(&self, file: &mut File, buf: &mut [u8]) -> usize {
        let (_path, content) = self.files[file.inode.id as usize];

        if file.offset >= content.len() {
            return 0;
        }

        let remaining = content.len() - file.offset;
        let to_read = core::cmp::min(remaining, buf.len());

        buf[..to_read].copy_from_slice(&content[file.offset..file.offset + to_read]);
        file.offset += to_read;

        to_read
    }
}
