pub mod task;
pub mod run_queue;
pub mod context_switch;
pub mod timer;
pub mod spinlock;

use self::run_queue::RUN_QUEUE;
use self::task::TaskState;

/// Tick handler called by the timer interrupt.
pub fn tick() {
    let mut rq = RUN_QUEUE.lock();

    // Process sleeping tasks
    for task in rq.tasks.iter_mut() {
        if task.state == TaskState::Blocked && task.sleep_ticks > 0 {
            task.sleep_ticks -= 1;
            if task.sleep_ticks == 0 {
                task.state = TaskState::Ready;
            }
        }
    }

    if let Some(task) = rq.get_current_mut() {
        if task.time_slice > 0 {
            task.time_slice -= 1;
        }
        if task.time_slice == 0 {
            task.state = TaskState::Ready;
            set_reschedule_flag();
        }
    }
}

static mut RESCHEDULE_REQUIRED: bool = false;

pub fn set_reschedule_flag() {
    unsafe { RESCHEDULE_REQUIRED = true; }
}

pub fn should_reschedule() -> bool {
    unsafe { RESCHEDULE_REQUIRED }
}

pub fn clear_reschedule_flag() {
    unsafe { RESCHEDULE_REQUIRED = false; }
}

/// The main scheduler entry point.
pub fn schedule() {
    if !should_reschedule() { return; }
    clear_reschedule_flag();

    let mut rq = RUN_QUEUE.lock();
    let old_idx = rq.current_task_idx;

    if let Some(next_idx) = rq.select_next() {
        if let Some(old_idx) = old_idx {
            if old_idx == next_idx { return; }

            unsafe {
                // 1. Switch Address Space (CR3)
                let next_pml4 = rq.tasks[next_idx].memory.pml4_phys;
                core::arch::asm!("mov cr3, {}", in(reg) next_pml4.as_u64());

                // 2. Perform Context Switch
                let old_ptr = &mut rq.tasks[old_idx].context as *mut _;
                let next_ptr = &rq.tasks[next_idx].context as *const _;
                rq.tasks[next_idx].state = TaskState::Running;
                rq.tasks[next_idx].time_slice = 10;

                core::mem::drop(rq);
                context_switch::switch_to(old_ptr, next_ptr);
            }
        } else {
            unsafe {
                // First switch from boot
                let next_pml4 = rq.tasks[next_idx].memory.pml4_phys;
                core::arch::asm!("mov cr3, {}", in(reg) next_pml4.as_u64());

                rq.tasks[next_idx].state = TaskState::Running;
                rq.tasks[next_idx].time_slice = 10;
                let next_ptr = &rq.tasks[next_idx].context as *const _;
                core::mem::drop(rq);

                let mut dummy = crate::user::context::ProcessContext::default();
                context_switch::switch_to(&mut dummy, next_ptr);
            }
        }
    }
}
