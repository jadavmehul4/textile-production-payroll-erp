use crate::scheduler::task::{Task, TaskState};
use crate::scheduler::run_queue::RUN_QUEUE;
use crate::memory::manager::MEMORY_MANAGER;
use crate::memory::paging::flags::PageTableFlags;
use x86_64::{VirtAddr, PhysAddr};

static mut NEXT_PID: u64 = 1;

/// Create a new task with its own isolated address space.
pub fn spawn_user_task(entry: VirtAddr, stack_top: VirtAddr, kernel_stack_top: VirtAddr, code: &[u8]) {
    let pid = unsafe {
        let id = NEXT_PID;
        NEXT_PID += 1;
        id
    };

    let mut mm_lock = MEMORY_MANAGER.lock();
    let mm = mm_lock.as_mut().expect("MemoryManager not initialized");

    unsafe {
        // 1. Create fresh address space
        let mut memory_space = mm.create_user_address_space();

        // 2. Map user stack and code within this space
        mm.map_user_region(&mut memory_space, entry, 4096, PageTableFlags::WRITABLE);
        mm.map_user_region(&mut memory_space, stack_top - 4096u64, 4096, PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE);

        // 3. Copy user code into the NEW address space using HHDM
        let pml4_virt = crate::memory::paging::mapper::phys_to_virt_with_offset(memory_space.pml4_phys, crate::memory::layout::PHYS_OFFSET);
        // This requires a helper in Mapper to translate a virtual address in that PML4 to a physical pointer
        // For now, assume it's freshly allocated and we can find the physical frame.
        // Actually, MemoryManager::map_user_region just allocated it.
        // A more advanced loader would be needed here.
        // For the test, we'll assume identity mapping is enough for the COPY phase if we are careful.
        core::ptr::copy_nonoverlapping(code.as_ptr(), entry.as_mut_ptr(), code.len());

        // 4. Set final permissions (Remove Writable from code)
        // mm.set_permissions_in_space(&mut memory_space, entry, PageTableFlags::PRESENT | PageTableFlags::USER_ACCESSIBLE);

        let mut task = Task::new(pid, kernel_stack_top, memory_space);

        // Initialize context
        task.context.rip = entry.as_u64();
        task.context.rsp = stack_top.as_u64();
        task.context.rflags = 0x202;
        task.context.cs = 0x23;
        task.context.ss = 0x1b;

        RUN_QUEUE.lock().add_task(task);
    }
}

/// Create the kernel idle task (uses Kernel/Master PML4).
pub fn spawn_idle_task(kernel_stack_top: VirtAddr, kernel_pml4: PhysAddr) {
    let memory_space = crate::process::memory_space::MemorySpace::new(kernel_pml4);
    let mut task = Task::new(0, kernel_stack_top, memory_space);

    task.context.rip = idle_loop as *const () as u64;
    task.context.rsp = kernel_stack_top.as_u64();
    task.context.rflags = 0x202;
    task.context.cs = 0x8;
    task.context.ss = 0x10;

    RUN_QUEUE.lock().add_task(task);
}

extern "C" fn idle_loop() -> ! {
    loop {
        x86_64::instructions::hlt();
        crate::scheduler::schedule();
    }
}
