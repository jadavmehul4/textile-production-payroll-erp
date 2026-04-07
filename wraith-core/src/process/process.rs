use crate::scheduler::task::{Task, TaskState};
use crate::scheduler::run_queue::RUN_QUEUE;
use crate::memory::manager::MEMORY_MANAGER;
use crate::memory::paging::flags::PageTableFlags;
use crate::elf::loader::ElfLoader;
use crate::fs::vfs;
use x86_64::{VirtAddr, PhysAddr};

static mut NEXT_PID: u64 = 1;

#[derive(Debug)]
pub enum ExecError {
    FileNotFound,
    InvalidElf,
    LoadingFailed,
}

/// Create a new process by loading an ELF image.
pub fn spawn_elf_process(elf_data: &[u8], kernel_stack_top: VirtAddr) {
    let pid = unsafe {
        let id = NEXT_PID;
        NEXT_PID += 1;
        id
    };

    let loader = ElfLoader::new(elf_data);
    let loaded = unsafe {
        loader.load().expect("Failed to load ELF process")
    };

    let user_stack_top = VirtAddr::new(0x0000_7FFF_FFFF_F000);
    unsafe {
        if let Some(ref mm) = *MEMORY_MANAGER.lock() {
            let mut space = loaded.memory_space;
            mm.map_user_region(&mut space, user_stack_top - 1024 * 1024u64, 1024 * 1024, PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE);

            let mut task = Task::new(pid, kernel_stack_top, space);
            task.context.rip = loaded.entry_point;
            task.context.rsp = user_stack_top.as_u64();
            task.context.rflags = 0x202;
            task.context.cs = 0x23;
            task.context.ss = 0x1b;

            RUN_QUEUE.lock().add_task(task);
        }
    }
}

/// Create a new task with its own isolated address space (Manual loader).
pub fn spawn_user_task(entry: VirtAddr, stack_top: VirtAddr, kernel_stack_top: VirtAddr, code: &[u8]) {
    let pid = unsafe {
        let id = NEXT_PID;
        NEXT_PID += 1;
        id
    };

    let mut mm_lock = MEMORY_MANAGER.lock();
    let mm = mm_lock.as_mut().expect("MemoryManager not initialized");

    unsafe {
        let mut memory_space = mm.create_user_address_space();
        mm.map_user_region(&mut memory_space, entry, 4096, PageTableFlags::WRITABLE);
        mm.map_user_region(&mut memory_space, stack_top - 4096u64, 4096, PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE);

        core::ptr::copy_nonoverlapping(code.as_ptr(), entry.as_mut_ptr(), code.len());

        let mut task = Task::new(pid, kernel_stack_top, memory_space);
        task.context.rip = entry.as_u64();
        task.context.rsp = stack_top.as_u64();
        task.context.rflags = 0x202;
        task.context.cs = 0x23;
        task.context.ss = 0x1b;

        RUN_QUEUE.lock().add_task(task);
    }
}

/// Replace the current process's memory and context with a new ELF.
pub fn exec_process(path: &str) -> Result<(), ExecError> {
    let elf_data = vfs::read_all(path).ok_or(ExecError::FileNotFound)?;
    let loader = ElfLoader::new(&elf_data);
    let loaded = unsafe {
        loader.load().map_err(|_| ExecError::InvalidElf)?
    };

    let user_stack_top = VirtAddr::new(0x0000_7FFF_FFFF_F000);
    let mut space = loaded.memory_space;
    unsafe {
        if let Some(ref mm) = *MEMORY_MANAGER.lock() {
            mm.map_user_region(&mut space, user_stack_top - 1024 * 1024u64, 1024 * 1024, PageTableFlags::WRITABLE | PageTableFlags::NO_EXECUTE);
        }
    }

    let mut rq = RUN_QUEUE.lock();
    if let Some(task) = rq.get_current_mut() {
        task.memory = space;
        task.context.rip = loaded.entry_point;
        task.context.rsp = user_stack_top.as_u64();
        task.context.rflags = 0x202;

        unsafe {
            core::arch::asm!("mov cr3, {}", in(reg) task.memory.pml4_phys.as_u64());
        }
        Ok(())
    } else {
        Err(ExecError::LoadingFailed)
    }
}

/// Create the kernel idle task.
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
