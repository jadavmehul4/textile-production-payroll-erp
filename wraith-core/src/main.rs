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
pub mod scheduler;
pub mod process;

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
    // 1. Initialize Serial and VGA
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

    // 5. Relocate drivers
    unsafe {
        vga::relocate_to_mmio();
    }

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

    // 8. Initialize Timer and Scheduler
    unsafe {
        scheduler::timer::init();
    }
    serial_println!("Wraith Core: LAPIC Timer Initialized.");

    // 9. Create Tasks
    let user_code_virt = x86_64::VirtAddr::new(0x0000_0000_0040_0000);
    let user_stack_a_top = x86_64::VirtAddr::new(0x0000_7FFF_FFFF_F000);
    let user_stack_b_top = x86_64::VirtAddr::new(0x0000_7FFF_FFF0_F000);

    unsafe {
        if let Some(ref mm) = *memory::manager::MEMORY_MANAGER.lock() {
            mm.map_user_range(user_code_virt, 4096, true);
            mm.map_user_range(user_stack_a_top - 4096u64, 4096, true);
            mm.map_user_range(user_stack_b_top - 4096u64, 4096, true);
        }

        // Prepare User Task A & B
        // Blob: sys_write(1, "Task A/B", 6), sys_yield(), jmp back
        let mut code_blob = [0u8; 128];
        let task_logic = [
            0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00, // mov rax, 1 (write)
            0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00, // mov rdi, 1
            0x48, 0x8d, 0x35, 0x0c, 0x00, 0x00, 0x00, // lea rsi, [rip+12]
            0x48, 0xc7, 0xc2, 0x06, 0x00, 0x00, 0x00, // mov rdx, 6
            0x0f, 0x05,                               // syscall
            0x48, 0xc7, 0xc0, 0x02, 0x00, 0x00, 0x00, // mov rax, 2 (yield)
            0x0f, 0x05,                               // syscall
            0xeb, 0xd9                                // jmp back
        ];
        // Logic length = 32
        core::ptr::copy_nonoverlapping(task_logic.as_ptr(), code_blob.as_mut_ptr(), task_logic.len());
        core::ptr::copy_nonoverlapping(b"Task A".as_ptr(), code_blob.as_mut_ptr().add(task_logic.len()), 6);
        core::ptr::copy_nonoverlapping(b"Task B".as_ptr(), code_blob.as_mut_ptr().add(task_logic.len() + 16), 6);

        core::ptr::copy_nonoverlapping(code_blob.as_ptr(), user_code_virt.as_mut_ptr(), 128);

        // Task A Entry
        process::process::spawn_user_task(user_code_virt, user_stack_a_top, x86_64::VirtAddr::new(0x800000));
        // Task B Entry (same code, offset for name)
        process::process::spawn_user_task(user_code_virt, user_stack_b_top, x86_64::VirtAddr::new(0x880000));

        process::process::spawn_idle_task(x86_64::VirtAddr::new(0x900000));
    }

    println!("Wraith Core: Preemptive Scheduler active.");
    serial_println!("Wraith Core: System fully initialized.");

    // Enable Interrupts and trigger first schedule
    x86_64::instructions::interrupts::enable();
    scheduler::set_reschedule_flag();

    loop {
        scheduler::schedule();
        x86_64::instructions::hlt();
    }
}

extern crate alloc;

/// Custom panic handler for bare-metal environment.
/// Implements the "Wraith Screen of Death".
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    serial_println!("\n!!! KERNEL PANIC !!!");
    serial_println!("{}", info);

    vga::set_panic_color();
    println!("--- WRAITH CORE KERNEL PANIC ---");
    println!("\n{}", info);

    if let Some(location) = info.location() {
        serial_println!("Panic at {}:{}", location.file(), location.line());
        println!("Panic at {}:{}", location.file(), location.line());
    }

    loop {
        x86_64::instructions::hlt();
    }
}
