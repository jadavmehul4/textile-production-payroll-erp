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
        let pml4_virt = x86_64::VirtAddr::new(kernel_pml4_phys + memory::layout::PHYS_OFFSET);

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

    // 7. Initialize File System
    fs::init_fs();
    serial_println!("Wraith Core: VFS Initialized.");

    // 8. Test File System
    if let Some(mut file) = fs::vfs::open("/test.txt") {
        serial_println!("Wraith Core: File Opened successfully.");
        let mut buf = [0u8; 32];
        let bytes_read = fs::vfs::read(&mut file, &mut buf);
        if let Ok(s) = core::str::from_utf8(&buf[..bytes_read]) {
            println!("[FS] /test.txt: {}", s);
            serial_println!("Wraith Core: [FS] /test.txt content: {}", s);
        }
    } else {
        serial_println!("Wraith Core: [ERROR] Failed to open /test.txt");
    }

    // 9. Initialize Syscalls
    unsafe {
        user::syscall::init_syscall_stack();
        user::syscall::init_syscalls();
    }
    serial_println!("Wraith Core: Syscall Interface Initialized.");

    // 10. Initialize Timer and Scheduler
    unsafe {
        scheduler::timer::init();
    }
    serial_println!("Wraith Core: LAPIC Timer Initialized.");

    // 11. Load and execute User Process from ELF (Mock)
    let mock_elf: [u8; 120] = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ];

    process::process::spawn_elf_process(&mock_elf, x86_64::VirtAddr::new(0x800000));
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
