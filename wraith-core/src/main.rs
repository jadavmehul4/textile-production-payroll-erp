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

    let boot_offset = boot_info.physical_memory_offset;

    unsafe {
        // Dynamic bitmap hole discovery enabled
        let mut frame_allocator = memory::frame_allocator::BitmapFrameAllocator::init(
            &boot_info.memory_map
        );

        // Initialize our new 4-level paging with HHDM, High-Half Kernel, and W^X enforcement
        memory::paging::init(&mut frame_allocator, boot_offset);

        // Use the newly established HHDM VirtAddr for the PML4 in MemoryManager
        let pml4_phys: u64;
        core::arch::asm!("mov {}, cr3", out(reg) pml4_phys);
        let pml4_virt = x86_64::VirtAddr::new((pml4_phys & !0xFFF) + memory::layout::PHYS_OFFSET);

        // Initialize MemoryManager with the static frame allocator
        static mut GLOBAL_FRAME_ALLOCATOR: Option<spin::Mutex<memory::frame_allocator::BitmapFrameAllocator>> = None;
        GLOBAL_FRAME_ALLOCATOR = Some(spin::Mutex::new(frame_allocator));

        memory::manager::init(pml4_virt, GLOBAL_FRAME_ALLOCATOR.as_ref().unwrap());
    }

    serial_println!("Wraith Core: Paging & HHDM Initialized.");

    // 5. Initialize the global allocator with the initial heap range
    unsafe {
        // Map initial heap range
        if let Some(ref mm) = *memory::manager::MEMORY_MANAGER.lock() {
            mm.expand_heap(
                x86_64::VirtAddr::new(memory::layout::HEAP_START),
                memory::layout::HEAP_INITIAL_SIZE
            );
        }

        memory::allocator::ALLOCATOR.lock().init(
            memory::layout::HEAP_START as usize,
            memory::layout::HEAP_INITIAL_SIZE
        );
    }
    serial_println!("Wraith Core: Heap Allocator Initialized.");

    println!("Wraith Core: System initialized successfully.");
    serial_println!("Wraith Core: Fully initialized.");

    // 6. Verification: Dynamic Allocation
    let test_box = alloc::boxed::Box::new(42u64);
    serial_println!("Wraith Core: Dynamic Allocation Successful (Value: {} at {:p})", *test_box, test_box);

    // Trigger a test breakpoint exception to verify IDT
    serial_println!("Wraith Core: Testing Breakpoint...");
    x86_64::instructions::interrupts::int3();
    serial_println!("Wraith Core: Breakpoint Test Completed.");

    loop {}
}

extern crate alloc;

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
