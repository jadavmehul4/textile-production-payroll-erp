use crate::{serial_println, println};
use crate::user::context::ProcessContext;

/// Initialize Syscall MSRs (STAR, LSTAR, FMASK).
pub unsafe fn init_syscalls() {
    use x86_64::registers::model_specific::{LStar, Star, SFMask, KernelGsBase};
    use x86_64::registers::control::Efer;
    use x86_64::registers::control::EferFlags;
    use crate::gdt;

    let selectors = gdt::get_selectors();

    Efer::update(|f| f.insert(EferFlags::SYSTEM_CALL_EXTENSIONS));

    Star::write(
        selectors.user_data_selector,
        selectors.user_code_selector,
        selectors.kernel_code_selector,
        selectors.kernel_data_selector,
    ).unwrap();

    LStar::write(x86_64::VirtAddr::new(syscall_entry as *const () as u64));
    SFMask::write(x86_64::registers::rflags::RFlags::INTERRUPT_FLAG);
    KernelGsBase::write(x86_64::VirtAddr::new(0));
}

#[unsafe(naked)]
unsafe extern "C" fn syscall_entry() -> ! {
    core::arch::naked_asm!(
        "swapgs",
        "mov r12, rsp",
        "mov rsp, [rip + {kernel_stack_ptr}]",

        "push 0x1b", // ss
        "push r12",  // rsp
        "push r11",  // rflags
        "push 0x23", // cs
        "push rcx",  // rip

        "push rax", "push rbx", "push rcx", "push rdx",
        "push rsi", "push rdi", "push rbp", "push r8",
        "push r9", "push r10", "push r11", "push r12",
        "push r13", "push r14", "push r15",

        "mov rdi, rsp",
        "call {dispatcher}",

        "pop r15", "pop r14", "pop r13", "pop r12",
        "pop r11", "pop r10", "pop r9", "pop r8",
        "pop rbp", "pop rdi", "pop rsi", "pop rdx",
        "pop rcx", "pop rbx", "pop rax",

        "pop rcx", "add rsp, 8", "pop r11", "pop rsp", "add rsp, 8",

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
        2 => sys_yield(),
        3 => sys_sleep(context.rdi),
        4 => context.rax = sys_exec(context.rdi),
        _ => {
            serial_println!("[WRAITH] Unknown syscall: {}", syscall_num);
            context.rax = 0xFFFFFFFFFFFFFFFF;
        }
    }
}

fn sys_exit(code: u64) -> ! {
    serial_println!("[WRAITH] Process exited with code: {}", code);
    loop { x86_64::instructions::hlt(); }
}

fn sys_yield() {
    crate::scheduler::set_reschedule_flag();
}

fn sys_sleep(ms: u64) {
    let mut rq = crate::scheduler::run_queue::RUN_QUEUE.lock();
    if let Some(task) = rq.get_current_mut() {
        task.state = crate::scheduler::task::TaskState::Blocked;
        task.sleep_ticks = ms / 10;
        crate::scheduler::set_reschedule_flag();
    }
}

fn sys_exec(path_ptr: u64) -> u64 {
    if let Some(ref mm) = *crate::memory::manager::MEMORY_MANAGER.lock() {
        // Basic path length check and validation
        if mm.validate_user_ptr(path_ptr, 1) {
            let mut path_buf = [0u8; 128];
            let mut i = 0;
            unsafe {
                while i < 127 {
                    let c = *( (path_ptr + i as u64) as *const u8 );
                    if c == 0 { break; }
                    path_buf[i] = c;
                    i += 1;
                }
            }
            if let Ok(path) = core::str::from_utf8(&path_buf[..i]) {
                serial_println!("[WRAITH] sys_exec: {}", path);
                if let Ok(_) = crate::process::process::exec_process(path) {
                    return 0; // Success (though context will be replaced)
                }
            }
        }
    }
    0xFFFFFFFFFFFFFFFF // Error
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
