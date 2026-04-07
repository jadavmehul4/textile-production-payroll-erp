use crate::user::context::ProcessContext;

/// Perform a low-level context switch between two tasks.
/// Swaps stacks and restores GPRs.
#[unsafe(naked)]
pub unsafe extern "C" fn switch_to(old_context: *mut ProcessContext, new_context: *const ProcessContext) {
    core::arch::naked_asm!(
        "mov [rdi + 0x00], r15",
        "mov [rdi + 0x08], r14",
        "mov [rdi + 0x10], r13",
        "mov [rdi + 0x18], r12",
        "mov [rdi + 0x20], r11",
        "mov [rdi + 0x28], r10",
        "mov [rdi + 0x30], r9",
        "mov [rdi + 0x38], r8",
        "mov [rdi + 0x40], rbp",
        "mov [rdi + 0x48], rdi",
        "mov [rdi + 0x50], rsi",
        "mov [rdi + 0x58], rdx",
        "mov [rdi + 0x60], rcx",
        "mov [rdi + 0x68], rbx",
        "mov [rdi + 0x70], rax",

        "pop rax",
        "mov [rdi + 0x78], rax",
        "mov [rdi + 0x90], rsp",

        "mov r15, [rsi + 0x00]",
        "mov r14, [rsi + 0x08]",
        "mov r13, [rsi + 0x10]",
        "mov r12, [rsi + 0x18]",
        "mov r11, [rsi + 0x20]",
        "mov r10, [rsi + 0x28]",
        "mov r9,  [rsi + 0x30]",
        "mov r8,  [rsi + 0x38]",
        "mov rbp, [rsi + 0x40]",
        "mov rdi, [rsi + 0x48]",
        "mov rsi, [rsi + 0x50]",
        "mov rdx, [rsi + 0x58]",
        "mov rcx, [rsi + 0x60]",
        "mov rbx, [rsi + 0x68]",
        "mov rax, [rsi + 0x70]",

        "mov rsp, [rsi + 0x90]",
        "push [rsi + 0x78]",

        "ret",
    );
}
