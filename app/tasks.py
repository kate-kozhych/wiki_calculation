from app.celery_app import celery_app
from app.fetcher import Fetcher
import math
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="calculate_pi")
def calculate_pi(self, n: int):
    self.update_state(state='PROGRESS', 
    meta={'progress': 0.0, 'status': 'Starting calculation...'})
    fetcher=Fetcher()
    objects=["Earth","Saturn", "Moon"]
    n = min(max(1, n), len(objects))
    objects_to_use=objects[:n]
    pi_values = []
    objects_data = []
    for i, obj_name in enumerate(objects_to_use):
        progress = (i + 0.5) / n
        self.update_state(state='PROGRESS', 
        meta={
                'progress': progress,
                'status': f'Fetching data for {obj_name}...',
                'current_object': obj_name
            }
        )
        try:
            data=fetcher.fetch_cosmic_object(obj_name)
            if data:
                pi = data["circumference_km"] / (2 * data["radius_km"])
                pi_values.append(pi)
                objects_data.append({
                        "name": obj_name,
                        "radius_km": data["radius_km"],
                        "circumference_km": data["circumference_km"],
                        "calculated_pi": round(pi, 10),
                        "error_percent": round(abs(pi - math.pi) / math.pi * 100, 6)
                    })
                logger.info(f"{obj_name}: π = {pi:.10f}")    
            else:
                logger.error(f"Failed to fetch data for {obj_name}")
                objects_data.append({
                    "name": obj_name,
                    "error": "Failed to fetch data"
                })
        except Exception as e:
            logger.error(f"Error processing {obj_name}: {e}")
            objects_data.append({
                "name": obj_name,
                "error": str(e)
            })
        time.sleep(10)
        progress = (i + 1) / n
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': progress,
                'status': f'Completed {obj_name}',
                'objects_processed': i + 1
            }
        )

    if not pi_values:
        return {
            "error": "Failed to fetch data for all objects",
            "objects_used": 0,
            "objects_data": objects_data
        }

    average_pi = sum(pi_values) / len(pi_values)
    error_percent = abs(average_pi - math.pi) / math.pi * 100
    result = {
    "pi": round(average_pi, 10),
    "objects_used": len(pi_values),
    "objects_requested": n,
    "objects_data": objects_data,
    "error_percent": round(error_percent, 6),
    "real_pi": round(math.pi, 10)
    }
    logger.info(f"\nCalculation complete")
    logger.info(f"   Average π: {average_pi:.10f}")
    logger.info(f"   Objects used: {len(pi_values)}/{n}")
    logger.info(f"   Error: {error_percent:.6f}%")
    
    return result
    


