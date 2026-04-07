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
pub const LAPIC_LVT_KBD: u32 = 0x330; // Placeholder for LINT0/LINT1 if needed
pub const LAPIC_TDCR: u32 = 0x3E0;
pub const LAPIC_TICR: u32 = 0x380;

/// Initialize the Local APIC Timer and I/O APIC mapping for Keyboard.
pub unsafe fn init() {
    let mut apic_base_msr = Msr::new(0x1B);
    let _apic_base_phys = apic_base_msr.read() & 0xFFFFF000;

    let lapic_virt = VirtAddr::new(MMIO_BASE + 0x1000);
    let lapic = lapic_virt.as_mut_ptr::<u32>();

    // Enable LAPIC
    write_reg(lapic, LAPIC_SVR, read_reg(lapic, LAPIC_SVR) | 0x100);

    // Timer Setup
    write_reg(lapic, LAPIC_TDCR, 0x3);
    write_reg(lapic, LAPIC_TIMER, (1 << 17) | 32);
    write_reg(lapic, LAPIC_TICR, 1000000);

    // Initialize PIC (8259) to map IRQs to vectors 32-47
    // This is necessary for keyboard IRQ1 to reach the CPU as vector 33.
    init_pic();
}

unsafe fn init_pic() {
    let mut cmd_1 = Port::<u8>::new(0x20);
    let mut data_1 = Port::<u8>::new(0x21);
    let mut cmd_2 = Port::<u8>::new(0xA0);
    let mut data_2 = Port::<u8>::new(0xA1);

    // ICW1: Init
    cmd_1.write(0x11);
    cmd_2.write(0x11);

    // ICW2: Vector offsets
    data_1.write(32);
    data_2.write(40);

    // ICW3: Cascading
    data_1.write(0x04);
    data_2.write(0x02);

    // ICW4: 8086 mode
    data_1.write(0x01);
    data_2.write(0x01);

    // Mask all except Keyboard (IRQ1) and Timer (IRQ0 - if used via PIC)
    // Here we use LAPIC for timer, but IRQ1 still comes through PIC or I/O APIC.
    data_1.write(0xFD); // 1111 1101 (Enable IRQ1)
    data_2.write(0xFF);
}

use x86_64::instructions::port::Port;

/// Signal End of Interrupt to LAPIC.
pub unsafe fn send_eoi() {
    let lapic_virt = VirtAddr::new(MMIO_BASE + 0x1000);
    let lapic = lapic_virt.as_mut_ptr::<u32>();
    write_reg(lapic, LAPIC_EOI, 0);

    // Also EOI to legacy PIC
    let mut port = Port::<u8>::new(0x20);
    port.write(0x20);
}

unsafe fn read_reg(base: *mut u32, offset: u32) -> u32 {
    core::ptr::read_volatile(base.add((offset / 4) as usize))
}

unsafe fn write_reg(base: *mut u32, offset: u32, val: u32) {
    core::ptr::write_volatile(base.add((offset / 4) as usize), val);
}
