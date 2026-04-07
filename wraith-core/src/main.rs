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
pub mod elf;
pub mod fs;
pub mod ipc;

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

    let mut kernel_pml4_phys: u64;
    unsafe {
        let mut frame_allocator = memory::frame_allocator::BitmapFrameAllocator::init(
            &boot_info.memory_map
        );

        memory::paging::init(&mut frame_allocator, boot_offset);

        core::arch::asm!("mov {}, cr3", out(reg) kernel_pml4_phys);
        kernel_pml4_phys &= !0xFFF;

        static mut GLOBAL_FRAME_ALLOCATOR: Option<spin::Mutex<memory::frame_allocator::BitmapFrameAllocator>> = None;
        GLOBAL_FRAME_ALLOCATOR = Some(spin::Mutex::new(frame_allocator));

        memory::manager::init(x86_64::PhysAddr::new(kernel_pml4_phys), GLOBAL_FRAME_ALLOCATOR.as_ref().unwrap());
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

    // 7. Initialize File System and IPC
    fs::init_fs();
    ipc::init_ipc();
    serial_println!("Wraith Core: VFS & IPC Initialized.");

    // 8. Initialize Syscalls
    unsafe {
        user::syscall::init_syscall_stack();
        user::syscall::init_syscalls();
    }
    serial_println!("Wraith Core: Syscall Interface Initialized.");

    // 9. Initialize Timer and Scheduler
    unsafe {
        scheduler::timer::init();
    }
    serial_println!("Wraith Core: LAPIC Timer Initialized.");

    // 10. Create Isolated Tasks (A sends to B)
    let user_code_a = x86_64::VirtAddr::new(0x0000_0000_0040_0000);
    let user_stack_a_top = x86_64::VirtAddr::new(0x0000_7FFF_FFFF_F000);
    let user_code_b = x86_64::VirtAddr::new(0x0000_0000_0040_0000);
    let user_stack_b_top = x86_64::VirtAddr::new(0x0000_7FFF_FFFF_F000);

    // Assembly for Task A: sys_send(2, "MsgA", 4), sys_exit(0)
    let logic_a = [
        0x48, 0xc7, 0xc0, 0x05, 0x00, 0x00, 0x00, // mov rax, 5 (send)
        0x48, 0xc7, 0xc7, 0x02, 0x00, 0x00, 0x00, // mov rdi, 2 (target PID)
        0x48, 0x8d, 0x35, 0x0a, 0x00, 0x00, 0x00, // lea rsi, [rip+10]
        0x48, 0xc7, 0xc2, 0x04, 0x00, 0x00, 0x00, // mov rdx, 4
        0x0f, 0x05,                               // syscall
        0x48, 0xc7, 0xc0, 0x00, 0x00, 0x00, 0x00, // mov rax, 0 (exit)
        0x0f, 0x05,                               // syscall
    ];
    let mut code_a = [0u8; 64];
    unsafe {
        core::ptr::copy_nonoverlapping(logic_a.as_ptr(), code_a.as_mut_ptr(), logic_a.len());
        core::ptr::copy_nonoverlapping(b"MsgA".as_ptr(), code_a.as_mut_ptr().add(logic_a.len()), 4);
    }

    // Assembly for Task B: sys_receive(buf, 64), sys_write(1, buf, len), sys_exit(0)
    let logic_b = [
        0x48, 0xc7, 0xc0, 0x06, 0x00, 0x00, 0x00, // mov rax, 6 (receive)
        0x48, 0x8d, 0x3d, 0x40, 0x00, 0x00, 0x00, // lea rdi, [rip+64] (buffer)
        0x48, 0xc7, 0xc2, 0x40, 0x00, 0x00, 0x00, // mov rdx, 64
        0x0f, 0x05,                               // syscall
        0x48, 0x89, 0xc2,                         // mov rdx, rax (len)
        0x48, 0xc7, 0xc0, 0x01, 0x00, 0x00, 0x00, // mov rax, 1 (write)
        0x48, 0xc7, 0xc7, 0x01, 0x00, 0x00, 0x00, // mov rdi, 1 (fd)
        0x48, 0x8d, 0x35, 0x2e, 0x00, 0x00, 0x00, // lea rsi, [rip+46] (buffer)
        0x0f, 0x05,                               // syscall
        0x48, 0xc7, 0xc0, 0x00, 0x00, 0x00, 0x00, // mov rax, 0 (exit)
        0x0f, 0x05,                               // syscall
    ];
    let mut code_b = [0u8; 128];
    unsafe {
        core::ptr::copy_nonoverlapping(logic_b.as_ptr(), code_b.as_mut_ptr(), logic_b.len());
    }

    process::process::spawn_user_task(user_code_a, user_stack_a_top, x86_64::VirtAddr::new(0x800000), &code_a);
    process::process::spawn_user_task(user_code_b, user_stack_b_top, x86_64::VirtAddr::new(0x880000), &code_b);
    process::process::spawn_idle_task(x86_64::VirtAddr::new(0x900000), x86_64::PhysAddr::new(kernel_pml4_phys));

    println!("Wraith Core: System fully initialized.");

    x86_64::instructions::interrupts::enable();
    scheduler::set_reschedule_flag();

    loop {
        scheduler::schedule();
        x86_64::instructions::hlt();
    }
}

extern crate alloc;

/// Custom panic handler for bare-metal environment.
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
