use x86_64::{VirtAddr};
use x86_64::registers::model_specific::Msr;
use crate::memory::layout::MMIO_BASE;

/// Local APIC Register Offsets
pub const LAPIC_ID: u32 = 0x20;
pub const LAPIC_VER: u32 = 0x30;
pub const LAPIC_TPR: u32 = 0x80;
pub const LAPIC_EOI: u32 = 0xB0;
pub const LAPIC_SVR: u32 = 0xF0;
pub const LAPIC_TIMER: u32 = 0x320;
pub const LAPIC_TDCR: u32 = 0x3E0;
pub const LAPIC_TICR: u32 = 0x380;

/// Initialize the Local APIC Timer for periodic interrupts.
pub unsafe fn init() {
    let mut apic_base_msr = Msr::new(0x1B);
    let _apic_base_phys = apic_base_msr.read() & 0xFFFFF000;

    let lapic_virt = VirtAddr::new(MMIO_BASE + 0x1000);
    let lapic = lapic_virt.as_mut_ptr::<u32>();

    // Enable LAPIC by setting bit 8 in SVR
    write_reg(lapic, LAPIC_SVR, read_reg(lapic, LAPIC_SVR) | 0x100);

    // Set TDCR to divide by 16
    write_reg(lapic, LAPIC_TDCR, 0x3);

    // Set Timer LVT to Periodic Mode (bit 17) and set vector to 32
    write_reg(lapic, LAPIC_TIMER, (1 << 17) | 32);

    // Set initial count (approximate for 10ms)
    write_reg(lapic, LAPIC_TICR, 1000000);
}

/// Signal End of Interrupt to LAPIC.
pub unsafe fn send_eoi() {
    let lapic_virt = VirtAddr::new(MMIO_BASE + 0x1000);
    let lapic = lapic_virt.as_mut_ptr::<u32>();
    write_reg(lapic, LAPIC_EOI, 0);
}

unsafe fn read_reg(base: *mut u32, offset: u32) -> u32 {
    core::ptr::read_volatile(base.add((offset / 4) as usize))
}

unsafe fn write_reg(base: *mut u32, offset: u32, val: u32) {
    core::ptr::write_volatile(base.add((offset / 4) as usize), val);
}
