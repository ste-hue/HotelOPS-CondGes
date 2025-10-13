#!/usr/bin/env python3
"""
CONDGES Dashboard Runner
Production-ready startup script
"""

import os
import sys
from app import app, logger

def main():
    """Main runner function"""
    
    # Environment configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting CONDGES Dashboard")
    logger.info(f"📍 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🐛 Debug: {debug}")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("👋 Dashboard stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
