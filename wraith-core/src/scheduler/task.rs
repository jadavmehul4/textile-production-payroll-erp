use x86_64::VirtAddr;
use crate::user::context::ProcessContext;
use crate::process::memory_space::MemorySpace;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskState {
    Ready,
    Running,
    Blocked,
}

pub struct Task {
    pub id: u64,
    pub context: ProcessContext,
    pub kernel_stack_top: VirtAddr,
    pub state: TaskState,
    pub time_slice: u64,
    pub sleep_ticks: u64,
    pub memory: MemorySpace,
}

impl Task {
    pub fn new(id: u64, kernel_stack_top: VirtAddr, memory: MemorySpace) -> Self {
        Self {
            id,
            context: ProcessContext::default(),
            kernel_stack_top,
            state: TaskState::Ready,
            time_slice: 10,
            sleep_ticks: 0,
            memory,
        }
    }
}
