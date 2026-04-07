/// Trait for providing hardware entropy.
pub trait EntropyProvider {
    fn get_u64(&self) -> Option<u64>;
}

/// x86_64 RDRAND implementation.
pub struct RdrandProvider;

impl EntropyProvider for RdrandProvider {
    fn get_u64(&self) -> Option<u64> {
        let mut val: u64 = 0;
        let mut success: u8;
        unsafe {
            // Using inline assembly for RDRAND with success check (Carry Flag)
            core::arch::asm!(
                "rdrand {0}",
                "setc {1}",
                out(reg) val,
                out(reg_byte) success,
            );
        }
        if success == 1 {
            Some(val)
        } else {
            None
        }
    }
}
