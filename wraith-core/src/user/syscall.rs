use crate::{serial_println, println};
use crate::user::context::ProcessContext;

/// Initialize Syscall MSRs (STAR, LSTAR, FMASK).
pub unsafe fn init_syscalls() {
    use x86_64::registers::model_specific::{LStar, Star, SFMask, KernelGsBase};
    use x86_64::registers::control::Efer;
    use x86_64::registers::control::EferFlags;
    use crate::gdt;

    let selectors = gdt::get_selectors();

    // Enable syscall instruction
    Efer::update(|f| f.insert(EferFlags::SYSTEM_CALL_EXTENSIONS));

    // STAR: CS/SS for syscall and sysret
    Star::write(
        selectors.user_code_selector,
        selectors.user_data_selector,
        selectors.kernel_code_selector,
        selectors.kernel_data_selector,
    ).unwrap();

    // LSTAR: Entry point for syscall instruction
    LStar::write(x86_64::VirtAddr::new(syscall_entry as *const () as u64));

    // FMASK: RFLAGS bits to mask on syscall (disable interrupts)
    SFMask::write(x86_64::registers::rflags::RFlags::INTERRUPT_FLAG);

    // Initialize KERNEL_GS_BASE to ensure swapgs works safely.
    // For now, we set it to 0 as we don't use GS for kernel per-CPU state yet.
    KernelGsBase::write(x86_64::VirtAddr::new(0));
}

#[unsafe(naked)]
unsafe extern "C" fn syscall_entry() -> ! {
    core::arch::naked_asm!(
        // CPU automatically saves RIP to RCX and RFLAGS to R11.
        "swapgs",
        "mov r12, rsp",
        "mov rsp, [rip + {kernel_stack_ptr}]",

        // Construct ProcessContext on stack (matches struct order)
        // Corrected selectors: RPL 3 (bits 0-1) + GDT Index
        "push 0x1b", // ss (user data selector 0x18 | 0x3)
        "push r12",  // rsp
        "push r11",  // rflags
        "push 0x23", // cs (user code selector 0x20 | 0x3)
        "push rcx",  // rip

        "push rax",
        "push rbx",
        "push rcx",
        "push rdx",
        "push rsi",
        "push rdi",
        "push rbp",
        "push r8",
        "push r9",
        "push r10",
        "push r11",
        "push r12",
        "push r13",
        "push r14",
        "push r15",

        "mov rdi, rsp",
        "call {dispatcher}",

        // Restore context
        "pop r15",
        "pop r14",
        "pop r13",
        "pop r12",
        "pop r11",
        "pop r10",
        "pop r9",
        "pop r8",
        "pop rbp",
        "pop rdi",
        "pop rsi",
        "pop rdx",
        "pop rcx",
        "pop rbx",
        "pop rax",

        "pop rcx",
        "add rsp, 8", // skip cs
        "pop r11",
        "pop rsp",
        "add rsp, 8", // skip ss

        "swapgs",
        "sysretq",
        kernel_stack_ptr = sym SYSCALL_STACK_PTR,
        dispatcher = sym syscall_dispatcher,
    )
}

#[no_mangle]
extern "C" fn syscall_dispatcher(context: &mut ProcessContext) {
    let syscall_num = context.rax;

    match syscall_num {
        0 => sys_exit(context.rdi),
        1 => context.rax = sys_write(context.rdi, context.rsi, context.rdx),
        _ => {
            serial_println!("[WRAITH] Unknown syscall: {}", syscall_num);
            context.rax = 0xFFFFFFFFFFFFFFFF;
        }
    }
}

fn sys_exit(code: u64) -> ! {
    serial_println!("[WRAITH] Process exited with code: {}", code);
    println!("[WRAITH] Process exited with code: {}", code);
    loop {
        x86_64::instructions::hlt();
    }
}

fn sys_write(fd: u64, buf: u64, len: u64) -> u64 {
    if fd == 1 {
        if let Some(ref mm) = *crate::memory::manager::MEMORY_MANAGER.lock() {
            if mm.validate_user_ptr(buf, len) {
                 let s = unsafe { core::slice::from_raw_parts(buf as *const u8, len as usize) };
                 if let Ok(st) = core::str::from_utf8(s) {
                     serial_println!("[USER] {}", st);
                     println!("[USER] {}", st);
                     return len;
                 }
            }
        }
    }
    0
}

static mut SYSCALL_STACK: [u8; 4096 * 4] = [0; 4096 * 4];
#[no_mangle]
static mut SYSCALL_STACK_PTR: u64 = 0;

pub unsafe fn init_syscall_stack() {
    SYSCALL_STACK_PTR = core::ptr::addr_of!(SYSCALL_STACK) as u64 + 4096 * 4;
}
