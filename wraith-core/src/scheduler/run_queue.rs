use alloc::collections::VecDeque;
use spin::Mutex;
use crate::scheduler::task::{Task, TaskState};
use lazy_static::lazy_static;

pub struct RunQueue {
    pub tasks: VecDeque<Task>,
    pub current_task_idx: Option<usize>,
}

impl RunQueue {
    pub const fn new() -> Self {
        Self {
            tasks: VecDeque::new(),
            current_task_idx: None,
        }
    }

    pub fn add_task(&mut self, task: Task) {
        self.tasks.push_back(task);
    }

    pub fn get_current_mut(&mut self) -> Option<&mut Task> {
        self.current_task_idx.and_then(|idx| self.tasks.get_mut(idx))
    }

    /// Select the next task to run (Round-Robin).
    pub fn select_next(&mut self) -> Option<usize> {
        if self.tasks.is_empty() { return None; }

        let start_idx = self.current_task_idx.map(|i| (i + 1) % self.tasks.len()).unwrap_or(0);

        for i in 0..self.tasks.len() {
            let idx = (start_idx + i) % self.tasks.len();
            if self.tasks[idx].state == TaskState::Ready {
                self.current_task_idx = Some(idx);
                return Some(idx);
            }
        }
        None
    }
}

lazy_static! {
    pub static ref RUN_QUEUE: Mutex<RunQueue> = Mutex::new(RunQueue::new());
}
