import asyncio
import os
import sys
import multiprocessing
from loguru import logger
from tools.base_tool import BaseTool

class SandboxExecutor:
    """Production-grade executor for validated code using isolated process pools."""

    async def execute_tool_logic(self, code: str, kwargs: dict):
        """Runs validated code in a highly restricted process-based sandbox."""
        logger.info("Jules AI: Initializing sandbox for tool execution...")

        # Define the worker function for the process pool
        def worker(code_str, args_dict, queue):
            # Capture stdout
            import sys, io
            from tools.base_tool import BaseTool

            stdout = io.StringIO()
            sys.stdout = stdout

            # Ultra-restricted namespace
            safe_globals = {
                "BaseTool": BaseTool,
                "logger": logger,
                "__builtins__": {
                    "print": print, "range": range, "len": len, "list": list, "dict": dict,
                    "str": str, "int": int, "float": float, "bool": bool, "Exception": Exception,
                    "sum": sum, "min": min, "max": max, "abs": abs, "round": round
                }
            }

            try:
                local_ns = {}
                exec(code_str, safe_globals, local_ns)

                # Identify the tool class
                tool_class = None
                for attr in local_ns.values():
                    if isinstance(attr, type) and issubclass(attr, BaseTool) and attr is not BaseTool:
                        tool_class = attr
                        break

                if tool_class:
                    instance = tool_class()
                    # Execute logic synchronously if not async, or use a bridge
                    # Since the user tools are async, we need an event loop in the worker process
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(instance.execute(**args_dict))
                    queue.put({"status": "success", "result": result, "output": stdout.getvalue()})
                else:
                    queue.put({"status": "error", "message": "No valid tool class found."})
            except Exception as e:
                queue.put({"status": "error", "message": str(e), "output": stdout.getvalue()})

        # Use a Queue to get result from process
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=worker, args=(code, kwargs, queue))

        try:
            p.start()
            # Wait for result with timeout
            start_time = asyncio.get_event_loop().time()
            while p.is_alive():
                if asyncio.get_event_loop().time() - start_time > 30.0:
                    p.terminate()
                    return {"status": "error", "message": "Sandbox execution timeout."}
                await asyncio.sleep(0.1)

            if not queue.empty():
                return queue.get()
            return {"status": "error", "message": "Sandbox process crashed or returned no data."}

        except Exception as e:
            logger.error("Sandbox initialization failed: {}", e)
            return {"status": "error", "message": str(e)}
        finally:
            if p.is_alive(): p.join()
