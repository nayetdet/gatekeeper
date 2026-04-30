import asyncio
from gatekeeper.logging import setup_logging
from gatekeeper.main import main

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
