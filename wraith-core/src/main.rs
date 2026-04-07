#![no_std]
#![no_main]
#![feature(abi_x86_interrupt)]
#![feature(naked_functions)]

use core::panic::PanicInfo;
use bootloader::{BootInfo, entry_point};

pub mod memory;
pub mod hardware;
pub mod security;
pub mod serial;
pub mod vga;
pub mod gdt;
pub mod interrupts;
pub mod user;

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
        let mut frame_allocator = memory::frame_allocator::BitmapFrameAllocator::init(
            &boot_info.memory_map
        );

        memory::paging::init(&mut frame_allocator, boot_offset);

        let pml4_phys: u64;
        core::arch::asm!("mov {}, cr3", out(reg) pml4_phys);
        let pml4_virt = x86_64::VirtAddr::new((pml4_phys & !0xFFF) + memory::layout::PHYS_OFFSET);

        static mut GLOBAL_FRAME_ALLOCATOR: Option<spin::Mutex<memory::frame_allocator::BitmapFrameAllocator>> = None;
        GLOBAL_FRAME_ALLOCATOR = Some(spin::Mutex::new(frame_allocator));

        memory::manager::init(pml4_virt, GLOBAL_FRAME_ALLOCATOR.as_ref().unwrap());
    }

    serial_println!("Wraith Core: Paging & HHDM Initialized.");

    // 5. Relocate drivers to High-Half regions
    unsafe {
        vga::relocate_to_mmio();
    }
    serial_println!("Wraith Core: Driver Relocation... OK");

    // 6. Initialize the global allocator
    unsafe {
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

    // 7. Initialize Syscalls
    unsafe {
        user::syscall::init_syscall_stack();
        user::syscall::init_syscalls();
    }
    serial_println!("Wraith Core: Syscall Interface Initialized.");

    println!("Wraith Core: System initialized successfully.");
    serial_println!("Wraith Core: Fully initialized.");

    // 8. Transition to User Mode
    serial_println!("Wraith Core: Transitioning to User Mode...");

    let user_code_virt = x86_64::VirtAddr::new(0x0000_0000_0040_0000);
    let user_stack_top = x86_64::VirtAddr::new(0x0000_7FFF_FFFF_F000);

    unsafe {
        if let Some(ref mm) = *memory::manager::MEMORY_MANAGER.lock() {
            // Map user code (1 page) and user stack (1 page)
            // Initially writable to allow copying the stub
            mm.map_user_range(user_code_virt, 4096, true);
            mm.map_user_range(user_stack_top - 4096u64, 4096, true);
        }

        // Prepare user code
        let mut final_code = [0u8; 64];
        let write_stub = [
            0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00, // mov rax, 1
            0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00, // mov rdi, 1
            0x48, 0x8d, 0x35, 0x0a, 0x00, 0x00, 0x00, // lea rsi, [rip+10]
            0x48, 0xc7, 0xc2, 0x09, 0x00, 0x00, 0x00, // mov rdx, 9
            0x0f, 0x05,                               // syscall
        ];
        let exit_stub = [
            0x48, 0xc7, 0xc0, 0x00, 0x00, 0x00, 0x00, // mov rax, 0
            0x48, 0x31, 0xff,                         // xor rdi, rdi
            0x0f, 0x05,                               // syscall
        ];
        let user_msg = b"User Mode";

        let mut offset = 0;
        core::ptr::copy_nonoverlapping(write_stub.as_ptr(), final_code.as_mut_ptr().add(offset), write_stub.len());
        offset += write_stub.len();
        core::ptr::copy_nonoverlapping(exit_stub.as_ptr(), final_code.as_mut_ptr().add(offset), exit_stub.len());
        offset += exit_stub.len();
        core::ptr::copy_nonoverlapping(user_msg.as_ptr(), final_code.as_mut_ptr().add(offset), user_msg.len());

        core::ptr::copy_nonoverlapping(final_code.as_ptr(), user_code_virt.as_mut_ptr(), final_code.len());

        // Protect user code (Remove writable)
        if let Some(ref mm) = *memory::manager::MEMORY_MANAGER.lock() {
            mm.set_permissions(user_code_virt,
                memory::paging::flags::PageTableFlags::PRESENT |
                memory::paging::flags::PageTableFlags::USER_ACCESSIBLE);
        }

        user::switch_to_user(user_code_virt, user_stack_top);
    }
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
