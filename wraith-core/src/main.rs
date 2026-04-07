#![no_std]
#![no_main]
#![feature(abi_x86_interrupt)]

use core::panic::PanicInfo;
use bootloader::{BootInfo, entry_point};

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

// Set the entry point via the bootloader macro
entry_point!(kernel_main);

/// Entry point of the Wraith Core system.
/// This function is called by the bootloader.
fn kernel_main(boot_info: &'static BootInfo) -> ! {
    // 1. Initialize Serial for early debug logging
    serial_println!("Wraith Core: Initializing Serial... OK");
    println!("Wraith Core: Booting up...");

    // 2. Initialize GDT and TSS
    gdt::init();
    serial_println!("Wraith Core: GDT/TSS Initialized.");

    // 3. Initialize IDT
    interrupts::init_idt();
    serial_println!("Wraith Core: IDT Initialized.");

    // 4. Initialize Paging and Physical Frame Allocator
    serial_println!("Wraith Core: Initializing Paging System...");

    // We use the bootloader-provided offset for bootstrapping our new page tables.
    let boot_offset = boot_info.physical_memory_offset;

    // Use a fixed address for the frame allocator bitmap within the identity-mapped 1MB
    // 0x90000 (around 576KB) is generally safe in standard x86 BIOS memory maps
    let bitmap_base = 0x90000 as *mut u8;

    unsafe {
        let mut frame_allocator = memory::frame_allocator::BitmapFrameAllocator::init(
            &boot_info.memory_map,
            bitmap_base
        );
        // Initialize our new 4-level paging with HHDM
        memory::paging::init(&mut frame_allocator, boot_offset);
    }

    serial_println!("Wraith Core: Paging & HHDM Initialized.");

    // 5. Initialize the global allocator with the secure heap region
    unsafe {
        let start = core::ptr::addr_of!(_secure_heap_start) as usize;
        let end = core::ptr::addr_of!(_secure_heap_end) as usize;
        let size = end - start;
        memory::allocator::ALLOCATOR.lock().init(start, size);
    }
    serial_println!("Wraith Core: Memory Allocator Initialized.");

    println!("Wraith Core: System initialized successfully.");
    serial_println!("Wraith Core: Fully initialized.");

    // 6. Verification: Access HHDM address
    let hhdm_vga_ptr = (0xb8000 + memory::paging::mapper::PHYS_OFFSET) as *mut u16;
    unsafe {
        *hhdm_vga_ptr = 0x0f41; // 'A' with White-on-Black at (0,0) in HHDM
    }
    serial_println!("Wraith Core: HHDM Access Verification Successful.");

    // 7. Verification: Run a stealth check (Instruction Overlapping and MMU check)
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

    if let Some(location) = info.location() {
        serial_println!("Panic at {}:{}", location.file(), location.line());
        println!("Panic at {}:{}", location.file(), location.line());
    }

    // Halt the CPU
    loop {
        x86_64::instructions::hlt();
    }
}
