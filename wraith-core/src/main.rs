#![no_std]
#![no_main]

use core::panic::PanicInfo;

pub mod memory;
pub mod hardware;
pub mod security;

// Import linker symbols for allocator initialization
extern "C" {
    static _secure_heap_start: usize;
    static _secure_heap_end: usize;
}

/// Entry point of the Wraith Core system.
/// This function is called by the bootloader.
#[no_mangle]
pub extern "C" fn _start() -> ! {
    // Initialize the global allocator with the secure heap region
    unsafe {
        let start = &_secure_heap_start as *const usize as usize;
        let end = &_secure_heap_end as *const usize as usize;
        let size = end - start;
        memory::allocator::ALLOCATOR.lock().init(start, size);
    }

    loop {}
}

/// Custom panic handler for bare-metal environment.
#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}
