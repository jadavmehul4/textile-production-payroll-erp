use alloc::vec::Vec;

/// Standard kernel IPC message.
/// Data is owned by the kernel during transit.
#[derive(Debug, Clone)]
pub struct Message {
    pub sender_pid: u64,
    pub data: Vec<u8>,
}

impl Message {
    pub const MAX_SIZE: usize = 256;

    pub fn new(sender_pid: u64, data: Vec<u8>) -> Self {
        Self { sender_pid, data }
    }
}
