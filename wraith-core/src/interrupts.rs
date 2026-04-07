use x86_64::structures::idt::{InterruptDescriptorTable, InterruptStackFrame, PageFaultErrorCode};
use crate::{println, serial_println};
use lazy_static::lazy_static;
use crate::gdt;
use crate::memory::paging;

lazy_static! {
    static ref IDT: InterruptDescriptorTable = {
        let mut idt = InterruptDescriptorTable::new();
        idt.breakpoint.set_handler_fn(breakpoint_handler);
        unsafe {
            idt.double_fault.set_handler_fn(double_fault_handler)
                .set_stack_index(gdt::DOUBLE_FAULT_IST_INDEX);
        }
        idt.page_fault.set_handler_fn(page_fault_handler);
        idt.general_protection_fault.set_handler_fn(general_protection_fault_handler);
        idt.divide_error.set_handler_fn(divide_error_handler);

        // Timer Interrupt (Local APIC)
        idt[32].set_handler_fn(timer_interrupt_handler);

        idt
    };
}

pub fn init_idt() {
    IDT.load();
}

extern "x86-interrupt" fn timer_interrupt_handler(
    _stack_frame: InterruptStackFrame)
{
    crate::scheduler::tick();
    unsafe {
        crate::scheduler::timer::send_eoi();
    }
}

extern "x86-interrupt" fn breakpoint_handler(
    stack_frame: InterruptStackFrame)
{
    serial_println!("EXCEPTION: BREAKPOINT\n{:#?}", stack_frame);
    println!("EXCEPTION: BREAKPOINT\n{:#?}", stack_frame);
}

extern "x86-interrupt" fn double_fault_handler(
    stack_frame: InterruptStackFrame, _error_code: u64) -> !
{
    panic!("EXCEPTION: DOUBLE FAULT\n{:#?}", stack_frame);
}

extern "x86-interrupt" fn page_fault_handler(
    stack_frame: InterruptStackFrame,
    error_code: PageFaultErrorCode,
) {
    use x86_64::registers::control::Cr2;

    let fault_addr = Cr2::read();
    serial_println!("EXCEPTION: PAGE FAULT");
    serial_println!("Accessed Address: {:?}", fault_addr);
    serial_println!("Error Code: {:?}", error_code);
    serial_println!("{:#?}", stack_frame);

    // Guard Page Detection
    if paging::is_guard_page_violation(fault_addr.as_u64()) {
         serial_println!("[WRAITH ALERT] STACK OVERRUN DETECTED (Guard Page Access)");
         println!("[WRAITH ALERT] STACK OVERRUN DETECTED (Guard Page Access)");
    } else if fault_addr.as_u64() < 0x1000 {
         serial_println!("[WRAITH ALERT] CRITICAL NULL POINTER ACCESS");
         println!("[WRAITH ALERT] CRITICAL NULL POINTER ACCESS");
    }

    println!("EXCEPTION: PAGE FAULT");
    println!("Accessed Address: {:?}", fault_addr);

    panic!("PAGE FAULT CANNOT BE RECOVERED AT THIS STAGE");
}

extern "x86-interrupt" fn general_protection_fault_handler(
    stack_frame: InterruptStackFrame, error_code: u64)
{
    panic!("EXCEPTION: GENERAL PROTECTION FAULT (Error Code: {})\n{:#?}", error_code, stack_frame);
}

extern "x86-interrupt" fn divide_error_handler(
    stack_frame: InterruptStackFrame)
{
    panic!("EXCEPTION: DIVIDE BY ZERO\n{:#?}", stack_frame);
}
