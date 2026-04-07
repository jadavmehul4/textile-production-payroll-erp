/// Core interface for hardware device drivers.
pub trait Device: Send + Sync {
    /// Initialize the hardware device.
    fn init(&self);
}
