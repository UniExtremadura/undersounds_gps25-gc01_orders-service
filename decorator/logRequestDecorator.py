from functools import wraps
from datetime import datetime
import time
from flask import request
import json
import os

def log(fichero_log):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            start_time = time.time()
            
            # Relative route into absolute route
            if not os.path.isabs(fichero_log):
                base_dir = os.path.dirname(os.path.abspath(__file__))
                fichero_log_abs = os.path.join(base_dir, fichero_log)
            else:
                fichero_log_abs = fichero_log 
                
            try:
                # Function exec
                response = f(*args, **kwargs)
                status_code = response[1] if isinstance(response, tuple) else 200
                success = True
            except Exception as e:
                status_code = 500
                success = False
                response = {"error": str(e)}, 500
                raise 
            
            finally:
                # Duration calc
                duration = time.time() - start_time
                
                # User info
                user_info = getattr(request, 'user_info', {})
                username = user_info.get('preferred_username', user_info.get('email', 'anon'))
                user_id = user_info.get('sub', 'unknown')
                
                # Request info
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "method": request.method,
                    "path": request.path,
                    "endpoint": f.__name__,
                    "user": username,
                    "user_id": user_id,
                    "status_code": status_code,
                    "success": success,
                    "duration_ms": round(duration * 1000, 2),
                    "ip": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', ''),
                    "query_params": dict(request.args)
                }
                
                # Write in log
                with open(fichero_log_abs, 'a', encoding='utf-8') as opened_file:
                    opened_file.write(f"{json.dumps(log_entry, ensure_ascii=False)}\n")
            
            return response
        return decorated
    return decorator