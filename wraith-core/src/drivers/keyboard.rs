use x86_64::instructions::port::Port;
use crate::drivers::device::Device;

pub struct Keyboard;

impl Device for Keyboard {
    fn init(&self) {
        // Initialization logic for PS/2 keyboard if necessary
    }
}

impl Keyboard {
    /// Read a scancode from the PS/2 data port.
    pub fn read_scancode() -> Option<u8> {
        let mut status_port = Port::<u8>::new(0x64);
        let mut data_port = Port::<u8>::new(0x60);

        unsafe {
            // Check if Output Buffer Full (bit 0)
            if status_port.read() & 0x01 != 0 {
                Some(data_port.read())
            } else {
                None
            }
        }
    }

    /// Translate PS/2 Scancode (Set 1) to ASCII.
    pub fn scancode_to_ascii(scancode: u8) -> Option<char> {
        match scancode {
            0x1E => Some('a'), 0x30 => Some('b'), 0x2E => Some('c'), 0x20 => Some('d'),
            0x12 => Some('e'), 0x21 => Some('f'), 0x22 => Some('g'), 0x23 => Some('h'),
            0x17 => Some('i'), 0x24 => Some('j'), 0x25 => Some('k'), 0x26 => Some('l'),
            0x32 => Some('m'), 0x31 => Some('n'), 0x18 => Some('o'), 0x19 => Some('p'),
            0x10 => Some('q'), 0x13 => Some('r'), 0x1F => Some('s'), 0x14 => Some('t'),
            0x16 => Some('u'), 0x2F => Some('v'), 0x11 => Some('w'), 0x2D => Some('x'),
            0x15 => Some('y'), 0x2C => Some('z'),
            0x02 => Some('1'), 0x03 => Some('2'), 0x04 => Some('3'), 0x05 => Some('4'),
            0x06 => Some('5'), 0x07 => Some('6'), 0x08 => Some('7'), 0x09 => Some('8'),
            0x0A => Some('9'), 0x0B => Some('0'),
            0x39 => Some(' '), 0x1C => Some('\n'),
            _ => None,
        }
    }
}
