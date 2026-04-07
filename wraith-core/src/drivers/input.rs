use alloc::collections::VecDeque;
use spin::Mutex;
use lazy_static::lazy_static;

/// Bounded kernel-side input buffer for keyboard and other input devices.
pub struct InputBuffer {
    buffer: VecDeque<u8>,
    max_size: usize,
}

impl InputBuffer {
    pub fn new(max_size: usize) -> Self {
        Self {
            buffer: VecDeque::with_capacity(max_size),
            max_size,
        }
    }

    /// Push a character into the buffer.
    pub fn push(&mut self, byte: u8) {
        if self.buffer.len() < self.max_size {
            self.buffer.push_back(byte);

            // Wake up tasks blocked on input read
            self.wakeup_readers();
        }
    }

    /// Pop a character from the buffer.
    pub fn pop(&mut self) -> Option<u8> {
        self.buffer.pop_front()
    }

    pub fn is_empty(&self) -> bool {
        self.buffer.is_empty()
    }

    fn wakeup_readers(&self) {
        // Implementation logic to wake up tasks blocked on sys_read_input
        let mut rq = crate::scheduler::run_queue::RUN_QUEUE.lock();
        for task in rq.tasks.iter_mut() {
            // Future: track which tasks are specifically blocked on input
            if task.state == crate::scheduler::task::TaskState::Blocked {
                task.state = crate::scheduler::task::TaskState::Ready;
            }
        }
    }
}

lazy_static! {
    pub static ref KERNEL_INPUT: Mutex<InputBuffer> = Mutex::new(InputBuffer::new(1024));
}
