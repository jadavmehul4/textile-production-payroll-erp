use crate::scheduler::task::{Task, TaskState};
use crate::scheduler::run_queue::RUN_QUEUE;
use x86_64::VirtAddr;

static mut NEXT_PID: u64 = 1;

/// Create a new task and add it to the run queue.
pub fn spawn_user_task(entry: VirtAddr, stack_top: VirtAddr, kernel_stack_top: VirtAddr) {
    let pid = unsafe {
        let id = NEXT_PID;
        NEXT_PID += 1;
        id
    };

    let mut task = Task::new(pid, kernel_stack_top);

    // Initialize user context for transition
    task.context.rip = entry.as_u64();
    task.context.rsp = stack_top.as_u64();
    task.context.rflags = 0x202; // Interrupts enabled
    task.context.cs = 0x23;      // User code
    task.context.ss = 0x1b;      // User data

    RUN_QUEUE.lock().add_task(task);
}

/// Create the kernel idle task.
pub fn spawn_idle_task(kernel_stack_top: VirtAddr) {
    let mut task = Task::new(0, kernel_stack_top);
    task.context.rip = idle_loop as *const () as u64;
    task.context.rsp = kernel_stack_top.as_u64();
    task.context.rflags = 0x202;
    task.context.cs = 0x8; // Kernel code
    task.context.ss = 0x10; // Kernel data

    RUN_QUEUE.lock().add_task(task);
}

extern "C" fn idle_loop() -> ! {
    loop {
        x86_64::instructions::hlt();
        crate::scheduler::schedule();
    }
}
