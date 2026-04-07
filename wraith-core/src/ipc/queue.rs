use alloc::collections::VecDeque;
use crate::ipc::message::Message;

/// Per-process mailbox queue.
pub struct MessageQueue {
    queue: VecDeque<Message>,
    max_capacity: usize,
}

impl MessageQueue {
    pub fn new(max_capacity: usize) -> Self {
        Self {
            queue: VecDeque::new(),
            max_capacity,
        }
    }

    pub fn push(&mut self, msg: Message) -> Result<(), ()> {
        if self.queue.len() >= self.max_capacity {
            return Err(());
        }
        self.queue.push_back(msg);
        Ok(())
    }

    pub fn pop(&mut self) -> Option<Message> {
        self.queue.pop_front()
    }

    pub fn is_empty(&self) -> bool {
        self.queue.is_empty()
    }
}
