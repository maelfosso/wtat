from .special_rn import extract_ads_from_special_rn
from .sunday_rn import extract_ads_from_sunday_rn

def split_ads(message: str, post_type: str) -> list[str]:
    fn = extract_ads_from_sunday_rn if post_type == 'Dimanche' else extract_ads_from_special_rn
    return fn(message) or []
