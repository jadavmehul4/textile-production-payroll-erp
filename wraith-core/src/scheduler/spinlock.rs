use core::sync::atomic::{AtomicBool, Ordering};
use core::cell::UnsafeCell;
use x86_64::instructions::interrupts;

/// A spinlock that disables interrupts while held.
pub struct InterruptSpinlock<T> {
    lock: AtomicBool,
    data: UnsafeCell<T>,
}

unsafe impl<T: Send> Sync for InterruptSpinlock<T> {}
unsafe impl<T: Send> Send for InterruptSpinlock<T> {}

impl<T> InterruptSpinlock<T> {
    pub const fn new(data: T) -> Self {
        Self {
            lock: AtomicBool::new(false),
            data: UnsafeCell::new(data),
        }
    }

    pub fn lock(&self) -> InterruptGuard<'_, T> {
        let interrupts_enabled = interrupts::are_enabled();
        interrupts::disable();

        while self.lock.compare_exchange_weak(false, true, Ordering::Acquire, Ordering::Relaxed).is_err() {
            core::hint::spin_loop();
        }

        InterruptGuard {
            lock: self,
            interrupts_enabled,
        }
    }
}

pub struct InterruptGuard<'a, T> {
    lock: &'a InterruptSpinlock<T>,
    interrupts_enabled: bool,
}

impl<'a, T> core::ops::Deref for InterruptGuard<'a, T> {
    type Target = T;
    fn deref(&self) -> &T {
        unsafe { &*self.lock.data.get() }
    }
}

impl<'a, T> core::ops::DerefMut for InterruptGuard<'a, T> {
    fn deref_mut(&mut self) -> &mut T {
        unsafe { &mut *self.lock.data.get() }
    }
}

impl<'a, T> Drop for InterruptGuard<'a, T> {
    fn drop(&mut self) {
        self.lock.lock.store(false, Ordering::Release);
        if self.interrupts_enabled {
            interrupts::enable();
        }
    }
}
