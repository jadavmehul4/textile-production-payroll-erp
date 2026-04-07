#![no_std]
#![no_main]
#![feature(abi_x86_interrupt)]

use core::panic::PanicInfo;

pub mod memory;
pub mod hardware;
pub mod security;
pub mod serial;
pub mod vga;
pub mod gdt;
pub mod interrupts;

// Import linker symbols for allocator initialization
extern "C" {
    static _secure_heap_start: usize;
    static _secure_heap_end: usize;
}

/// Entry point of the Wraith Core system.
/// This function is called by the bootloader.
#[no_mangle]
pub extern "C" fn _start() -> ! {
    // 1. Initialize Serial for early debug logging
    // Already initialized in lazy_static

    serial_println!("Wraith Core: Initializing Serial... OK");
    println!("Wraith Core: Booting up...");

    // 2. Initialize GDT and TSS
    gdt::init();
    serial_println!("Wraith Core: GDT/TSS Initialized.");

    // 3. Initialize IDT
    interrupts::init_idt();
    serial_println!("Wraith Core: IDT Initialized.");

    // 4. Initialize the global allocator with the secure heap region
    unsafe {
        let start = core::ptr::addr_of!(_secure_heap_start) as usize;
        let end = core::ptr::addr_of!(_secure_heap_end) as usize;
        let size = end - start;
        memory::allocator::ALLOCATOR.lock().init(start, size);
    }
    serial_println!("Wraith Core: Memory Allocator Initialized.");

    println!("Wraith Core: System initialized successfully.");
    serial_println!("Wraith Core: Fully initialized.");

    // 5. Run a stealth check (Instruction Overlapping and MMU check)
    serial_println!("Wraith Core: Verifying Stealth Engine...");
    let cr3 = security::stealth::StealthEngine::monitor_mmu();
    serial_println!("Wraith Core: CR3 State: 0x{:x}", cr3);

    // Trigger a test breakpoint exception to verify IDT
    serial_println!("Wraith Core: Testing Breakpoint...");
    x86_64::instructions::interrupts::int3();
    serial_println!("Wraith Core: Breakpoint Test Completed.");

    loop {}
}

/// Custom panic handler for bare-metal environment.
/// Implements the "Wraith Screen of Death".
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    // Log to serial first for reliability
    serial_println!("\n!!! KERNEL PANIC !!!");
    serial_println!("{}", info);

    // Visual feedback on VGA
    vga::set_panic_color();
    println!("--- WRAITH CORE KERNEL PANIC ---");
    println!("\n{}", info);

    // Register dump logic would ideally go here, but requires an InterruptStackFrame.
    // In a generic panic, we capture the instruction pointer from the PanicInfo if possible.
    if let Some(location) = info.location() {
        serial_println!("Panic at {}:{}", location.file(), location.line());
        println!("Panic at {}:{}", location.file(), location.line());
    }

    // Halt the CPU
    loop {
        x86_64::instructions::hlt();
    }
}
