import bcrypt

class PinAuth:
    """
    Handles secure PIN storage and verification using bcrypt hashing.
    """
    def __init__(self):
        # Default hashed PIN for simulation (e.g., '1234')
        self._hashed_pin = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt())

    def set_pin(self, pin: str):
        """
        Hashes and stores a new PIN.
        """
        self._hashed_pin = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())

    def verify_pin(self, input_pin: str) -> bool:
        """
        Verifies the provided PIN against the stored hash.
        """
        if not self._hashed_pin:
            return False
        return bcrypt.checkpw(input_pin.encode('utf-8'), self._hashed_pin)
