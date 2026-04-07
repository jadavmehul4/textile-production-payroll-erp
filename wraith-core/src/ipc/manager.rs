use alloc::collections::BTreeMap;
use spin::Mutex;
use crate::ipc::message::Message;
use crate::ipc::queue::MessageQueue;
use lazy_static::lazy_static;

#[derive(Debug)]
pub enum IPCError {
    ProcessNotFound,
    QueueFull,
}

pub struct IPCManager {
    queues: BTreeMap<u64, MessageQueue>,
}

impl IPCManager {
    pub const fn new() -> Self {
        Self {
            queues: BTreeMap::new(),
        }
    }

    /// Send a message to a target process.
    pub fn send(&mut self, target_pid: u64, msg: Message) -> Result<(), IPCError> {
        // Find or create queue for the target process
        let queue = self.queues.entry(target_pid).or_insert_with(|| MessageQueue::new(16));

        if queue.push(msg).is_err() {
            return Err(IPCError::QueueFull);
        }

        // Wake up target if it was blocked on receive
        self.wakeup_process(target_pid);

        Ok(())
    }

    /// Receive a message from the current process's queue.
    pub fn receive(&mut self, pid: u64) -> Option<Message> {
        let queue = self.queues.get_mut(&pid)?;
        queue.pop()
    }

    fn wakeup_process(&self, pid: u64) {
        let mut rq = crate::scheduler::run_queue::RUN_QUEUE.lock();
        for task in rq.tasks.iter_mut() {
            if task.id == pid && task.state == crate::scheduler::task::TaskState::Blocked {
                task.state = crate::scheduler::task::TaskState::Ready;
            }
        }
    }
}

lazy_static! {
    pub static ref IPC_MANAGER: Mutex<IPCManager> = Mutex::new(IPCManager::new());
}
