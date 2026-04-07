pub mod context;
pub mod syscall;

use crate::gdt;
use x86_64::VirtAddr;

/// Start a user mode process by manually setting up the stack and using sysret or iret.
/// For x86_64, we often use a custom assembly stub to perform the privilege switch.
pub unsafe fn switch_to_user(entry: VirtAddr, stack_top: VirtAddr) -> ! {
    let selectors = gdt::get_selectors();

    // Data segment selectors for user mode (Ring 3)
    let ds_selector = selectors.user_data_selector.0;
    let cs_selector = selectors.user_code_selector.0;

    core::arch::asm!(
        "mov ds, {0:x}",
        "mov es, {0:x}",
        "mov fs, {0:x}",
        "mov gs, {0:x}",
        "push {0}",        // SS
        "push {1}",        // RSP
        "pushfq",          // RFLAGS
        "pop rax",
        "or rax, 0x200",   // Enable interrupts in user mode
        "push rax",
        "push {2}",        // CS
        "push {3}",        // RIP
        "iretq",
        in(reg) ds_selector as u64,
        in(reg) stack_top.as_u64(),
        in(reg) cs_selector as u64,
        in(reg) entry.as_u64(),
        options(noreturn)
    );
}
